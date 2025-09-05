#!/usr/bin/env python3
"""
Debug session management
"""

import requests
import json

def debug_session():
    print("🔍 Debugging Session Management")
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Step 1: Login
    print("\n🔐 Step 1: Logging in...")
    login_data = {
        "method": "email",
        "email": "tumd@tajir.com",
        "password": "demo123"
    }
    response = session.post(f"{base_url}/api/auth/login", json=login_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    
    if response.status_code == 200:
        # Check cookies
        print(f"\n🍪 Step 2: Checking cookies...")
        cookies = session.cookies.get_dict()
        print(f"   Cookies: {cookies}")
        
        # Step 3: Test shop settings API
        print(f"\n📋 Step 3: Testing shop settings API...")
        response = session.get(f"{base_url}/api/shop-settings")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            settings = response.json()
            user_id = settings['settings'].get('user_id')
            print(f"   📊 API returned user_id: {user_id}")
            
            # Step 4: Check what the database actually has
            print(f"\n🔍 Step 4: Checking database directly...")
            import psycopg2
            import psycopg2.extras
            
            db_config = {
                'host': 'localhost',
                'port': '5432',
                'database': 'tajir_pos',
                'user': 'postgres',
                'password': 'aykha123'
            }
            
            try:
                conn = psycopg2.connect(**db_config)
                cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                
                # Check user_id 35
                cursor.execute("SELECT * FROM shop_settings WHERE user_id = %s", (35,))
                settings_35 = cursor.fetchone()
                
                if settings_35:
                    print(f"   📊 Database user_id 35:")
                    boolean_fields = [
                        "enable_trial_date", "enable_delivery_date", "enable_advance_payment",
                        "enable_customer_notes", "enable_employee_assignment"
                    ]
                    for field in boolean_fields:
                        value = settings_35[field]
                        status = "✅" if value else "❌"
                        print(f"     {status} {field}: {value}")
                else:
                    print(f"   ❌ No settings found for user_id 35")
                
                # Check user_id 27
                cursor.execute("SELECT * FROM shop_settings WHERE user_id = %s", (27,))
                settings_27 = cursor.fetchone()
                
                if settings_27:
                    print(f"   📊 Database user_id 27:")
                    for field in boolean_fields:
                        value = settings_27[field]
                        status = "✅" if value else "❌"
                        print(f"     {status} {field}: {value}")
                else:
                    print(f"   ❌ No settings found for user_id 27")
                
                conn.close()
                
            except Exception as e:
                print(f"   ❌ Database error: {e}")
        
        # Step 5: Check if there's a session issue
        print(f"\n🔍 Step 5: Testing session persistence...")
        response = session.get(f"{base_url}/api/shop-settings")
        print(f"   Second API call status: {response.status_code}")
        if response.status_code == 200:
            settings2 = response.json()
            user_id2 = settings2['settings'].get('user_id')
            print(f"   📊 Second API call returned user_id: {user_id2}")
            
            if user_id != user_id2:
                print(f"   ❌ Session is not persistent!")
            else:
                print(f"   ✅ Session is persistent")

if __name__ == "__main__":
    debug_session()
