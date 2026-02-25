from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated

from marketplaces.models import Product
from notifications.serializers import PriceNotificationSerializer


class CreatePriceNotificationView(CreateAPIView):
    serializer_class = PriceNotificationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        external_id = self.kwargs["external_id"]

        product = get_object_or_404(Product, external_id=external_id)

        serializer.save(
            user=self.request.user,
            product=product,

        )