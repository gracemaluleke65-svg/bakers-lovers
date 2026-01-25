# app/routes/admin.py - UPDATED VERSION WITH FIXED DASHBOARD
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta
from app import db
from app.models import User, Order, Product, CartItem, Favorite, Feedback

bp = Blueprint('admin', __name__)

@bp.before_request
@login_required
def require_admin():
    if not current_user.is_admin:
        flash('Admin access required.', 'error')
        return redirect(url_for('main.index'))

@bp.route('/dashboard')
def dashboard():
    """Admin dashboard with statistics"""
    try:
        # Basic counts
        total_users = User.query.count()
        total_orders = Order.query.count()
        pending_orders = Order.query.filter_by(status='Pending').all()
        total_products = Product.query.count()
        
        # Calculate total revenue from paid orders
        paid_orders = Order.query.filter_by(payment_status='Paid').all()
        total_revenue = sum(float(order.total_amount) for order in paid_orders)
        
        # Get recent orders (last 10)
        recent_orders = Order.query.order_by(Order.order_date.desc()).limit(10).all()
        
        # Get low stock products (less than 5 items)
        low_stock_products = Product.query.filter(Product.stock < 5, Product.available == True).all()
        
        # Get current date for the template
        current_date = datetime.utcnow()
        
        # Debug output
        print(f"DEBUG: Dashboard stats - Users: {total_users}, Orders: {total_orders}, Revenue: {total_revenue}")
        
        return render_template('admin/dashboard.html',
                             total_users=total_users,
                             total_orders=total_orders,
                             pending_orders=pending_orders,
                             total_products=total_products,
                             recent_orders=recent_orders,
                             total_revenue=total_revenue,
                             low_stock_products=low_stock_products,
                             current_date=current_date)
    except Exception as e:
        print(f"ERROR in dashboard: {e}")
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@bp.route('/generate-report', methods=['POST'])
def generate_report():
    """Generate sales report"""
    try:
        report_type = request.form.get('report_type')
        format_type = request.form.get('format')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        # Calculate date range based on report type
        now = datetime.utcnow()
        
        if report_type == 'daily':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif report_type == 'weekly':
            start_date = now - timedelta(days=7)
            end_date = now
        elif report_type == 'monthly':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif report_type == 'yearly':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif report_type == 'custom' and start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        else:
            flash('Invalid report parameters.', 'error')
            return redirect(url_for('admin.dashboard'))
        
        # Get orders within date range
        orders = Order.query.filter(
            Order.order_date >= start_date,
            Order.order_date <= end_date
        ).all()
        
        total_sales = sum(float(order.total_amount) for order in orders if order.payment_status == 'Paid')
        total_orders_count = len(orders)
        
        flash(f'Report generated successfully! Total sales: R{total_sales:.2f} from {total_orders_count} orders between {start_date.strftime("%Y-%m-%d")} and {end_date.strftime("%Y-%m-%d")}', 'success')
        
        return redirect(url_for('admin.dashboard'))
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))

