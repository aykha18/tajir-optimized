#!/usr/bin/env python3
"""
Remove CSRF Tokens from Templates
This script removes CSRF tokens from templates since CSRF protection isn't properly configured.
"""

import re
import os

def remove_csrf_tokens():
    """Remove CSRF tokens from templates."""
    print("Removing CSRF tokens from templates...")
    
    templates = [
        'templates/login.html',
        'templates/admin_login.html'
    ]
    
    for template_file in templates:
        if os.path.exists(template_file):
            print(f"Processing {template_file}...")
            
            with open(template_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Remove CSRF token lines
            content = re.sub(
                r'\s*<input type="hidden" name="csrf_token" value="{{ csrf_token\(\) }}">\s*\n?',
                '',
                content
            )
            
            with open(template_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"✅ CSRF tokens removed from {template_file}")
        else:
            print(f"⚠️ Template {template_file} not found")

def main():
    """Main function to remove CSRF tokens."""
    print("Starting CSRF token removal...")
    
    try:
        remove_csrf_tokens()
        print("\n✅ CSRF token removal completed!")
        print("\nNext steps:")
        print("1. Deploy to Railway: railway up")
        print("2. Test login functionality")
        
    except Exception as e:
        print(f"\n❌ Error during CSRF token removal: {e}")

if __name__ == "__main__":
    main()
