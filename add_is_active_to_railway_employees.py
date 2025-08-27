#!/usr/bin/env python3
"""
Add is_active column to Railway employees table for soft delete
"""
import psycopg2
import os

def add_is_active_to_railway_employees():
    """Add is_active column to Railway employees table."""
    
    # Railway PostgreSQL connection
    railway_config = {
        'host': os.getenv('PGHOST', 'monorail.proxy.rlwy.net'),
        'port': int(os.getenv('PGPORT', '45132')),
        'database': os.getenv('PGDATABASE', 'railway'),
        'user': os.getenv('PGUSER', 'postgres'),
        'password': os.getenv('PGPASSWORD', 'SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd')
    }
    
    print("🔧 Adding is_active column to Railway employees table...")
    
    try:
        # Connect to Railway database
        conn = psycopg2.connect(**railway_config)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database!")
        
        # Check if is_active column already exists
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'employees' AND column_name = 'is_active'
        """)
        column = cursor.fetchone()
        
        if column:
            print(f"✅ is_active column already exists: {column}")
        else:
            # Add is_active column with default value TRUE
            print("🔧 Adding is_active column...")
            cursor.execute("ALTER TABLE employees ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE")
            conn.commit()
            print("✅ Added is_active column!")
            
            # Update existing records to have is_active = TRUE
            print("🔧 Setting existing employees to active...")
            cursor.execute("UPDATE employees SET is_active = TRUE WHERE is_active IS NULL")
            conn.commit()
            print("✅ Updated existing employees!")
        
        # Verify the column exists
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'employees' AND column_name = 'is_active'
        """)
        column = cursor.fetchone()
        
        if column:
            print(f"✅ Verified is_active column: {column}")
        else:
            print("❌ is_active column not found!")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n🎉 is_active column added successfully to Railway database!")
        print("💡 Now employee deletion will use soft delete!")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_is_active_to_railway_employees()
