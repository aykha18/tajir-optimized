#!/usr/bin/env python3
"""
Check shop settings directly from database for user_id 35
"""

import psycopg2
import os
from dotenv import load_dotenv

def check_user_35_direct():
    print("🔍 Checking Shop Settings for User ID 35 (Direct Database Query)")
    
    # Load environment variables
    load_dotenv()
    
    # Database connection parameters
    db_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'tajir_pos',
        'user': 'postgres',
        'password': 'aykha123'
    }
    
    try:
        # Connect to database
        print("\n🔌 Connecting to database...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        print("   ✅ Database connected successfully")
        
        # Query shop settings for user_id 35
        print("\n📋 Querying shop settings for user_id 35...")
        cursor.execute("""
            SELECT user_id, shop_name, enable_trial_date, enable_delivery_date, 
                   enable_advance_payment, enable_customer_notes, enable_employee_assignment,
                   use_dynamic_invoice_template, default_trial_days, default_delivery_days,
                   currency_code, timezone, created_at, updated_at
            FROM shop_settings 
            WHERE user_id = 35
        """)
        
        result = cursor.fetchone()
        
        if result:
            print("   ✅ Found shop settings for user_id 35")
            print("\n📊 Shop Settings for User ID 35:")
            print("   📝 user_id:", result[0])
            print("   📝 shop_name:", result[1])
            print("   📝 currency_code:", result[10])
            print("   📝 timezone:", result[11])
            print("   📝 created_at:", result[12])
            print("   📝 updated_at:", result[13])
            
            print("\n   Boolean Fields:")
            boolean_fields = [
                ("enable_trial_date", result[2]),
                ("enable_delivery_date", result[3]),
                ("enable_advance_payment", result[4]),
                ("enable_customer_notes", result[5]),
                ("enable_employee_assignment", result[6]),
                ("use_dynamic_invoice_template", result[7])
            ]
            
            for field_name, value in boolean_fields:
                status = "✅" if value else "❌"
                print(f"   {status} {field_name}: {value}")
            
            print("\n   Numeric Fields:")
            print(f"   📊 default_trial_days: {result[8]}")
            print(f"   📊 default_delivery_days: {result[9]}")
            
        else:
            print("   ❌ No shop settings found for user_id 35")
            
            # Check if user_id 35 exists in users table
            print("\n🔍 Checking if user_id 35 exists in users table...")
            cursor.execute("SELECT user_id, email, name FROM users WHERE user_id = 35")
            user_result = cursor.fetchone()
            
            if user_result:
                print(f"   ✅ User 35 exists: {user_result[2]} ({user_result[1]})")
                print("   📝 But no shop_settings record found")
            else:
                print("   ❌ User_id 35 does not exist in users table")
        
        # Also check what user_ids exist in shop_settings
        print("\n📋 All user_ids in shop_settings table:")
        cursor.execute("SELECT user_id, shop_name FROM shop_settings ORDER BY user_id")
        all_settings = cursor.fetchall()
        
        for user_id, shop_name in all_settings:
            print(f"   📝 user_id {user_id}: {shop_name}")
        
        conn.close()
        print("\n✅ Database check completed!")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_user_35_direct()
