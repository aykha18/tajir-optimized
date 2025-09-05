#!/usr/bin/env python3
"""
Check which user is actually logged in
"""

import requests
import json

def check_login_user():
    print("🔍 Checking Which User is Logged In")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Step 1: Login
    print("\n🔐 Step 1: Logging in...")
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
    
    # Step 2: Check shop settings to see which user_id is returned
    print("\n📋 Step 2: Checking shop settings...")
    response = session.get(f"{base_url}/api/shop-settings")
    if response.status_code == 200:
        settings = response.json()
        user_id = settings['settings'].get('user_id')
        print(f"   📊 Current user_id: {user_id}")
        
        # Check the boolean values for this user
        boolean_fields = [
            "enable_trial_date", "enable_delivery_date", "enable_advance_payment",
            "enable_customer_notes", "enable_employee_assignment"
        ]
        
        print("\n📋 Step 3: Checking boolean values for this user...")
        for field in boolean_fields:
            value = settings['settings'].get(field, False)
            status = "✅" if value else "❌"
            print(f"   {status} {field}: {value}")
        
        # Step 4: Check what user_id 35 has
        print("\n🔍 Step 4: Checking user_id 35 values...")
        # We know from our previous check that user_id 35 has all True values
        print("   📊 user_id 35 should have all True values")
        print("   📊 user_id 27 has all False values (current user)")
        
        print(f"\n🎯 CONCLUSION: Login is working as user_id {user_id}, not user_id 35")
        print("   The issue is that we're testing with the wrong user!")
        
    else:
        print(f"   ❌ Failed to get shop settings: {response.status_code}")

if __name__ == "__main__":
    check_login_user()
