#!/usr/bin/env python3
"""
Check loyalty_tiers table structure
"""
import psycopg2

def check_tiers_structure():
    """Check loyalty_tiers table structure"""
    try:
        print("🔍 CHECKING LOYALTY_TIERS STRUCTURE")
        print("=" * 50)
        
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database")
        
        # Check table structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'loyalty_tiers' 
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        print(f"📊 loyalty_tiers table structure:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        # Check data
        cursor.execute("SELECT * FROM loyalty_tiers WHERE user_id = 1 ORDER BY points_threshold")
        tiers = cursor.fetchall()
        
        print(f"\n📝 Found {len(tiers)} tiers:")
        for i, tier in enumerate(tiers):
            print(f"  {i+1}. {tier}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_tiers_structure()

