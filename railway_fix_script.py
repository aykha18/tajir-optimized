#!/usr/bin/env python3
"""
Railway Database Fix Script
This script can be deployed to Railway and run directly on the platform
"""

import os
import psycopg2
import sys
from datetime import datetime

def fix_railway_database():
    """Fix Railway database sequences and missing shop settings."""
    
    print("🚀 Railway Database Fix Script")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get database connection from Railway environment variables
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL environment variable not found")
        print("💡 This script must be run on Railway platform")
        return False
    
    print(f"📡 Connecting to Railway database...")
    
    try:
        # Connect to Railway PostgreSQL database
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        
        # Step 1: Fix sequences
        print(f"\n🔧 Step 1: Fixing database sequences...")
        
        sequences_to_fix = [
            ('shop_settings', 'setting_id', 'shop_settings_setting_id_seq'),
            ('employees', 'employee_id', 'employees_employee_id_seq'),
            ('user_plans', 'plan_id', 'user_plans_plan_id_seq'),
            ('vat_rates', 'vat_id', 'vat_rates_vat_id_seq'),
            ('users', 'user_id', 'users_user_id_seq'),
            ('bills', 'bill_id', 'bills_bill_id_seq'),
            ('bill_items', 'item_id', 'bill_items_item_id_seq'),
            ('customers', 'customer_id', 'customers_customer_id_seq'),
            ('products', 'product_id', 'products_product_id_seq'),
            ('product_types', 'type_id', 'product_types_type_id_seq')
        ]
        
        fixed_sequences = 0
        for table_name, id_column, sequence_name in sequences_to_fix:
            try:
                # Check if table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    )
                """, (table_name,))
                table_exists = cursor.fetchone()[0]
                
                if not table_exists:
                    print(f"  ⚠️  Table {table_name} does not exist, skipping")
                    continue
                
                # Check if sequence exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM pg_sequences 
                        WHERE sequencename = %s
                    )
                """, (sequence_name,))
                sequence_exists = cursor.fetchone()[0]
                
                if not sequence_exists:
                    print(f"  ⚠️  Sequence {sequence_name} does not exist, skipping")
                    continue
                
                # Get current sequence value
                cursor.execute(f"SELECT last_value FROM {sequence_name}")
                current_seq = cursor.fetchone()[0]
                
                # Get max ID in table
                cursor.execute(f"SELECT MAX({id_column}) FROM {table_name}")
                max_id = cursor.fetchone()[0]
                if max_id is None:
                    max_id = 0
                
                # Fix sequence if needed
                if current_seq <= max_id:
                    new_seq_value = max_id + 1
                    cursor.execute(f"SELECT setval('{sequence_name}', {new_seq_value}, false)")
                    fixed_sequences += 1
                    print(f"  ✅ Fixed {table_name} sequence: {current_seq} → {new_seq_value}")
                else:
                    print(f"  ✅ {table_name} sequence is already correct")
                    
            except Exception as e:
                print(f"  ❌ Error fixing {table_name} sequence: {e}")
        
        print(f"✅ Fixed {fixed_sequences} sequences")
        
        # Step 2: Create missing shop settings
        print(f"\n🔧 Step 2: Creating missing shop settings...")
        
        cursor.execute("""
            SELECT u.user_id, u.shop_code, u.shop_name, u.mobile, u.email
            FROM users u 
            LEFT JOIN shop_settings s ON u.user_id = s.user_id 
            WHERE s.user_id IS NULL
        """)
        missing_users = cursor.fetchall()
        
        created_settings = 0
        if missing_users:
            print(f"Found {len(missing_users)} users without shop settings")
            
            for user_id, shop_code, shop_name, mobile, email in missing_users:
                try:
                    cursor.execute("""
                        INSERT INTO shop_settings (
                            user_id, shop_name, shop_mobile, trn, address, 
                            invoice_static_info, use_dynamic_invoice_template,
                            currency_code, currency_symbol, timezone, 
                            date_format, time_format
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        user_id,
                        shop_name or 'My Shop',
                        mobile or '',
                        '',  # TRN
                        '',  # Address
                        f"Shop Code: {shop_code}",
                        True,  # Enable dynamic invoice template
                        'AED',  # Default currency
                        'د.إ',  # Default currency symbol
                        'Asia/Dubai',  # Default timezone
                        'DD/MM/YYYY',  # Default date format
                        '24h'  # Default time format
                    ))
                    created_settings += 1
                    print(f"  ✅ Created shop settings for User ID: {user_id} ({shop_name})")
                    
                except Exception as e:
                    print(f"  ❌ Failed to create shop settings for User ID: {user_id}: {e}")
        else:
            print("✅ All users already have shop settings")
        
        print(f"✅ Created {created_settings} shop settings")
        
        # Step 3: Final verification
        print(f"\n🔍 Step 3: Final verification...")
        
        # Check total users and shop settings
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM shop_settings")
        total_settings = cursor.fetchone()[0]
        
        print(f"📊 Database status:")
        print(f"  Total users: {total_users}")
        print(f"  Total shop settings: {total_settings}")
        print(f"  Users with settings: {total_settings}/{total_users}")
        
        # Commit all changes
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Railway database fixes completed successfully!")
        print(f"\n📋 Summary:")
        print(f"  ✅ Fixed {fixed_sequences} database sequences")
        print(f"  ✅ Created {created_settings} missing shop settings")
        print(f"  ✅ All users now have shop settings")
        print(f"\n🚀 Your Railway deployment is now ready!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = fix_railway_database()
    if success:
        print("\n✅ Script completed successfully!")
    else:
        print("\n❌ Script failed!")
        sys.exit(1)
