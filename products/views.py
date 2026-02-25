from datetime import date, timedelta

from django.db.models import Min, Max, Avg, Q, Case, When, F, Value, CharField, IntegerField
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from marketplaces.models import Product
from products.serializers import ProductListSerializer, ProductDetailSerializer


class ListProductsTrackingView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        user = self.request.user
        today = date.today()
        last_30_days = today - timedelta(days=30)

        queryset = Product.objects.filter(tracking_products__user=user).annotate(
            min_price=Min(
                'offers__history__price_usd',
                filter=Q(offers__history__timestamp__date=today)
            ),
            max_price=Max(
                'offers__history__price_usd',
                filter=Q(offers__history__timestamp__date=today)
            ),

            avg_30d=Avg(
                'offers__history__price_usd',
                filter=Q(
                    offers__history__timestamp__date__gte=last_30_days,
                    offers__history__timestamp__date__lt=today
                )
            )
        ).annotate(
            trend_ordered=Case(
                When(min_price__gt=F('avg_30d'), then=Value(2)),
                When(max_price__lt=F('avg_30d'), then=Value(0)),
                default=Value(1),
                output_field=IntegerField()
            ),
            # for serializer
            trend=Case(
                When(min_price__gt=F('avg_30d'), then=Value('up')),
                When(max_price__lt=F('avg_30d'), then=Value('down')),
                default=Value('stable'),
                output_field=CharField()
            )
        )

        sort_by = self.request.query_params.get('sort', 'price')
        if sort_by == 'price':
            queryset = queryset.order_by('min_price')
        elif sort_by == 'trend':
            queryset = queryset.order_by('-trend_ordered', 'min_price')

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAuthenticated, ]

    lookup_field = 'external_id'

    def get_queryset(self):
        today = date.today()
        return super().get_queryset().annotate(
            min_price=Min('offers__history__price_usd', filter=Q(offers__history__timestamp__date=today)),
            max_price=Max('offers__history__price_usd', filter=Q(offers__history__timestamp__date=today))
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['today'] = date.today()
        return context
