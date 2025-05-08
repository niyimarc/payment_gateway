from django_pg.paystack.paystack_payment import verify_paystack_payment

def verify_payment(order_id, reference, user, payment_method):
    # Dispatches the payment verification to the correct gateway handler..
    if payment_method == 'paystack':
        return verify_paystack_payment(order_id, reference, user)
    else:
        return {"success": False, "message": "Unsupported payment method"}
