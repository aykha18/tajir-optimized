#!/usr/bin/env python3
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
    base_url = "https://tajir.up.railway.app"  # Railway URL
    print("Security Testing for Tajir POS")
    print("=" * 40)
    
    test_security_headers(base_url)
    print()
    test_rate_limiting(base_url)
    print()
    test_csrf_protection(base_url)
