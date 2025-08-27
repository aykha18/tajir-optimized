#!/usr/bin/env python3
"""
Add is_active column to local customers table for soft delete
"""
import psycopg2

def add_is_active_to_local_customers():
    """Add is_active column to local customers table."""
    
    # Local PostgreSQL connection
    local_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'tajir_pos',
        'user': 'postgres',
        'password': 'aykha123'
    }
    
    print("🔧 Adding is_active column to local customers table...")
    
    try:
        # Connect to local database
        conn = psycopg2.connect(**local_config)
        cursor = conn.cursor()
        
        print("✅ Connected to local database!")
        
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
        
        print("\n🎉 is_active column added successfully to local database!")
        print("💡 Now both local and Railway databases have soft delete functionality!")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_is_active_to_local_customers()
