from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from marketplaces.models import Product
from tracking.models import TrackingProducts
from tracking.serializer import CreateTrackingProductsSerializer


class CreateTrackingProductsView(CreateAPIView):
    serializer_class = CreateTrackingProductsSerializer
    permission_classes = [IsAuthenticated, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_ids = serializer.validated_data['product_ids']
        user = request.user

        try:
            existing_product_ids = set(
                TrackingProducts.objects
                .filter(user=user, product__external_id__in=product_ids)
                .values_list('product__external_id', flat=True)
            )

            ids_to_tracking = set(product_ids) - set(map(int, existing_product_ids))
            if not ids_to_tracking:
                return Response({"detail": "All products are already being tracked."}, status=status.HTTP_200_OK)

            products_to_track = Product.objects.filter(external_id__in=ids_to_tracking)

            tracking_objects = [TrackingProducts(user=user, product=product)
                                for product in products_to_track]

            TrackingProducts.objects.bulk_create(tracking_objects, ignore_conflicts=True)
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
