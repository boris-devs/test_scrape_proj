from celery import shared_task
import httpx
from celery.utils.log import get_task_logger
from datetime import datetime

from currencies.models import Currency, CurrencyRate

logger = get_task_logger(__name__)


@shared_task(autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def periodic_usd_rate():
    logger.info("Starting periodic_usd_rate")

    URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"

    try:
        response = httpx.get(URL, timeout=10)
        response.raise_for_status()
        list_of_rates = response.json()
        usd_rate = validate_curr_data(list_of_rates, "USD")

        currency, _ = Currency.objects.get_or_create(
            code=usd_rate["cc"],
            defaults={"name": usd_rate["txt"]}
        )

        rate_date = datetime.strptime(usd_rate["exchangedate"], "%d.%m.%Y").date()

        CurrencyRate.objects.create(
            currency=currency,
            rate=usd_rate["rate"],
            date=rate_date
        )

        logger.info(f"USD rate saved: {usd_rate['rate']} for {rate_date}")

    except Exception as e:
        logger.error(f"Error in periodic_usd_rate: {e}", exc_info=True)
        raise e


def validate_curr_data(currencies: list[dict], currency_code: str) -> dict:
    if not isinstance(currencies, list):
        raise ValueError("Currencies data must be a list")

    currency_data = next(
        (item for item in currencies if item.get("cc", "").upper() == currency_code.upper()),
        None
    )

    if currency_data is None:
        raise ValueError(f"Currency {currency_code} not found")

    required_fields = {"rate", "cc", "txt", "exchangedate"}

    if not required_fields.issubset(currency_data.keys()):
        raise ValueError("Invalid currency data structure")

    return currency_data