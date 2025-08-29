#!/usr/bin/env python3
"""
Simple Railway test to see what's actually happening
"""

import requests

def test_railway():
    """Simple test of Railway app"""
    base_url = "https://tajir-pos-production.up.railway.app"
    
    print("🔍 SIMPLE RAILWAY TEST")
    print("=" * 40)
    
    # Test basic endpoints
    endpoints = [
        "/",
        "/api",
        "/api/",
        "/api/loyalty",
        "/api/loyalty/",
        "/api/loyalty/tiers",
        "/api/products",
        "/api/customers"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n🔍 Testing: {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=15)
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   JSON Response: {str(data)[:100]}...")
                except:
                    print(f"   Text Response: {response.text[:100]}...")
            elif response.status_code == 404:
                print(f"   Not Found")
            elif response.status_code == 500:
                print(f"   Server Error")
            else:
                print(f"   Other Status")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 CONNECTION ERROR")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")

if __name__ == "__main__":
    test_railway()

