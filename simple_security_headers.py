#!/usr/bin/env python3
"""
Simple Security Headers Integration
Adds basic security headers to app.py
"""

import re

def add_security_headers():
    """Add security headers to app.py."""
    
    # Read the current app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add security headers function
    security_headers_function = '''

@app.after_request
def add_security_headers(response):
    """Add security headers to response."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self';"
    
    # Add HSTS header for HTTPS
    if request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response'''
    
    # Add the function after the app configuration
    if 'add_security_headers' not in content:
        # Find a good place to insert (after app configuration)
        insert_pattern = r'(app\.secret_key = os\.getenv\(.*?\)\n\n)'
        replacement = r'\1' + security_headers_function + '\n'
        content = re.sub(insert_pattern, replacement, content, flags=re.DOTALL)
    
    # Write the updated content back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("SUCCESS: Added security headers to app.py")

def main():
    """Main function."""
    print("Adding Security Headers to Tajir POS")
    print("=" * 40)
    
    add_security_headers()
    
    print("\n" + "=" * 40)
    print("SUCCESS: Security headers added!")
    print("\nNEXT STEPS:")
    print("1. Deploy to Railway: railway up")
    print("2. Test security headers: python test_security.py")
    
    print("\nSECURITY HEADERS ADDED:")
    print("- X-Content-Type-Options: nosniff")
    print("- X-Frame-Options: DENY")
    print("- X-XSS-Protection: 1; mode=block")
    print("- Referrer-Policy: strict-origin-when-cross-origin")
    print("- Content-Security-Policy: Comprehensive CSP")
    print("- Strict-Transport-Security: HSTS for HTTPS")

if __name__ == "__main__":
    main()
