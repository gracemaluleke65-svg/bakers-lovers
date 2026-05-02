# init_db_remote.py - Run this locally to create tables on Render database
from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Creating all database tables on Render...")
    db.create_all()
    print("✅ Tables created successfully!")
    
    # Verify tables exist
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"\n📋 Tables created: {', '.join(tables)}")