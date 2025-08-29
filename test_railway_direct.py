#!/usr/bin/env python3
"""
Direct test of Railway API endpoints after schema migration
"""

import requests
import json
import time

def test_railway_endpoints():
    """Test Railway API endpoints directly"""
    base_url = "https://tajir-pos-production.up.railway.app"
    
    print("🌐 TESTING RAILWAY API ENDPOINTS")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    
    endpoints = [
        "/api/loyalty/tiers",
        "/api/loyalty/customers", 
        "/api/loyalty/analytics",
        "/api/loyalty/rewards",
        "/api/products",
        "/api/customers"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            print(f"\n🔍 Testing: {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {endpoint} - WORKING (200)")
                try:
                    data = response.json()
                    if data.get('success'):
                        print(f"   Response: Success")
                        if 'tiers' in data:
                            print(f"   Found {len(data['tiers'])} tiers")
                        elif 'customers' in data:
                            print(f"   Found {len(data['customers'])} customers")
                        elif 'products' in data:
                            print(f"   Found {len(data['products'])} products")
                    else:
                        print(f"   Response: {data.get('error', 'Unknown error')}")
                except:
                    print(f"   Response: Non-JSON response")
            elif response.status_code == 404:
                print(f"❌ {endpoint} - NOT FOUND (404)")
            elif response.status_code == 500:
                print(f"❌ {endpoint} - SERVER ERROR (500)")
            else:
                print(f"⚠️  {endpoint} - STATUS {response.status_code}")
                
            results[endpoint] = response.status_code
            
        except requests.exceptions.Timeout:
            print(f"⏰ {endpoint} - TIMEOUT")
            results[endpoint] = "timeout"
        except requests.exceptions.ConnectionError:
            print(f"🔌 {endpoint} - CONNECTION ERROR")
            results[endpoint] = "connection_error"
        except Exception as e:
            print(f"❌ {endpoint} - ERROR: {e}")
            results[endpoint] = "error"
    
    return results

def test_railway_health():
    """Test basic Railway app health"""
    try:
        print("\n🏥 TESTING RAILWAY APP HEALTH")
        print("=" * 50)
        
        # Test root endpoint
        response = requests.get("https://tajir-pos-production.up.railway.app/", timeout=10)
        if response.status_code == 200:
            print("✅ Root endpoint - WORKING")
        else:
            print(f"⚠️  Root endpoint - STATUS {response.status_code}")
        
        # Test if app is responding at all
        response = requests.get("https://tajir-pos-production.up.railway.app/api/", timeout=10)
        if response.status_code in [200, 404, 405]:
            print("✅ API base - RESPONDING")
        else:
            print(f"⚠️  API base - STATUS {response.status_code}")
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")

def main():
    """Run all tests"""
    print("🚀 RAILWAY DIRECT API TEST")
    print("=" * 60)
    
    # Test app health first
    test_railway_health()
    
    # Test specific endpoints
    results = test_railway_endpoints()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    
    working = sum(1 for status in results.values() if status == 200)
    total = len(results)
    
    print(f"Working endpoints: {working}/{total}")
    
    if working == total:
        print("🎉 ALL ENDPOINTS WORKING!")
    elif working > 0:
        print("⚠️  SOME ENDPOINTS WORKING")
    else:
        print("❌ NO ENDPOINTS WORKING")
        print("\nPossible issues:")
        print("- Railway app not deployed")
        print("- Railway app crashed")
        print("- Railway app needs restart")
        print("- Network connectivity issues")

if __name__ == "__main__":
    main()

