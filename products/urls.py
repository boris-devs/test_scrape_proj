from django.urls import path

from products.views import ListProductsTrackingView, ProductDetailView

urlpatterns = [
    path("tracking/",  ListProductsTrackingView.as_view(), name="list-products-tracking"),
    path("tracking/<str:external_id>/",  ProductDetailView.as_view(), name="list-products-tracking"),
]