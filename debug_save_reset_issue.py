#!/usr/bin/env python3
"""
Debug the save settings reset issue
"""

import requests
import json
import time

def debug_save_reset_issue():
    print("🔍 Debugging Save Settings Reset Issue")
    
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
    
    # Step 2: Check initial state
    print("\n📋 Step 2: Checking initial state...")
    response = session.get(f"{base_url}/api/shop-settings")
    if response.status_code == 200:
        initial_settings = response.json()
        print("   📊 Initial settings:")
        boolean_fields = [
            "enable_trial_date", "enable_delivery_date", "enable_advance_payment",
            "enable_customer_notes", "enable_employee_assignment"
        ]
        for field in boolean_fields:
            value = initial_settings['settings'].get(field, False)
            status = "✅" if value else "❌"
            print(f"   {status} {field}: {value}")
    else:
        print(f"   ❌ Failed to get initial settings: {response.status_code}")
        return
    
    # Step 3: Simulate the save operation that's causing the reset
    print("\n💾 Step 3: Simulating save operation...")
    
    # Get the current form data (what the frontend would send)
    current_data = initial_settings['settings'].copy()
    
    # Simulate what happens when you click "Save Settings" - send the same data back
    save_data = {
        "shop_name": current_data.get('shop_name', ''),
        "shop_mobile": current_data.get('shop_mobile', ''),
        "city": current_data.get('city', ''),
        "area": current_data.get('area', ''),
        "address": current_data.get('address', ''),
        "trn": current_data.get('trn', ''),
        "default_delivery_days": current_data.get('default_delivery_days', 0),
        "default_trial_days": current_data.get('default_trial_days', 0),
        "enable_trial_date": current_data.get('enable_trial_date', False),
        "enable_delivery_date": current_data.get('enable_delivery_date', False),
        "enable_advance_payment": current_data.get('enable_advance_payment', False),
        "use_dynamic_invoice_template": current_data.get('use_dynamic_invoice_template', False),
        "enable_customer_notes": current_data.get('enable_customer_notes', False),
        "enable_employee_assignment": current_data.get('enable_employee_assignment', False),
        "default_employee_id": current_data.get('default_employee_id'),
        "currency_code": current_data.get('currency_code', 'AED'),
        "timezone": current_data.get('timezone', 'Asia/Dubai')
    }
    
    print("   📤 Sending save data:")
    for field in boolean_fields:
        value = save_data.get(field, False)
        status = "✅" if value else "❌"
        print(f"   {status} {field}: {value}")
    
    # Send the save request
    response = session.put(f"{base_url}/api/shop-settings", json=save_data)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Save response: {result}")
    else:
        print(f"   ❌ Save failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return
    
    # Step 4: Check state after save
    print("\n🔍 Step 4: Checking state after save...")
    time.sleep(1)  # Give a moment for the save to complete
    
    response = session.get(f"{base_url}/api/shop-settings")
    if response.status_code == 200:
        after_save_settings = response.json()
        print("   📊 Settings after save:")
        for field in boolean_fields:
            value = after_save_settings['settings'].get(field, False)
            status = "✅" if value else "❌"
            print(f"   {status} {field}: {value}")
        
        # Compare with initial state
        print("\n🔄 Step 5: Comparing before and after...")
        for field in boolean_fields:
            initial_value = initial_settings['settings'].get(field, False)
            after_value = after_save_settings['settings'].get(field, False)
            if initial_value != after_value:
                print(f"   ❌ {field}: {initial_value} → {after_value} (CHANGED!)")
            else:
                print(f"   ✅ {field}: {initial_value} → {after_value} (unchanged)")
    else:
        print(f"   ❌ Failed to get settings after save: {response.status_code}")
    
    # Step 6: Check if there are any default values being applied
    print("\n🔍 Step 6: Checking for default value issues...")
    
    # Test with explicit True values
    print("\n🧪 Step 7: Testing with explicit True values...")
    explicit_true_data = save_data.copy()
    for field in boolean_fields:
        explicit_true_data[field] = True
    
    print("   📤 Sending explicit True values:")
    for field in boolean_fields:
        print(f"   ✅ {field}: True")
    
    response = session.put(f"{base_url}/api/shop-settings", json=explicit_true_data)
    if response.status_code == 200:
        print("   ✅ Explicit True save successful")
        
        # Check if they're actually saved as True
        time.sleep(1)
        response = session.get(f"{base_url}/api/shop-settings")
        if response.status_code == 200:
            final_settings = response.json()
            print("   📊 Final settings after explicit True:")
            for field in boolean_fields:
                value = final_settings['settings'].get(field, False)
                status = "✅" if value else "❌"
                print(f"   {status} {field}: {value}")
        else:
            print(f"   ❌ Failed to get final settings: {response.status_code}")
    else:
        print(f"   ❌ Explicit True save failed: {response.status_code}")
        print(f"   Response: {response.text}")

if __name__ == "__main__":
    debug_save_reset_issue()
