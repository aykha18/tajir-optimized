#!/usr/bin/env python3
"""
Check current shop settings for user 35
"""

import requests
import json

def check_user_35_settings():
    print("🔍 Checking Shop Settings for User 35")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Login as user 35
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
    
    # Get current shop settings
    print("\n📋 Getting current shop settings...")
    try:
        response = session.get(f"{base_url}/api/shop-settings")
        if response.status_code == 200:
            settings = response.json()
            print("   ✅ Shop settings retrieved successfully")
            
            # Display the key boolean and numeric fields
            print("\n📊 Current Settings for User 35:")
            print("   Boolean Fields:")
            boolean_fields = [
                "enable_trial_date", "enable_delivery_date", "enable_advance_payment",
                "enable_customer_notes", "enable_employee_assignment", "use_dynamic_invoice_template"
            ]
            for field in boolean_fields:
                value = settings['settings'].get(field, False)
                status = "✅" if value else "❌"
                print(f"   {status} {field}: {value}")
            
            print("\n   Numeric Fields:")
            numeric_fields = ["default_trial_days", "default_delivery_days"]
            for field in numeric_fields:
                value = settings['settings'].get(field, 0)
                print(f"   📊 {field}: {value}")
            
            print("\n   Other Key Fields:")
            other_fields = ["shop_name", "user_id", "currency_code", "timezone"]
            for field in other_fields:
                value = settings['settings'].get(field, "N/A")
                print(f"   📝 {field}: {value}")
                
        else:
            print(f"   ❌ Failed to get shop settings: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error getting shop settings: {e}")

if __name__ == "__main__":
    check_user_35_settings()
