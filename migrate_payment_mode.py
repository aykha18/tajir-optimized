#!/usr/bin/env python3
"""
Migration script to add payment_mode column to shop_settings table
This script should be run on existing databases that don't have the payment_mode column
"""

import sqlite3
import os

def migrate_payment_mode():
    """Add payment_mode column to shop_settings table if it doesn't exist"""
    
    # Database file path
    db_path = 'pos_tailor.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found. Skipping migration.")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if payment_mode column already exists
        cursor.execute("PRAGMA table_info(shop_settings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'payment_mode' not in columns:
            print("Adding payment_mode column to shop_settings table...")
            
            # Add the payment_mode column
            cursor.execute("""
                ALTER TABLE shop_settings 
                ADD COLUMN payment_mode TEXT DEFAULT 'advance' 
                CHECK (payment_mode IN ('advance', 'full'))
            """)
            
            # Update existing records to have 'advance' as default
            cursor.execute("""
                UPDATE shop_settings 
                SET payment_mode = 'advance' 
                WHERE payment_mode IS NULL
            """)
            
            conn.commit()
            print("✅ Migration completed successfully!")
            print("   - Added payment_mode column to shop_settings table")
            print("   - Set default value to 'advance' for existing records")
            
        else:
            print("✅ payment_mode column already exists in shop_settings table. No migration needed.")
        
        # Verify the migration
        cursor.execute("PRAGMA table_info(shop_settings)")
        columns = cursor.fetchall()
        payment_mode_col = None
        
        for col in columns:
            if col[1] == 'payment_mode':
                payment_mode_col = col
                break
        
        if payment_mode_col:
            print(f"✅ Verified: payment_mode column exists with type: {payment_mode_col[2]}")
            print(f"   Default value: {payment_mode_col[4]}")
            print(f"   Constraint: {payment_mode_col[5]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔄 Starting payment_mode migration...")
    migrate_payment_mode()
    print("🏁 Migration process completed.")
