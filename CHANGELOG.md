# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.5.0] – 2026-01-06

### Added
- Stripe payment gateway support
- Stripe Checkout Session integration (server-side)
- Stripe webhook support for reliable payment confirmation
- `stripe_checkout_session_id` field on `BaseOrder` (abstract model)
- Centralized Stripe checkout helpers:
  - `create_stripe_checkout_session`
- New payment-related exceptions:
  - `PaymentConfigurationError` (misconfiguration / missing setup)
  - `PaymentRuntimeError` (gateway / network / Stripe API errors)
- Stripe webhook endpoint configurable via:
  - `DJANGO_PG_STRIPE_WEBHOOK_PATH`
- Support for server-side payment confirmation even if:
  - User closes browser
  - Redirect back to frontend fails
  - Network drops after payment

### Changed
- Payment verification architecture now supports:
  - Redirect-based flows (Paystack, Flutterwave, Interswitch)
  - Webhook-based confirmation (Stripe)
- Stripe payment confirmation is now **authoritative via webhook**
- Frontend redirect is treated as UX only, not payment truth

### Fixed
- Prevented false negatives when Stripe payments succeed but frontend redirect fails
- Improved error handling consistency across payment gateways

### Security
- Stripe webhook signature verification using `STRIPE_WEBHOOK_SECRET`
- Clear separation between configuration errors and runtime gateway errors

### Notes
- Developers must register the Stripe webhook endpoint in the Stripe Dashboard for production.
- Stripe CLI can be used for local webhook testing.
- Frontend applications are responsible for redirecting users to the Stripe Checkout URL returned by the backend.
---

## [0.4.1] - 2025-08-19
### Added
- Introduced a new JSON-based payment verification view.
  - Useful for projects where the frontend and backend are separated.
  - Returns JSON responses (`success`, `message`, `data`) instead of performing redirects.
  - Enables frontend apps (SPA, mobile, etc.) to handle post-payment flow directly.
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
