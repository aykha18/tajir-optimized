#!/usr/bin/env python3
"""
Simple check of Railway bills endpoint
"""

import requests

def check_railway_bills():
    """Check Railway bills endpoint"""
    try:
        print("🔍 CHECKING RAILWAY BILLS ENDPOINT")
        print("=" * 50)
        
        # Test bills endpoint
        response = requests.get("https://tajir.up.railway.app/api/bills", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                if isinstance(data, dict):
                    if 'bills' in data:
                        bills = data['bills']
                        print(f"Found {len(bills)} bills")
                        if bills:
                            print(f"First bill: {bills[0]}")
                    else:
                        print(f"Full response: {data}")
                else:
                    print(f"Response is not a dict: {type(data)}")
                    print(f"Response content: {data[:200]}")
                    
            except Exception as e:
                print(f"JSON parsing error: {e}")
                print(f"Raw response: {response.text[:200]}")
        else:
            print(f"Error response: {response.text[:200]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def check_railway_customers():
    """Check Railway customers endpoint"""
    try:
        print(f"\n🔍 CHECKING RAILWAY CUSTOMERS ENDPOINT")
        print("=" * 50)
        
        response = requests.get("https://tajir.up.railway.app/api/customers", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'customers' in data:
                customers = data['customers']
                print(f"Found {len(customers)} customers")
                if customers:
                    print(f"First customer: {customers[0]}")
            else:
                print(f"Response: {data}")
        else:
            print(f"Error: {response.text[:200]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_railway_bills()
    check_railway_customers()

