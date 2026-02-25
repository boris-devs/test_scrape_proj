from django.urls import path

from notifications.views import CreatePriceNotificationView

urlpatterns = [
    path("<str:external_id>/", CreatePriceNotificationView.as_view(), name="notification-detail"),
]