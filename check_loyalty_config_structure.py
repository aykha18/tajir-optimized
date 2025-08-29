#!/usr/bin/env python3
"""
Check loyalty_config table structure
"""

import psycopg2

def check_loyalty_config_structure():
    """Check loyalty_config table structure"""
    try:
        print("🔍 CHECKING LOYALTY_CONFIG STRUCTURE")
        print("=" * 50)
        
        # Connect to Railway database
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database")
        
        # Check table structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'loyalty_config'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        print(f"Columns in loyalty_config:")
        for col in columns:
            print(f"   - {col[0]}: {col[1]}")
        
        # Check sample data
        cursor.execute("SELECT * FROM loyalty_config LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            print(f"\nSample record: {sample}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_loyalty_config_structure()

