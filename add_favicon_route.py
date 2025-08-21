#!/usr/bin/env python3
"""
Add Favicon Route to app.py
This script adds a favicon route to serve the icon-144.png file.
"""

import re

def add_favicon_route():
    """Add a favicon route to app.py."""
    print("Adding favicon route...")
    
    # Read the current app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Define the favicon route
    favicon_route = '''
@app.route('/favicon.ico')
def favicon():
    """Serve favicon."""
    return send_from_directory('static/icons', 'icon-144.png', mimetype='image/png')

'''
    
    # Find a good place to insert (after other static file routes)
    # Look for the QR code route
    qr_pattern = r'@app\.route\(\'/URL QR Code\.png\'\)'
    match = re.search(qr_pattern, content, re.MULTILINE)
    
    if match:
        # Find the end of the QR code function
        lines = content.split('\n')
        start_line = content[:match.start()].count('\n')
        
        # Find the end of the function (look for the next route or function)
        for i in range(start_line + 1, len(lines)):
            if lines[i].strip().startswith('@app.route') or (lines[i].strip().startswith('def ') and not lines[i].strip().startswith('def favicon')):
                break
        
        # Insert after the QR code function
        insert_pos = content.find('\n', content.find('\n', content.find('\n', match.end()))) + 1
        content = content[:insert_pos] + favicon_route + content[insert_pos:]
        
        # Write back to app.py
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Favicon route added successfully!")
    else:
        print("❌ Could not find QR code route to insert favicon route after")

def main():
    """Main function to add favicon route."""
    print("Starting favicon route addition...")
    
    try:
        add_favicon_route()
        print("\n✅ Favicon route addition completed!")
        print("\nNext steps:")
        print("1. Deploy to Railway: railway up")
        print("2. Test favicon loading")
        
    except Exception as e:
        print(f"\n❌ Error during favicon route addition: {e}")

if __name__ == "__main__":
    main()
