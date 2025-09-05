#!/usr/bin/env python3
"""
Test manual API call to see what's being sent
"""

import requests
import json

def test_manual_api_call():
    print("🧪 Testing Manual API Call")
    
    # Test data
    test_data = {
        'shop_name': 'Tumble Dry',
        'address': 'Test Address',
        'enable_trial_date': True,
        'enable_delivery_date': False,
        'enable_advance_payment': True,
        'enable_customer_notes': True,
        'enable_employee_assignment': False,
        'use_dynamic_invoice_template': False,
        'currency_code': 'AED',
        'timezone': 'Asia/Dubai'
    }
    
    print("📝 Test data being sent:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    # Make API call
    try:
        response = requests.put(
            'http://localhost:5000/api/shop-settings',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n📊 API Response Status: {response.status_code}")
        print(f"📊 API Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ API call successful!")
            else:
                print(f"❌ API call failed: {result.get('error')}")
        else:
            print(f"❌ API call failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ API call error: {e}")

if __name__ == "__main__":
    test_manual_api_call()
