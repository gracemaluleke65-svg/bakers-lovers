# run.py - Fix database schema by removing old full_name column
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
        columns_info = inspector.get_columns('user')
        columns = {col['name']: col for col in columns_info}
        column_names = list(columns.keys())
        print(f"Existing columns: {column_names}")
        
        with db.engine.connect() as conn:
            
            # Step 1: Handle the problematic full_name column
            if 'full_name' in columns:
                print("\n⚠️ Found old 'full_name' column - migrating data...")
                
                # If we don't have first_name/last_name, create them first
                if 'first_name' not in columns:
                    conn.execute(text('ALTER TABLE "user" ADD COLUMN first_name VARCHAR(100)'))
                    print("✅ Added first_name")
                
                if 'last_name' not in columns:
                    conn.execute(text('ALTER TABLE "user" ADD COLUMN last_name VARCHAR(100)'))
                    print("✅ Added last_name")
                
                conn.commit()
                
                # Migrate data: split full_name or use email as fallback
                conn.execute(text('''
                    UPDATE "user" 
                    SET first_name = COALESCE(SPLIT_PART(full_name, ' ', 1), 'User'),
                        last_name = COALESCE(NULLIF(SPLIT_PART(full_name, ' ', 2), ''), 'Unknown')
                    WHERE first_name IS NULL OR first_name = ''
                '''))
                conn.commit()
                print("✅ Migrated full_name data to first_name/last_name")
                
                # Make first_name and last_name NOT NULL before dropping full_name
                conn.execute(text('UPDATE "user" SET first_name = \'User\' WHERE first_name IS NULL OR first_name = \'\''))
                conn.execute(text('UPDATE "user" SET last_name = \'Unknown\' WHERE last_name IS NULL OR last_name = \'\''))
                conn.commit()
                
                # Now drop the full_name column
                conn.execute(text('ALTER TABLE "user" DROP COLUMN full_name'))
                conn.commit()
                print("✅ Dropped old full_name column")
            
            # Step 2: Ensure all required columns exist with proper constraints
            required_columns = {
                'first_name': 'VARCHAR(100) NOT NULL DEFAULT \'User\'',
                'last_name': 'VARCHAR(100) NOT NULL DEFAULT \'Unknown\'',
                'phone_number': 'VARCHAR(10) NOT NULL DEFAULT \'0000000000\'',
                'id_number': 'VARCHAR(13)',
                'last_login': 'TIMESTAMP'
            }
            
            for col_name, col_type in required_columns.items():
                if col_name not in columns:
                    conn.execute(text(f'ALTER TABLE "user" ADD COLUMN {col_name} {col_type}'))
                    conn.commit()
                    print(f"✅ Added missing column: {col_name}")
            
            # Step 3: Handle id_number specially (needs unique constraint)
            if 'id_number' in columns or 'id_number' not in columns:
                # Ensure id_number has values for all rows
                conn.execute(text('UPDATE "user" SET id_number = LPAD(id::text, 13, \'0\') WHERE id_number IS NULL'))
                conn.commit()
                
                # Try to add NOT NULL constraint
                try:
                    conn.execute(text('ALTER TABLE "user" ALTER COLUMN id_number SET NOT NULL'))
                    conn.commit()
                    print("✅ Set id_number to NOT NULL")
                except:
                    print("⚠️ Could not set id_number to NOT NULL (may have duplicates)")
            
            # Step 4: Clean up old columns that are no longer needed
            old_columns = ['student_number', 'phone']  # Old column names
            for old_col in old_columns:
                if old_col in columns:
                    try:
                        conn.execute(text(f'ALTER TABLE "user" DROP COLUMN {old_col}'))
                        conn.commit()
                        print(f"✅ Dropped old column: {old_col}")
                    except Exception as e:
                        print(f"⚠️ Could not drop {old_col}: {e}")
        
        print("\n✅ Schema fix complete!")
        
        # Step 5: Verify and create admin user
        db.session.expire_all()
        
        # Check if admin exists
        admin = User.query.filter_by(email='admin@bakerslovers.com').first()
        if not admin:
            print("\nCreating admin user...")
            try:
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
            except Exception as e:
                print(f"❌ Error creating admin: {e}")
                db.session.rollback()
        else:
            print(f"\n✅ Admin exists: {admin.email}")
        
        # Step 6: Seed products
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
        
        # Step 7: Seed coupon
        if Coupon.query.count() == 0:
            coupon = Coupon(code='BAKERS10', discount_amount=10, is_percentage=True, valid_from=datetime.utcnow() - timedelta(days=1), valid_to=datetime.utcnow() + timedelta(days=30), active=True)
            db.session.add(coupon)
            db.session.commit()
            print("✅ Sample coupon created")
        
        print("=" * 60)
        print("DATABASE READY")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during schema fix: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)