# Django Payment Gateways Package

A pluggable Django package for integrating multiple payment gateways
including Paystack, Flutterwave, Interswitch, and Stripe, with an
extensible architecture for adding more gateways.


---

## ✨ Features

- 🔌 Plug-and-play integration
- 🔐 Paystack, Flutterwave, Interswitch, and Stripe support
- 📦 Dispatcher pattern for gateway switching
- 🧱 Abstract `BaseOrder` model for customization
- ✅ Built-in Payment Verification View (redirect-based gateways)
- 🟦 Webhook-based verification for Stripe
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

```python
# settings.py
INSTALLED_APPS = [
    ...
    'django_pg',  # Your payment package
]
```

2. **Configure your Order model (Extend the BaseOrder abstract model)**
In your own app, create your order model by extending gateways.models.BaseOrder:
```python
# yourapp/models.py
from django.db import models
from django_pg.models import BaseOrder
from django.contrib.auth.models import User

class Order(BaseOrder):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    # Add your fields here
```

3. **Define the model that handles the Order in settings.py**

```python
# settings.py

# Models used for order
PAYMENT_ORDER_MODEL = 'yourapp.Order'

```

## 🎯 Choose Your Payment Gateway
If you're using multiple payment methods (e.g. Paystack, Flutterwave, Interswitch, and stripe), make sure your template checks for the selected `payment_method`. If you're only using one payment method, you can pass the preferred payment method in a hidden field when the order is created.

| Gateway | Region | Best For | Setup Guide |
|---------|--------|----------|-------------|
| **Paystack** | Nigeria, Ghana, SA | Cards, Bank Transfer, USSD | [📘 Paystack Setup](https://github.com/niyimarc/payment_gateway/blob/master/docs/PAYSTACK_SETUP.md) |
| **Flutterwave** | Africa | Pan-African payments | [📘 Flutterwave Setup](https://github.com/niyimarc/payment_gateway/blob/master/docs/FLUTTERWAVE_SETUP.md) |
| **Interswitch** | Nigeria | Enterprise, WebPAY | [📘 Interswitch Setup](https://github.com/niyimarc/payment_gateway/blob/master/docs/INTERSWITCH_SETUP.md) |
| **Stripe** | Global | International customers | [📘 Stripe Setup](https://github.com/niyimarc/payment_gateway/blob/master/docs/STRIPE_SETUP.md) |

Each guide covers:
- 🔑 API key configuration
- ⚙️ Gateway-specific settings
- 🧪 Testing with sandbox credentials
- 🚀 Going live checklist
- 🔧 Troubleshooting common issues

4. **Built-in Payment Verification View**
django-pg provides a built-in payment_verification view that handles verifying transactions for all the payment gateways out of the box.
#### 🔌 URL Configuration
You can use the built-in view directly in your urls.py:
```python
from django.urls import path
from django_pg.views import payment_verification  # Import from the package

urlpatterns = [
    path("verify/<int:order_id>/<str:payment_method>/", payment_verification, name="payment_verification"),
]
```

**Note: Users attempting to make a payment via Paystack and Flutterwave must have a valid email address. The Paystack and Flutterwave gateway requires this for transaction initiation. Make sure you enforce email submission when a user registers**


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