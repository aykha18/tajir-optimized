#!/usr/bin/env python3
"""
Check loyalty configuration
"""

import requests

def check_loyalty_config():
    """Check loyalty configuration"""
    try:
        print("🔍 CHECKING LOYALTY CONFIGURATION")
        print("=" * 50)
        
        response = requests.get("https://tajir.up.railway.app/api/loyalty/config", timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Loyalty Config: {data}")
        else:
            print(f"Error: {response.text[:200]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_loyalty_config()

