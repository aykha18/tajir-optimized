#!/usr/bin/env python3
"""
Quick Security Integration for Tajir POS
Adds basic security features to app.py
"""

import re

def integrate_security_features():
    """Integrate security features into app.py."""
    
    # Read the current app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add security imports
    security_imports = '''
# Security imports
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
'''
    
    # Add imports after the existing imports
    if 'from flask import Flask' in content and 'CSRFProtect' not in content:
        # Find the last import and add security imports
        import_pattern = r'(from werkzeug\.utils import secure_filename\n)'
        replacement = r'\1' + security_imports
        content = re.sub(import_pattern, replacement, content)
    
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
)'''
    
    content = re.sub(app_config_pattern, new_app_config, content, flags=re.DOTALL)
    
    # Add security middleware functions
    security_middleware = '''

# Security middleware functions
@app.before_request
def check_security():
    """Check security before each request."""
    # Update session activity
    if 'user_id' in session:
        session['last_activity'] = datetime.now().isoformat()
    
    # Check session timeout
    if 'last_activity' in session:
        last_activity = datetime.fromisoformat(session['last_activity'])
        timeout_hours = int(os.getenv('SESSION_TIMEOUT_HOURS', 8))
        if datetime.now() - last_activity > timedelta(hours=timeout_hours):
            session.clear()
            return jsonify({'success': False, 'message': 'Session expired. Please login again.'}), 401

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
    
    # Add security middleware after app configuration
    if 'app.secret_key' in content and 'add_security_headers' not in content:
        # Find where to insert the security middleware
        insert_pattern = r'(app\.config\[.*?\]\n)'
        replacement = r'\1' + security_middleware + '\n'
        content = re.sub(insert_pattern, replacement, content, flags=re.DOTALL)
    
    # Update the auth_login function to add rate limiting
    auth_login_pattern = r'(@app\.route\(\'/api/auth/login\', methods=\[\'POST\'\]\)\n)'
    new_auth_login = '''@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
'''
    
    if 'def auth_login():' in content and '@limiter.limit' not in content:
        content = re.sub(auth_login_pattern, new_auth_login, content)
    
    # Write the updated content back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("SUCCESS: Integrated security features into app.py")

def main():
    """Main integration function."""
    print("Quick Security Integration for Tajir POS")
    print("=" * 50)
    
    integrate_security_features()
    
    print("\n" + "=" * 50)
    print("SUCCESS: Security integration completed!")
    print("\nNEXT STEPS:")
    print("1. Deploy to Railway: railway up")
    print("2. Test security features: python test_security.py")
    print("3. Monitor logs: railway logs")
    
    print("\nSECURITY FEATURES ADDED:")
    print("- CSRF Protection")
    print("- Rate Limiting (5 requests per minute on login)")
    print("- Security Headers (XSS, clickjacking protection)")
    print("- Session Timeout (8 hours)")
    print("- Secure Cookie Settings")

if __name__ == "__main__":
    main()
