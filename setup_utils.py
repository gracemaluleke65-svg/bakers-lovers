# setup_utils.py
import os

def setup_utils_directory():
    """Create the missing utils directory and files"""
    
    # Create utils directory
    utils_dir = 'app/utils'
    if not os.path.exists(utils_dir):
        os.makedirs(utils_dir)
        print(f"✅ Created {utils_dir}")
    
    # Create __init__.py
    init_file = os.path.join(utils_dir, '__init__.py')
    with open(init_file, 'w') as f:
        f.write('# app/utils/__init__.py\n')
        f.write('# This file makes the utils directory a Python package\n')
    print(f"✅ Created {init_file}")
    
    # Create cart_helper.py
    cart_helper_content = '''from flask import session
from app.models import Cart, CartItem
from datetime import datetime
from app import db


def get_cart():
    """Get or create cart for current session"""
    session_id = session.get('cart_id')
    if not session_id:
        session_id = str(datetime.utcnow().timestamp())
        session['cart_id'] = session_id
    
    cart = Cart(session_id=session_id)
    cart.load_from_db()
    return cart


def save_cart(cart):
    """Save cart to database"""
    cart.save_to_db()


def clear_cart():
    """Clear cart from database and session"""
    session_id = session.get('cart_id')
    if session_id:
        CartItem.query.filter_by(session_id=session_id).delete()
        db.session.commit()
        session.pop('cart_id', None)
'''
    
    cart_file = os.path.join(utils_dir, 'cart_helper.py')
    with open(cart_file, 'w') as f:
        f.write(cart_helper_content)
    print(f"✅ Created {cart_file}")
    
    # Create stripe_service.py
    stripe_service_content = '''import stripe
from flask import current_app, url_for


def create_checkout_session(order_id, amount, customer_email=None, success_url=None, cancel_url=None):
    """Create Stripe checkout session"""
    try:
        # Round to avoid floating point issues
        amount_cents = int(round(amount * 100))
        
        session_data = {
            "payment_method_types": ["card"],
            "line_items": [{
                "price_data": {
                    "currency": "zar",
                    "unit_amount": amount_cents,
                    "product_data": {
                        "name": f"Bakers Lovers - Order #{order_id}",
                        "description": "Delicious cakes from Bakers Lovers"
                    }
                },
                "quantity": 1
            }],
            "mode": "payment",
            "success_url": success_url or url_for("checkout.success", _external=True),
            "cancel_url": cancel_url or url_for("checkout.cancel", _external=True),
            "metadata": {
                "order_id": str(order_id)
            },
            "billing_address_collection": "required",
            "shipping_address_collection": {
                "allowed_countries": ["ZA"],
            }
        }
        
        # Add customer email if provided
        if customer_email:
            session_data["customer_email"] = customer_email
        
        session = stripe.checkout.Session.create(**session_data)
        return session
    except stripe.error.StripeError as e:
        current_app.logger.error(f"Stripe error: {str(e)}")
        raise
    except Exception as e:
        current_app.logger.error(f"Unexpected error creating checkout session: {str(e)}")
        raise


def get_stripe_keys():
    """Get Stripe configuration keys"""
    return {
        "publishable_key": current_app.config["STRIPE_PUBLISHABLE_KEY"],
        "secret_key": current_app.config["STRIPE_SECRET_KEY"]
    }
'''
    
    stripe_file = os.path.join(utils_dir, 'stripe_service.py')
    with open(stripe_file, 'w') as f:
        f.write(stripe_service_content)
    print(f"✅ Created {stripe_file}")
    
    print("\n🎉 Utils directory setup complete!")

if __name__ == '__main__':
    setup_utils_directory()