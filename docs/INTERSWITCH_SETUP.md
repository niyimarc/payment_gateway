**Define required settings in your settings.py**
```python
# It's recommended that you put the secret key 
# in a .env file and load it in your settings

# Interswitch keys
INTERSWITCH_MERCHANT_CODE = "your-interswitch-merchant-code"
INTERSWITCH_PAY_ITEM_ID = "your-interswitch-pay-item-id"
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
#### ✅ Interswitch Integration (HTML Template)
[Check Interswitch Documentation](https://docs.interswitchgroup.com/docs/web-checkout)
```bash
{% if payment_method == 'interswitch' %}
<script src="https://newwebpay.qa.interswitchng.com/inline-checkout.js"></script>
<script>
(function() {
    const redirectUrl = "{% url 'yourapp:payment_verification' order.id payment_method %}?reference={{ order.order_reference }}";
    const paymentAmount = {{ order.total_price|floatformat:0 }} * 100;

    function paymentCallback(response) {
        console.log("Interswitch Payment Response:", response);

        if (response?.resp === '00') {
            // Successful payment
            window.location.href = redirectUrl;
        } else {
            alert("Payment was not successful. Please try again.");
        }
    }

    const paymentRequest = {
        merchant_code: "{{ INTERSWITCH_MERCHANT_CODE }}",
        pay_item_id: "{{ INTERSWITCH_PAY_ITEM_ID }}",
        txn_ref: "{{ order.order_reference }}",
        site_redirect_url: redirectUrl,
        amount: paymentAmount,
        currency: 566,
        cust_email: "{{ request.user.email }}",
        cust_name: "{{ request.user.get_full_name|default:request.user.username }}",
        onComplete: paymentCallback,
        mode: "TEST"
    };

    window.webpayCheckout(paymentRequest);
})();
</script>
{% endif %}
```