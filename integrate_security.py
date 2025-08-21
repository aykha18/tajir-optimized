#!/usr/bin/env python3
"""
Security Integration Script for Tajir POS
Integrates security middleware and features into app.py
"""

import os
import re
from datetime import timedelta

def update_app_configuration():
    """Update app.py with security configuration."""
    
    # Read the current app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add security imports at the top
    security_imports = '''
# Security imports
from security_middleware import SecurityMiddleware
from security_logger import setup_security_logging, log_security_event, log_failed_login, log_successful_login
from validation import validate_input, LoginSchema, MobileLoginSchema, ShopCodeLoginSchema
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
'''
    
    # Find the imports section and add security imports
    if 'from flask import Flask' in content and 'SecurityMiddleware' not in content:
        # Add after the last import
        import_pattern = r'(from flask import.*?)(\n\n|\napp =)'
        replacement = r'\1' + security_imports + r'\2'
        content = re.sub(import_pattern, replacement, content, flags=re.DOTALL)
    
    # Update app configuration
    app_config_pattern = r'(app = Flask\(__name__\)\napp\.config\[.*?\])'
    new_app_config = '''app = Flask(__name__)
app.config['DATABASE'] = os.getenv('DATABASE_PATH', 'pos_tailor.db')

# Security configuration
app.secret_key = os.getenv('SECRET_KEY')
if not app.secret_key:
    raise ValueError("SECRET_KEY environment variable is required")

# Session configuration
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=int(os.getenv('SESSION_TIMEOUT_HOURS', 8)))
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection

# CSRF protection
csrf = CSRFProtect(app)
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Security middleware
security_middleware = SecurityMiddleware(app)

# Setup security logging
setup_security_logging()'''
    
    content = re.sub(app_config_pattern, new_app_config, content, flags=re.DOTALL)
    
    # Add security middleware functions
    security_middleware_functions = '''

# Security middleware functions
@app.before_request
def check_security():
    """Check security before each request."""
    # Check session timeout
    timeout_check = security_middleware.check_session_timeout()
    if timeout_check:
        return timeout_check
    
    # Check rate limiting for API endpoints
    if request.path.startswith('/api/'):
        rate_check = security_middleware.check_rate_limit(request.path, 50)
        if rate_check:
            return rate_check

@app.after_request
def add_security_headers(response):
    """Add security headers to response."""
    return security_middleware.add_security_headers(response)

def log_user_action_with_security(action, user_id=None, details=None):
    """Enhanced user action logging with security context."""
    try:
        # Log to database
        log_user_action(action, user_id, details)
        
        # Log security event
        log_security_event(
            event_type=action,
            user_id=user_id,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
    except Exception as e:
        logger.error(f"Failed to log user action with security: {e}")'''
    
    # Add after the existing log_user_action function
    if 'def log_user_action(' in content and 'log_user_action_with_security' not in content:
        content = content.replace('def log_user_action(', security_middleware_functions + '\n\ndef log_user_action(')
    
    # Update the auth_login function to use security features
    auth_login_pattern = r'(@app\.route\(\'/api/auth/login\', methods=\[\'POST\'\]\)\n@limiter\.limit\("5 per minute"\)\n)?def auth_login\(\):'
    
    new_auth_login = '''@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def auth_login():
    """Handle user login with security features."""
    try:
        data = request.get_json()
        method = data.get('method')
        
        # Log login attempt
        log_user_action_with_security("LOGIN_ATTEMPT", None, {
            'method': method,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        })
        
        # Check for too many failed attempts
        identifier = data.get('email') or data.get('mobile') or data.get('shop_code')
        if identifier:
            failed_check = security_middleware.check_failed_attempts(identifier, 5)
            if failed_check:
                return failed_check
        
        conn = get_db_connection()
        
        if method == 'email':
            # Validate input
            validated_data, errors = validate_input(LoginSchema, data)
            if errors:
                return jsonify({'success': False, 'message': 'Invalid input', 'errors': errors}), 400
            
            email = validated_data['email']
            password = validated_data['password']
            
            user = conn.execute('SELECT * FROM users WHERE email = ? AND is_active = 1', (email,)).fetchone()
            
            if not user:
                security_middleware.record_failed_attempt(email)
                log_failed_login(email, 'email', request.remote_addr, request.headers.get('User-Agent'))
                return jsonify({'success': False, 'message': 'Invalid email or password'})
            
            import bcrypt
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                security_middleware.record_failed_attempt(email)
                log_failed_login(email, 'email', request.remote_addr, request.headers.get('User-Agent'))
                return jsonify({'success': False, 'message': 'Invalid email or password'})
                
        elif method == 'mobile':
            # Validate input
            validated_data, errors = validate_input(MobileLoginSchema, data)
            if errors:
                return jsonify({'success': False, 'message': 'Invalid input', 'errors': errors}), 400
            
            mobile = validated_data['mobile']
            otp = validated_data['otp']
            
            # Verify OTP
            otp_record = conn.execute('''
                SELECT * FROM otp_codes 
                WHERE mobile = ? AND otp_code = ? AND is_used = 0 AND expires_at > CURRENT_TIMESTAMP
                ORDER BY created_at DESC LIMIT 1
            ''', (mobile, otp)).fetchone()
            
            if not otp_record:
                security_middleware.record_failed_attempt(mobile)
                log_failed_login(mobile, 'mobile', request.remote_addr, request.headers.get('User-Agent'))
                return jsonify({'success': False, 'message': 'Invalid or expired OTP'})
            
            # Mark OTP as used
            conn.execute('UPDATE otp_codes SET is_used = 1 WHERE id = ?', (otp_record['id'],))
            
            user = conn.execute('SELECT * FROM users WHERE mobile = ? AND is_active = 1', (mobile,)).fetchone()
            
            if not user:
                security_middleware.record_failed_attempt(mobile)
                log_failed_login(mobile, 'mobile', request.remote_addr, request.headers.get('User-Agent'))
                return jsonify({'success': False, 'message': 'No account found with this mobile number'})
                
        elif method == 'shop_code':
            # Validate input
            validated_data, errors = validate_input(ShopCodeLoginSchema, data)
            if errors:
                return jsonify({'success': False, 'message': 'Invalid input', 'errors': errors}), 400
            
            shop_code = validated_data['shop_code']
            password = validated_data['password']
            
            user = conn.execute('SELECT * FROM users WHERE shop_code = ? AND is_active = 1', (shop_code,)).fetchone()
            
            if not user:
                security_middleware.record_failed_attempt(shop_code)
                log_failed_login(shop_code, 'shop_code', request.remote_addr, request.headers.get('User-Agent'))
                return jsonify({'success': False, 'message': 'Invalid shop code or password'})
            
            import bcrypt
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                security_middleware.record_failed_attempt(shop_code)
                log_failed_login(shop_code, 'shop_code', request.remote_addr, request.headers.get('User-Agent'))
                return jsonify({'success': False, 'message': 'Invalid shop code or password'})
        else:
            return jsonify({'success': False, 'message': 'Invalid login method'})
        
        # Set session data with security
        session.permanent = True
        session['user_id'] = user['user_id']
        session['shop_name'] = user['shop_name']
        session['shop_code'] = user['shop_code']
        session['last_activity'] = datetime.now().isoformat()
        
        # Log successful login
        log_successful_login(user['user_id'], method, request.remote_addr, request.headers.get('User-Agent'))
        log_user_action_with_security("LOGIN_SUCCESS", user['user_id'], {
            'shop_name': user['shop_name'],
            'shop_code': user['shop_code'],
            'method': method
        })
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'user_id': user['user_id'],
                'shop_name': user['shop_name'],
                'shop_code': user['shop_code']
            }
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'success': False, 'message': 'Login failed. Please try again.'})'''
    
    # Replace the existing auth_login function
    if 'def auth_login():' in content:
        content = re.sub(auth_login_pattern, new_auth_login, content, flags=re.DOTALL)
    
    # Write the updated content back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("SUCCESS: Updated app.py with security features")

