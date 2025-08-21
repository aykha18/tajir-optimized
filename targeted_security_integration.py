#!/usr/bin/env python3
"""
Targeted Security Integration Script for Tajir POS
This script adds the most critical security features step by step.
"""

import re
import os
import shutil
from datetime import datetime

def backup_app():
    """Create a backup of the current app.py"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"app_backup_{timestamp}.py"
    shutil.copy2("app.py", backup_file)
    print(f"Backup created: {backup_file}")
    return backup_file

def add_security_imports():
    """Add security-related imports to app.py"""
    print("Adding security imports...")
    
    # Read the current app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Define the imports to add
    security_imports = '''# Security imports
from security_middleware import SecurityMiddleware
from validation import validate_input, LoginSchema, MobileLoginSchema, ShopCodeLoginSchema
from security_logger import log_security_event, log_failed_login, log_successful_login
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta

'''
    
    # Find the import section and add security imports
    import_pattern = r'^import\s+.*$'
    imports = re.findall(import_pattern, content, re.MULTILINE)
    
    if imports:
        # Add after the last import
        last_import = imports[-1]
        content = content.replace(last_import, last_import + '\n' + security_imports)
    else:
        # Add at the beginning if no imports found
        content = security_imports + content
    
    # Write back to app.py
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("Security imports added successfully")

def add_security_initialization():
    """Add security initialization after app creation"""
    print("Adding security initialization...")
    
    # Read the current app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find the app creation line
    app_creation_pattern = r'^app\s*=\s*Flask\(__name__\)'
    match = re.search(app_creation_pattern, content, re.MULTILINE)
    
    if match:
        # Add security initialization after app creation
        security_init = '''
# Security initialization
csrf = CSRFProtect(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize security middleware
security_middleware = SecurityMiddleware(app)

# Set secure session configuration
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=int(os.getenv('SESSION_TIMEOUT_HOURS', 8)))

# Set CSRF configuration
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour

'''
        
        # Insert after app creation
        insert_pos = match.end()
        content = content[:insert_pos] + security_init + content[insert_pos:]
        
        # Write back to app.py
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("Security initialization added successfully")
    else:
        print("Could not find app creation line")

def add_security_headers():
    """Add security headers function and after_request decorator"""
    print("Adding security headers...")
    
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
    
    # Add CSP header with unpkg.com allowed for Lucide icons
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self';"
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
        
        print("Security headers added successfully")
    else:
        print("Could not find route definitions")

def main():
    """Main integration function"""
    print("Starting targeted security integration...")
    
    # Create backup
    backup_file = backup_app()
    print(f"Backup created: {backup_file}")
    
    try:
        # Add security features step by step
        add_security_imports()
        add_security_initialization()
        add_security_headers()
        
        print("\n✅ Targeted security integration completed successfully!")
        print("\nNext steps:")
        print("1. Test the application locally")
        print("2. Deploy to Railway: railway up")
        print("3. Verify security headers are working")
        
    except Exception as e:
        print(f"\n❌ Error during integration: {e}")
        print(f"Restoring from backup: {backup_file}")
        
        # Restore from backup
        shutil.copy2(backup_file, "app.py")
        print("Backup restored successfully")

if __name__ == "__main__":
    main()
