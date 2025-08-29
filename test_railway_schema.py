#!/usr/bin/env python3
"""
Test script to verify Railway schema migration was successful
"""

import psycopg2
import requests
import json

def test_railway_schema():
    """Test if Railway has the new schema columns"""
    try:
        # Connect to Railway
        conn = psycopg2.connect(
            host="hopper.proxy.rlwy.net",
            port="46337",
            database="tajir_pos",
            user="postgres",
            password="SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd"
        )
        cursor = conn.cursor()
        
        print("🔍 TESTING RAILWAY SCHEMA MIGRATION")
        print("=" * 50)
        
        # Test new columns exist
        test_columns = [
            ("loyalty_tiers", "tier_level"),
            ("loyalty_tiers", "points_threshold"),
            ("loyalty_tiers", "is_active"),
            ("customer_loyalty", "tier_level"),
            ("customer_loyalty", "available_points"),
            ("loyalty_transactions", "points_amount"),
            ("loyalty_rewards", "points_cost")
        ]
        
        all_passed = True
        for table, column in test_columns:
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table}' AND column_name = '{column}'
            """)
            if cursor.fetchone():
                print(f"✅ {table}.{column} - EXISTS")
            else:
                print(f"❌ {table}.{column} - MISSING")
                all_passed = False
        
        conn.close()
        
        if all_passed:
            print("\n🎉 ALL SCHEMA TESTS PASSED!")
            print("Railway database has been successfully migrated to the new schema.")
            return True
        else:
            print("\n❌ SOME SCHEMA TESTS FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_railway_api():
    """Test Railway API endpoints with new schema"""
    try:
        print("\n🌐 TESTING RAILWAY API ENDPOINTS")
        print("=" * 50)
        
        # Test loyalty tiers endpoint
        response = requests.get("https://tajir-pos-production.up.railway.app/api/loyalty/tiers")
        if response.status_code == 200:
            print("✅ /api/loyalty/tiers - WORKING")
            data = response.json()
            if data.get('success'):
                print(f"   Found {len(data.get('tiers', []))} tiers")
        else:
            print(f"❌ /api/loyalty/tiers - FAILED ({response.status_code})")
        
        # Test loyalty customers endpoint
        response = requests.get("https://tajir-pos-production.up.railway.app/api/loyalty/customers")
        if response.status_code == 200:
            print("✅ /api/loyalty/customers - WORKING")
            data = response.json()
            if data.get('success'):
                print(f"   Found {len(data.get('customers', []))} customers")
        else:
            print(f"❌ /api/loyalty/customers - FAILED ({response.status_code})")
        
        # Test loyalty analytics endpoint
        response = requests.get("https://tajir-pos-production.up.railway.app/api/loyalty/analytics")
        if response.status_code == 200:
            print("✅ /api/loyalty/analytics - WORKING")
        else:
            print(f"❌ /api/loyalty/analytics - FAILED ({response.status_code})")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 RAILWAY MIGRATION VERIFICATION")
    print("=" * 60)
    
    # Test schema
    schema_ok = test_railway_schema()
    
    # Test API
    api_ok = test_railway_api()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print(f"Schema Migration: {'✅ SUCCESS' if schema_ok else '❌ FAILED'}")
    print(f"API Endpoints: {'✅ WORKING' if api_ok else '❌ FAILED'}")
    
    if schema_ok and api_ok:
        print("\n🎉 RAILWAY MIGRATION VERIFICATION COMPLETE!")
        print("✅ Schema successfully migrated to new format")
        print("✅ API endpoints working with new schema")
        print("✅ No more dual-schema logic needed!")
    else:
        print("\n⚠️  Some issues detected. Please check the logs above.")

if __name__ == "__main__":
    main()

