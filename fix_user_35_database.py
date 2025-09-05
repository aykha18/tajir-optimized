#!/usr/bin/env python3
"""
Fix user_id 35 database values
"""

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os

def fix_user_35_database():
    print("🔧 Fixing User ID 35 Database Values")
    
    load_dotenv()
    
    db_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'tajir_pos',
        'user': 'postgres',
        'password': 'aykha123'
    }
    
    conn = None
    try:
        print("\n🔌 Connecting to database...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        print("   ✅ Database connected successfully")
        
        print(f"\n📋 Step 1: Checking current values for user_id 35...")
        cursor.execute("SELECT * FROM shop_settings WHERE user_id = %s", (35,))
        settings = cursor.fetchone()
        
        if settings:
            print(f"   📊 Current values for user_id 35:")
            boolean_fields = [
                "enable_trial_date", "enable_delivery_date", "enable_advance_payment",
                "enable_customer_notes", "enable_employee_assignment"
            ]
            for field in boolean_fields:
                value = settings[field]
                status = "✅" if value else "❌"
                print(f"     {status} {field}: {value}")
        
        print(f"\n🔧 Step 2: Updating user_id 35 to have correct values...")
        
        # Update the boolean fields to True
        update_query = """
        UPDATE shop_settings 
        SET enable_trial_date = %s,
            enable_delivery_date = %s,
            enable_advance_payment = %s,
            enable_customer_notes = %s,
            enable_employee_assignment = %s,
            default_trial_days = %s,
            default_delivery_days = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = %s
        """
        
        cursor.execute(update_query, (
            True,   # enable_trial_date
            True,   # enable_delivery_date
            True,   # enable_advance_payment
            True,   # enable_customer_notes
            True,   # enable_employee_assignment
            3,      # default_trial_days
            5,      # default_delivery_days
            35      # user_id
        ))
        
        conn.commit()
        print("   ✅ Database updated successfully")
        
        print(f"\n📋 Step 3: Verifying the update...")
        cursor.execute("SELECT * FROM shop_settings WHERE user_id = %s", (35,))
        updated_settings = cursor.fetchone()
        
        if updated_settings:
            print(f"   📊 Updated values for user_id 35:")
            for field in boolean_fields:
                value = updated_settings[field]
                status = "✅" if value else "❌"
                print(f"     {status} {field}: {value}")
            
            print(f"   📊 Numeric values:")
            print(f"     📝 default_trial_days: {updated_settings['default_trial_days']}")
            print(f"     📝 default_delivery_days: {updated_settings['default_delivery_days']}")
        
        print(f"\n🎉 SUCCESS: User ID 35 database values have been restored!")
        print("   ✅ All boolean fields are now True")
        print("   ✅ The frontend should now load the correct values")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_user_35_database()
