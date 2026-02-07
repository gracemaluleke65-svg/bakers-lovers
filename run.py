# run.py - Add missing columns to existing table
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

# Fix database schema - add missing columns
with app.app_context():
    print("=" * 60)
    print("CHECKING DATABASE SCHEMA")
    print("=" * 60)
    
    try:
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('user')]
        print(f"Existing columns in 'user' table: {columns}")
        
        # Define missing columns with their types and defaults
        missing_columns = {
            'first_name': 'VARCHAR(100)',
            'last_name': 'VARCHAR(100)',
            'phone_number': 'VARCHAR(10)',
            'id_number': 'VARCHAR(13)',
            'last_login': 'TIMESTAMP'
        }
        
        columns_added = []
        
        for col_name, col_type in missing_columns.items():
            if col_name not in columns:
                try:
                    # Add column with default value to avoid NOT NULL issues
                    if col_name == 'last_login':
                        # Nullable column
                        alter_sql = f'ALTER TABLE "user" ADD COLUMN {col_name} {col_type}'
                    else:
                        # Add with default empty string, then make NOT NULL
                        alter_sql = f'ALTER TABLE "user" ADD COLUMN {col_name} {col_type} DEFAULT \'\''
                    
                    with db.engine.connect() as conn:
                        conn.execute(text(alter_sql))
                        conn.commit()
                    
                    columns_added.append(col_name)
                    print(f"✅ Added column: {col_name}")
                    
                except Exception as e:
                    print(f"⚠️ Error adding {col_name}: {e}")
        
        if columns_added:
            print(f"\n✅ Successfully added {len(columns_added)} columns")
            
            # Update existing users with default values if needed
            if 'first_name' in columns_added:
                with db.engine.connect() as conn:
                    conn.execute(text('UPDATE "user" SET first_name = \'Admin\' WHERE first_name = \'\''))
                    conn.execute(text('UPDATE "user" SET last_name = \'User\' WHERE last_name = \'\''))
                    conn.execute(text('UPDATE "user" SET phone_number = \'0123456789\' WHERE phone_number = \'\''))
                    conn.execute(text('UPDATE "user" SET id_number = \'1234567890123\' WHERE id_number = \'\''))
                    conn.commit()
                print("✅ Updated existing users with default values")
        else:
            print("✅ All required columns already exist")
        
        # Check if admin exists and has required fields
        admin = User.query.filter_by(email='admin@bakerslovers.com').first()
        if admin:
            print(f"\n✅ Admin user found: {admin.email}")
            print(f"   is_admin: {admin.is_admin}")
            print(f"   first_name: {admin.first_name}")
            print(f"   last_name: {admin.last_name}")
        else:
            print("\n⚠️ Admin user not found, creating...")
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
            print(f"✅ Created admin: admin@bakerslovers.com / {admin_password}")
        
        # Seed products if none exist
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
        
        # Seed coupon if none exist
        if Coupon.query.count() == 0:
            coupon = Coupon(code='BAKERS10', discount_amount=10, is_percentage=True, valid_from=datetime.utcnow() - timedelta(days=1), valid_to=datetime.utcnow() + timedelta(days=30), active=True)
            db.session.add(coupon)
            db.session.commit()
            print("✅ Sample coupon created")
        
        print("=" * 60)
        print("DATABASE SCHEMA FIX COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during schema fix: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)