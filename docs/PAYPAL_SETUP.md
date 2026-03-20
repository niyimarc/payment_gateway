# PayPal Setup

Add the following to your `settings.py`:

```python
# PayPal Configuration
PAYPAL_CLIENT_ID = 'your_client_id'
PAYPAL_SECRET = 'your_secret'
PAYPAL_ENV = 'sandbox'  # or 'live' for production

# Optional settings
PAYPAL_CURRENCY = 'USD'  # Default: USD
PAYPAL_WEBHOOK_ID = 'your_webhook_id'  # Required for webhook verification
PAYPAL_WEBHOOK_PATH = 'webhooks/paypal/'  # Default: 'webhooks/paypal/'
```

## Payment Initialization

When creating an order with PayPal, use the package's `create_paypal_checkout` function:

```python
from django_pg.paypal.paypal_checkout import create_paypal_checkout

class OrderCreateView(APIView):
    def post(self, request):
        # ... order creation logic ...
        
        if order.payment_method == 'paypal':
            base_url = request.build_absolute_uri('/').rstrip('/')
            success_url = f"{base_url}/payment/verification/{order.order_reference}/paypal/"
            cancel_url = f"{base_url}/payment/cancelled/{order.order_reference}/paypal/"
            
            paypal_order_data = create_paypal_checkout(
                order=order,
                request=request,
                success_url=success_url,
                cancel_url=cancel_url
            )
            
            # Save PayPal order ID and approval URL
            order.paypal_order_id = paypal_order_data.get('id')
            order.paypal_approve_url = paypal_order_data.get('approve_url')
            order.save(update_fields=['paypal_order_id', 'paypal_approve_url'])
            
            return Response({
                'success': True,
                'order_id': order.id,
                'order_reference': order.order_reference,
                'payment_method': 'paypal',
                'paypal_approve_url': paypal_order_data.get('approve_url'),
                'paypal_order_id': paypal_order_data.get('id'),
            })
```

## Frontend Integration

```html
<button id="paypal-pay-btn">Pay with PayPal</button>

<script>
document.getElementById('paypal-pay-btn').addEventListener('click', function() {
    document.getElementById('payment-type-input').value = 'paypal';
    document.getElementById('checkout-form').submit();
});

// If you receive PayPal approval URL directly from backend
{% if paypal_approve_url %}
<script>
    window.location.href = "{{ paypal_approve_url }}";
</script>
{% endif %}
</script>
```

## Redirect Flow

After successful payment, PayPal redirects to your `success_url` with a token. The package's built-in `payment_verification` view handles this automatically:

```python
from django_pg.views import payment_verification

urlpatterns = [
    path("payment/verification/<str:order_reference>/<str:payment_method>/", payment_verification, name="payment_verification"),
    path("payment/cancelled/<str:order_reference>/<str:payment_method>/", payment_cancelled, name="payment_cancelled"),
]
```

## Webhook Configuration (Optional)

1. **Set webhook ID in settings**:
```python
PAYPAL_WEBHOOK_ID = 'your_webhook_id'  # From PayPal Developer Dashboard
PAYPAL_WEBHOOK_PATH = 'webhooks/paypal/'  # Customize as needed
```

2. **Include package URLs**:
```python
# urls.py
from django.urls import include, path

urlpatterns = [
    path('', include('django_pg.urls')),
]
```

3. **Configure in PayPal Developer Dashboard**:
   - Go to Developer Dashboard → My Apps & Credentials
   - Select your app
   - Click "Add Webhook"
   - URL: `https://your-domain.com/webhooks/paypal/`
   - Select events to receive (PAYMENT.CAPTURE.COMPLETED, etc.)

## Available Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `PAYPAL_CLIENT_ID` | Your PayPal client ID | Required |
| `PAYPAL_SECRET` | Your PayPal secret key | Required |
| `PAYPAL_ENV` | Environment: 'sandbox' or 'live' | Required |
| `PAYPAL_CURRENCY` | Currency code (USD, EUR, GBP, etc.) | 'USD' |
| `PAYPAL_WEBHOOK_ID` | Webhook ID for signature verification | None |
| `PAYPAL_WEBHOOK_PATH` | Webhook URL path | 'webhooks/paypal/' |

## Testing with Sandbox

```python
PAYPAL_ENV = 'sandbox'
PAYPAL_CLIENT_ID = 'your_sandbox_client_id'
PAYPAL_SECRET = 'your_sandbox_secret'
```

Use PayPal sandbox test accounts:
- Business account: `sb-xxxxxxxx-business@example.com`
- Personal account: `sb-xxxxxxxx-personal@example.com`

## Order Model Fields

The package's `BaseOrder` abstract model includes:

```python
class BaseOrder(models.Model):
    # ... other fields ...
    paypal_order_id = models.CharField(max_length=120, blank=True, null=True)
    paypal_capture_id = models.CharField(max_length=120, blank=True, null=True)
    paypal_approve_url = models.URLField(max_length=500, blank=True, null=True)
```