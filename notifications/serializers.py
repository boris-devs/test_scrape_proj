from rest_framework import serializers

from notifications.models import PriceNotification


class PriceNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceNotification
        fields = ['target_price']