**Define required settings in your settings.py**
```python
# It's recommended that you put the secret key 
# in a .env file and load it in your settings

# Stripe keys
STRIPE_SECRET_KEY = "your_stripe_secret"
STRIPE_WEBHOOK_SECRET = "your_webhook_secret_if_using_webhooks"
DJANGO_PG_STRIPE_WEBHOOK_PATH = "webhooks/stripe/" #if using webhook
```

## 🟦 Stripe Integration (Important)

Stripe payments are **server-authoritative** and rely on **webhooks**.

### How Stripe works in this package:
1. Backend creates a Stripe Checkout Session
2. Backend returns `stripe_checkout_url` and `stripe_session_id`
3. Frontend redirects user to Stripe Checkout
4. Stripe sends a webhook (`checkout.session.completed`) to the backend
5. Backend marks the order as paid
6. Frontend redirect is **UX only**, not payment truth

⚠️ Do not rely solely on frontend redirects to confirm Stripe payments.
⚠️ Stripe Checkout requires a webhook in production to reliably confirm payments.
### Creating a Stripe Checkout Session (Backend)

```python
from django_pg.stripe.stripe_checkout import create_stripe_checkout_session

session = create_stripe_checkout_session(
    order=order,
    success_url="https://frontend.com/payment/ORDER_REF/stripe/?reference={CHECKOUT_SESSION_ID}",
    cancel_url="https://frontend.com/payment/ORDER_REF/stripe/?cancelled=true",
    customer_email=request.user.email,
)

order.stripe_checkout_session_id = session.id
order.save()
```

#### ✅ Stripe Integration (HTML Template)
[Check Stripe Documentation](https://docs.stripe.com/payments/quickstart-checkout-sessions)
```bash
{% if payment_method == 'stripe' %}
<script src="https://js.stripe.com/v3/"></script>
<script>
document.addEventListener("DOMContentLoaded", function () {
    const stripe = Stripe("{{ STRIPE_PUBLIC_KEY }}");
    const sessionId = "{{ STRIPE_SESSION_ID|default:'' }}";

    if (!sessionId) {
        alert("Unable to start Stripe checkout (missing session id).");
        return;
    }

    stripe.redirectToCheckout({ sessionId: sessionId });
});
</script>
{% endif %}
```
## Add URLs to backend if using webhook
```bash
urlpatterns = [
    path("", include("django_pg.urls")),
]
```