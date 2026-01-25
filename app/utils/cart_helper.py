from flask import session
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