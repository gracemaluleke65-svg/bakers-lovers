# run.py - Fix mixed database schema
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

# Fix database schema
with app.app_context():
    print("=" * 60)
    print("FIXING DATABASE SCHEMA")
    print("=" * 60)
    
    try:
        inspector = inspect(db.engine)
        columns = {col['name']: col for col in inspector.get_columns('user')}
        print(f"Existing columns: {list(columns.keys())}")
        
        # Check if we have the old schema (full_name) mixed with new
        has_full_name = 'full_name' in columns
        has_first_name = 'first_name' in columns
        
        with db.engine.connect() as conn:
            
            # Case 1: Has full_name but missing first_name/last_name
            if has_full_name and not has_first_name:
                print("Detected old schema with full_name, migrating...")
                
                # Add first_name and last_name columns (nullable first)
                conn.execute(text('ALTER TABLE "user" ADD COLUMN first_name VARCHAR(100)'))
                conn.execute(text('ALTER TABLE "user" ADD COLUMN last_name VARCHAR(100)'))
                conn.commit()
                print("✅ Added first_name and last_name columns")
                
                # Migrate data from full_name to first_name/last_name
                conn.execute(text('UPDATE "user" SET first_name = full_name, last_name = \'\''))
                conn.commit()
                print("✅ Migrated full_name data to first_name")
                
                # Now make them NOT NULL
                conn.execute(text('ALTER TABLE "user" ALTER COLUMN first_name SET NOT NULL'))
                conn.execute(text('ALTER TABLE "user" ALTER COLUMN last_name SET NOT NULL'))
                conn.commit()
                print("✅ Set first_name and last_name to NOT NULL")
                
                # Drop the old full_name column
                conn.execute(text('ALTER TABLE "user" DROP COLUMN full_name'))
                conn.commit()
                print("✅ Dropped old full_name column")
                
            # Case 2: Has first_name but it's nullable (needs NOT NULL)
            elif has_first_name and not columns['first_name'].get('nullable', True):
                print("first_name exists but may have issues...")
            
            # Ensure phone_number and id_number exist
            if 'phone_number' not in columns:
                conn.execute(text('ALTER TABLE "user" ADD COLUMN phone_number VARCHAR(10) DEFAULT \'0000000000\' NOT NULL'))
                conn.commit()
                print("✅ Added phone_number column")
            elif columns['phone_number'].get('nullable', True):
                # Update nulls and make NOT NULL
                conn.execute(text('UPDATE "user" SET phone_number = \'0000000000\' WHERE phone_number IS NULL'))
                conn.execute(text('ALTER TABLE "user" ALTER COLUMN phone_number SET NOT NULL'))
                conn.commit()
                print("✅ Fixed phone_number column")
            
            if 'id_number' not in columns:
                # Generate unique default ID numbers for existing users
                conn.execute(text('ALTER TABLE "user" ADD COLUMN id_number VARCHAR(13)'))
                conn.commit()
                # Update with unique IDs based on user id
                conn.execute(text('UPDATE "user" SET id_number = LPAD(id::text, 13, \'0\')'))
                conn.execute(text('ALTER TABLE "user" ALTER COLUMN id_number SET NOT NULL'))
                conn.execute(text('ALTER TABLE "user" ADD CONSTRAINT unique_id_number UNIQUE (id_number)'))
                conn.commit()
                print("✅ Added id_number column with unique values")
            elif columns['id_number'].get('nullable', True):
                conn.execute(text('UPDATE "user" SET id_number = LPAD(id::text, 13, \'0\') WHERE id_number IS NULL'))
                conn.execute(text('ALTER TABLE "user" ALTER COLUMN id_number SET NOT NULL'))
                conn.commit()
                print("✅ Fixed id_number column")
            
            if 'last_login' not in columns:
                conn.execute(text('ALTER TABLE "user" ADD COLUMN last_login TIMESTAMP'))
                conn.commit()
                print("✅ Added last_login column")
        
        print("\n✅ Schema fix complete!")
        
        # Now verify and seed data
        db.session.expire_all()  # Clear any cached metadata
        
        # Check admin user
        admin = User.query.filter_by(email='admin@bakerslovers.com').first()
        if not admin:
            print("\nCreating admin user...")
            admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
            new_admin = User(
                email='admin@bakerslovers.com',
                password_hash=generate_password_hash(admin_password),
                first_name='Admin',
                last_name='User',
                phone_number='0123456789',
                id_number='1234567890123',
                is_admin=True
            )
            db.session.add(new_admin)
            db.session.commit()
            print(f"✅ Admin created: admin@bakerslovers.com / {admin_password}")
        else:
            print(f"\n✅ Admin exists: {admin.email}")
            # Ensure admin has all required fields
            if not admin.first_name:
                admin.first_name = 'Admin'
            if not admin.last_name:
                admin.last_name = 'User'
            if not admin.phone_number:
                admin.phone_number = '0123456789'
            if not admin.id_number:
                admin.id_number = '1234567890123'
            db.session.commit()
        
        # Seed products
        if Product.query.count() == 0:
            products = [
                Product(name='Chocolate Birthday Cake', description='Rich chocolate cake', category='Birthday', size='8-inch', stock=10, price=450.00, available=True),
                Product(name='Wedding Vanilla Cake', description='Elegant vanilla cake', category='Wedding', size='3-tier', stock=5, price=2500.00, available=True),
                Product(name='Custom Red Velvet', description='Customizable red velvet', category='Custom', size='6-inch', stock=8, price=380.00, available=True)
            ]
            for p in products:
                db.session.add(p)
            db.session.commit()
            print("✅ Sample products created")
        
        # Seed coupon
        if Coupon.query.count() == 0:
            coupon = Coupon(code='BAKERS10', discount_amount=10, is_percentage=True, valid_from=datetime.utcnow() - timedelta(days=1), valid_to=datetime.utcnow() + timedelta(days=30), active=True)
            db.session.add(coupon)
            db.session.commit()
            print("✅ Sample coupon created")
        
        print("=" * 60)
        print("DATABASE READY")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)