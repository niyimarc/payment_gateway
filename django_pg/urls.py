from django.urls import path
from django.conf import settings
from .views import StripeWebhookView, PayPalWebhookView

stripe_webhook_path = getattr(settings, "DJANGO_PG_STRIPE_WEBHOOK_PATH", "webhooks/stripe/")
paypal_webhook_path = getattr(settings, "DJANGO_PG_PAYPAL_WEBHOOK_PATH", "webhooks/paypal/")

urlpatterns = [
    path(stripe_webhook_path, StripeWebhookView.as_view(), name="stripe_webhook"),
    path(paypal_webhook_path, PayPalWebhookView.as_view(), name="paypal_webhook"),
]
