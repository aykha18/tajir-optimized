#!/usr/bin/env python3
"""
Simple Security Integration for Tajir POS
Adds basic security features to the application
"""

import os

def install_security_packages():
    """Install required security packages."""
    print("Installing security packages...")
    os.system("pip install Flask-WTF==1.1.1 Flask-Limiter==3.5.0 marshmallow==3.20.1 cryptography==41.0.7")
    print("SUCCESS: Security packages installed")

def create_security_config():
    """Create a security configuration file."""
    config_content = '''"""
Security configuration for Tajir POS
"""
import os
from datetime import timedelta

# Security settings
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")

# Session configuration
SESSION_TIMEOUT_HOURS = int(os.getenv('SESSION_TIMEOUT_HOURS', 8))
PERMANENT_SESSION_LIFETIME = timedelta(hours=SESSION_TIMEOUT_HOURS)
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # Prevent XSS
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection

# Rate limiting
MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 50))

# CSRF protection
WTF_CSRF_TIME_LIMIT = 3600  # 1 hour

# Security headers
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self';"
}
'''
    
    with open('security_config.py', 'w') as f:
        f.write(config_content)
    
    print("SUCCESS: Created security_config.py")

def create_security_app_wrapper():
    """Create a security wrapper for the Flask app."""
    wrapper_content = '''"""
Security wrapper for Tajir POS Flask app
"""
from flask import Flask, request, jsonify, session
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
import os
from security_config import *
from security_middleware import SecurityMiddleware
from security_logger import setup_security_logging, log_security_event, log_failed_login, log_successful_login

def create_secure_app():
    """Create a Flask app with security features."""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['DATABASE'] = os.getenv('DATABASE_PATH', 'pos_tailor.db')
    
    # Security configuration
    app.secret_key = SECRET_KEY
    app.config['PERMANENT_SESSION_LIFETIME'] = PERMANENT_SESSION_LIFETIME
    app.config['SESSION_COOKIE_SECURE'] = SESSION_COOKIE_SECURE
    app.config['SESSION_COOKIE_HTTPONLY'] = SESSION_COOKIE_HTTPONLY
    app.config['SESSION_COOKIE_SAMESITE'] = SESSION_COOKIE_SAMESITE
    
    # CSRF protection
    csrf = CSRFProtect(app)
    app.config['WTF_CSRF_TIME_LIMIT'] = WTF_CSRF_TIME_LIMIT
    
    # Rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    
    # Security middleware
    security_middleware = SecurityMiddleware(app)
    
    # Setup security logging
    setup_security_logging()
    
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
            rate_check = security_middleware.check_rate_limit(request.path, RATE_LIMIT_PER_MINUTE)
            if rate_check:
                return rate_check

    @app.after_request
    def add_security_headers(response):
        """Add security headers to response."""
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # Add HSTS header for HTTPS
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    return app, limiter, security_middleware

def log_user_action_with_security(action, user_id=None, details=None):
    """Enhanced user action logging with security context."""
    try:
        # Import the original log_user_action function
        from app import log_user_action
        
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
        print(f"Failed to log user action with security: {e}")
'''
    
    with open('security_app.py', 'w') as f:
        f.write(wrapper_content)
    
    print("SUCCESS: Created security_app.py")

def create_deployment_script():
    """Create a deployment script."""
    deploy_content = '''#!/bin/bash
# Tajir POS Secure Deployment Script

echo "Deploying Tajir POS with security features..."

# Install security packages
pip install Flask-WTF==1.1.1 Flask-Limiter==3.5.0 marshmallow==3.20.1 cryptography==41.0.7

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Deploy to Railway
echo "Deploying to Railway..."
railway up

echo "Deployment completed!"
echo "Check your application at: railway open"
'''
    
    with open('deploy.sh', 'w') as f:
        f.write(deploy_content)
    
    # Make it executable on Unix systems
    try:
        os.chmod('deploy.sh', 0o755)
    except:
        pass
    
    print("SUCCESS: Created deploy.sh")

def create_test_script():
    """Create a security test script."""
    test_content = '''#!/usr/bin/env python3
"""
Security Test Script for Tajir POS
Tests basic security features
"""

import requests
import time

def test_rate_limiting(base_url):
    """Test rate limiting on login endpoint."""
    print("Testing rate limiting...")
    
    for i in range(10):
        response = requests.post(f"{base_url}/api/auth/login", 
                               json={"method": "email", "email": "test@test.com", "password": "wrong"})
        print(f"Request {i+1}: Status {response.status_code}")
        
        if response.status_code == 429:
            print("Rate limiting working correctly!")
            break
        
        time.sleep(0.1)
    else:
        print("Rate limiting not working as expected")

def test_csrf_protection(base_url):
    """Test CSRF protection."""
    print("Testing CSRF protection...")
    
    # Try to make a POST request without CSRF token
    response = requests.post(f"{base_url}/api/auth/login", 
                           json={"method": "email", "email": "test@test.com", "password": "wrong"})
    
    if response.status_code == 400 and "CSRF" in response.text:
        print("CSRF protection working correctly!")
    else:
        print("CSRF protection not working as expected")

def test_security_headers(base_url):
    """Test security headers."""
    print("Testing security headers...")
    
    response = requests.get(base_url)
    headers = response.headers
    
    required_headers = [
        'X-Content-Type-Options',
        'X-Frame-Options', 
        'X-XSS-Protection',
        'Content-Security-Policy'
    ]
    
    for header in required_headers:
        if header in headers:
            print(f"SUCCESS: {header}: {headers[header]}")
        else:
            print(f"FAILED: {header}: Missing")

if __name__ == "__main__":
    base_url = "http://localhost:5000"  # Change this to your Railway URL
    print("Security Testing for Tajir POS")
    print("=" * 40)
    
    test_security_headers(base_url)
    print()
    test_rate_limiting(base_url)
    print()
    test_csrf_protection(base_url)
'''
    
    with open('test_security.py', 'w') as f:
        f.write(test_content)
    
    print("SUCCESS: Created test_security.py")

def main():
    """Main integration function."""
    print("Simple Security Integration for Tajir POS")
    print("=" * 50)
    
    # Install security packages
    install_security_packages()
    
    # Create security configuration
    create_security_config()
    
    # Create security app wrapper
    create_security_app_wrapper()
    
    # Create deployment script
    create_deployment_script()
    
    # Create test script
    create_test_script()
    
    print("\n" + "=" * 50)
    print("SUCCESS: Simple security integration completed!")
    print("\nNEXT STEPS:")
    print("1. Deploy to Railway: railway up")
    print("2. Test security features: python test_security.py")
    print("3. Monitor logs: railway logs")
    
    print("\nFILES CREATED:")
    print("- security_config.py: Security configuration")
    print("- security_app.py: Security app wrapper")
    print("- deploy.sh: Deployment script")
    print("- test_security.py: Security testing script")
    
    print("\nIMPORTANT:")
    print("- Your environment variables are already set in Railway")
    print("- The app will use the security configuration automatically")
    print("- Test thoroughly before going live")

if __name__ == "__main__":
    main()
