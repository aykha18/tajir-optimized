#!/usr/bin/env python3
"""
Check the use_dynamic_invoice_template field specifically
"""

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os

def check_use_dynamic_invoice():
    print("🔍 Checking use_dynamic_invoice_template Field")
    
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
        
        print(f"\n📋 Checking user_id 35...")
        cursor.execute("SELECT * FROM shop_settings WHERE user_id = %s", (35,))
        settings = cursor.fetchone()
        
        if settings:
            print(f"   📊 All boolean fields for user_id 35:")
            boolean_fields = [
                "enable_trial_date", "enable_delivery_date", "enable_advance_payment",
                "enable_customer_notes", "enable_employee_assignment", "use_dynamic_invoice_template"
            ]
            
            for field in boolean_fields:
                value = settings[field]
                status = "✅" if value else "❌"
                print(f"     {status} {field}: {value}")
            
            # Check if use_dynamic_invoice_template is False
            if not settings['use_dynamic_invoice_template']:
                print(f"\n🔧 use_dynamic_invoice_template is False, fixing it...")
                
                cursor.execute("""
                UPDATE shop_settings 
                SET use_dynamic_invoice_template = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
                """, (True, 35))
                
                conn.commit()
                print("   ✅ Updated use_dynamic_invoice_template to True")
                
                # Verify the update
                cursor.execute("SELECT use_dynamic_invoice_template FROM shop_settings WHERE user_id = %s", (35,))
                updated_value = cursor.fetchone()
                print(f"   📊 Updated value: {updated_value['use_dynamic_invoice_template']}")
            else:
                print(f"   ✅ use_dynamic_invoice_template is already True")
        else:
            print(f"   ❌ No settings found for user_id 35")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_use_dynamic_invoice()
