# Django Payment Gateways Package

A pluggable Django package for integrating multiple payment gateways (starting with Paystack and Flutterwave), with an extensible architecture that supports more gateways like Stripe, etc.

---

## ✨ Features

- 🔌 Plug-and-play integration
- 🔐 Paystack support (more gateways coming)
- 📦 Dispatcher pattern for gateway switching
- 🧱 Abstract `Order` model for customization
- 📮 Admin notification hook support
- 🧠 Smart unique order reference generation
- 🧪 Built-in signal handling for order reference
- 💡 Fully customizable frontend and views

---

## Example Project

A sample Django project demonstrating how to use this package is available here:

👉 [django_pg_test_project](https://github.com/niyimarc/payment_gateway_test)

---

## 📦 Installation

```bash
pip install django-pg
```

## ⚙️ Project Setup
1. **Add the app to INSTALLED_APPS**

```bash
# settings.py
INSTALLED_APPS = [
    ...
    'django_pg',  # Your payment package
]
```

2. **Define required settings in your settings.py**

```bash
# settings.py

# Models used for order
PAYMENT_ORDER_MODEL = 'yourapp.Order'

# It's recomended that you put the secret key 
# in a .env file and load it in your settings

# Paystack keys
PAYSTACK_PUBLIC_KEY = 'your-paystack-public-key'
PAYSTACK_SECRET_KEY = 'your-paystack-secret-key'

# Flutterwave keys
FLUTTERWAVE_PUBLIC_KEY = "your-public-key"
FLUTTERWAVE_SECRET_KEY = "your-secret-key"

```

3. **Extend the BaseOrder abstract model**
In your own app, create your order model by extending gateways.models.BaseOrder:

```bash
# yourapp/models.py
from django.db import models
from django_pg.models import BaseOrder
from django.contrib.auth.models import User

class Order(BaseOrder):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    # Add your fields here
```

4. 🔍 **Verifying Payments in Your View**
In your views.py, use the dispatcher like this:
```bash
from django_pg.payment import verify_payment

@login_required
def payment_verification(request, order_id, payment_method):
    if payment_method == "paystack":
        transaction_id = request.GET.get('reference')
    if payment_method == "flutterwave":
        transaction_id = request.GET.get('transaction_id')
    else:
        messages.error(request, "Unsupported payment method")
        return redirect('store:create_order')
    
    result = verify_payment(order_id, transaction_id, request.user, payment_method)

    if result.get("success"):
        # redirect to track order for example if payment is successful
        return redirect('store:track_order', order_reference=result["order_reference"])
    else:
        print("Payment verification failed")
        messages.error(request, result.get("message", "Payment verification failed"))
        return redirect('store:create_order')
```

**Note: Users attempting to make a payment via Paystack and Flutterwave must have a valid email address. The Paystack and Flutterwave gateway requires this for transaction initiation. Make sure you enforce email submission when a user register**

### 5. Add JS to Your HTML Template

If you're using multiple payment methods (e.g. Paystack and Flutterwave), make sure your template checks for the selected `payment_method`. If you're only using one method, you can pass the preferred payment method in a hidden field when the order is created.

#### ✅ Paystack Integration (HTML Template)
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
                window.location.href = "{% url 'store:payment_verification' order.id payment_method %}?reference=" + response.reference;
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

#### ✅ Flutterwave Integration (HTML Template)
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
      redirect_url: "{% url 'store:payment_verification' order.id payment_method %}",
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

## 🔁 Signals (Auto Order Reference)

You don’t need to register anything. The gateways app automatically registers a pre_save signal that generates a unique order_reference.
```bash
# gateways/signals.py
@receiver(pre_save, sender=Order)
def set_order_reference(sender, instance, **kwargs):
    if not instance.order_reference:
        instance.order_reference = generate_unique_order_reference()
```

## 🧠 Gateway Dispatcher (Behind the scenes)

The following function routes the verification based on the selected payment method:
```bash
# gateways/payment.py
def verify_payment(order_id, reference, user, payment_method):
    if payment_method == 'paystack':
        return verify_paystack_payment(order_id, reference, user)
    # elif payment_method == 'flutterwave': ...

```
You don't need to modify this — it's extendable internally.

## 🛡 License

This project is licensed under the MIT License – see the [LICENSE](./LICENSE) file for details.

---

## 🤝 Contributing

Pull requests are welcome! If you find a bug or have a feature request, feel free to [open an issue](https://github.com/niyimarc/payment_gateways/issues).

See full [Changelog](https://github.com/niyimarc/payment_gateway/blob/master/CHANGELOG.md).