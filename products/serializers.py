from datetime import date

from django.db.models import Min, Q
from rest_framework import serializers
from marketplaces.models import Product, ProductOffer, PriceHistory


class ProductListSerializer(serializers.ModelSerializer):
    min_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    max_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    trend = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'external_id', 'title', 'min_price', 'max_price', 'trend']


class ProductOfferTodaySerializer(serializers.ModelSerializer):
    current_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, source='current_price_usd'
    )

    class Meta:
        model = ProductOffer
        fields = ['store_name', 'current_price']


class PriceHistorySerializer(serializers.Serializer):
    date = serializers.DateField()
    store_prices = serializers.DictField()  # {'Amazon': 1200, 'eBay': 1180, ...}
    avg_price = serializers.DecimalField(max_digits=12, decimal_places=2)


class ProductDetailSerializer(serializers.ModelSerializer):
    min_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    max_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    offers_today = serializers.SerializerMethodField()
    price_history_chart = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'external_id', 'title', 'description',
            'min_price', 'max_price',
            'offers_today', 'price_history_chart'
        ]

    def get_offers_today(self, obj):

        today = self.context.get('today', date.today())
        offers = obj.offers.annotate(
            today_price=Min('history__price_usd', filter=Q(history__timestamp__date=today))
        )
        return [{'store_name': o.store_name, 'current_price': o.today_price} for o in offers]

    def get_price_history_chart(self, obj):
        history_qs = PriceHistory.objects.filter(store_product__product=obj).order_by('timestamp')
        if not history_qs.exists():
            return []

        grouped = {}
        for h in history_qs:
            day = h.timestamp.date()
            if day not in grouped:
                grouped[day] = {'store_prices': {}, 'prices': []}
            grouped[day]['store_prices'][h.store_product.store_name] = float(h.price_usd)
            grouped[day]['prices'].append(float(h.price_usd))

        chart_data = []
        for day, data in grouped.items():
            chart_data.append({
                'date': day,
                'store_prices': data['store_prices'],
                'avg_price': sum(data['prices']) / len(data['prices'])
            })

        return chart_data