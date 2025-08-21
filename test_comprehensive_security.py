#!/usr/bin/env python3
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
    print("\n1. Testing Security Headers...")
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
    print("\n2. Testing Rate Limiting...")
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
    print("\n3. Testing CSRF Protection...")
    response = requests.post(f"{base_url}/api/login", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    if response.status_code == 400 and "CSRF" in response.text:
        print("  ✓ CSRF protection working")
    else:
        print("  ✗ CSRF protection not working")
    
    # Test 4: Input Validation
    print("\n4. Testing Input Validation...")
    response = requests.post(f"{base_url}/api/login", json={
        "email": "invalid-email",
        "password": "123"
    })
    if response.status_code == 400 and "validation" in response.text.lower():
        print("  ✓ Input validation working")
    else:
        print("  ✗ Input validation not working")
    
    print("\nSecurity testing completed!")

if __name__ == "__main__":
    test_security_features()