def add_csrf_tokens_to_templates():
    """Add CSRF tokens to HTML templates."""
    templates_dir = 'templates'
    
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(templates_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add CSRF meta tag to head section
            if '<head>' in content and 'csrf-token' not in content:
                csrf_meta = '    <meta name="csrf-token" content="{{ csrf_token() }}">'
                content = content.replace('<head>', '<head>\n' + csrf_meta)
            
            # Add CSRF tokens to forms
            if '<form' in content and 'csrf_token()' not in content:
                # Replace form tags to include CSRF token
                content = re.sub(
                    r'(<form[^>]*method=["\']POST["\'][^>]*>)',
                    r'\1\n        {{ csrf_token() }}',
                    content
                )
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
    
    print("SUCCESS: Added CSRF tokens to templates")

def update_javascript_for_csrf():
    """Update JavaScript to include CSRF tokens in AJAX requests."""
    js_dir = 'static/js'
    
    if os.path.exists(js_dir):
        for filename in os.listdir(js_dir):
            if filename.endswith('.js'):
                filepath = os.path.join(js_dir, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Add CSRF token function if not present
                if 'getCSRFToken' not in content:
                    csrf_function = '''
// CSRF token function
function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// Update fetch requests to include CSRF token
function fetchWithCSRF(url, options = {}) {
    const token = getCSRFToken();
    return fetch(url, {
        ...options,
        headers: {
            ...options.headers,
            'X-CSRFToken': token,
            'Content-Type': 'application/json'
        }
    });
}
'''
                    content = csrf_function + content
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    print("SUCCESS: Updated JavaScript for CSRF protection")

def main():
    """Main integration function."""
    print("Security Integration for Tajir POS")
    print("=" * 50)
    
    # Update app.py with security features
    update_app_configuration()
    
    # Add CSRF tokens to templates
    add_csrf_tokens_to_templates()
    
    # Update JavaScript for CSRF
    update_javascript_for_csrf()
    
    print("\n" + "=" * 50)
    print("SUCCESS: Security integration completed!")
    print("\nNEXT STEPS:")
    print("1. Test the application locally: python app.py")
    print("2. Deploy to Railway: railway up")
    print("3. Test all functionality in production")
    print("4. Monitor security logs: railway logs")
    
    print("\nIMPORTANT:")
    print("- All forms now require CSRF tokens")
    print("- Session timeout is enabled (8 hours)")
    print("- Rate limiting is active on API endpoints")
    print("- Failed login attempts are tracked")
    print("- Security events are logged")

if __name__ == "__main__":
    main()
