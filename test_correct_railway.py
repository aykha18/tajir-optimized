#!/usr/bin/env python3
"""
Test the correct Railway URL
"""

import requests

def test_correct_railway():
    """Test the correct Railway URL"""
    try:
        print("🔍 TESTING CORRECT RAILWAY URL")
        print("=" * 50)
        
        base_url = "https://tajir.up.railway.app"
        
        # Test basic endpoints
        endpoints = [
            "/api/customers",
            "/api/loyalty/customers",
            "/api/loyalty/config",
            "/api/products"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                print(f"{endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ {endpoint} working!")
                    data = response.json()
                    if 'customers' in data:
                        customers = data['customers']
                        print(f"   Found {len(customers)} customers")
                        if customers:
                            first = customers[0]
                            print(f"   First: {first.get('name', 'N/A')} - AED {first.get('total_spent', 'N/A')}")
                else:
                    print(f"❌ {endpoint} failed: {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint} error: {e}")
        
        # Test loyalty customers specifically
        print(f"\n🔍 TESTING LOYALTY CUSTOMERS")
        try:
            response = requests.get(f"{base_url}/api/loyalty/customers", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    customers = data.get('customers', [])
                    print(f"✅ Found {len(customers)} loyalty customers")
                    
                    # Show first few customers
                    for i, customer in enumerate(customers[:3]):
                        print(f"   {i+1}. {customer.get('name', 'N/A')}: AED {customer.get('total_spent', 'N/A')}, {customer.get('available_points', 'N/A')} points")
                else:
                    print(f"❌ API Error: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_correct_railway()

