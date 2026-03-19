from django.conf import settings
from django.urls import reverse
from ..exceptions import PaymentConfigurationError, PaymentRuntimeError
from . import paypal_services


def create_paypal_checkout(*, order, request, success_url: str = None, cancel_url: str = None):
    """
    Create a PayPal checkout session and return the approval URL
    
    This is the high-level function that developers will use in their views.
    
    Args:
        order: The order object
        request: The HTTP request object
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if payment is cancelled
    
    Returns:
        dict: Processed PayPal order data with approval URL
    
    Example:
        >>> from django_pg.paypal.paypal_checkout import create_paypal_checkout
        >>> checkout_data = create_paypal_checkout(
        ...     order=order,
        ...     request=request,
        ...     success_url="https://example.com/success/",
        ...     cancel_url="https://example.com/cancel/"
        ... )
        >>> approve_url = checkout_data['approve_url']
    """
    # Validate PayPal configuration
    if not hasattr(settings, 'PAYPAL_CLIENT_ID') or not hasattr(settings, 'PAYPAL_SECRET'):
        raise PaymentConfigurationError(
            "PayPal credentials are not configured. Set PAYPAL_CLIENT_ID and PAYPAL_SECRET."
        )
    
    if not hasattr(settings, 'PAYPAL_ENV'):
        raise PaymentConfigurationError(
            "PAYPAL_ENV is not configured. Set to 'sandbox' or 'live'."
        )
    
    # Build URLs if not provided
    base_url = request.build_absolute_uri('/').rstrip('/')
    
    if not success_url:
        try:
            success_url = f"{base_url}{reverse('django_pg:payment_verification', args=[order.id, 'paypal'])}"
        except Exception:
            success_url = f"{base_url}/payment/verification/{order.id}/paypal/"
    
    if not cancel_url:
        try:
            cancel_url = f"{base_url}{reverse('django_pg:payment_cancelled', args=[order.id, 'paypal'])}"
        except Exception:
            cancel_url = f"{base_url}/payment/cancelled/{order.id}/paypal/"
    
    # Get order amount
    try:
        if hasattr(order, 'get_total_amount'):
            amount = float(order.get_total_amount())
        elif hasattr(order, 'total_price'):
            amount = float(order.total_price)
        elif hasattr(order, 'amount'):
            amount = float(order.amount)
        elif hasattr(order, 'total'):
            amount = float(order.total)
        else:
            raise PaymentConfigurationError(
                "Could not determine order amount. Ensure order has total_price, amount, or total attribute."
            )
    except (TypeError, ValueError) as e:
        raise PaymentConfigurationError(f"Invalid order amount: {str(e)}") from e
    
    # Get currency from settings or default to USD
    currency = getattr(settings, "PAYPAL_CURRENCY", "USD")
    
    # Prepare description
    description = f"Payment for Order {order.order_reference}"
    
    try:
        # Call low-level service to create PayPal order
        order_data = paypal_services.create_paypal_order(
            amount=amount,
            currency=currency,
            order_reference=order.order_reference,
            description=description[:127],  # PayPal has length limit
            return_url=success_url,
            cancel_url=cancel_url,
        )
        
        # Extract approval URL for convenience
        approve_url = None
        for link in order_data.get("links", []):
            if link.get("rel") == "approve":
                approve_url = link.get("href")
                break
        
        # Add approval URL to response
        order_data['approve_url'] = approve_url
        
        return order_data
        
    except Exception as e:
        raise PaymentRuntimeError(
            f"PayPal checkout creation failed: {str(e)}"
        ) from e