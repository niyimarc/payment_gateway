# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.4.0] - 2025-05-28
### Added
- Integrated Interswitch payment gateway support.

### Fixed
- Added validation to ensure the paid amount matches the expected amount before confirming the transaction.

---

## [0.3.0] - 2025-05-26
### Added
- Built-in verification views for all gateways — implementers no longer need to define them manually.
- Enhanced redirect resolution:
  - Supports named URL patterns.
  - Supports callable paths (e.g. `'store.utils.payment_success_redirect'`).
  - Accepts hardcoded paths (e.g. `'/success/'`).
- Redirect functions now support dynamic `order_reference` injection.

### Changed
- Refactored `resolve_redirect` to correctly handle and return `HttpResponseRedirect` objects.

### Fixed
- Improved error handling for misconfigured redirect settings and dotted path functions.
---
## [0.2.0] - 2025-05-24
### Added
- Added flutterwave payment gateway:

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
