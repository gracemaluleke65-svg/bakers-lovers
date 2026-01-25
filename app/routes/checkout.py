from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Order, OrderItem, Product
from app.utils.cart_helper import get_cart, clear_cart
from app.utils.stripe_service import create_checkout_session
import stripe

bp = Blueprint('checkout', __name__)

@bp.route('/')
@login_required
def index():
    cart = get_cart()
    if not cart.items:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('cart.index'))
    
    # Calculate discount
    coupon_code = session.get('coupon_code')
    coupon_value = session.get('coupon_value', 0)
    coupon_is_percentage = session.get('coupon_is_percentage', False)
    
    discount = 0
    if coupon_code:
        if coupon_is_percentage:
            discount = float(cart.total) * (float(coupon_value) / 100)
        else:
            discount = float(coupon_value)
        
        if discount > float(cart.total):
            discount = float(cart.total)
    
    grand_total = float(cart.total) - discount
    
    return render_template('checkout/index.html', 
                         cart=cart, 
                         coupon_code=coupon_code,
                         discount=discount,
                         grand_total=grand_total)

@bp.route('/create-order', methods=['POST'])
@login_required
def create_order():
    delivery_address = request.form.get('delivery_address', '').strip()
    if not delivery_address:
        flash('Please provide a delivery address.', 'error')
        return redirect(url_for('checkout.index'))
    
    cart = get_cart()
    if not cart.items:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('cart.index'))
    
    # Stock check with row locking to prevent race conditions
    try:
        for item in cart.items:
            # Use with_for_update to lock the row
            product = Product.query.with_for_update().get(item.product_id)
            if not product:
                flash('One or more products are no longer available.', 'error')
                return redirect(url_for('checkout.index'))
            
            if product.stock < item.quantity:
                flash(f'Sorry, {product.name} is no longer available in the requested quantity. Only {product.stock} left.', 'error')
                return redirect(url_for('checkout.index'))
        
        # Calculate discount
        coupon_code = session.get('coupon_code')
        coupon_value = session.get('coupon_value', 0)
        coupon_is_percentage = session.get('coupon_is_percentage', False)
        
        discount = 0
        if coupon_code:
            if coupon_is_percentage:
                discount = float(cart.total) * (float(coupon_value) / 100)
            else:
                discount = float(coupon_value)
            
            if discount > float(cart.total):
                discount = float(cart.total)
        
        grand_total = float(cart.total) - discount
        
        # Create order
        order = Order(
            user_id=current_user.id,
            delivery_address=delivery_address,
            total_amount=grand_total,
            status='Pending',
            payment_status='Pending'
        )
        db.session.add(order)
        db.session.flush()  # Get the order ID without committing
        
        # Create order items and update stock
        for item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=float(item.unit_price)
            )
            db.session.add(order_item)
            
            # Update stock
            product = Product.query.get(item.product_id)
            product.stock -= item.quantity
        
        # Create Stripe session with proper parameters
        stripe_session = create_checkout_session(
            order_id=order.id,
            amount=grand_total,
            customer_email=current_user.email,
            success_url=url_for('checkout.success', order_id=order.id, _external=True),
            cancel_url=url_for('checkout.cancel', _external=True)
        )
        
        order.stripe_session_id = stripe_session.id
        db.session.commit()
        
        # Clear cart
        clear_cart()
        
        # Clear coupon from session
        session.pop('coupon_code', None)
        session.pop('coupon_value', None)
        session.pop('coupon_is_percentage', None)
        
        # Redirect to Stripe Checkout
        return redirect(stripe_session.url)
        
    except stripe.error.StripeError as e:
        current_app.logger.error(f'Stripe error: {str(e)}')
        db.session.rollback()
        flash('Payment service error. Please try again.', 'error')
        return redirect(url_for('checkout.index'))
    except Exception as e:
        current_app.logger.error(f'Order creation failed: {str(e)}')
        db.session.rollback()
        flash('An error occurred while creating your order. Please try again.', 'error')
        return redirect(url_for('checkout.index'))

@bp.route('/success')
@login_required
def success():
    order_id = request.args.get('order_id', type=int)
    if not order_id:
        flash('Invalid order ID.', 'error')
        return redirect(url_for('main.index'))
    
    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()
    
    # Update order status only if still pending
    if order.payment_status == 'Pending':
        order.payment_status = 'Paid'
        order.status = 'Baking'
        db.session.commit()
    
    return render_template('checkout/success.html', order=order)

@bp.route('/cancel')
@login_required
def cancel():
    return render_template('checkout/cancel.html')