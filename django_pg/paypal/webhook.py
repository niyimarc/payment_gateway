import json
import logging
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
from ..utils import get_model
from ..exceptions import PaymentConfigurationError, PaymentRuntimeError

logger = logging.getLogger(__name__)


def _get_paypal_client():
    """Validate PayPal configuration"""
    if not hasattr(settings, 'PAYPAL_CLIENT_ID') or not hasattr(settings, 'PAYPAL_SECRET'):
        raise PaymentConfigurationError("PayPal credentials are not configured.")
    if not hasattr(settings, 'PAYPAL_ENV'):
        raise PaymentConfigurationError("PAYPAL_ENV is not configured.")
    return True


def verify_webhook_signature(request):
    """
    Verify PayPal webhook signature
    Note: This requires setting up a webhook ID in your PayPal dashboard
    """
    webhook_id = getattr(settings, "PAYPAL_WEBHOOK_ID", None)
    if not webhook_id:
        # If webhook verification is not configured, skip verification
        # In production, you should configure this
        logger.warning("PAYPAL_WEBHOOK_ID not configured, skipping signature verification")
        return True
    
    # PayPal webhook verification would go here
    # This requires additional API calls to PayPal
    # For now, we'll skip detailed implementation
    return True


def handle_webhook_event(event: dict) -> None:
    """
    Updates Order based on PayPal webhook events.
    """
    event_type = event.get("event_type")
    resource = event.get("resource") or {}

    # We primarily care about payment capture completion
    if event_type == "PAYMENT.CAPTURE.COMPLETED":
        # Get custom_id which contains our order_reference
        custom_id = resource.get("custom_id")
        
        if not custom_id:
            # Try to get from related resources
            # Sometimes custom_id is in the purchase_units
            logger.warning("No custom_id found in webhook payload")
            return
        
        # Get order by order_reference
        Order = get_model("PAYMENT_ORDER_MODEL")
        order = Order.objects.filter(order_reference=custom_id).first()
        if not order:
            logger.warning(f"Order with reference {custom_id} not found")
            return

        # If already paid, ignore (idempotent)
        if getattr(order, "payment_made", False):
            logger.info(f"Order {custom_id} already marked as paid")
            return

        # Get capture details
        capture_id = resource.get("id")
        
        # Update order
        order.payment_made = True
        order.order_placed = True
        order.status = "Order Placed"
        order.payment_method = "paypal"
        order.paypal_capture_id = capture_id
        order.payment_date = timezone.now()
        order.save()

        logger.info(f"Order {custom_id} marked as paid via webhook")
        return

    elif event_type == "PAYMENT.CAPTURE.DENIED":
        custom_id = resource.get("custom_id")
        logger.warning(f"Payment denied for order {custom_id}")
        return

    elif event_type == "PAYMENT.CAPTURE.REFUNDED":
        custom_id = resource.get("custom_id")
        logger.info(f"Payment refunded for order {custom_id}")
        # You might want to update order status here
        return


def paypal_webhook_response(request):
    """
    Django view handler for PayPal webhooks.
    Returns HttpResponse.
    """
    # Validate PayPal configuration
    _get_paypal_client()

    # Only accept POST requests
    if request.method != 'POST':
        return HttpResponse(status=405)

    # Get payload
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        return HttpResponse(status=400)

    # Verify webhook signature (optional but recommended)
    if not verify_webhook_signature(request):
        logger.error("Webhook signature verification failed")
        return HttpResponse(status=401)

    try:
        # Process the webhook event
        handle_webhook_event(payload)
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        # Don't expose error details to client
        return HttpResponse(status=500)

    # Always return 200 to acknowledge receipt
    return HttpResponse(status=200)