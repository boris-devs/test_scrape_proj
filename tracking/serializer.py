from rest_framework import serializers


class CreateTrackingProductsSerializer(serializers.Serializer):
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False, )
