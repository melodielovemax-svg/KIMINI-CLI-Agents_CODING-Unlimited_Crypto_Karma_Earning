import os

try:
    import stripe
except ImportError:
    stripe = None

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

if stripe is not None and STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY


def meter_usage(customer, tokens):
    if stripe is None:
        return {"customer": customer, "tokens": tokens, "metered": False, "reason": "stripe not installed"}
    if not STRIPE_SECRET_KEY:
        return {"customer": customer, "tokens": tokens, "metered": False, "reason": "STRIPE_SECRET_KEY not set"}
    return {"customer": customer, "tokens": tokens, "metered": True}
