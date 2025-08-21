#!/usr/bin/env python3
"""
Add Security Headers to app.py
This script adds security headers with a comprehensive CSP policy.
"""

import re

def add_security_headers():
    """Add security headers to app.py."""
    print("Adding security headers to app.py...")
    
    # Read the current app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Define the security headers function
    security_headers_function = '''
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Add HSTS header for HTTPS
    if request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Add comprehensive CSP header
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://unpkg.com https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https://images.unsplash.com https://*.unsplash.com; "
        "connect-src 'self' https://cdn.tailwindcss.com https://fonts.googleapis.com https://fonts.gstatic.com https://unpkg.com https://cdn.jsdelivr.net; "
        "worker-src 'self' blob:; "
        "child-src 'self' blob:;"
    )
    response.headers['Content-Security-Policy'] = csp_policy
    
    return response

'''
    
    # Find a good place to insert (after imports and before routes)
    # Look for the first route definition
    route_pattern = r'^@app\.route'
    match = re.search(route_pattern, content, re.MULTILINE)
    
    if match:
        # Insert before the first route
        insert_pos = match.start()
        content = content[:insert_pos] + security_headers_function + content[insert_pos:]
        
        # Write back to app.py
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Security headers added successfully!")
    else:
        print("❌ Could not find route definitions")

def main():
    """Main function to add security headers."""
    print("Starting security headers addition...")
    
    try:
        add_security_headers()
        print("\n✅ Security headers addition completed!")
        print("\nNext steps:")
        print("1. Deploy to Railway: railway up")
        print("2. Test all external resources loading")
        print("3. Verify CSP allows necessary resources")
        
    except Exception as e:
        print(f"\n❌ Error during security headers addition: {e}")

if __name__ == "__main__":
    main()
