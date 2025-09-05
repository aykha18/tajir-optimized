#!/usr/bin/env python3
"""
Debug script to test boolean value handling
"""

import requests
import json

def debug_boolean_values():
    print("🔍 Debugging Boolean Value Handling")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Login
    print("\n🔐 Logging in...")
    login_data = {
        "method": "email",
        "email": "td@tajir.com",
        "password": "demo123"
    }
    response = session.post(f"{base_url}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"   ❌ Login failed: {response.status_code}")
        return
    print("   ✅ Login successful")
    
    # Test with explicit boolean values
    print("\n🧪 Testing with explicit boolean values...")
    test_data = {
        "shop_name": "Test Shop",
        "enable_trial_date": True,
        "enable_delivery_date": True,
        "enable_advance_payment": True,
        "enable_customer_notes": True,
        "enable_employee_assignment": True,
        "default_trial_days": 3,
        "default_delivery_days": 5
    }
    
    print(f"   Sending data: {json.dumps(test_data, indent=2)}")
    
    response = session.put(f"{base_url}/api/shop-settings", json=test_data)
    print(f"   Response status: {response.status_code}")
    print(f"   Response: {response.text}")
    
    # Check what was actually saved
    print("\n🔍 Checking what was saved...")
    response = session.get(f"{base_url}/api/shop-settings")
    if response.status_code == 200:
        settings = response.json()
        print("   Current settings:")
        for key in ['enable_trial_date', 'enable_delivery_date', 'enable_advance_payment', 
                   'enable_customer_notes', 'enable_employee_assignment', 'default_trial_days', 'default_delivery_days']:
            value = settings['settings'].get(key)
            print(f"   {key}: {value} (type: {type(value)})")

if __name__ == "__main__":
    debug_boolean_values()
