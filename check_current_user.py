#!/usr/bin/env python3
"""
Check which user is currently logged in via the API
"""

import requests
import json

def check_current_user():
    print("🔍 Checking Current Logged-in User")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Step 1: Login with the credentials you're using
    print("\n🔐 Step 1: Logging in...")
    login_data = {
        "method": "email",
        "email": "td@tajir.com",  # This is what you're probably using
        "password": "demo123"
    }
    response = session.post(f"{base_url}/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"   ❌ Login failed: {response.status_code}")
        return
    print("   ✅ Login successful")
    
    # Step 2: Check which user_id we're logged in as
    print("\n📋 Step 2: Checking current user...")
    response = session.get(f"{base_url}/api/shop-settings")
    if response.status_code == 200:
        settings = response.json()
        user_id = settings['settings'].get('user_id')
        print(f"   📊 Current user_id: {user_id}")
        
        if user_id == 35:
            print("   ✅ You're logged in as user_id 35 (correct user)")
        elif user_id == 27:
            print("   ❌ You're logged in as user_id 27 (wrong user)")
            print("   🔧 Solution: Use email 'tumd@tajir.com' instead of 'td@tajir.com'")
        else:
            print(f"   ❓ You're logged in as user_id {user_id} (unknown user)")
        
        # Show the boolean values
        boolean_fields = [
            "enable_trial_date", "enable_delivery_date", "enable_advance_payment",
            "enable_customer_notes", "enable_employee_assignment"
        ]
        
        print(f"\n📋 Step 3: Boolean values for user_id {user_id}:")
        for field in boolean_fields:
            value = settings['settings'].get(field, False)
            status = "✅" if value else "❌"
            print(f"   {status} {field}: {value}")
            
    else:
        print(f"   ❌ Failed to get shop settings: {response.status_code}")

if __name__ == "__main__":
    check_current_user()
