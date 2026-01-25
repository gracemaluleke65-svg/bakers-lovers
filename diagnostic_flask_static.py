# diagnostic_flask_static.py
import os
import sys

def analyze_flask_structure():
    """Analyze the current Flask project structure"""
    print("=" * 50)
    print("FLASK PROJECT STRUCTURE ANALYSIS")
    print("=" * 50)
    
    # Check current directory
    current_dir = os.getcwd()
    print(f"\nCurrent working directory: {current_dir}")
    
    # List all files and directories
    print("\nDirectory structure:")
    for root, dirs, files in os.walk(current_dir):
        level = root.replace(current_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f'{subindent}{file}')
    
    # Check for common Flask static file patterns
    print("\n" + "=" * 50)
    print("STATIC FILES CHECK")
    print("=" * 50)
    
    static_extensions = {
        '.css': 'CSS files',
        '.js': 'JavaScript files',
        '.png': 'PNG images',
        '.jpg': 'JPG images',
        '.jpeg': 'JPEG images',
        '.gif': 'GIF images',
        '.ico': 'Favicon',
        '.svg': 'SVG images',
        '.woff': 'Web fonts',
        '.woff2': 'Web fonts',
        '.ttf': 'Web fonts',
        '.eot': 'Web fonts'
    }
    
    found_files = {ext: [] for ext in static_extensions}
    
    for root, dirs, files in os.walk(current_dir):
        for file in files:
            _, ext = os.path.splitext(file)
            ext = ext.lower()
            if ext in found_files:
                found_files[ext].append(os.path.join(root, file))
    
    # Display found files
    for ext, description in static_extensions.items():
        if found_files[ext]:
            print(f"\n{description} ({ext}): {len(found_files[ext])} found")
            for i, filepath in enumerate(found_files[ext][:5], 1):
                rel_path = os.path.relpath(filepath, current_dir)
                print(f"  {i}. {rel_path}")
            if len(found_files[ext]) > 5:
                print(f"  ... and {len(found_files[ext]) - 5} more")
        else:
            print(f"\n{description} ({ext}): NOT FOUND")
    
    # Check for app.py, main.py, or similar Flask files
    print("\n" + "=" * 50)
    print("FLASK APP FILES CHECK")
    print("=" * 50)
    
    flask_files = [
        'app.py', 'main.py', 'application.py', 
        'wsgi.py', 'run.py', '__init__.py'
    ]
    
    flask_found = []
    for file in flask_files:
        if os.path.exists(os.path.join(current_dir, file)):
            flask_found.append(file)
    
    if flask_found:
        print(f"Flask files found: {', '.join(flask_found)}")
    else:
        print("No common Flask app files found in root directory")
        # Look for any Python file that might be the Flask app
        py_files = [f for f in os.listdir(current_dir) if f.endswith('.py')]
        if py_files:
            print(f"Python files found: {', '.join(py_files[:10])}")
    
    # Check for templates and static directories
    print("\n" + "=" * 50)
    print("STANDARD FLASK DIRECTORIES")
    print("=" * 50)
    
    standard_dirs = ['static', 'templates', 'static/css', 'static/js', 'static/images']
    
    for directory in standard_dirs:
        dir_path = os.path.join(current_dir, directory)
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            count = len([f for f in os.listdir(dir_path) if not f.startswith('.')])
            print(f"✓ {directory}/ - {count} items")
        else:
            print(f"✗ {directory}/ - Not found")
    
    # Provide recommendations
    print("\n" + "=" * 50)
    print("RECOMMENDATIONS")
    print("=" * 50)
    
    if not os.path.exists(os.path.join(current_dir, 'static')):
        print("1. Create a 'static' directory in your project root")
        print("2. Inside 'static', create subdirectories: css/, js/, images/")
    
    print("\nOnce you've confirmed your structure, please share:")
    print("1. Your Flask app code (e.g., app.py)")
    print("2. Your directory structure (shown above)")
    print("3. How you're referencing static files in your templates")

if __name__ == "__main__":
    analyze_flask_structure()