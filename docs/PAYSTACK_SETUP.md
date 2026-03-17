**Define required settings in your settings.py**
```python
# It's recommended that you put the secret key 
# in a .env file and load it in your settings

# Paystack keys
PAYSTACK_PUBLIC_KEY = 'your-paystack-public-key'
PAYSTACK_SECRET_KEY = 'your-paystack-secret-key'
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
#### ✅ Paystack Integration (HTML Template)
[Check Paystack Documentation](https://paystack.com/docs/payments/accept-payments/)
```bash
{% if payment_method == 'paystack' %}
<script src="https://js.paystack.co/v2/inline.js"></script>
<script type="text/javascript">
    function payWithPaystack() {
        var handler = PaystackPop.setup({
            key: '{{ PAYSTACK_PUBLIC_KEY }}',
            email: '{{ request.user.email }}',
            amount: {{ order.total_price|multiply:100 }},
            currency: "NGN",
            ref: '' + Math.floor((Math.random() * 1000000000) + 1),
            callback: function(response) {
                window.location.href = "{% url 'yourapp:payment_verification' order.id payment_method %}?reference=" + response.reference;
            },
            onClose: function() {
                alert('Payment was not completed.');
            }
        });
        handler.openIframe();
    }

    window.onload = function() {
        payWithPaystack();
    };
</script>
{% endif %}
```