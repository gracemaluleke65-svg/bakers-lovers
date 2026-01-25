from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Product, CartItem, Coupon
from app.utils.cart_helper import get_cart, save_cart, clear_cart
from datetime import datetime

bp = Blueprint('cart', __name__)


@bp.route('/')
@login_required
def index():
    cart = get_cart()
    
    # Get coupon from session
    coupon_code = session.get('coupon_code')
    coupon_value = session.get('coupon_value', 0)
    coupon_is_percentage = session.get('coupon_is_percentage', False)
    
    # Calculate discount
    discount = 0
    if coupon_code:
        if coupon_is_percentage:
            discount = float(cart.total) * (float(coupon_value) / 100)
        else:
            discount = float(coupon_value)
        
        # Never allow negative total
        if discount > float(cart.total):
            discount = float(cart.total)
    
    grand_total = max(0, float(cart.total) - discount)  # Ensure non-negative
    
    return render_template('cart/index.html', 
                         cart=cart, 
                         coupon_code=coupon_code,
                         discount=discount,
                         grand_total=grand_total)


@bp.route('/add/<int:product_id>', methods=['POST'])
def add(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = request.form.get('quantity', 1, type=int)
    
    if not product.available or product.stock < 1 or quantity < 1:
        flash('Product not available or invalid quantity.', 'error')
        return redirect(url_for('products.index'))
    
    if quantity > product.stock:
        flash(f'Only {product.stock} items available in stock.', 'error')
        return redirect(url_for('products.index'))
    
    cart = get_cart()
    cart.add_item(product, quantity)
    save_cart(cart)
    
    flash(f'{product.name} added to cart!', 'success')
    return redirect(url_for('cart.index'))


@bp.route('/remove/<int:product_id>', methods=['POST'])
def remove(product_id):
    cart = get_cart()
    cart.remove_item(product_id)
    save_cart(cart)
    
    flash('Item removed from cart.', 'success')
    return redirect(url_for('cart.index'))


@bp.route('/update/<int:product_id>', methods=['POST'])
def update_item_ajax(product_id):
    """AJAX endpoint for updating cart items"""
    product = Product.query.get_or_404(product_id)
    quantity = request.form.get('quantity', 1, type=int)
    
    if quantity < 1:
        return jsonify({'error': 'Quantity must be at least 1'}), 400
    
    if quantity > product.stock:
        return jsonify({'error': f'Only {product.stock} items available in stock'}), 400
    
    cart = get_cart()
    
    # Update the cart item
    cart_item = CartItem.query.filter_by(
        session_id=cart.session_id,
        product_id=product_id
    ).first()
    
    if cart_item:
        cart_item.quantity = quantity
        try:
            db.session.commit()
            
            # Calculate new totals
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
            
            grand_total = max(0, float(cart.total) - discount)
            
            # Get updated item subtotal
            item_subtotal = float(cart_item.unit_price) * cart_item.quantity
            
            return jsonify({
                'success': True,
                'item_subtotal': round(item_subtotal, 2),
                'cart_total': round(float(cart.total), 2),
                'discount': round(discount, 2),
                'grand_total': round(grand_total, 2),
                'item_count': len(cart)
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Error updating cart'}), 500
    
    return jsonify({'error': 'Item not found in cart'}), 404


@bp.route('/apply-coupon', methods=['POST'])
def apply_coupon():
    code = request.form.get('code', '').strip()
    if not code:
        flash('Please enter a coupon code.', 'error')
        return redirect(url_for('cart.index'))
    
    # Find coupon (case-insensitive)
    coupon = Coupon.query.filter(
        Coupon.code.ilike(code),
        Coupon.active == True
    ).first()
    
    if not coupon or not coupon.is_valid():
        flash('Invalid or expired coupon code.', 'error')
        return redirect(url_for('cart.index'))
    
    # Store coupon in session
    session['coupon_code'] = coupon.code
    session['coupon_value'] = float(coupon.discount_amount)
    session['coupon_is_percentage'] = coupon.is_percentage
    
    flash(f'Coupon "{coupon.code}" applied!', 'success')
    return redirect(url_for('cart.index'))


@bp.route('/remove-coupon', methods=['POST'])
def remove_coupon():
    # Remove coupon from session
    session.pop('coupon_code', None)
    session.pop('coupon_value', None)
    session.pop('coupon_is_percentage', None)
    
    flash('Coupon removed.', 'success')
    return redirect(url_for('cart.index'))


@bp.route('/get-count')
def get_count():
    cart = get_cart()
    return jsonify({'count': len(cart)})


@bp.route('/get-totals', methods=['GET'])
def get_totals():
    """Get current cart totals for AJAX refresh"""
    cart = get_cart()
    
    # Get coupon info
    coupon_code = session.get('coupon_code')
    coupon_value = session.get('coupon_value', 0)
    coupon_is_percentage = session.get('coupon_is_percentage', False)
    
    # Calculate discount
    discount = 0
    if coupon_code:
        if coupon_is_percentage:
            discount = float(cart.total) * (float(coupon_value) / 100)
        else:
            discount = float(coupon_value)
        
        if discount > float(cart.total):
            discount = float(cart.total)
    
    grand_total = max(0, float(cart.total) - discount)
    
    return jsonify({
        'cart_total': round(float(cart.total), 2),
        'discount': round(discount, 2),
        'grand_total': round(grand_total, 2),
        'item_count': len(cart)
    })