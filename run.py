# run.py - TEMPORARY VERSION for database reset
import os
from app import create_app, db
from app.models import User, Product, Order, OrderItem, CartItem, Coupon, Favorite, Feedback, Payment
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash

# Get config
env = os.environ.get('FLASK_ENV', 'production')

# Force database reset flag - set to True to reset, False to run normally
RESET_DATABASE = True  # <-- Set this to False after first successful deploy

app = create_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Product': Product,
        'Order': Order,
        'OrderItem': OrderItem,
        'CartItem': CartItem,
        'Coupon': Coupon,
        'Favorite': Favorite,
        'Feedback': Feedback,
        'Payment': Payment
    }

# ONE-TIME DATABASE RESET
if RESET_DATABASE:
    with app.app_context():
        print("=" * 50)
        print("RESETTING DATABASE - ONE TIME FIX")
        print("=" * 50)
        
        # Drop all tables
        db.drop_all()
        print("✅ All tables dropped")
        
        # Create all tables with current schema
        db.create_all()
        print("✅ All tables recreated with correct schema")
        
        # Create admin user
        admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
        admin = User(
            email='admin@bakerslovers.com',
            password_hash=generate_password_hash(admin_password),
            first_name='Admin',
            last_name='User',
            phone_number='0123456789',
            id_number='1234567890123',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Admin user created: admin@bakerslovers.com / {admin_password}")
        
        # Create sample products
        if Product.query.count() == 0:
            from datetime import datetime, timedelta
            products = [
                Product(
                    name='Chocolate Birthday Cake',
                    description='Rich chocolate cake perfect for birthdays',
                    category='Birthday',
                    size='8-inch',
                    stock=10,
                    price=450.00,
                    available=True
                ),
                Product(
                    name='Wedding Vanilla Cake',
                    description='Elegant vanilla cake for weddings',
                    category='Wedding',
                    size='3-tier',
                    stock=5,
                    price=2500.00,
                    available=True
                ),
                Product(
                    name='Custom Red Velvet',
                    description='Customizable red velvet cake',
                    category='Custom',
                    size='6-inch',
                    stock=8,
                    price=380.00,
                    available=True
                )
            ]
            for product in products:
                db.session.add(product)
            db.session.commit()
            print("✅ Sample products created")
        
        # Create sample coupon
        if Coupon.query.count() == 0:
            from datetime import datetime, timedelta
            coupon = Coupon(
                code='BAKERS10',
                discount_amount=10,
                is_percentage=True,
                valid_from=datetime.utcnow() - timedelta(days=1),
                valid_to=datetime.utcnow() + timedelta(days=30),
                active=True
            )
            db.session.add(coupon)
            db.session.commit()
            print("✅ Sample coupon created")
        
        print("=" * 50)
        print("DATABASE RESET COMPLETE")
        print("IMPORTANT: Set RESET_DATABASE = False and redeploy!")
        print("=" * 50)

if __name__ == '__main__':
    # For local development only
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)