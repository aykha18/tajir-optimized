#!/usr/bin/env python3
"""
Add is_active column to customers table for soft delete
"""
import psycopg2

def add_is_active_to_customers():
    """Add is_active column to customers table."""
    
    # Railway PostgreSQL connection
    railway_config = {
        'host': 'hopper.proxy.rlwy.net',
        'port': 46337,
        'database': 'tajir_pos',
        'user': 'postgres',
        'password': 'SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd'
    }
    
    print("🔧 Adding is_active column to customers table...")
    
    try:
        # Connect to Railway
        conn = psycopg2.connect(**railway_config)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway!")
        
        # Add is_active column with default value TRUE
        print("🔧 Adding is_active column...")
        cursor.execute("ALTER TABLE customers ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE")
        conn.commit()
        print("✅ Added is_active column!")
        
        # Update existing records to have is_active = TRUE
        print("🔧 Setting existing customers to active...")
        cursor.execute("UPDATE customers SET is_active = TRUE WHERE is_active IS NULL")
        conn.commit()
        print("✅ Updated existing customers!")
        
        # Verify the column was added
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'customers' AND column_name = 'is_active'
        """)
        column = cursor.fetchone()
        
        if column:
            print(f"✅ Verified is_active column: {column}")
        else:
            print("❌ is_active column not found!")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n🎉 is_active column added successfully!")
        print("💡 Now customers can use soft delete like products!")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_is_active_to_customers()
