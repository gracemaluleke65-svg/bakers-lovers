# run.py - Complete with BKL_ prefix
import os
from app import create_app, db
from app.models import BKL_User, BKL_Product, BKL_Order, BKL_OrderItem, BKL_CartItem, BKL_Coupon, BKL_Favorite, BKL_Feedback, BKL_Payment
from flask_migrate import Migrate
from sqlalchemy import text, inspect
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

app = create_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'BKL_User': BKL_User, 
        'BKL_Product': BKL_Product, 
        'BKL_Order': BKL_Order,
        'BKL_OrderItem': BKL_OrderItem, 
        'BKL_CartItem': BKL_CartItem, 
        'BKL_Coupon': BKL_Coupon,
        'BKL_Favorite': BKL_Favorite, 
        'BKL_Feedback': BKL_Feedback, 
        'BKL_Payment': BKL_Payment
    }

# Create all tables and seed data on startup
with app.app_context():
    print("=" * 60)
    print("BAKERS LOVERS - DATABASE INITIALIZATION")
    print("=" * 60)
    
    try:
        # Create all tables
        print("\n📦 Creating database tables...")
        db.create_all()
        print("✅ Tables created successfully!")
        
        # Check if admin exists
        admin = BKL_User.query.filter_by(email='admin@bakerslovers.com').first()
        admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
        
        if not admin:
            print("\n👤 Creating admin user...")
            # Generate unique 13-digit ID
            while True:
                new_id = f'{random.randint(1000000000000, 9999999999999)}'
                if not BKL_User.query.filter_by(id_number=new_id).first():
                    break
            
            admin = BKL_User(
                email='admin@bakerslovers.com',
                password_hash=generate_password_hash(admin_password),
                first_name='Admin',
                last_name='User',
                phone_number='0123456789',
                id_number=new_id,
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Admin created: admin@bakerslovers.com / {admin_password}")
        else:
            # Ensure admin has correct password
            admin.password_hash = generate_password_hash(admin_password)
            admin.is_admin = True
            db.session.commit()
            print(f"✅ Admin updated: admin@bakerslovers.com / {admin_password}")
        
        # Create sample products if none exist
        if BKL_Product.query.count() == 0:
            print("\n🍰 Creating sample products...")
            products = [
                BKL_Product(name='Chocolate Birthday Cake', description='Rich chocolate cake perfect for birthdays', category='Birthday', size='8-inch', stock=10, price=450.00, available=True),
                BKL_Product(name='Wedding Vanilla Cake', description='Elegant vanilla cake for weddings', category='Wedding', size='3-tier', stock=5, price=2500.00, available=True),
                BKL_Product(name='Custom Red Velvet', description='Customizable red velvet cake', category='Custom', size='6-inch', stock=8, price=380.00, available=True)
            ]
            for p in products:
                db.session.add(p)
            db.session.commit()
            print(f"✅ Created {len(products)} products")
        
        # Create sample coupon if none exist
        if BKL_Coupon.query.count() == 0:
            print("\n🎟️ Creating sample coupon...")
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
            print("✅ Coupon created: BAKERS10")
        
        print("\n" + "=" * 60)
        print("✅ DATABASE IS READY FOR USE!")
        print(f"🔑 Admin Login: admin@bakerslovers.com")
        print(f"🔑 Admin Password: {admin_password}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)