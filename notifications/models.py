from django.db import models
from django.contrib.auth.models import User
from marketplaces.models import Product


class PriceNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='price_notifications')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_notifications')
    target_price = models.DecimalField(max_digits=12, decimal_places=2)
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    triggered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'product', 'target_price')