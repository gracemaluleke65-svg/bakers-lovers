from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models import Product, Cart
from app.utils.cart_helper import get_cart
import os

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Get featured products - fix decimal conversion
    featured_products = Product.query.filter_by(available=True).order_by(func.random()).limit(3).all()
    
    # Convert prices to float to avoid SQLite decimal warnings
    for product in featured_products:
        product.price = float(product.price)
    
    cart = get_cart() if current_user.is_authenticated else None
    
    return render_template('main/index.html',
                         featured_products=featured_products,
                         cart=cart)

@bp.route('/about')
def about():
    return render_template('main/about.html')

@bp.route('/contact')
def contact():
    return render_template('main/contact.html')

@bp.route('/terms')
def terms():
    return render_template('main/terms.html')

@bp.route('/privacy')
def privacy():
    return render_template('main/privacy.html')

# Fixed - use @bp.route instead of @app.route
@bp.route('/test-image')
def test_image():
    from flask import current_app
    
    static_path = os.path.join(current_app.static_folder, 'img')
    image_path = os.path.join(static_path, 'shichabo_nkuna.jpg')
    
    return jsonify({
        'static_folder': current_app.static_folder,
        'static_url_path': current_app.static_url_path,
        'file_exists': os.path.exists(image_path),
        'file_size': os.path.getsize(image_path) if os.path.exists(image_path) else 0,
        'image_url': url_for('static', filename='img/shichabo_nkuna.jpg'),
        'direct_test': "/static/img/shichabo_nkuna.jpg",
        'python_path': os.path.abspath(image_path) if os.path.exists(image_path) else 'File not found'
    })