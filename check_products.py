#!/usr/bin/env python3
"""
Check products endpoint
"""

import requests

def check_products():
    """Check products endpoint"""
    try:
        print("🔍 CHECKING PRODUCTS ENDPOINT")
        print("=" * 50)
        
        response = requests.get("https://tajir.up.railway.app/api/products", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            if isinstance(data, dict):
                if 'products' in data:
                    products = data['products']
                    print(f"Found {len(products)} products")
                    if products:
                        print(f"First product: {products[0]}")
                    else:
                        print("No products in list")
                else:
                    print(f"Full response: {data}")
            else:
                print(f"Response: {data[:200]}")
        else:
            print(f"Error: {response.text[:200]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_products()

