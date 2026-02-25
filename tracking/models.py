from django.db import models

class TrackingProducts(models.Model):
    product = models.ForeignKey('marketplaces.Product', on_delete=models.CASCADE, related_name='tracking_products')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)