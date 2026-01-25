from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Order, OrderItem, Product
from app.forms import OrderForm  # Removed duplicate form definitions

bp = Blueprint('orders', __name__)

@bp.route('/')
@login_required
def index():
    if current_user.is_admin:
        orders = Order.query.order_by(Order.order_date.desc()).all()
    else:
        orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    
    return render_template('orders/index.html', orders=orders)

@bp.route('/<int:id>')
@login_required
def details(id):
    order = Order.query.get_or_404(id)
    
    # Check if user owns the order or is admin
    if not current_user.is_admin and order.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('orders.index'))
    
    return render_template('orders/details.html', order=order)

@bp.route('/<int:id>/change-status', methods=['POST'])
@login_required
def change_status(id):
    if not current_user.is_admin:
        flash('Admin access required.', 'error')
        return redirect(url_for('orders.index'))
    
    order = Order.query.get_or_404(id)
    new_status = request.form.get('status')
    
    if new_status in ['Pending', 'Baking', 'Shipped', 'Delivered', 'Cancelled']:
        order.status = new_status
        
        # If order is delivered, automatically mark as paid if not already
        if new_status == 'Delivered' and order.payment_status == 'Pending':
            order.payment_status = 'Paid'
        
        db.session.commit()
        flash(f'Order status updated to {new_status}.', 'success')
    
    return redirect(url_for('orders.details', id=id))

@bp.route('/<int:id>/cancel', methods=['POST'])
@login_required
def cancel(id):
    order = Order.query.get_or_404(id)
    
    # Check if user owns the order
    if order.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('orders.index'))
    
    # Check if order can be cancelled
    if order.status in ['Shipped', 'Delivered', 'Cancelled']:
        flash('Order cannot be cancelled once shipped, delivered, or already cancelled.', 'error')
        return redirect(url_for('orders.details', id=id))
    
    # Cancel order
    order.status = 'Cancelled'
    order.payment_status = 'Refunded'
    
    # Restore stock only if not already restored
    if order.status != 'Cancelled':  # Prevent double restoration
        for item in order.items:
            if item.product:  # Check if product still exists
                item.product.stock += item.quantity
    
    db.session.commit()
    
    flash('Your order was cancelled successfully.', 'success')
    return redirect(url_for('orders.details', id=id))

@bp.route('/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete(id):
    order = Order.query.get_or_404(id)
    
    # Check if user is admin (only admins can delete orders)
    if not current_user.is_admin:
        flash('Admin access required.', 'error')
        return redirect(url_for('orders.index'))
    
    # Check if order can be deleted (only pending or cancelled orders)
    if order.status not in ['Pending', 'Cancelled']:
        flash('Only pending or cancelled orders can be deleted.', 'error')
        return redirect(url_for('orders.details', id=id))
    
    if request.method == 'POST':
        try:
            # Restore stock before deleting (only for pending orders)
            if order.status == 'Pending':
                for item in order.items:
                    if item.product:
                        item.product.stock += item.quantity
            
            # Delete the order (cascade will delete order items)
            db.session.delete(order)
            db.session.commit()
            
            flash('Order deleted successfully.', 'success')
            return redirect(url_for('orders.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting order: {str(e)}', 'error')
            return redirect(url_for('orders.details', id=id))
    
    return render_template('orders/delete.html', order=order)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    order = Order.query.get_or_404(id)
    
    # Check if user is admin (only admins can edit orders)
    if not current_user.is_admin:
        flash('Admin access required.', 'error')
        return redirect(url_for('orders.index'))
    
    form = OrderForm(obj=order)
    
    if form.validate_on_submit():
        # Preserve order_date when editing
        order.user_id = form.user_id.data
        order.total_amount = form.total_amount.data
        order.status = form.status.data
        order.payment_status = form.payment_status.data
        order.delivery_address = form.delivery_address.data
        order.stripe_session_id = form.stripe_session_id.data
        
        db.session.commit()
        flash('Order updated successfully!', 'success')
        return redirect(url_for('orders.details', id=id))
    
    return render_template('orders/edit.html', order=order, form=form)