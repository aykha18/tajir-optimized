#!/usr/bin/env python3
"""
Migration script to add configurable input fields to shop_settings table
This allows shops to enable/disable certain billing fields based on their business type
"""

import sqlite3
import os
from datetime import datetime

def migrate_configurable_fields():
    """Add configurable input fields to shop_settings table"""
    
    # Database path
    db_path = 'pos_tailor.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Starting migration: Adding configurable input fields...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(shop_settings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # New columns to add
        new_columns = [
            ('enable_trial_date', 'BOOLEAN DEFAULT 1'),
            ('enable_delivery_date', 'BOOLEAN DEFAULT 1'),
            ('enable_advance_payment', 'BOOLEAN DEFAULT 1'),
            ('enable_customer_notes', 'BOOLEAN DEFAULT 1'),
            ('enable_employee_assignment', 'BOOLEAN DEFAULT 1'),
            ('default_delivery_days', 'INTEGER DEFAULT 3'),
            ('default_trial_days', 'INTEGER DEFAULT 3'),
            ('city', 'TEXT DEFAULT ""'),
            ('area', 'TEXT DEFAULT ""')
        ]
        
        # Add each column if it doesn't exist
        for column_name, column_def in new_columns:
            if column_name not in columns:
                print(f"Adding column: {column_name}")
                cursor.execute(f"ALTER TABLE shop_settings ADD COLUMN {column_name} {column_def}")
            else:
                print(f"Column {column_name} already exists, skipping...")
        
        # Commit changes
        conn.commit()
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(shop_settings)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        
        print("\nMigration completed successfully!")
        print("Updated shop_settings table columns:")
        for column in updated_columns:
            print(f"  - {column}")
        
        # Update existing records with default values
        print("\nUpdating existing shop settings with default values...")
        cursor.execute("""
            UPDATE shop_settings SET 
                enable_trial_date = 1,
                enable_delivery_date = 1,
                enable_advance_payment = 1,
                enable_customer_notes = 1,
                enable_employee_assignment = 1,
                default_delivery_days = 3,
                default_trial_days = 3,
                city = '',
                area = ''
            WHERE enable_trial_date IS NULL
        """)
        
        updated_rows = cursor.rowcount
        print(f"Updated {updated_rows} existing shop settings records")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Migration completed successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Configurable Input Fields Migration")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = migrate_configurable_fields()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("You can now configure billing fields in Shop Settings.")
    else:
        print("\n💥 Migration failed! Please check the error messages above.")
    
    print("\n" + "=" * 60)
