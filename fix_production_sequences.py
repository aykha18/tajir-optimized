#!/usr/bin/env python3
"""
Script to check and fix database sequences in production
This addresses the 500 error when creating bills due to sequence mismatches
"""

import os
import sys
import psycopg2
from datetime import datetime

def get_database_url():
    """Get database URL from environment"""
    # Check for Railway's DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url
    
    # Check for Railway's PG_ variables
    pg_host = os.getenv('PGHOST')
    pg_database = os.getenv('PGDATABASE')
    pg_user = os.getenv('PGUSER')
    pg_password = os.getenv('PGPASSWORD')
    pg_port = os.getenv('PGPORT', '5432')
    
    if all([pg_host, pg_database, pg_user, pg_password]):
        return f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
    
    # Check for our custom POSTGRES_ variables
    postgres_host = os.getenv('POSTGRES_HOST')
    postgres_db = os.getenv('POSTGRES_DB')
    postgres_user = os.getenv('POSTGRES_USER')
    postgres_password = os.getenv('POSTGRES_PASSWORD')
    postgres_port = os.getenv('POSTGRES_PORT', '5432')
    
    if all([postgres_host, postgres_db, postgres_user, postgres_password]):
        return f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
    
    return None

def check_and_fix_sequences():
    """Check and fix database sequences"""
    database_url = get_database_url()
    if not database_url:
        print("ERROR: No database URL found in environment variables")
        print("Available environment variables:")
        for key, value in os.environ.items():
            if 'DATABASE' in key or 'POSTGRES' in key or 'PG' in key:
                print(f"  {key}: {value[:20]}..." if len(str(value)) > 20 else f"  {key}: {value}")
        return False
    
    try:
        print(f"Connecting to database...")
        conn = psycopg2.connect(database_url)
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
        print(f"❌ Database connection error: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Production Database Sequence Fix Tool")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = check_and_fix_sequences()
    
    if success:
        print("\n🎉 Success! Database sequences have been checked and fixed.")
        print("The bill creation should now work properly.")
    else:
        print("\n💥 Failed to fix sequences. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
