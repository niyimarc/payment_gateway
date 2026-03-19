from django.conf import settings
from django.utils import timezone
from ..utils import get_model, validate_user_for_payment, validate_payment_amount
from . import paypal_services


def verify_paypal_payment(order_id, transaction_id, user):
    """
    Verify and capture a PayPal payment
    
    Args:
        order_id: The order ID in your system
        transaction_id: The PayPal order ID
        user: The user making the payment
    
    Returns:
        dict: Result of verification
    """
    # Validate user
    validation = validate_user_for_payment(user)
    if not validation["success"]:
        return validation

    # Get Order model
    Order = get_model("PAYMENT_ORDER_MODEL")

    # Retrieve order
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return {"success": False, "message": "Order not found."}

    # Validate PayPal configuration
    if not hasattr(settings, 'PAYPAL_CLIENT_ID') or not hasattr(settings, 'PAYPAL_SECRET'):
        return {"success": False, "message": "PayPal is not configured."}
    
    if not hasattr(settings, 'PAYPAL_ENV'):
        return {"success": False, "message": "PAYPAL_ENV is not configured."}

    # Validate transaction_id
    if not transaction_id:
        return {"success": False, "message": "PayPal order ID is required for verification"}

    # Capture the PayPal order
    try:
        capture_data = paypal_services.capture_paypal_order(transaction_id)
    except Exception as e:
        return {"success": False, "message": f"Error verifying PayPal payment: {str(e)}"}

    # Confirm payment was completed
    if capture_data.get("status") == "COMPLETED":
        # Extract capture details
        try:
            purchase_unit = capture_data["purchase_units"][0]
            capture = purchase_unit["payments"]["captures"][0]
            
            paid_amount = float(capture["amount"]["value"])
            
            # Validate amount matches order
            amount_validation = validate_payment_amount(order, paid_amount)
            if not amount_validation["success"]:
                return amount_validation

            # Update order
            order.payment_made = True
            order.order_placed = True
            order.status = "Order Placed"
            order.payment_method = "paypal"
            order.paypal_order_id = transaction_id
            order.paypal_capture_id = capture.get("id")
            order.payment_date = timezone.now()
            order.save()

            return {
                "success": True, 
                "order_reference": order.order_reference,
                "paypal_capture_id": capture.get("id")
            }
            
        except (KeyError, IndexError, ValueError) as e:
            return {"success": False, "message": f"Failed to parse PayPal response: {str(e)}"}

    return {"success": False, "message": "Payment verification failed"}