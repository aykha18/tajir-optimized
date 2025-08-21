#!/usr/bin/env python3
"""
Fix CSP Policy for Chart.js and Other Resources
This script updates the Content Security Policy to allow necessary external resources.
"""

import re

def fix_csp_policy():
    """Update the CSP policy in app.py to allow Chart.js and other resources."""
    print("Fixing CSP policy for Chart.js and other resources...")
    
    # Read the current app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find the current CSP policy
    csp_pattern = r'csp_policy\s*=\s*\(\s*"([^"]+)"'
    match = re.search(csp_pattern, content, re.DOTALL)
    
    if match:
        # Update the CSP policy to allow necessary resources
        new_csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https://images.unsplash.com; "
            "connect-src 'self';"
        )
        
        # Replace the CSP policy
        content = re.sub(
            r'csp_policy\s*=\s*\(\s*"[^"]+"',
            f'csp_policy = ("{new_csp_policy}"',
            content,
            flags=re.DOTALL
        )
        
        # Write back to app.py
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ CSP policy updated successfully!")
        print("   - Added cdn.jsdelivr.net for Chart.js")
        print("   - Added images.unsplash.com for images")
        print("   - Maintained security for other resources")
    else:
        print("❌ Could not find CSP policy in app.py")

def main():
    """Main function to fix CSP issues."""
    print("Starting CSP policy fix...")
    
    try:
        fix_csp_policy()
        print("\n✅ CSP policy fix completed!")
        print("\nNext steps:")
        print("1. Deploy to Railway: railway up")
        print("2. Test Chart.js functionality")
        print("3. Verify dashboard charts are working")
        
    except Exception as e:
        print(f"\n❌ Error during CSP fix: {e}")

if __name__ == "__main__":
    main()
