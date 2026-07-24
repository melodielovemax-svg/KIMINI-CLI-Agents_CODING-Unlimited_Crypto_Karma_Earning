import stripe
import os


stripe.api_key=os.getenv(
"STRIPE_SECRET_KEY"
)


def meter_usage(
    customer,
    tokens
):

    return {
        "customer":customer,
        "tokens":tokens
    }
