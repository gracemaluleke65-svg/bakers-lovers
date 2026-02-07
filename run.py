# run.py - Complete database and admin fix
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
        # First, let's see what we have
        inspector = inspect(db.engine)
        columns_info = inspector.get_columns('user')
        columns = {col['name']: col for col in columns_info}
        print(f"\nDatabase columns: {list(columns.keys())}")
        
        # Check existing users
        all_users = User.query.all()
        print(f"\nTotal users in database: {len(all_users)}")
        
        for user in all_users:
            print(f"  - ID: {user.id}, Email: {user.email}, Admin: {user.is_admin}")
            print(f"    first_name: {getattr(user, 'first_name', 'N/A')}, last_name: {getattr(user, 'last_name', 'N/A')}")
        
        # Check specifically for admin
        admin_email = 'admin@bakerslovers.com'
        admin = User.query.filter_by(email=admin_email).first()
        
        if admin:
            print(f"\n✅ Admin user FOUND (ID: {admin.id})")
            print(f"   Email: {admin.email}")
            print(f"   is_admin: {admin.is_admin}")
            print(f"   first_name: {admin.first_name}")
            print(f"   last_name: {admin.last_name}")
            print(f"   phone_number: {admin.phone_number}")
            print(f"   id_number: {admin.id_number}")
            
            # Fix any missing fields
            needs_update = False
            
            if not admin.first_name:
                admin.first_name = 'Admin'
                needs_update = True
            if not admin.last_name:
                admin.last_name = 'User'
                needs_update = True
            if not admin.phone_number:
                admin.phone_number = '0123456789'
                needs_update = True
            if not admin.id_number:
                # Generate unique ID
                admin.id_number = f'ADMIN{admin.id:08d}'
                needs_update = True
            if not admin.is_admin:
                admin.is_admin = True
                needs_update = True
            
            # Reset password
            admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
            admin.password_hash = generate_password_hash(admin_password)
            needs_update = True
            
            if needs_update:
                db.session.commit()
                print(f"\n✅ Admin user UPDATED with new password: {admin_password}")
            else:
                print(f"\n✅ Admin user already complete, password reset to: {admin_password}")
                
        else:
            print(f"\n⚠️ Admin user NOT FOUND - creating new one...")
            
            # Generate unique id_number
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M')
            
            try:
                admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
                new_admin = User(
                    email=admin_email,
                    password_hash=generate_password_hash(admin_password),
                    first_name='Admin',
                    last_name='User',
                    phone_number='0123456789',
                    id_number=f'ADMIN{timestamp}',  # Unique ID
                    is_admin=True
                )
                db.session.add(new_admin)
                db.session.commit()
                print(f"✅ NEW ADMIN CREATED:")
                print(f"   Email: {admin_email}")
                print(f"   Password: {admin_password}")
                print(f"   ID Number: {timestamp}")
                
            except Exception as create_error:
                db.session.rollback()
                print(f"❌ Error creating admin: {create_error}")
                print("Trying alternative method...")
                
                # Try raw SQL insert
                with db.engine.connect() as conn:
                    from sqlalchemy import text
                    hashed = generate_password_hash(admin_password)
                    conn.execute(text(f'''
                        INSERT INTO "user" (email, password_hash, first_name, last_name, phone_number, id_number, is_admin, created_at)
                        VALUES ('{admin_email}', '{hashed}', 'Admin', 'User', '0123456789', 'ADMIN{timestamp}', true, NOW())
                        ON CONFLICT (email) DO UPDATE SET
                        password_hash = EXCLUDED.password_hash,
                        is_admin = true,
                        first_name = 'Admin',
                        last_name = 'User'
                    '''))
                    conn.commit()
                    print(f"✅ Admin created/updated via SQL")
        
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
        print(f"\n🔑 ADMIN LOGIN:")
        print(f"   URL: https://bakers-lovers.onrender.com/auth/login")
        print(f"   Email: admin@bakerslovers.com")
        print(f"   Password: {os.environ.get('ADMIN_PASSWORD', 'Admin@123')}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)