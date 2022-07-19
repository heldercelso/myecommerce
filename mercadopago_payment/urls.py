from django.urls import path

from .views import (
    PaymentView,
    PaymentFailureView,
    PaymentPendingView,
    PaymentSuccessView,
    payment_webhook
)

app_name = "payments"

urlpatterns = [
    path("process/", PaymentView.as_view(), name="process"),
    path("failure/", PaymentFailureView.as_view(), name="failure"),
    path("pending/", PaymentPendingView.as_view(), name="pending"),
    path("success/", PaymentSuccessView.as_view(), name="success"),
    path("webhook/", payment_webhook, name="webhook"),
]