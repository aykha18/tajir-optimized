#!/usr/bin/env python3
"""
Test script to check shop settings backend API
"""

import requests
import json

def test_shop_settings_backend():
    print("🧪 Testing Shop Settings Backend API")
    
    base_url = "http://localhost:5000"
    
    # Create a session to maintain login state
    session = requests.Session()
    
    # Step 0: Login first
    print("\n🔐 Step 0: Logging in...")
    try:
        login_data = {
            "method": "email",
            "email": "td@tajir.com",
            "password": "demo123"
        }
        response = session.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            print("   ✅ Login successful")
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return
    
    # Test 1: Get current shop settings
    print("\n📋 Step 1: Getting current shop settings...")
    try:
        response = session.get(f"{base_url}/api/shop-settings")
        if response.status_code == 200:
            settings = response.json()
            print("   ✅ Shop settings retrieved successfully")
            print(f"   Current settings: {json.dumps(settings, indent=2)}")
        else:
            print(f"   ❌ Failed to get shop settings: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error getting shop settings: {e}")
        return
    
    # Test 2: Update shop settings with checkbox values
    print("\n💾 Step 2: Updating shop settings with checkbox values...")
    test_settings = {
        "shop_name": "Test Shop",
        "shop_mobile": "1234567890",
        "city": "Dubai",
        "area": "Test Area",
        "address": "Test Address",
        "trn": "123456789",
        "enable_trial_date": True,
        "enable_delivery_date": True,
        "enable_advance_payment": True,
        "enable_customer_notes": True,
        "enable_employee_assignment": True,
        "default_trial_days": 3,
        "default_delivery_days": 5,
        "currency_code": "AED",
        "timezone": "Asia/Dubai"
    }
    
    try:
        response = session.put(f"{base_url}/api/shop-settings", json=test_settings)
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Shop settings updated successfully")
            print(f"   Response: {json.dumps(result, indent=2)}")
        else:
            print(f"   ❌ Failed to update shop settings: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error updating shop settings: {e}")
        return
    
    # Test 3: Verify the settings were saved
    print("\n🔍 Step 3: Verifying settings were saved...")
    try:
        response = session.get(f"{base_url}/api/shop-settings")
        if response.status_code == 200:
            updated_settings = response.json()
            print("   ✅ Updated settings retrieved successfully")
            print(f"   Updated settings: {json.dumps(updated_settings, indent=2)}")
            
            # Check if boolean values are correct
            boolean_fields = [
                "enable_trial_date", "enable_delivery_date", "enable_advance_payment",
                "enable_customer_notes", "enable_employee_assignment"
            ]
            
            print("\n   📊 Boolean field verification:")
            for field in boolean_fields:
                value = updated_settings.get(field, False)
                expected = test_settings.get(field, False)
                status = "✅" if value == expected else "❌"
                print(f"   {status} {field}: {value} (expected: {expected})")
            
            # Check if numeric values are correct
            numeric_fields = ["default_trial_days", "default_delivery_days"]
            print("\n   📊 Numeric field verification:")
            for field in numeric_fields:
                value = updated_settings.get(field, 0)
                expected = test_settings.get(field, 0)
                status = "✅" if value == expected else "❌"
                print(f"   {status} {field}: {value} (expected: {expected})")
                
        else:
            print(f"   ❌ Failed to verify settings: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error verifying settings: {e}")
    
    print("\n✅ Backend API test completed!")

if __name__ == "__main__":
    test_shop_settings_backend()
