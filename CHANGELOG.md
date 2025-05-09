# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---
## [0.1.1] - 2025-05-08
### Added
- User validation to `verify_paystack_payment`:
  - Ensures the user is authenticated.
  - Ensures the user has a valid email address.
- Clear error messages returned if validation fails.

---

## [0.1.0] - 2025-05-08

### Added
- Initial release of `django_pg`.
- Core support for Paystack payments.
- Abstract `BaseOrder` model with built-in fields (`payment_made`, `order_placed`, `status`, `payment_date`, `order_reference`).
- Automatic unique `order_reference` generation via Django signals.
- Dispatcher-based gateway handler with `verify_payment()` interface.
- Utility functions to dynamically load models and notification functions.
- Sample Paystack JS integration and backend verification function.
- Admin notification support via customizable hook.
- Documentation including setup guide and integration example.

---

## [Unreleased]

- Flutterwave and Stripe integrations (planned).
- Webhook support.
- Enhanced error logging.
