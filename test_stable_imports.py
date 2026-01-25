# test_stable_imports.py
print("Testing stable SQLAlchemy installation...")

try:
    import sqlalchemy
    print(f"✓ SQLAlchemy version: {sqlalchemy.__version__}")
    
    from flask_sqlalchemy import SQLAlchemy
    print("✓ Flask-SQLAlchemy imported")
    
    from flask_migrate import Migrate
    print("✓ Flask-Migrate imported")
    
    print("\n🎉 All imports successful! Ready for migrations.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()