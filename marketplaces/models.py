from django.db import models


class Product(models.Model):
    external_id = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ProductOffer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='offers')
    store_name = models.CharField(max_length=100)
    external_id = models.CharField(max_length=100)

    current_price_usd = models.DecimalField(max_digits=12, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['store_name', 'external_id'],
                name='unique_store_product'
            )
        ]
        verbose_name = "Product Offer"
        verbose_name_plural = "Product Offers"


class PriceHistory(models.Model):
    store_product = models.ForeignKey(ProductOffer, on_delete=models.CASCADE, related_name='history')
    price_usd = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['store_product', 'timestamp']),
        ]