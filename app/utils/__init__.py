
# app/__init__.py - COMPLETE with admin seeding
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
import random
from werkzeug.security import generate_password_hash
from datetime import datetime

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
    migrate.init_app(app, db)
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
        from app.models import BKL_User
        return BKL_User.query.get(int(user_id))
    
    # Add b64encode filter to Jinja2
    def b64encode(value):
        if value is None:
            return ''
        if isinstance(value, str):
            value = value.encode('utf-8')
        return base64.b64encode(value).decode('utf-8')
    
    app.jinja_env.filters['b64encode'] = b64encode
    
    # =============================================
    # CREATE TABLES AND SEED ADMIN ON STARTUP
    # =============================================
    with app.app_context():
        try:
            # Create all tables
            print("📦 Creating database tables...")
            db.create_all()
            print("✅ Tables created successfully!")
            
            # Import models here to avoid circular imports
            from app.models import BKL_User, BKL_Product, BKL_Coupon
            
            # Check if admin exists
            admin_email = 'admin@bakerslovers.com'
            admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
            
            admin = BKL_User.query.filter_by(email=admin_email).first()
            
            if not admin:
                print("👤 Creating admin user...")
                # Generate unique 13-digit ID
                import random
                while True:
                    new_id = f'{random.randint(1000000000000, 9999999999999)}'
                    if not BKL_User.query.filter_by(id_number=new_id).first():
                        break
                
                admin = BKL_User(
                    email=admin_email,
                    password_hash=generate_password_hash(admin_password),
                    first_name='Admin',
                    last_name='User',
                    phone_number='0123456789',
                    id_number=new_id,
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print(f"✅ Admin created: {admin_email} / {admin_password}")
            else:
                # Ensure admin has correct password and admin flag
                admin.password_hash = generate_password_hash(admin_password)
                admin.is_admin = True
                db.session.commit()
                print(f"✅ Admin verified: {admin_email}")
            
            # Create sample products if none exist
            if BKL_Product.query.count() == 0:
                print("🍰 Creating sample products...")
                from datetime import datetime, timedelta
                products = [
                    BKL_Product(name='Chocolate Birthday Cake', description='Rich chocolate cake perfect for birthdays', category='Birthday', size='8-inch', stock=10, price=450.00, available=True),
                    BKL_Product(name='Wedding Vanilla Cake', description='Elegant vanilla cake for weddings', category='Wedding', size='3-tier', stock=5, price=2500.00, available=True),
                    BKL_Product(name='Custom Red Velvet', description='Customizable red velvet cake', category='Custom', size='6-inch', stock=8, price=380.00, available=True)
                ]
                for p in products:
                    db.session.add(p)
                db.session.commit()
                print(f"✅ Created {len(products)} sample products")
            
            # Create sample coupon if none exist
            if BKL_Coupon.query.count() == 0:
                print("🎟️ Creating sample coupon...")
                from datetime import datetime, timedelta
                coupon = BKL_Coupon(
                    code='BAKERS10',
                    discount_amount=10,
                    is_percentage=True,
                    valid_from=datetime.utcnow() - timedelta(days=1),
                    valid_to=datetime.utcnow() + timedelta(days=365),
                    active=True
                )
                db.session.add(coupon)
                db.session.commit()
                print("✅ Created sample coupon: BAKERS10")
            
            print("=" * 50)
            print("✅ DATABASE INITIALIZATION COMPLETE!")
            print(f"🔑 Admin Login: {admin_email}")
            print(f"🔑 Admin Password: {admin_password}")
            print("=" * 50)
            
        except Exception as e:
            print(f"⚠️ Database initialization error: {e}")
            import traceback
            traceback.print_exc()
    
    # =============================================
    # REGISTER BLUEPRINTS
    # =============================================
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