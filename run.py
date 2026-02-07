# run.py - Complete database schema fix for all tables
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

def check_and_fix_table(table_name, required_columns):
    """Check table and add missing columns"""
    try:
        inspector = inspect(db.engine)
        existing_cols = {col['name'] for col in inspector.get_columns(table_name)}
        
        missing = set(required_columns.keys()) - existing_cols
        if missing:
            print(f"\n  Fixing {table_name}: missing {missing}")
            with db.engine.connect() as conn:
                for col in missing:
                    col_type = required_columns[col]
                    try:
                        conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {col} {col_type}'))
                        conn.commit()
                        print(f"    ✅ Added {col}")
                    except Exception as e:
                        print(f"    ⚠️ Could not add {col}: {e}")
            return True
        return False
    except Exception as e:
        print(f"  ❌ Error checking {table_name}: {e}")
        return False

# Database schema fix
with app.app_context():
    print("=" * 60)
    print("COMPREHENSIVE DATABASE SCHEMA FIX")
    print("=" * 60)
    
    try:
        # Fix all tables
        print("\n🔧 Checking and fixing all tables...")
        
        # User table
        check_and_fix_table('user', {
            'first_name': 'VARCHAR(100) DEFAULT \'User\'',
            'last_name': 'VARCHAR(100) DEFAULT \'Unknown\'',
            'phone_number': 'VARCHAR(10) DEFAULT \'0000000000\'',
            'id_number': 'VARCHAR(13)',
            'last_login': 'TIMESTAMP',
            'is_admin': 'BOOLEAN DEFAULT FALSE'
        })
        
        # Favorite table - THIS IS THE ONE CAUSING THE ERROR
        check_and_fix_table('favorite', {
            'id': 'SERIAL PRIMARY KEY',
            'user_id': 'INTEGER REFERENCES "user"(id)',
            'product_id': 'INTEGER REFERENCES product(id)',
            'added_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        })
        
        # Order table
        check_and_fix_table('order', {
            'user_id': 'INTEGER REFERENCES "user"(id)',
            'order_date': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'total_amount': 'FLOAT NOT NULL',
            'status': 'VARCHAR(50) DEFAULT \'Pending\'',
            'payment_status': 'VARCHAR(50) DEFAULT \'Pending\'',
            'stripe_session_id': 'VARCHAR(200)',
            'delivery_address': 'TEXT NOT NULL',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        })
        
        # OrderItem table
        check_and_fix_table('order_item', {
            'order_id': 'INTEGER REFERENCES "order"(id)',
            'product_id': 'INTEGER REFERENCES product(id)',
            'quantity': 'INTEGER NOT NULL',
            'unit_price': 'FLOAT NOT NULL'
        })
        
        # CartItem table
        check_and_fix_table('cart_item', {
            'session_id': 'VARCHAR(255) NOT NULL',
            'product_id': 'INTEGER REFERENCES product(id)',
            'product_name': 'VARCHAR(150) NOT NULL',
            'unit_price': 'FLOAT NOT NULL',
            'quantity': 'INTEGER DEFAULT 1',
            'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        })
        
        # Feedback table
        check_and_fix_table('feedback', {
            'user_id': 'INTEGER REFERENCES "user"(id)',
            'order_id': 'INTEGER REFERENCES "order"(id)',
            'rating': 'INTEGER NOT NULL',
            'comment': 'TEXT DEFAULT \'\'',
            'submitted_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        })
        
        # Payment table
        check_and_fix_table('payment', {
            'order_id': 'INTEGER REFERENCES "order"(id)',
            'stripe_payment_intent_id': 'VARCHAR(100) NOT NULL',
            'amount': 'FLOAT NOT NULL',
            'paid_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            'status': 'VARCHAR(50) DEFAULT \'Succeeded\''
        })
        
        # Product table (less likely to have issues but check anyway)
        check_and_fix_table('product', {
            'name': 'VARCHAR(150) NOT NULL',
            'description': 'TEXT DEFAULT \'\'',
            'category': 'VARCHAR(100) DEFAULT \'Birthday\'',
            'size': 'VARCHAR(50) DEFAULT \'6-inch\'',
            'stock': 'INTEGER DEFAULT 0',
            'price': 'FLOAT NOT NULL',
            'image_bytes': 'BYTEA',
            'available': 'BOOLEAN DEFAULT TRUE'
        })
        
        # Coupon table
        check_and_fix_table('coupon', {
            'code': 'VARCHAR(20) UNIQUE NOT NULL',
            'discount_amount': 'FLOAT NOT NULL',
            'is_percentage': 'BOOLEAN DEFAULT FALSE',
            'valid_from': 'TIMESTAMP NOT NULL',
            'valid_to': 'TIMESTAMP NOT NULL',
            'active': 'BOOLEAN DEFAULT TRUE'
        })
        
        print("\n✅ Schema fix complete!")
        
        # Now handle admin user
        print("\n👤 Checking admin user...")
        admin_email = 'admin@bakerslovers.com'
        admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
        
        # List all users
        all_users = User.query.all()
        print(f"   Total users: {len(all_users)}")
        for u in all_users:
            print(f"   - ID:{u.id} {u.email} (Admin:{u.is_admin})")
        
        # Find or create admin
        admin = User.query.filter_by(email=admin_email).first()
        
        if not admin:
            # Check if any user has admin id_number
            admin = User.query.filter_by(id_number='1234567890123').first()
            if admin:
                print(f"   Found user with admin ID, updating email...")
                admin.email = admin_email
            else:
                print(f"   Creating new admin...")
                # Generate unique id_number
                import random
                while True:
                    new_id = f'ADMIN{random.randint(1000000000000, 9999999999999)}'
                    if not User.query.filter_by(id_number=new_id).first():
                        break
                
                admin = User(
                    email=admin_email,
                    password_hash=generate_password_hash(admin_password),
                    first_name='Admin',
                    last_name='User',
                    phone_number='0123456789',
                    id_number=new_id,
                    is_admin=True
                )
                db.session.add(admin)
        
        # Update admin credentials
        admin.password_hash = generate_password_hash(admin_password)
        admin.is_admin = True
        if not admin.first_name:
            admin.first_name = 'Admin'
        if not admin.last_name:
            admin.last_name = 'User'
        if not admin.phone_number:
            admin.phone_number = '0123456789'
        
        db.session.commit()
        
        print(f"\n✅ Admin ready:")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        
        # Seed products if none
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
            print("   ✅ Sample products created")
        
        # Seed coupon if none
        if Coupon.query.count() == 0:
            print("\n🎟️ Creating sample coupon...")
            coupon = Coupon(code='BAKERS10', discount_amount=10, is_percentage=True, valid_from=datetime.utcnow() - timedelta(days=1), valid_to=datetime.utcnow() + timedelta(days=30), active=True)
            db.session.add(coupon)
            db.session.commit()
            print("   ✅ Sample coupon created")
        
        print("\n" + "=" * 60)
        print("DATABASE READY")
        print("=" * 60)
        print(f"\n🔑 ADMIN LOGIN:")
        print(f"   https://bakers-lovers.onrender.com/auth/login")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)