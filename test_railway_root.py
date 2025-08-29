#!/usr/bin/env python3
"""
Test Railway app root and basic endpoints
"""

import requests

def test_railway_root():
    """Test Railway app root URL"""
    try:
        print("🔍 TESTING RAILWAY ROOT")
        print("=" * 50)
        
        # Test root URL
        response = requests.get("https://tajir-pos-production.up.railway.app/", timeout=10)
        print(f"Root URL: {response.status_code}")
        if response.status_code == 200:
            print("✅ Root URL working!")
            print(f"Content: {response.text[:200]}...")
        else:
            print(f"❌ Root URL failed: {response.status_code}")
        
        # Test app URL
        response = requests.get("https://tajir-pos-production.up.railway.app/app", timeout=10)
        print(f"App URL: {response.status_code}")
        if response.status_code == 200:
            print("✅ App URL working!")
        else:
            print(f"❌ App URL failed: {response.status_code}")
        
        # Test API endpoints with different paths
        api_endpoints = [
            "/api/customers",
            "/api/loyalty/customers", 
            "/api/loyalty/config",
            "/api/products"
        ]
        
        for endpoint in api_endpoints:
            try:
                response = requests.get(f"https://tajir-pos-production.up.railway.app{endpoint}", timeout=10)
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
        
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_railway_root()

