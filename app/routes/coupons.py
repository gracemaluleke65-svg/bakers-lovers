from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Coupon
from app.forms import CouponForm

bp = Blueprint('coupons', __name__)


@bp.route('/')
@login_required
def index():
    if not current_user.is_admin:
        flash('Admin access required.', 'error')
        return redirect(url_for('main.index'))
    
    coupons = Coupon.query.all()
    return render_template('coupons/index.html', coupons=coupons)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_admin:
        flash('Admin access required.', 'error')
        return redirect(url_for('main.index'))
    
    form = CouponForm()
    if form.validate_on_submit():
        coupon = Coupon(
            code=form.code.data.upper(),
            discount_amount=form.discount_amount.data,
            is_percentage=form.is_percentage.data,
            valid_from=form.valid_from.data,
            valid_to=form.valid_to.data,
            active=form.active.data
        )
        db.session.add(coupon)
        db.session.commit()
        
        flash('Coupon created successfully!', 'success')
        return redirect(url_for('coupons.index'))
    
    return render_template('coupons/create.html', form=form)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    if not current_user.is_admin:
        flash('Admin access required.', 'error')
        return redirect(url_for('main.index'))
    
    coupon = Coupon.query.get_or_404(id)
    form = CouponForm(obj=coupon)
    
    if form.validate_on_submit():
        coupon.code = form.code.data.upper()
        coupon.discount_amount = form.discount_amount.data
        coupon.is_percentage = form.is_percentage.data
        coupon.valid_from = form.valid_from.data
        coupon.valid_to = form.valid_to.data
        coupon.active = form.active.data
        
        db.session.commit()
        flash('Coupon updated successfully!', 'success')
        return redirect(url_for('coupons.index'))
    
    return render_template('coupons/edit.html', form=form, coupon=coupon)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    if not current_user.is_admin:
        flash('Admin access required.', 'error')
        return redirect(url_for('main.index'))
    
    coupon = Coupon.query.get_or_404(id)
    db.session.delete(coupon)
    db.session.commit()
    
    flash('Coupon deleted successfully!', 'success')
    return redirect(url_for('coupons.index'))