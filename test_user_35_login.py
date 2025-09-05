#!/usr/bin/env python3
"""
Test login with user_id 35 credentials
"""

import requests
import json

def test_user_35_login():
    print("🧪 Testing Login with User ID 35 Credentials")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Step 1: Login with user_id 35 credentials
    print("\n🔐 Step 1: Logging in with user_id 35 credentials...")
    login_data = {
        "method": "email",
        "email": "tumd@tajir.com",  # Correct email for user_id 35
        "password": "demo123"
    }
    response = session.post(f"{base_url}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"   ❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return
    print("   ✅ Login successful")
    
    # Step 2: Check shop settings to confirm user_id
    print("\n📋 Step 2: Checking shop settings...")
    response = session.get(f"{base_url}/api/shop-settings")
    if response.status_code == 200:
        settings = response.json()
        user_id = settings['settings'].get('user_id')
        print(f"   📊 Current user_id: {user_id}")
        
        if user_id == 35:
            print("   🎉 SUCCESS: Now logged in as user_id 35!")
            
            # Check the boolean values
            boolean_fields = [
                "enable_trial_date", "enable_delivery_date", "enable_advance_payment",
                "enable_customer_notes", "enable_employee_assignment"
            ]
            
            print("\n📋 Step 3: Checking boolean values for user_id 35...")
            all_true = True
            for field in boolean_fields:
                value = settings['settings'].get(field, False)
                status = "✅" if value else "❌"
                print(f"   {status} {field}: {value}")
                if not value:
                    all_true = False
            
            if all_true:
                print("\n🎉 PERFECT: All checkboxes should be True for user_id 35!")
                print("   ✅ The frontend should now load the correct values")
            else:
                print("\n❌ ISSUE: Some values are still False")
        else:
            print(f"   ❌ Still logged in as user_id {user_id}, not 35")
    else:
        print(f"   ❌ Failed to get shop settings: {response.status_code}")

if __name__ == "__main__":
    test_user_35_login()
