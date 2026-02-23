import logging
from decimal import Decimal
from typing import List, Dict, Optional

from django.db import transaction, IntegrityError
from django.conf import settings
from marketplaces.models import Product, ProductOffer, PriceHistory
from marketplaces.services.base import BaseMarketProducts

logger = logging.getLogger(__name__)


class SyncResult:
    """Data class for synchronization results."""

    def __init__(self):
        self.products_created = 0
        self.offers_created = 0
        self.offers_updated = 0
        self.price_history_created = 0
        self.errors = []

    def __repr__(self):
        return (
            f"SyncResult(products={self.products_created}, "
            f"offers_created={self.offers_created}, "
            f"offers_updated={self.offers_updated}, "
            f"price_history={self.price_history_created}, "
            f"errors={len(self.errors)})"
        )


class ServicesSynchronizer:
    """
    Synchronizes product data from marketplace APIs to the database.

    Features:
    - Bulk operations for performance
    - Price change tracking
    - Transaction safety
    - Comprehensive logging
    """

    BULK_CREATE_BATCH_SIZE = getattr(settings, 'SYNC_BULK_BATCH_SIZE', 1000)
    PRICE_COMPARISON_PRECISION = Decimal('0.01')

    def __init__(self, market_client: BaseMarketProducts):
        """
        Initialize synchronizer with a market client.

        Args:
            market_client: Implementation of BaseMarketProducts interface
        """
        self.market_client = market_client
        self.store_name = market_client.get_store_name()

    def sync_all(self) -> SyncResult:
        """
        Fetch and synchronize all products from the marketplace.

        Returns:
            SyncResult object with operation statistics

        Raises:
            ValueError: If product data is invalid
            IntegrityError: If database constraints are violated
        """
        result = SyncResult()

        try:
            logger.info(f"Starting synchronization for store: {self.store_name}")
            products_data = self.market_client.fetch_products()

            if not products_data:
                logger.warning(f"No products fetched from {self.store_name}")
                return result

            self._bulk_process_items(products_data, result)
            logger.info(f"Synchronization completed: {result}")

        except Exception as e:
            logger.error(
                f"Synchronization failed for {self.store_name}: {e}",
                exc_info=True
            )
            result.errors.append(str(e))
            raise

        return result

    def _validate_product_data(self, item: dict) -> Optional[str]:
        """
        Validate required fields in product data.

        Returns:
            Error message if validation fails, None otherwise
        """
        required_fields = ['id', 'title', 'price']

        for field in required_fields:
            if field not in item:
                return f"Missing required field: {field}"

        if not isinstance(item['id'], (int, str)):
            return f"Invalid id type: {type(item['id'])}"

        try:
            float(item['price'])
        except (ValueError, TypeError):
            return f"Invalid price value: {item.get('price')}"

        return None

    def _bulk_process_items(
            self,
            products_list: List[dict],
            result: SyncResult
    ) -> None:
        """
        Process products in bulk: create/update products and offers.

        Args:
            products_list: List of product dictionaries from API
            result: SyncResult object to update with statistics
        """
        validated_products = []

        for item in products_list:
            error = self._validate_product_data(item)
            if error:
                logger.warning(f"Skipping invalid product: {error}")
                result.errors.append(error)
                continue
            validated_products.append(item)

        if not validated_products:
            logger.warning("No valid products to process")
            return

        external_ids = [str(item["id"]) for item in validated_products]

        existing_product_ids = set(
            Product.objects.filter(external_id__in=external_ids)
            .values_list("external_id", flat=True)
        )

        new_products = [
            Product(
                external_id=str(item["id"]),
                title=item["title"],
                category=item.get("category", ""),
                description=item.get("description", ""),
            )
            for item in validated_products
            if str(item["id"]) not in existing_product_ids
        ]

        if new_products:
            try:
                created = Product.objects.bulk_create(
                    new_products,
                    batch_size=self.BULK_CREATE_BATCH_SIZE
                )
                result.products_created = len(created)
                logger.info(f"Created {result.products_created} new products")
            except IntegrityError as e:
                logger.error(f"Failed to create products: {e}")
                result.errors.append(f"Product creation error: {e}")
                raise

        existing_offers_qs = (
            ProductOffer.objects
            .filter(product__external_id__in=external_ids, store_name=self.store_name)
            .select_related('product')
        )

        existing_offers: Dict[str, ProductOffer] = {
            offer.product.external_id: offer
            for offer in existing_offers_qs
        }

        products = Product.objects.filter(external_id__in=external_ids)
        products_map = {product.external_id: product for product in products}

        to_create = []
        to_update = []
        price_history = []

        for item in validated_products:
            ext_id = str(item["id"])
            new_price = Decimal(str(item["price"]))

            if ext_id not in existing_offers:
                product = products_map.get(ext_id)
                if product:
                    to_create.append(
                        ProductOffer(
                            product=product,
                            external_id=ext_id,
                            current_price_usd=new_price,
                            store_name=self.store_name
                        )
                    )
                else:
                    logger.warning(f"Product not found for external_id: {ext_id}")

            else:
                offer = existing_offers[ext_id]
                price_diff = abs(offer.current_price_usd - new_price)

                if price_diff >= self.PRICE_COMPARISON_PRECISION:
                    offer.current_price_usd = new_price
                    to_update.append(offer)

                    price_history.append(
                        PriceHistory(
                            store_product=offer,
                            price_usd=new_price
                        )
                    )

        try:
            with transaction.atomic():
                if to_create:
                    created_offers = ProductOffer.objects.bulk_create(
                        to_create,
                        batch_size=self.BULK_CREATE_BATCH_SIZE
                    )
                    result.offers_created = len(created_offers)
                    logger.info(f"Created {result.offers_created} new offers")

                if to_update:
                    ProductOffer.objects.bulk_update(
                        to_update,
                        ['current_price_usd'],
                        batch_size=self.BULK_CREATE_BATCH_SIZE
                    )
                    result.offers_updated = len(to_update)
                    logger.info(f"Updated {result.offers_updated} offers")

                if price_history:
                    PriceHistory.objects.bulk_create(
                        price_history,
                        batch_size=self.BULK_CREATE_BATCH_SIZE
                    )
                    result.price_history_created = len(price_history)
                    logger.info(
                        f"Created {result.price_history_created} price history records"
                    )

        except IntegrityError as e:
            logger.error(f"Database integrity error during sync: {e}")
            result.errors.append(f"Database error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during sync: {e}", exc_info=True)
            result.errors.append(f"Unexpected error: {e}")
            raise
