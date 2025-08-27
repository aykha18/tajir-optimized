#!/usr/bin/env python3
"""
Railway-specific script to fix database sequences
This script is designed to run directly on Railway to fix sequence issues
"""

import os
import psycopg2
from datetime import datetime

def get_railway_db_connection():
    """Get database connection using Railway environment variables"""
    try:
        # Try DATABASE_URL first
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            return psycopg2.connect(database_url)
        
        # Fallback to individual PostgreSQL variables
        host = os.getenv('POSTGRES_HOST')
        database = os.getenv('POSTGRES_DB')
        user = os.getenv('POSTGRES_USER')
        password = os.getenv('POSTGRES_PASSWORD')
        port = os.getenv('POSTGRES_PORT', '5432')
        
        if all([host, database, user, password]):
            return psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                port=port
            )
        
        raise Exception("No database connection details found")
        
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def fix_sequences():
    """Fix database sequences"""
    print("🔧 Railway Database Sequence Fix Tool")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    conn = get_railway_db_connection()
    if not conn:
        print("❌ Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Tables and their ID columns that need sequence fixing
        tables_to_check = [
            ('bills', 'bill_id'),
            ('bill_items', 'item_id'),
            ('customers', 'customer_id'),
            ('employees', 'employee_id'),
            ('products', 'product_id'),
            ('product_types', 'type_id'),
            ('expenses', 'expense_id'),
            ('expense_categories', 'category_id'),
            ('vat_rates', 'vat_id'),
            ('user_plans', 'plan_id'),
            ('shop_settings', 'setting_id'),
            ('users', 'user_id'),
            ('otp_codes', 'id'),
            ('error_logs', 'id'),
            ('user_actions', 'action_id')
        ]
        
        print(f"\nChecking and fixing sequences for {len(tables_to_check)} tables...")
        print("=" * 60)
        
        for table_name, id_column in tables_to_check:
            try:
                # Check if table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    )
                """, (table_name,))
                
                if not cursor.fetchone()[0]:
                    print(f"⚠️  Table '{table_name}' does not exist, skipping...")
                    continue
                
                # Get current sequence value
                cursor.execute(f"""
                    SELECT last_value, is_called 
                    FROM {table_name}_{id_column}_seq
                """)
                sequence_info = cursor.fetchone()
                
                if not sequence_info:
                    print(f"⚠️  Sequence for '{table_name}.{id_column}' not found, skipping...")
                    continue
                
                current_seq_value = sequence_info[0]
                
                # Get max ID from table
                cursor.execute(f"SELECT COALESCE(MAX({id_column}), 0) FROM {table_name}")
                max_id = cursor.fetchone()[0]
                
                print(f"📊 {table_name}.{id_column}:")
                print(f"   Current sequence value: {current_seq_value}")
                print(f"   Max ID in table: {max_id}")
                
                if current_seq_value <= max_id:
                    # Fix sequence
                    new_seq_value = max_id + 1
                    cursor.execute(f"""
                        SELECT setval('{table_name}_{id_column}_seq', %s, false)
                    """, (new_seq_value,))
                    
                    print(f"   🔧 Fixed sequence to: {new_seq_value}")
                else:
                    print(f"   ✅ Sequence is correct")
                
                conn.commit()
                
            except Exception as e:
                print(f"❌ Error checking {table_name}.{id_column}: {e}")
                conn.rollback()
        
        print("\n" + "=" * 60)
        print("✅ Sequence check and fix completed!")
        
        # Test bill creation by checking if we can get a new bill_id
        print("\n🧪 Testing bill ID generation...")
        cursor.execute("SELECT nextval('bills_bill_id_seq')")
        test_bill_id = cursor.fetchone()[0]
        print(f"   Generated test bill_id: {test_bill_id}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error during sequence fixing: {e}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    success = fix_sequences()
    if success:
        print("\n🎉 Success! Database sequences have been fixed.")
        print("The bill creation should now work properly.")
    else:
        print("\n💥 Failed to fix sequences.")
        exit(1)