@bp.route('/users')
def users():
    """Display all users in the system"""
    try:
        # Get all users
        users = User.query.order_by(User.created_at.desc()).all()
        
        # Debug output
        print(f"DEBUG: Users route - Found {len(users)} users")
        
        # Get current time
        now = datetime.utcnow()
        
        return render_template('admin/users.html', 
                             users=users, 
                             now=now)
    except Exception as e:
        print(f"ERROR in users route: {e}")
        flash(f'Error loading users: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))

@bp.route('/users/<int:user_id>')
def user_detail(user_id):
    """View detailed information about a specific user"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Get user's orders
        orders = Order.query.filter_by(user_id=user.id).order_by(Order.order_date.desc()).all()
        
        # Get user's favorites
        favorites = Favorite.query.filter_by(user_id=user.id).order_by(Favorite.added_at.desc()).all()
        
        # Get user's feedback
        feedbacks = Feedback.query.filter_by(user_id=user.id).order_by(Feedback.submitted_at.desc()).all()
        
        # Calculate total spent
        total_spent = sum(float(order.total_amount) for order in orders if order.payment_status == 'Paid')
        
        return render_template('admin/user_detail.html', 
                             user=user, 
                             orders=orders,
                             favorites=favorites,
                             feedbacks=feedbacks,
                             total_spent=total_spent)
    except Exception as e:
        flash(f'Error loading user details: {str(e)}', 'error')
        return redirect(url_for('admin.users'))

@bp.route('/users/make-admin/<int:user_id>', methods=['POST'])
def make_admin(user_id):
    """Grant admin privileges to a user"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent self-demotion
        if user.id == current_user.id:
            flash('You cannot change your own admin status.', 'error')
            return redirect(url_for('admin.users'))
        
        user.is_admin = True
        db.session.commit()
        flash(f'{user.full_name()} is now an admin.', 'success')
        return redirect(url_for('admin.users'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error making user admin: {str(e)}', 'error')
        return redirect(url_for('admin.users'))

@bp.route('/users/remove-admin/<int:user_id>', methods=['POST'])
def remove_admin(user_id):
    """Remove admin privileges from a user"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent self-demotion
        if user.id == current_user.id:
            flash('You cannot change your own admin status.', 'error')
            return redirect(url_for('admin.users'))
        
        user.is_admin = False
        db.session.commit()
        flash(f'{user.full_name()} is no longer an admin.', 'success')
        return redirect(url_for('admin.users'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing admin privileges: {str(e)}', 'error')
        return redirect(url_for('admin.users'))

@bp.route('/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """Delete a user and all associated data"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent self-deletion
        if user.id == current_user.id:
            flash('You cannot delete your own account.', 'error')
            return redirect(url_for('admin.users'))
        
        # Get user's full name for flash message
        user_name = user.full_name()
        
        # Delete all related data
        Order.query.filter_by(user_id=user.id).delete()
        CartItem.query.filter_by(session_id=str(user.id)).delete()  # Fixed: session_id is string
        Favorite.query.filter_by(user_id=user.id).delete()
        Feedback.query.filter_by(user_id=user.id).delete()
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        flash(f'User {user_name} and all associated data have been deleted.', 'success')
        return redirect(url_for('admin.users'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'error')
        return redirect(url_for('admin.users'))

@bp.route('/orders')
def orders():
    """Display all orders in the system"""
    try:
        orders = Order.query.order_by(Order.order_date.desc()).all()
        return render_template('admin/orders.html', orders=orders)
    except Exception as e:
        flash(f'Error loading orders: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))

@bp.route('/orders/<int:order_id>')
def order_detail(order_id):
    """View detailed information about a specific order"""
    try:
        order = Order.query.get_or_404(order_id)
        return render_template('admin/order_detail.html', order=order)
    except Exception as e:
        flash(f'Error loading order details: {str(e)}', 'error')
        return redirect(url_for('admin.orders'))

@bp.route('/orders/update-status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    """Update the status of an order"""
    try:
        order = Order.query.get_or_404(order_id)
        new_status = request.form.get('status')
        
        if new_status in ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']:
            order.status = new_status
            db.session.commit()
            flash(f'Order #{order.id} status updated to {new_status}.', 'success')
        else:
            flash('Invalid order status.', 'error')
        
        return redirect(url_for('admin.order_detail', order_id=order.id))
    except Exception as e:
        flash(f'Error updating order status: {str(e)}', 'error')
        return redirect(url_for('admin.order_detail', order_id=order_id))

@bp.route('/debug-users')
def debug_users():
    """Debug route to check users in database"""
    try:
        # Get all users
        all_users = User.query.all()
        user_list = []
        
        for user in all_users:
            user_list.append({
                'id': user.id,
                'email': user.email,
                'name': user.full_name(),
                'is_admin': user.is_admin,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None
            })
        
        return jsonify({
            'total_users': len(all_users),
            'users': user_list
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Simple route to check admin access
@bp.route('/check-access')
@login_required
def check_access():
    """Check if current user has admin access"""
    return jsonify({
        'authenticated': current_user.is_authenticated,
        'user_id': current_user.id,
        'email': current_user.email,
        'is_admin': current_user.is_admin
    })