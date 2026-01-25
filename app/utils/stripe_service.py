import stripe
from flask import current_app, url_for


def create_checkout_session(order_id, amount, customer_email=None, success_url=None, cancel_url=None):
    """Create Stripe checkout session"""
    try:
        # Round to avoid floating point issues
        amount_cents = int(round(amount * 100))
        
        session_data = {
            'payment_method_types': ['card'],
            'line_items': [{
                'price_data': {
                    'currency': 'zar',
                    'unit_amount': amount_cents,
                    'product_data': {
                        'name': f'Bakers Lovers - Order #{order_id}',
                        'description': 'Delicious cakes from Bakers Lovers'
                    }
                },
                'quantity': 1
            }],
            'mode': 'payment',
            'success_url': success_url or url_for('checkout.success', order_id=order_id, _external=True),
            'cancel_url': cancel_url or url_for('checkout.cancel', _external=True),
            'metadata': {
                'order_id': str(order_id)
            },
            'billing_address_collection': 'required',
            'shipping_address_collection': {
                'allowed_countries': ['ZA'],
            }
        }
        
        # Add customer email if provided
        if customer_email:
            session_data['customer_email'] = customer_email
        
        session = stripe.checkout.Session.create(**session_data)
        return session
    except stripe.error.StripeError as e:
        current_app.logger.error(f'Stripe error: {str(e)}')
        raise
    except Exception as e:
        current_app.logger.error(f'Unexpected error creating checkout session: {str(e)}')
        raise


def get_stripe_keys():
    """Get Stripe configuration keys"""
    return {
        'publishable_key': current_app.config['STRIPE_PUBLISHABLE_KEY'],
        'secret_key': current_app.config['STRIPE_SECRET_KEY']
    }