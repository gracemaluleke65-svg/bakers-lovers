# debug_templates.py
import os
from app import create_app

def debug_templates():
    app = create_app()
    
    print("=== TEMPLATE DEBUG INFO ===")
    print(f"App root path: {app.root_path}")
    print(f"Template folder: {app.template_folder}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check where Flask thinks templates should be
    if app.template_folder:
        template_base = os.path.join(app.root_path, app.template_folder)
    else:
        template_base = os.path.join(app.root_path, 'templates')
    
    print(f"Template base directory: {template_base}")
    print(f"Template base exists: {os.path.exists(template_base)}")
    
    # Check main/index.html specifically
    main_index = os.path.join(template_base, 'main', 'index.html')
    print(f"Expected template path: {main_index}")
    print(f"Template exists: {os.path.exists(main_index)}")
    
    # Check alternative locations
    alternatives = [
        os.path.join(os.getcwd(), 'templates', 'main', 'index.html'),
        os.path.join(app.root_path, 'templates', 'main', 'index.html'),
        os.path.join(os.path.dirname(__file__), 'templates', 'main', 'index.html'),
    ]
    
    print("\n=== CHECKING ALTERNATIVE LOCATIONS ===")
    for alt_path in alternatives:
        exists = os.path.exists(alt_path)
        print(f"{alt_path}: {'✅' if exists else '❌'}")
        if exists:
            print(f"  -> File size: {os.path.getsize(alt_path)} bytes")

if __name__ == '__main__':
    debug_templates()