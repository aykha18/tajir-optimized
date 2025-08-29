#!/usr/bin/env python3
"""
Fix Railway database using external connection
"""

import requests
import psycopg2

def test_railway_after_fix():
    """Test Railway API after database fix"""
    try:
        print("🧪 TESTING RAILWAY AFTER FIX")
        print("=" * 50)
        
        response = requests.get("https://tajir.up.railway.app/api/loyalty/customers", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                customers = data.get('customers', [])
                
                # Find Abdullah Al Marri
                for customer in customers:
                    if 'Abdullah Al Marri' in customer.get('name', ''):
                        print(f"✅ Abdullah Al Marri:")
                        print(f"   Total Spent: {customer.get('total_spent')}")
                        print(f"   Available Points: {customer.get('available_points')}")
                        print(f"   Tier Level: {customer.get('tier_level')}")
                        return
                
                print("❌ Abdullah Al Marri not found")
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Failed: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def create_test_bill_for_abdullah():
    """Create a test bill for Abdullah to trigger loyalty update"""
    try:
        print("🧪 CREATING TEST BILL FOR ABDULLAH")
        print("=" * 50)
        
        # Create a test bill via Railway API
        bill_data = {
            "customer_id": 41,  # Abdullah Al Marri's ID
            "items": [
                {
                    "product_id": 39,
                    "quantity": 1,
                    "unit_price": 100.0,
                    "discount": 0.0
                }
            ],
            "payment_mode": "cash",
            "total_amount": 100.0
        }
        
        response = requests.post("https://tajir.up.railway.app/api/bills", json=bill_data, timeout=10)
        print(f"Bill creation status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Test bill created successfully!")
        else:
            print(f"❌ Bill creation failed: {response.text[:100]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def check_railway_database_status():
    """Check Railway database status"""
    try:
        print("🔍 CHECKING RAILWAY DATABASE STATUS")
        print("=" * 50)
        
        # Test various endpoints to see what data is available
        endpoints = [
            "/api/customers",
            "/api/loyalty/customers",
            "/api/bills"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"https://tajir.up.railway.app{endpoint}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'customers' in data:
                        customers = data['customers']
                        print(f"{endpoint}: {len(customers)} customers")
                        
                        # Show first few customers
                        for i, customer in enumerate(customers[:3]):
                            print(f"   {i+1}. {customer.get('name', 'N/A')}: AED {customer.get('total_spent', 'N/A')}")
                    elif 'bills' in data:
                        bills = data['bills']
                        print(f"{endpoint}: {len(bills)} bills")
                else:
                    print(f"{endpoint}: Failed ({response.status_code})")
            except Exception as e:
                print(f"{endpoint}: Error - {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_railway_database_status()
    create_test_bill_for_abdullah()
    test_railway_after_fix()

