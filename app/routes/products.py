from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from app import db
from app.models import Product, CartItem
from app.forms import ProductForm
from app.utils.cart_helper import get_cart
import io

bp = Blueprint('products', __name__)

@bp.route('/')
def index():
    # Added try-except for better error handling
    try:
        products = Product.query.filter(Product.stock > 0, Product.available == True).all()
        cart = get_cart()
        return render_template('products/index.html', products=products, cart=cart)
    except Exception as e:
        flash('Error loading products. Please try again.', 'error')
        return render_template('products/index.html', products=[], cart=None)

@bp.route('/<int:id>')
def details(id):
    try:
        product = Product.query.get_or_404(id)
        cart = get_cart()
        return render_template('products/details.html', product=product, cart=cart)
    except Exception as e:
        flash('Product not found or error loading details.', 'error')
        return redirect(url_for('products.index'))

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    # Enhanced admin check
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Admin access required.', 'error')
        return redirect(url_for('products.index'))
    
    form = ProductForm()
    if form.validate_on_submit():
        try:
            product = Product(
                name=form.name.data,
                description=form.description.data,
                category=form.category.data,
                size=form.size.data,
                stock=form.stock.data,
                price=form.price.data,
                available=True  # Added this field
            )
            
            if form.image_file.data:
                # Add file size validation
                image_data = form.image_file.data.read()
                if len(image_data) > 4 * 1024 * 1024:  # 4MB limit
                    flash('Image file size must be less than 4MB.', 'error')
                    return render_template('products/create.html', form=form)
                product.image_bytes = image_data
            
            db.session.add(product)
            db.session.commit()
            
            flash('Product created successfully!', 'success')
            return redirect(url_for('products.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating product: {str(e)}', 'error')
            return render_template('products/create.html', form=form)
    
    return render_template('products/create.html', form=form)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Admin access required.', 'error')
        return redirect(url_for('products.index'))
    
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        try:
            product.name = form.name.data
            product.description = form.description.data
            product.category = form.category.data
            product.size = form.size.data
            product.stock = form.stock.data
            product.price = form.price.data
            
            # Check if new image is uploaded
            if form.image_file.data:
                image_data = form.image_file.data.read()
                if len(image_data) > 4 * 1024 * 1024:  # 4MB limit
                    flash('Image file size must be less than 4MB.', 'error')
                    return render_template('products/edit.html', form=form, product=product)
                product.image_bytes = image_data
            
            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('products.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {str(e)}', 'error')
            return render_template('products/edit.html', form=form, product=product)
    
    return render_template('products/edit.html', form=form, product=product)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    # CSRF protection is handled by Flask-WTF automatically
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Admin access required.', 'error')
        return redirect(url_for('products.index'))
    
    try:
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'error')
    
    return redirect(url_for('products.index'))

@bp.route('/<int:id>/image')
def product_image(id):
    try:
        product = Product.query.get_or_404(id)
        if product.image_bytes:
            return send_file(
                io.BytesIO(product.image_bytes),
                mimetype='image/jpeg',
                as_attachment=False,
                download_name=f'{product.name.replace(" ", "_")}.jpg'
            )
        return redirect(url_for('static', filename='images/no-image.png'))
    except Exception as e:
        flash('Error loading image.', 'error')
        return redirect(url_for('products.index'))

@bp.route('/<int:id>/download-image')
@login_required
def download_image(id):
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Admin access required.', 'error')
        return redirect(url_for('products.index'))
    
    try:
        product = Product.query.get_or_404(id)
        if product.image_bytes:
            return send_file(
                io.BytesIO(product.image_bytes),
                mimetype='image/jpeg',
                as_attachment=True,
                download_name=f'{product.name.replace(" ", "_")}.jpg'
            )
        flash('No image available for download.', 'error')
        return redirect(url_for('products.edit', id=id))
    except Exception as e:
        flash('Error downloading image.', 'error')
        return redirect(url_for('products.index'))