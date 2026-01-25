from app import db
from app.models import User, Product, Coupon
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import os

def seed_database():
    """Seed initial data for the application"""
    
    # Get admin password from environment variable or use default
    admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
    
    # Create admin user if not exists
    admin = User.query.filter_by(email='admin@bakerslovers.com').first()
    if not admin:
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
        print("Admin user created")
    
    # Create sample products if none exist
    if Product.query.count() == 0:
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
        print("Sample products created")
    
    # Create sample coupon if none exist
    if Coupon.query.count() == 0:
        coupon = Coupon(
            code='BAKERS10',
            discount_amount=10,
            is_percentage=True,
            valid_from=datetime.utcnow() - timedelta(days=1),
            valid_to=datetime.utcnow() + timedelta(days=30),
            active=True
        )
        db.session.add(coupon)
        print("Sample coupon created")
    
    try:
        db.session.commit()
        print("Database seeded successfully")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding database: {e}")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_database()