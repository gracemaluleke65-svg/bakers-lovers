# run.py - Fix existing admin user
import os
from app import create_app, db
from app.models import User, Product, Order, OrderItem, CartItem, Coupon, Favorite, Feedback, Payment
from flask_migrate import Migrate
from sqlalchemy import text, inspect
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

app = create_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 'User': User, 'Product': Product, 'Order': Order,
        'OrderItem': OrderItem, 'CartItem': CartItem, 'Coupon': Coupon,
        'Favorite': Favorite, 'Feedback': Feedback, 'Payment': Payment
    }

# Database schema and admin fix
with app.app_context():
    print("=" * 60)
    print("DATABASE ADMIN UTILITY")
    print("=" * 60)
    
    try:
        # Check existing users
        all_users = User.query.all()
        print(f"\nTotal users in database: {len(all_users)}")
        
        for user in all_users:
            print(f"  - ID: {user.id}, Email: {user.email}, Admin: {user.is_admin}, ID Num: {user.id_number}")
        
        # Admin credentials
        admin_email = 'admin@bakerslovers.com'
        admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
        
        # Check if admin exists by email
        admin_by_email = User.query.filter_by(email=admin_email).first()
        
        # Check if any user has the default id_number
        admin_by_id = User.query.filter_by(id_number='1234567890123').first()
        
        if admin_by_email:
            print(f"\n✅ Found admin by email (ID: {admin_by_email.id})")
            admin = admin_by_email
            # Update password and ensure is_admin is True
            admin.password_hash = generate_password_hash(admin_password)
            admin.is_admin = True
            if not admin.first_name:
                admin.first_name = 'Admin'
            if not admin.last_name:
                admin.last_name = 'User'
            if not admin.phone_number:
                admin.phone_number = '0123456789'
            db.session.commit()
            print(f"✅ Admin updated! Password: {admin_password}")
            
        elif admin_by_id:
            print(f"\n⚠️ Found user with admin id_number but different email (ID: {admin_by_id.id})")
            print(f"   Current email: {admin_by_id.email}")
            # Update this user to be the admin
            admin_by_id.email = admin_email
            admin_by_id.password_hash = generate_password_hash(admin_password)
            admin_by_id.is_admin = True
            admin_by_id.first_name = 'Admin'
            admin_by_id.last_name = 'User'
            admin_by_id.phone_number = '0123456789'
            db.session.commit()
            print(f"✅ Converted to admin! Email: {admin_email}, Password: {admin_password}")
            
        else:
            print(f"\n⚠️ No admin found - creating new one...")
            # Find a unique id_number
            import random
            while True:
                new_id = f'ADMIN{random.randint(1000000000000, 9999999999999)}'
                if not User.query.filter_by(id_number=new_id).first():
                    break
            
            new_admin = User(
                email=admin_email,
                password_hash=generate_password_hash(admin_password),
                first_name='Admin',
                last_name='User',
                phone_number='0123456789',
                id_number=new_id,
                is_admin=True
            )
            db.session.add(new_admin)
            db.session.commit()
            print(f"✅ New admin created!")
            print(f"   Email: {admin_email}")
            print(f"   Password: {admin_password}")
            print(f"   ID Number: {new_id}")
        
        # Verify final state
        final_check = User.query.filter_by(email=admin_email).first()
        if final_check:
            print(f"\n🔑 FINAL ADMIN LOGIN DETAILS:")
            print(f"   URL: https://bakers-lovers.onrender.com/auth/login")
            print(f"   Email: {admin_email}")
            print(f"   Password: {admin_password}")
            print(f"   Is Admin: {final_check.is_admin}")
        
        # Seed products if none exist
        if Product.query.count() == 0:
            print("\n📦 Creating sample products...")
            products = [
                Product(name='Chocolate Birthday Cake', description='Rich chocolate cake', category='Birthday', size='8-inch', stock=10, price=450.00, available=True),
                Product(name='Wedding Vanilla Cake', description='Elegant vanilla cake', category='Wedding', size='3-tier', stock=5, price=2500.00, available=True),
                Product(name='Custom Red Velvet', description='Customizable red velvet', category='Custom', size='6-inch', stock=8, price=380.00, available=True)
            ]
            for p in products:
                db.session.add(p)
            db.session.commit()
            print("✅ Sample products created")
        
        # Seed coupon if none exist
        if Coupon.query.count() == 0:
            print("\n🎟️ Creating sample coupon...")
            coupon = Coupon(code='BAKERS10', discount_amount=10, is_percentage=True, valid_from=datetime.utcnow() - timedelta(days=1), valid_to=datetime.utcnow() + timedelta(days=30), active=True)
            db.session.add(coupon)
            db.session.commit()
            print("✅ Sample coupon created (BAKERS10 - 10% off)")
        
        print("\n" + "=" * 60)
        print("SETUP COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)