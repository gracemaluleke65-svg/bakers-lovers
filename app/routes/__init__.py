# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import stripe
from config import Config
import base64
import os

db = SQLAlchemy()
login_manager = LoginManager()
session_store = Session()
csrf = CSRFProtect()
migrate = Migrate()

def create_app(config_class=Config):
    # Get the base directory of the app package
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_folder = os.path.join(base_dir, 'static')
    
    # Create app with explicit static folder
    app = Flask(
        __name__, 
        static_folder=static_folder,
        static_url_path='/static'
    )
    app.config.from_object(config_class)
    
    # Initialize extensions in correct order
    db.init_app(app)
    migrate.init_app(app, db)  # Initialize migrate BEFORE login manager
    login_manager.init_app(app)
    session_store.init_app(app)
    csrf.init_app(app)
    
    # Configure Stripe
    stripe.api_key = app.config['STRIPE_SECRET_KEY']
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    # Add b64encode filter to Jinja2
    def b64encode(value):
        if value is None:
            return ''
        if isinstance(value, str):
            value = value.encode('utf-8')
        return base64.b64encode(value).decode('utf-8')
    
    app.jinja_env.filters['b64encode'] = b64encode
    
    # Register blueprints
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.routes.products import bp as products_bp
    app.register_blueprint(products_bp, url_prefix='/products')
    
    from app.routes.cart import bp as cart_bp
    app.register_blueprint(cart_bp, url_prefix='/cart')
    
    from app.routes.checkout import bp as checkout_bp
    app.register_blueprint(checkout_bp, url_prefix='/checkout')
    
    from app.routes.orders import bp as orders_bp
    app.register_blueprint(orders_bp, url_prefix='/orders')
    
    from app.routes.favorites import bp as favorites_bp
    app.register_blueprint(favorites_bp, url_prefix='/favorites')
    
    from app.routes.feedback import bp as feedback_bp
    app.register_blueprint(feedback_bp, url_prefix='/feedback')
    
    from app.routes.coupons import bp as coupons_bp
    app.register_blueprint(coupons_bp, url_prefix='/coupons')
    
    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    return app