#!/usr/bin/env python3
"""
Update Railway database schema to add missing columns
"""

import psycopg2
import sys
from datetime import datetime

def update_railway_schema():
    """Add missing columns to Railway database."""
    
    print("🚀 Updating Railway Database Schema")
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
        
        # Check current shop_settings table structure
        print(f"\n🔍 Checking current shop_settings table structure...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'shop_settings'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print(f"Current columns in shop_settings:")
        for col_name, data_type, nullable, default in columns:
            print(f"  - {col_name}: {data_type}, nullable={nullable}, default={default}")
        
        # Add missing columns
        print(f"\n🔧 Adding missing columns to shop_settings...")
        
        missing_columns = [
            ("currency_code", "VARCHAR(10) DEFAULT 'AED'"),
            ("currency_symbol", "VARCHAR(10) DEFAULT 'د.إ'"),
            ("timezone", "VARCHAR(50) DEFAULT 'Asia/Dubai'"),
            ("date_format", "VARCHAR(20) DEFAULT 'DD/MM/YYYY'"),
            ("time_format", "VARCHAR(20) DEFAULT '24h'")
        ]
        
        added_columns = 0
        for column_name, column_def in missing_columns:
            try:
                # Check if column already exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'shop_settings' AND column_name = %s
                    )
                """, (column_name,))
                
                column_exists = cursor.fetchone()[0]
                
                if not column_exists:
                    cursor.execute(f"ALTER TABLE shop_settings ADD COLUMN {column_name} {column_def}")
                    added_columns += 1
                    print(f"  ✅ Added column: {column_name}")
                else:
                    print(f"  ✅ Column already exists: {column_name}")
                    
            except Exception as e:
                print(f"  ❌ Failed to add column {column_name}: {e}")
        
        # Remove global unique constraints on users table if they exist
        print(f"\n🔧 Checking users table constraints...")
        
        cursor.execute("""
            SELECT conname, contype, pg_get_constraintdef(oid) as definition
            FROM pg_constraint 
            WHERE conrelid = 'users'::regclass
            AND contype = 'u'
        """)
        
        constraints = cursor.fetchall()
        print(f"Current unique constraints on users table:")
        for conname, contype, definition in constraints:
            print(f"  - {conname}: {definition}")
        
        # Remove problematic global unique constraints
        removed_constraints = 0
        for conname, contype, definition in constraints:
            if 'email' in str(definition) or 'mobile' in str(definition):
                try:
                    cursor.execute(f"ALTER TABLE users DROP CONSTRAINT IF EXISTS {conname}")
                    removed_constraints += 1
                    print(f"  ✅ Removed constraint: {conname}")
                except Exception as e:
                    print(f"  ❌ Failed to remove constraint {conname}: {e}")
        
        # Commit all changes
        conn.commit()
        print(f"\n✅ Schema update completed successfully!")
        print(f"  ✅ Added {added_columns} new columns")
        print(f"  ✅ Removed {removed_constraints} problematic constraints")
        
        # Verify the changes
        print(f"\n🔍 Verifying updated schema...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'shop_settings'
            ORDER BY ordinal_position
        """)
        
        updated_columns = cursor.fetchall()
        print(f"Updated columns in shop_settings:")
        for col_name, data_type, nullable, default in updated_columns:
            print(f"  - {col_name}: {data_type}, nullable={nullable}, default={default}")
        
        conn.close()
        
        print(f"\n🎉 Railway database schema updated successfully!")
        print(f"\n📋 Next steps:")
        print(f"  1. Run: python fix_railway_shop_settings.py")
        print(f"  2. Run: python fix_railway_sequences.py")
        print(f"  3. Test your Railway deployment")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)

if __name__ == "__main__":
    update_railway_schema()
