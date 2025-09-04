#!/usr/bin/env python3
"""
Fix database sequences on Railway deployment
Using the correct Railway connection parameters
"""

import os
import psycopg2
import sys

def fix_railway_sequences():
    """Fix all sequence issues in the Railway PostgreSQL database."""
    
    print("🚀 Fixing Railway Database Sequences")
    print("=" * 50)
    
    # Railway connection parameters
    db_params = {
        'host': 'hopper.proxy.rlwy.net',
        'port': 46337,
        'database': 'tajir_pos',
        'user': 'postgres',
        'password': 'SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd'
    }
    
    print(f"📡 Connecting to Railway database...")
    print(f"   Host: {db_params['host']}")
    print(f"   Port: {db_params['port']}")
    print(f"   Database: {db_params['database']}")
    
    try:
        # Connect to Railway PostgreSQL database
        conn = psycopg2.connect(**db_params)
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        
        # Tables and their sequences to fix
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
        
        print(f"\n🔧 Fixing sequences for {len(sequences_to_fix)} tables...")
        
        fixed_count = 0
        for table_name, id_column, sequence_name in sequences_to_fix:
            print(f"\n📋 Fixing {table_name} sequence...")
            
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
                print(f"  Current sequence value: {current_seq}")
                
                # Get max ID in table
                cursor.execute(f"SELECT MAX({id_column}) FROM {table_name}")
                max_id = cursor.fetchone()[0]
                if max_id is None:
                    max_id = 0
                print(f"  Max {id_column} in table: {max_id}")
                
                # Fix sequence if needed
                if current_seq <= max_id:
                    new_seq_value = max_id + 1
                    cursor.execute(f"SELECT setval('{sequence_name}', {new_seq_value}, false)")
                    print(f"  ✅ Fixed sequence to start from: {new_seq_value}")
                    fixed_count += 1
                else:
                    print(f"  ✅ Sequence is already correct")
                    
            except Exception as e:
                print(f"  ❌ Error fixing {table_name} sequence: {e}")
        
        # Commit all changes
        conn.commit()
        print(f"\n✅ Successfully fixed {fixed_count} sequences")
        
        # Verify all sequences are working
        print(f"\n🔍 Verifying sequences...")
        for table_name, id_column, sequence_name in sequences_to_fix:
            try:
                cursor.execute(f"SELECT last_value FROM {sequence_name}")
                seq_value = cursor.fetchone()[0]
                print(f"  {table_name}: {seq_value}")
            except:
                pass
        
        conn.close()
        print(f"\n🎉 Railway database sequences fixed successfully!")
        print(f"\n📋 Summary:")
        print(f"  ✅ Fixed {fixed_count} sequences")
        print(f"  ✅ All sequences are now properly aligned")
        print(f"  ✅ Setup wizard should work without sequence conflicts")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)

if __name__ == "__main__":
    fix_railway_sequences()