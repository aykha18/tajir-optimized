#!/usr/bin/env python3
"""
Simple test to verify checkbox styling works
"""

import requests
import json

def test_shop_settings_api():
    """Test shop settings API to verify data structure"""
    
    # Test login
    login_data = {
        "email": "dressme@tajir.com",
        "password": "password123"
    }
    
    session = requests.Session()
    
    try:
        # Login
        response = session.post("http://localhost:5000/api/login", json=login_data)
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")
            return
        
        print("✅ Login successful")
        
        # Get shop settings
        response = session.get("http://localhost:5000/api/shop-settings")
        if response.status_code != 200:
            print(f"Shop settings failed: {response.status_code}")
            return
        
        settings = response.json()
        print("✅ Shop settings retrieved")
        
        # Check checkbox values
        checkbox_fields = [
            'enable_trial_date',
            'enable_delivery_date', 
            'enable_advance_payment',
            'use_dynamic_invoice_template',
            'enable_customer_notes',
            'enable_employee_assignment'
        ]
        
        print("\n📋 Checkbox Values:")
        for field in checkbox_fields:
            value = settings.get('settings', {}).get(field, False)
            print(f"  {field}: {value} ({type(value)})")
        
        # Test updating a checkbox
        print("\n🔄 Testing checkbox update...")
        update_data = {
            "enable_trial_date": True,
            "enable_delivery_date": False,
            "enable_advance_payment": True,
            "use_dynamic_invoice_template": False,
            "enable_customer_notes": True,
            "enable_employee_assignment": False
        }
        
        response = session.post("http://localhost:5000/api/shop-settings", json=update_data)
        if response.status_code == 200:
            print("✅ Checkbox update successful")
            
            # Verify the update
            response = session.get("http://localhost:5000/api/shop-settings")
            if response.status_code == 200:
                updated_settings = response.json()
                print("\n📋 Updated Checkbox Values:")
                for field in checkbox_fields:
                    value = updated_settings.get('settings', {}).get(field, False)
                    print(f"  {field}: {value} ({type(value)})")
        else:
            print(f"❌ Checkbox update failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_shop_settings_api()
