# run.py - Complete database cleanup
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

def get_table_columns(table_name):
    """Get current columns in a table"""
    try:
        inspector = inspect(db.engine)
        return {col['name']: col for col in inspector.get_columns(table_name)}
    except:
        return {}

# Database cleanup and fix
with app.app_context():
    print("=" * 60)
    print("DATABASE CLEANUP & FIX")
    print("=" * 60)
    
    try:
        # ========== FIX FAVORITE TABLE ==========
        print("\n🔧 Fixing 'favorite' table...")
        fav_cols = get_table_columns('favorite')
        print(f"   Current columns: {list(fav_cols.keys())}")
        
        with db.engine.connect() as conn:
            # Drop old columns that shouldn't exist
            old_columns = ['accommodation_id', 'accommodation_admin_id']  # Old schema columns
            for old_col in old_columns:
                if old_col in fav_cols:
                    try:
                        conn.execute(text(f'ALTER TABLE favorite DROP COLUMN {old_col}'))
                        conn.commit()
                        print(f"   ✅ Dropped old column: {old_col}")
                    except Exception as e:
                        print(f"   ⚠️ Could not drop {old_col}: {e}")
            
            # Ensure correct columns exist
            if 'id' not in fav_cols:
                conn.execute(text('ALTER TABLE favorite ADD COLUMN id SERIAL PRIMARY KEY'))
                conn.commit()
                print("   ✅ Added id column")
            
            if 'user_id' not in fav_cols:
                conn.execute(text('ALTER TABLE favorite ADD COLUMN user_id INTEGER REFERENCES "user"(id)'))
                conn.commit()
                print("   ✅ Added user_id column")
            
            if 'product_id' not in fav_cols:
                conn.execute(text('ALTER TABLE favorite ADD COLUMN product_id INTEGER REFERENCES product(id)'))
                conn.commit()
                print("   ✅ Added product_id column")
            
            if 'added_at' not in fav_cols:
                conn.execute(text('ALTER TABLE favorite ADD COLUMN added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP'))
                conn.commit()
                print("   ✅ Added added_at column")
        
        # ========== FIX USER TABLE ==========
        print("\n🔧 Fixing 'user' table...")
        user_cols = get_table_columns('user')
        
        with db.engine.connect() as conn:
            # Drop old columns
            old_user_cols = ['full_name', 'student_number', 'phone']
            for old_col in old_user_cols:
                if old_col in user_cols:
                    try:
                        conn.execute(text(f'ALTER TABLE "user" DROP COLUMN {old_col}'))
                        conn.commit()
                        print(f"   ✅ Dropped old column: {old_col}")
                    except:
                        pass
            
            # Ensure required columns
            required = {
                'first_name': 'VARCHAR(100) DEFAULT \'User\' NOT NULL',
                'last_name': 'VARCHAR(100) DEFAULT \'Unknown\' NOT NULL',
                'phone_number': 'VARCHAR(10) DEFAULT \'0000000000\' NOT NULL',
                'id_number': 'VARCHAR(13) UNIQUE NOT NULL',
                'last_login': 'TIMESTAMP'
            }
            
            for col, col_type in required.items():
                if col not in user_cols:
                    conn.execute(text(f'ALTER TABLE "user" ADD COLUMN {col} {col_type}'))
                    conn.commit()
                    print(f"   ✅ Added {col}")
        
        # ========== ADMIN USER SETUP ==========
        print("\n👤 Setting up admin user...")
        admin_email = 'admin@bakerslovers.com'
        admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
        
        # Check all users
        all_users = User.query.all()
        print(f"   Total users: {len(all_users)}")
        for u in all_users:
            print(f"   - ID:{u.id} {u.email}")
        
        # Find or create admin
        admin = User.query.filter_by(email=admin_email).first()
        
        if not admin:
            # Check if any user has the admin id_number
            admin = User.query.filter_by(id_number='1234567890123').first()
            if admin:
                print(f"   Found user with admin ID, updating to {admin_email}")
                admin.email = admin_email
            else:
                print("   Creating new admin...")
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
        
        # Update admin
        admin.password_hash = generate_password_hash(admin_password)
        admin.is_admin = True
        db.session.commit()
        
        print(f"   ✅ Admin ready: {admin_email} / {admin_password}")
        
        # ========== SEED DATA ==========
        if Product.query.count() == 0:
            print("\n📦 Creating products...")
            products = [
                Product(name='Chocolate Birthday Cake', description='Rich chocolate cake', category='Birthday', size='8-inch', stock=10, price=450.00, available=True),
                Product(name='Wedding Vanilla Cake', description='Elegant vanilla cake', category='Wedding', size='3-tier', stock=5, price=2500.00, available=True),
                Product(name='Custom Red Velvet', description='Customizable red velvet', category='Custom', size='6-inch', stock=8, price=380.00, available=True)
            ]
            for p in products:
                db.session.add(p)
            db.session.commit()
            print("   ✅ Products created")
        
        if Coupon.query.count() == 0:
            print("\n🎟️ Creating coupon...")
            coupon = Coupon(code='BAKERS10', discount_amount=10, is_percentage=True, valid_from=datetime.utcnow() - timedelta(days=1), valid_to=datetime.utcnow() + timedelta(days=30), active=True)
            db.session.add(coupon)
            db.session.commit()
            print("   ✅ Coupon created")
        
        print("\n" + "=" * 60)
        print("✅ DATABASE READY")
        print("=" * 60)
        print(f"\n🔑 Login: {admin_email} / {admin_password}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)