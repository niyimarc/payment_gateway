**Define required settings in your settings.py**
```python
# It's recommended that you put the secret key 
# in a .env file and load it in your settings

# Flutterwave keys
FLUTTERWAVE_PUBLIC_KEY = "your-flutterwave-public-key"
FLUTTERWAVE_SECRET_KEY = "your-flutterwave-secret-key"
```

#### 🌐 Redirect Behavior
After verifying a transaction, the view will redirect the user based on settings defined in your settings.py.

Option 1: Use named URL patterns
```python
# settings.py
DJANGO_PG_SUCCESS_REDIRECT = 'yourapp:track_order'
DJANGO_PG_FAILURE_REDIRECT = 'yourapp:create_order'
```
Option 2: Use custom Python functions (advanced)
You can also pass a function that takes the verification result dictionary and returns a HttpResponseRedirect.
```python
# settings.py
DJANGO_PG_SUCCESS_REDIRECT = 'yourapp.utils.payment_success_redirect'
DJANGO_PG_FAILURE_REDIRECT = 'yourapp.utils.payment_failure_redirect'
```

If you go with option 2, you will need to add the functions in yourapp/utils.py:
```python
from django.shortcuts import redirect

def payment_success_redirect(result):
    return redirect('yourapp:track_order', order_reference=result["order_reference"])

def payment_failure_redirect(result):
    return redirect('yourapp:create_order')
```

### Add JS to Your HTML Template
#### ✅ Flutterwave Integration (HTML Template)
[Check Flutterwave Documentation](https://developer.flutterwave.com/docs/inline)
```bash
{% if payment_method == 'flutterwave' %}
<script src="https://checkout.flutterwave.com/v3.js"></script>
<script>
  document.addEventListener("DOMContentLoaded", function () {
    FlutterwaveCheckout({
      public_key: "{{ FLUTTERWAVE_PUBLIC_KEY }}",
      tx_ref: "{{ order.order_reference }}",
      amount: {{order.total_price}},
      currency: "NGN",
      payment_options: "card, ussd, banktransfer",
      redirect_url: "{% url 'yourapp:payment_verification' order.id payment_method %}",
      customer: {
        email: "{{ request.user.email }}",
        name: "{{ request.user.get_full_name|default:request.user.username }}"
      },
      customizations: {
        title: "My Store",
        description: "Payment for order {{ order.order_reference }}"
      }
    });
  });
</script>
{% endif %}
```