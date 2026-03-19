import base64
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings


def _paypal_base_url():
    return "https://api-m.sandbox.paypal.com" if settings.PAYPAL_ENV == "sandbox" else "https://api-m.paypal.com"


# shared session with retries
_session = requests.Session()
_retries = Retry(
    total=3,
    connect=3,
    read=3,
    backoff_factor=0.7,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["POST", "GET"],
    raise_on_status=False,
)
_adapter = HTTPAdapter(max_retries=_retries)
_session.mount("https://", _adapter)


def get_access_token():
    """
    PayPal OAuth token (server-to-server)
    """
    auth = f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_SECRET}"
    b64 = base64.b64encode(auth.encode()).decode()

    url = f"{_paypal_base_url()}/v1/oauth2/token"
    headers = {
        "Authorization": f"Basic {b64}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}

    try:
        r = _session.post(url, headers=headers, data=data, timeout=(10, 30))
        r.raise_for_status()
        return r.json()["access_token"]
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to get PayPal access token: {str(e)}")


def create_paypal_order(*, amount, currency, order_reference, description, return_url, cancel_url):
    """
    Low-level function to create a PayPal order via API
    
    Args:
        amount: Float amount to charge
        currency: Currency code
        order_reference: Your order reference (stored in custom_id)
        description: Description of the payment
        return_url: URL to redirect after successful payment
        cancel_url: URL to redirect if payment is cancelled
    
    Returns:
        dict: Raw PayPal API response
    """
    token = get_access_token()
    url = f"{_paypal_base_url()}/v2/checkout/orders"

    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "custom_id": str(order_reference),
                "description": description,
                "amount": {
                    "currency_code": currency,
                    "value": f"{amount:.2f}",
                },
            }
        ],
        "application_context": {
            "return_url": return_url,
            "cancel_url": cancel_url,
            "shipping_preference": "NO_SHIPPING",
            "user_action": "PAY_NOW",
        },
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to create PayPal order: {str(e)}")


def capture_paypal_order(paypal_order_id: str):
    """
    Low-level function to capture a PayPal order via API
    
    Args:
        paypal_order_id: The PayPal order ID to capture
    
    Returns:
        dict: Raw PayPal API response
    """
    token = get_access_token()
    url = f"{_paypal_base_url()}/v2/checkout/orders/{paypal_order_id}/capture"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        r = requests.post(url, headers=headers, json={}, timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to capture PayPal order: {str(e)}")


def get_paypal_order(paypal_order_id: str):
    """
    Low-level function to get PayPal order details via API
    
    Args:
        paypal_order_id: The PayPal order ID
    
    Returns:
        dict: Raw PayPal API response
    """
    token = get_access_token()
    url = f"{_paypal_base_url()}/v2/checkout/orders/{paypal_order_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to get PayPal order details: {str(e)}")