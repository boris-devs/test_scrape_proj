from celery import shared_task
from django.core.mail import send_mail
from django.db.models import Min
from django.utils import timezone

from marketplaces.models import ProductOffer
from notifications.models import PriceNotification


@shared_task
def check_price_alerts():
    alerts = PriceNotification.objects.filter(is_sent=False)
    for alert in alerts:
        current_min_price = ProductOffer.objects.filter(product=alert.product)\
            .aggregate(min_price=Min('current_price_usd'))['min_price']

        if current_min_price is not None and current_min_price <= alert.target_price:
            send_mail(
                subject=f"Price was dropped {alert.product.title}!",
                message=f"Price on product {alert.product.title} was down {current_min_price}. "
                        f"Your goal is {alert.target_price}.",
                from_email='no-reply@example.com',
                recipient_list=[alert.user.email],
            )
            alert.is_sent = True
            alert.triggered_at = timezone.now()
            alert.save()