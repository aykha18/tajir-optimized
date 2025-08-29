#!/usr/bin/env python3
"""
Check loyalty tiers in Railway database
"""

import psycopg2

def check_loyalty_tiers():
    """Check loyalty tiers in Railway database"""
    try:
        print("🔍 CHECKING LOYALTY TIERS")
        print("=" * 50)
        
        # Connect to Railway database
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database")
        
        # Check loyalty_tiers table
        cursor.execute("SELECT COUNT(*) FROM loyalty_tiers")
        count = cursor.fetchone()[0]
        print(f"Records in loyalty_tiers: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM loyalty_tiers")
            tiers = cursor.fetchall()
            
            print(f"\n📊 Loyalty Tiers:")
            for tier in tiers:
                print(f"   - Tier ID: {tier[0]}, User ID: {tier[1]}, Tier Level: {tier[2]}, Points Threshold: {tier[3]}, Bonus Multiplier: {tier[4]}")
        else:
            print("❌ No loyalty tiers found")
            
            # Check table structure
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'loyalty_tiers'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            print(f"\nTable structure:")
            for col in columns:
                print(f"   - {col[0]}: {col[1]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_loyalty_tiers()

