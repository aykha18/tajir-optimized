#!/usr/bin/env python3
"""
Login Test Script for Tajir POS
Tests login functionality and provides correct credentials
"""

import requests
import json

def test_login(base_url, email, password):
    """Test login with provided credentials."""
    print(f"Testing login for: {email}")
    
    login_data = {
        "method": "email",
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Login successful!")
                return True
            else:
                print(f"❌ Login failed: {result.get('message')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function to test login."""
    base_url = "https://tajir.up.railway.app"
    
    print("Tajir POS Login Test")
    print("=" * 40)
    
    # Test admin login
    print("\n1. Testing Admin Login:")
    admin_success = test_login(base_url, "admin@tailorpos.com", "admin123")
    
    # Test with different variations
    print("\n2. Testing with different email formats:")
    test_login(base_url, "admin@tailorpos.com", "admin123")
    test_login(base_url, "ADMIN@TAILORPOS.COM", "admin123")
    test_login(base_url, " admin@tailorpos.com ", "admin123")
    
    print("\n3. Testing with different password formats:")
    test_login(base_url, "admin@tailorpos.com", "Admin123")
    test_login(base_url, "admin@tailorpos.com", "ADMIN123")
    test_login(base_url, "admin@tailorpos.com", " admin123 ")
    
    print("\n" + "=" * 40)
    print("LOGIN CREDENTIALS:")
    print("Email: admin@tailorpos.com")
    print("Password: admin123")
    print("\nIf login still fails, try:")
    print("1. Clear browser cache and cookies")
    print("2. Try incognito/private browsing mode")
    print("3. Check if the application is running properly")

if __name__ == "__main__":
    main()
