#!/usr/bin/env python3
"""
Comprehensive Security Integration Script for Tajir POS
This script integrates all security features into the main application.
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
from validation import validate_input, LoginSchema, MobileLoginSchema, ShopCodeLoginSchema, ProductSchema, CustomerSchema, BillSchema
from security_logger import log_security_event, log_failed_login, log_successful_login
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
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

def add_security_decorators():
    """Add security decorators to sensitive routes"""
    print("Adding security decorators...")
    
    # Read the current app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Define security decorators
    security_decorators = '''
def require_csrf_token(f):
    """Decorator to require CSRF token for POST requests."""
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            if not request.form.get('csrf_token'):
                return jsonify({'error': 'CSRF token missing'}), 400
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def rate_limit_sensitive(f):
    """Decorator to apply rate limiting to sensitive endpoints."""
    def decorated_function(*args, **kwargs):
        # Check rate limit
        rate_limit_result = security_middleware.check_rate_limit(request.endpoint, 10)
        if rate_limit_result:
            return rate_limit_result
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

'''
    
    # Find a good place to insert (after security headers)
    # Look for the security headers function
    headers_pattern = r'def add_security_headers'
    match = re.search(headers_pattern, content, re.MULTILINE)
    
    if match:
        # Find the end of the security headers function
        lines = content.split('\n')
        start_line = content[:match.start()].count('\n')
        
        # Find the end of the function (look for the next function or route)
        for i in range(start_line + 1, len(lines)):
            if lines[i].strip().startswith('def ') or lines[i].strip().startswith('@app.route'):
                break
        
        # Insert after the security headers function
        insert_pos = content.find('\n', content.find('\n', match.end())) + 1
        content = content[:insert_pos] + security_decorators + content[insert_pos:]
        
        # Write back to app.py
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("Security decorators added successfully")
    else:
        print("Could not find security headers function")

def enhance_login_routes():
    """Enhance login routes with security features"""
    print("Enhancing login routes...")
    
    # Read the current app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find the auth_login function
    login_pattern = r'def auth_login\(\):'
    match = re.search(login_pattern, content, re.MULTILINE)
    
    if match:
        # Get the function content
        lines = content.split('\n')
        start_line = content[:match.start()].count('\n')
        
        # Find the end of the function
        indent_level = len(lines[start_line + 1]) - len(lines[start_line + 1].lstrip())
        end_line = start_line + 1
        
        for i in range(start_line + 2, len(lines)):
            if lines[i].strip() and len(lines[i]) - len(lines[i].lstrip()) <= indent_level:
                break
            end_line = i
        
        # Extract the function
        function_lines = lines[start_line:end_line + 1]
        function_content = '\n'.join(function_lines)
        
        # Add security enhancements
        enhanced_function = function_content.replace(
            'def auth_login():',
            '''@rate_limit_sensitive
@require_csrf_token
def auth_login():'''
        )
        
        # Add input validation at the beginning
        validation_code = '''
    # Input validation
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Determine login type and validate
        if 'email' in data and 'password' in data:
            validated_data, errors = validate_input(LoginSchema, data)
            if errors:
                log_failed_login('email', data.get('email', 'unknown'), 'validation_error', str(errors))
                return jsonify({'error': 'Invalid input data', 'details': errors}), 400
        elif 'mobile' in data and 'otp' in data:
            validated_data, errors = validate_input(MobileLoginSchema, data)
            if errors:
                log_failed_login('mobile', data.get('mobile', 'unknown'), 'validation_error', str(errors))
                return jsonify({'error': 'Invalid input data', 'details': errors}), 400
        elif 'shop_code' in data and 'password' in data:
            validated_data, errors = validate_input(ShopCodeLoginSchema, data)
            if errors:
                log_failed_login('shop_code', data.get('shop_code', 'unknown'), 'validation_error', str(errors))
                return jsonify({'error': 'Invalid input data', 'details': errors}), 400
        else:
            return jsonify({'error': 'Invalid login method'}), 400
        
        # Check for too many failed attempts
        identifier = data.get('email') or data.get('mobile') or data.get('shop_code', 'unknown')
        failed_check = security_middleware.check_failed_attempts(identifier)
        if failed_check:
            return failed_check
'''
        
        # Insert validation code after the function definition
        enhanced_function = enhanced_function.replace(
            '    if request.method == "POST":',
            validation_code + '    if request.method == "POST":'
        )
        
        # Add success logging
        enhanced_function = enhanced_function.replace(
            'session["user_id"] = user["id"]',
            '''session["user_id"] = user["id"]
            log_successful_login('email' if 'email' in data else 'mobile' if 'mobile' in data else 'shop_code', identifier)'''
        )
        
        # Add failure logging
        enhanced_function = enhanced_function.replace(
            'return jsonify({"error": "Invalid credentials"}), 401',
            '''log_failed_login('email' if 'email' in data else 'mobile' if 'mobile' in data else 'shop_code', identifier, 'invalid_credentials', 'Invalid credentials')
            security_middleware.record_failed_attempt(identifier)
            return jsonify({"error": "Invalid credentials"}), 401'''
        )
        
        # Replace the function in the content
        content = content.replace(function_content, enhanced_function)
        
        # Write back to app.py
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("Login routes enhanced successfully")
    else:
        print("Could not find auth_login function")

def add_csrf_tokens_to_templates():
    """Add CSRF tokens to HTML templates"""
    print("Adding CSRF tokens to templates...")
    
    # List of templates to update
    templates = [
        'templates/login.html',
        'templates/admin_login.html',
        'templates/register.html'
    ]
    
    for template_file in templates:
        if os.path.exists(template_file):
            with open(template_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Add CSRF token to forms
            if '<form' in content and 'csrf_token' not in content:
                # Add CSRF token after form opening tag
                content = re.sub(
                    r'(<form[^>]*>)',
                    r'\1\n    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">',
                    content
                )
                
                with open(template_file, "w", encoding="utf-8") as f:
                    f.write(content)
                
                print(f"CSRF token added to {template_file}")

def create_security_test():
    """Create a comprehensive security test"""
    print("Creating security test...")
    
    test_content = '''#!/usr/bin/env python3
"""
Comprehensive Security Test for Tajir POS
"""

import requests
import json
import time

def test_security_features():
    """Test all security features."""
    base_url = "https://tailor-pos-production.up.railway.app"
    
    print("Testing security features...")
    
    # Test 1: Security Headers
    print("\\n1. Testing Security Headers...")
    response = requests.get(f"{base_url}/")
    headers = response.headers
    
    security_headers = [
        'X-Content-Type-Options',
        'X-Frame-Options', 
        'X-XSS-Protection',
        'Content-Security-Policy',
        'Referrer-Policy'
    ]
    
    for header in security_headers:
        if header in headers:
            print(f"  ✓ {header}: {headers[header]}")
        else:
            print(f"  ✗ {header}: Missing")
    
    # Test 2: Rate Limiting
    print("\\n2. Testing Rate Limiting...")
    for i in range(15):
        response = requests.post(f"{base_url}/api/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })
        if response.status_code == 429:
            print(f"  ✓ Rate limiting triggered after {i+1} requests")
            break
    else:
        print("  ✗ Rate limiting not triggered")
    
    # Test 3: CSRF Protection
    print("\\n3. Testing CSRF Protection...")
    response = requests.post(f"{base_url}/api/login", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    if response.status_code == 400 and "CSRF" in response.text:
        print("  ✓ CSRF protection working")
    else:
        print("  ✗ CSRF protection not working")
    
    # Test 4: Input Validation
    print("\\n4. Testing Input Validation...")
    response = requests.post(f"{base_url}/api/login", json={
        "email": "invalid-email",
        "password": "123"
    })
    if response.status_code == 400 and "validation" in response.text.lower():
        print("  ✓ Input validation working")
    else:
        print("  ✗ Input validation not working")
    
    print("\\nSecurity testing completed!")

if __name__ == "__main__":
    test_security_features()
'''
    
    with open("test_comprehensive_security.py", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    print("Comprehensive security test created")

def main():
    """Main integration function"""
    print("Starting comprehensive security integration...")
    
    # Create backup
    backup_file = backup_app()
    print(f"Backup created: {backup_file}")
    
    try:
        # Add security features
        add_security_imports()
        add_security_initialization()
        add_security_headers()
        add_security_decorators()
        enhance_login_routes()
        add_csrf_tokens_to_templates()
        create_security_test()
        
        print("\\n✅ Comprehensive security integration completed successfully!")
        print("\\nNext steps:")
        print("1. Test the application locally")
        print("2. Deploy to Railway: railway up")
        print("3. Run security tests: python test_comprehensive_security.py")
        print("4. Verify all features work correctly")
        
    except Exception as e:
        print(f"\\n❌ Error during integration: {e}")
        print(f"Restoring from backup: {backup_file}")
        
        # Restore from backup
        shutil.copy2(backup_file, "app.py")
        print("Backup restored successfully")

if __name__ == "__main__":
    main()
