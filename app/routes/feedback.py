from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Feedback, Order
from app.forms import FeedbackForm
from flask_wtf.csrf import validate_csrf
from wtforms import ValidationError

bp = Blueprint('feedback', __name__)

@bp.route('/create', methods=['GET'])
@login_required
def create_select():
    """Show page to select an order to review"""
    # Get delivered orders that haven't been reviewed yet
    reviewed_order_ids = [f.order_id for f in Feedback.query.filter_by(user_id=current_user.id).all()]
    
    orders = Order.query.filter_by(
        user_id=current_user.id,
        status='Delivered'
    ).filter(~Order.id.in_(reviewed_order_ids) if reviewed_order_ids else True).all()
    
    return render_template('feedback/select_order.html', orders=orders)

@bp.route('/create/<int:order_id>', methods=['GET', 'POST'])
@login_required
def create(order_id):
    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()
    
    # Check if feedback already exists
    existing = Feedback.query.filter_by(
        order_id=order_id,
        user_id=current_user.id
    ).first()
    
    if existing:
        flash('You have already submitted feedback for this order.', 'info')
        return redirect(url_for('feedback.index'))
    
    # Check if order is delivered (only allow feedback for delivered orders)
    if order.status != 'Delivered':
        flash('You can only review delivered orders.', 'warning')
        return redirect(url_for('orders.index'))
    
    form = FeedbackForm()
    
    if form.validate_on_submit():
        feedback = Feedback(
            user_id=current_user.id,
            order_id=order_id,
            rating=form.rating.data,
            comment=form.comment.data.strip()
        )
        db.session.add(feedback)
        db.session.commit()
        
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('feedback.index'))
    
    return render_template('feedback/create.html', form=form, order=order)

@bp.route('/')
@login_required
def index():
    feedbacks = Feedback.query.filter_by(user_id=current_user.id).order_by(Feedback.submitted_at.desc()).all()
    return render_template('feedback/index.html', feedbacks=feedbacks)

@bp.route('/<int:id>')
@login_required
def details(id):
    feedback = Feedback.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('feedback/details.html', feedback=feedback)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    feedback = Feedback.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()
    
    form = FeedbackForm(obj=feedback)
    
    if form.validate_on_submit():
        feedback.rating = form.rating.data
        feedback.comment = form.comment.data.strip()
        db.session.commit()
        
        flash('Review updated successfully!', 'success')
        return redirect(url_for('feedback.details', id=feedback.id))
    
    return render_template('feedback/edit.html', form=form, feedback=feedback)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    feedback = Feedback.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()
    
    # Flask-WTF CSRF is already protecting this via the form
    db.session.delete(feedback)
    db.session.commit()
    flash('Review deleted successfully!', 'success')
    return redirect(url_for('feedback.index'))