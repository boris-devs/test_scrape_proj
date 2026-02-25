from django.urls import path

from tracking.views import CreateTrackingProductsView

urlpatterns = [
    path("create/", CreateTrackingProductsView.as_view(), name="create-tracking-products"),
]
