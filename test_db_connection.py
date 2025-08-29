#!/usr/bin/env python3
"""
Test direct database connection to Railway PostgreSQL
"""

import psycopg2

def test_railway_db():
    """Test Railway database connection and schema"""
    try:
        # Connect using the provided connection string
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        print("🔗 TESTING RAILWAY DATABASE CONNECTION")
        print("=" * 50)
        print("✅ Connected to Railway PostgreSQL successfully!")
        
        # Test loyalty tables
        tables = ['loyalty_tiers', 'customer_loyalty', 'loyalty_transactions', 'loyalty_rewards']
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ {table}: {count} rows")
                
                # Check for new schema columns
                if table == 'loyalty_tiers':
                    cursor.execute("SELECT tier_level, points_threshold, is_active FROM loyalty_tiers LIMIT 1")
                    print(f"   ✅ New schema columns working")
                elif table == 'customer_loyalty':
                    cursor.execute("SELECT tier_level, available_points FROM customer_loyalty LIMIT 1")
                    print(f"   ✅ New schema columns working")
                    
            except Exception as e:
                print(f"❌ {table}: Error - {e}")
        
        # Test some sample data
        print("\n📊 SAMPLE DATA:")
        cursor.execute("SELECT tier_name, tier_level, points_threshold FROM loyalty_tiers LIMIT 3")
        tiers = cursor.fetchall()
        for tier in tiers:
            print(f"   Tier: {tier[0]} -> {tier[1]} (threshold: {tier[2]})")
        
        conn.close()
        print("\n🎉 Database connection and schema migration verified!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_railway_db()

