#!/usr/bin/env python3
"""
Fix Content Security Policy for Tajir POS
Updates CSP to allow Lucide icons library
"""

import re

def fix_content_security_policy():
    """Fix the Content Security Policy to allow Lucide icons."""
    
    # Read the current app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the CSP policy
    old_csp = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self';"
    
    new_csp = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self';"
    
    # Replace the CSP policy
    if old_csp in content:
        content = content.replace(old_csp, new_csp)
        print("✅ Updated Content Security Policy")
    else:
        print("⚠️ Could not find exact CSP policy to replace")
        return False
    
    # Write the updated content back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("SUCCESS: Fixed Content Security Policy")
    return True

def main():
    """Main function."""
    print("Fixing Content Security Policy for Tajir POS")
    print("=" * 50)
    
    success = fix_content_security_policy()
    
    if success:
        print("\n" + "=" * 50)
        print("SUCCESS: CSP Fixed!")
        print("\nNEXT STEPS:")
        print("1. Deploy to Railway: railway up")
        print("2. Test login functionality")
        print("3. Clear browser cache and try again")
        
        print("\nCHANGES MADE:")
        print("- Added https://unpkg.com to script-src directive")
        print("- This allows Lucide icons library to load")
        print("- Should fix the login functionality")
    else:
        print("\n❌ Failed to fix CSP")

if __name__ == "__main__":
    main()
