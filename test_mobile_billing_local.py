#!/usr/bin/env python3
"""
Test Mobile Billing Local Environment
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_mobile_billing_endpoints():
    """Test mobile billing related endpoints"""
    
    print("Testing Mobile Billing Local Environment...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/products")
        if response.status_code == 200:
            print("✅ Server is running and responding")
        else:
            print(f"❌ Server responded with status: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to local server. Is it running?")
        return
    
    # Test 2: Check products endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/products")
        products = response.json()
        print(f"✅ Products endpoint: {len(products)} products available")
    except Exception as e:
        print(f"❌ Products endpoint error: {e}")
    
    # Test 3: Check customers endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/customers")
        customers = response.json()
        print(f"✅ Customers endpoint: {len(customers)} customers available")
    except Exception as e:
        print(f"❌ Customers endpoint error: {e}")
    
    # Test 4: Check billing configuration
    try:
        response = requests.get(f"{BASE_URL}/api/billing/config")
        config = response.json()
        print(f"✅ Billing config endpoint: {config.get('currency', 'N/A')} currency")
    except Exception as e:
        print(f"❌ Billing config endpoint error: {e}")
    
    # Test 5: Check if mobile billing HTML is accessible
    try:
        response = requests.get(f"{BASE_URL}/app")
        if response.status_code == 200:
            print("✅ Main app page is accessible")
        else:
            print(f"❌ Main app page error: {response.status_code}")
    except Exception as e:
        print(f"❌ Main app page error: {e}")
    
    print("\n" + "=" * 50)
    print("Mobile Billing Local Test Complete")
    print("\nTo test the mobile billing interface:")
    print("1. Open http://localhost:5000/app in your browser")
    print("2. Navigate to the billing section")
    print("3. Look for mobile billing options")

if __name__ == "__main__":
    test_mobile_billing_endpoints()

