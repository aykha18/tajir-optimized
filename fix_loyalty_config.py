#!/usr/bin/env python3
"""
Fix loyalty configuration in Railway database
"""

import psycopg2

def fix_loyalty_config():
    """Fix loyalty configuration in Railway database"""
    try:
        print("🔧 FIXING LOYALTY CONFIGURATION")
        print("=" * 50)
        
        # Connect to Railway database
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database")
        
        # Check if loyalty_config has data
        cursor.execute("SELECT COUNT(*) FROM loyalty_config")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("📝 Adding loyalty configuration...")
            
            # Add loyalty configuration
            cursor.execute("""
                INSERT INTO loyalty_config (
                    user_id, program_name, points_per_currency, min_purchase_amount,
                    points_expiry_days, referral_bonus_points, created_at, updated_at
                ) VALUES (1, 'Loyalty Program', 1.0, 0.0, 365, 200, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """)
            
            conn.commit()
            print("✅ Loyalty configuration added successfully")
        else:
            print(f"✅ Loyalty configuration already exists ({count} records)")
        
        # Verify the configuration
        cursor.execute("SELECT * FROM loyalty_config")
        config = cursor.fetchone()
        if config:
            print(f"\n📊 Current Loyalty Configuration:")
            print(f"   Program Name: {config[2]}")
            print(f"   Points per Currency: {config[3]}")
            print(f"   Min Purchase Amount: {config[4]}")
            print(f"   Points Expiry Days: {config[5]}")
            print(f"   Referral Bonus Points: {config[6]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_loyalty_config()

