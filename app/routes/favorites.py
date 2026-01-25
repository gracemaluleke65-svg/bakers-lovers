from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf
from wtforms import ValidationError
from app import db
from app.models import Favorite, Product

bp = Blueprint('favorites', __name__)


@bp.route('/')
@login_required
def index():
    favorites = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.added_at.desc()).all()
    return render_template('favorites/index.html', favorites=favorites)


@bp.route('/toggle/<int:product_id>', methods=['POST'])
@login_required
def toggle(product_id):
    # Validate CSRF token
    try:
        csrf_token = request.form.get('csrf_token')
        if not csrf_token:
            csrf_token = request.headers.get('X-CSRFToken')
        validate_csrf(csrf_token)
    except ValidationError:
        return jsonify({'error': 'Invalid CSRF token', 'favorited': False}), 400
    
    product = Product.query.get_or_404(product_id)
    
    existing = Favorite.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()
    
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'favorited': False})
    else:
        favorite = Favorite(
            user_id=current_user.id,
            product_id=product_id
        )
        db.session.add(favorite)
        db.session.commit()
        return jsonify({'favorited': True})