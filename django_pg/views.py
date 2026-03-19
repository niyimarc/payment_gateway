from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse
from django.views import View
import json
from .utils import resolve_redirect
from .stripe.webhook import stripe_webhook_response
from .paypal.webhook import paypal_webhook_response
from .exceptions import PaymentConfigurationError, PaymentRuntimeError

SUCCESS_REDIRECT = getattr(settings, 'DJANGO_PG_SUCCESS_REDIRECT', None)
FAILURE_REDIRECT = getattr(settings, 'DJANGO_PG_FAILURE_REDIRECT', None)

@login_required
def payment_verification(request, order_id, payment_method):
    if payment_method == "paystack":
        transaction_id = request.GET.get('reference')
    elif payment_method == "flutterwave":
        transaction_id = request.GET.get('transaction_id')
    elif payment_method == "interswitch":
        transaction_id = request.GET.get('reference')
    elif payment_method == "stripe":
        transaction_id = request.GET.get('reference') or request.GET.get('session_id')
    elif payment_method == "paypal":
        # PayPal returns a token, but we need the PayPal order ID
        # The PayPal order ID is already stored in the order during checkout
        from .utils import get_model
        Order = get_model("PAYMENT_ORDER_MODEL")
        try:
            order = Order.objects.get(id=order_id)
            # Use the stored PayPal order ID as the transaction_id
            transaction_id = getattr(order, 'paypal_order_id', None)
            if not transaction_id:
                messages.error(request, "PayPal order ID not found")
                return redirect(resolve_redirect(FAILURE_REDIRECT))
        except Order.DoesNotExist:
            messages.error(request, "Order not found")
            return redirect(resolve_redirect(FAILURE_REDIRECT))
    else:
        messages.error(request, "Unsupported payment method")
        return redirect(resolve_redirect(FAILURE_REDIRECT))

    from .payment import verify_payment
    result = verify_payment(order_id, transaction_id, request.user, payment_method)

    if result.get("success"):
        return resolve_redirect(SUCCESS_REDIRECT, result)
    else:
        messages.error(request, result.get("message", "Payment verification failed"))
        return redirect(resolve_redirect(FAILURE_REDIRECT, result))
    
class PaymentVerificationJSONView(View):
    def post(self, request, order_id, payment_method):
        try:
            body = json.loads(request.body.decode("utf-8"))
        except Exception:
            body = {}

        if payment_method == "paystack":
            transaction_id = body.get("reference")
        elif payment_method == "flutterwave":
            transaction_id = body.get("reference") or body.get("transaction_id")
        elif payment_method == "interswitch":
            transaction_id = body.get("reference")
        elif payment_method == "stripe":
            transaction_id = body.get('reference') or body.get('session_id')
        elif payment_method == "paypal":
            # For JSON API, client can send the paypal_order_id
            # But if not sent, we can still get it from the order
            transaction_id = body.get('paypal_order_id')
            if not transaction_id:
                from .utils import get_model
                Order = get_model("PAYMENT_ORDER_MODEL")
                try:
                    order = Order.objects.get(id=order_id)
                    transaction_id = getattr(order, 'paypal_order_id', None)
                except Order.DoesNotExist:
                    pass
        else:
            return JsonResponse(
                {"success": False, "message": "Unsupported payment method"},
                status=400
            )

        from .payment import verify_payment
        result = verify_payment(order_id, transaction_id, request.user, payment_method)

        if result.get("success"):
            return JsonResponse(
                {"success": True, "message": "Payment verified", "data": result}
            )
        else:
            return JsonResponse(
                {"success": False, "message": result.get("message", "Payment verification failed")},
                status=400
            )
        
@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    def post(self, request, *args, **kwargs):
        try:
            return stripe_webhook_response(request)
        except PaymentConfigurationError as e:
            # misconfigured server
            return HttpResponse(str(e), status=500)
        except PaymentRuntimeError:
            # bad payload/signature etc.
            return HttpResponse(status=400)
        except Exception:
            # don't leak details
            return HttpResponse(status=500)
        
@method_decorator(csrf_exempt, name="dispatch")
class PayPalWebhookView(View):
    """
    PayPal webhook handler for receiving payment notifications
    """
    def post(self, request, *args, **kwargs):
        try:
            return paypal_webhook_response(request)
        except PaymentConfigurationError as e:
            # misconfigured server
            return HttpResponse(str(e), status=500)
        except PaymentRuntimeError:
            # bad payload/signature etc.
            return HttpResponse(status=400)
        except Exception:
            # don't leak details
            return HttpResponse(status=500)