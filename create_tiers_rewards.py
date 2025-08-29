#!/usr/bin/env python3
"""
Create tiers and rewards in Railway database
"""
import psycopg2

def create_tiers_rewards():
    """Create tiers and rewards in Railway database"""
    try:
        print("🎯 CREATING TIERS AND REWARDS")
        print("=" * 50)
        
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database")
        
        # Check existing tiers
        cursor.execute("SELECT COUNT(*) FROM loyalty_tiers WHERE user_id = 1")
        tier_count = cursor.fetchone()[0]
        print(f"Current tiers: {tier_count}")
        
        # Check existing rewards
        cursor.execute("SELECT COUNT(*) FROM loyalty_rewards WHERE user_id = 1")
        reward_count = cursor.fetchone()[0]
        print(f"Current rewards: {reward_count}")
        
        # Create tiers if they don't exist
        if tier_count == 0:
            print("\n📊 Creating loyalty tiers...")
            
            tiers = [
                ('Bronze', 0, 1.0, 'Basic tier with standard benefits'),
                ('Silver', 1000, 1.2, 'Enhanced tier with 20% bonus points'),
                ('Gold', 5000, 1.5, 'Premium tier with 50% bonus points'),
                ('Platinum', 15000, 2.0, 'Elite tier with 100% bonus points')
            ]
            
            for tier_name, points_threshold, multiplier, description in tiers:
                cursor.execute("""
                    INSERT INTO loyalty_tiers (
                        user_id, tier_level, points_threshold, multiplier, description, is_active
                    ) VALUES (1, %s, %s, %s, %s, true)
                """, (tier_name, points_threshold, multiplier, description))
                print(f"   ✅ Created {tier_name} tier")
            
            conn.commit()
            print(f"✅ Created {len(tiers)} tiers")
        else:
            print("✅ Tiers already exist")
        
        # Create rewards if they don't exist
        if reward_count == 0:
            print("\n🎁 Creating loyalty rewards...")
            
            rewards = [
                ('Free Delivery', 'Free delivery on next order', 500, 'delivery', True),
                ('10% Discount', '10% discount on next purchase', 1000, 'discount', True),
                ('Free Product', 'Free product up to AED 50', 2000, 'product', True),
                ('VIP Service', 'Priority service and support', 5000, 'service', True),
                ('Birthday Gift', 'Special birthday gift', 100, 'gift', True)
            ]
            
            for reward_name, description, points_required, reward_type, is_active in rewards:
                cursor.execute("""
                    INSERT INTO loyalty_rewards (
                        user_id, reward_name, description, points_required, reward_type, is_active
                    ) VALUES (1, %s, %s, %s, %s, %s)
                """, (reward_name, description, points_required, reward_type, is_active))
                print(f"   ✅ Created {reward_name} reward")
            
            conn.commit()
            print(f"✅ Created {len(rewards)} rewards")
        else:
            print("✅ Rewards already exist")
        
        # Show current tiers and rewards
        print("\n📊 Current Tiers:")
        cursor.execute("SELECT tier_level, points_threshold, multiplier FROM loyalty_tiers WHERE user_id = 1 ORDER BY points_threshold")
        tiers = cursor.fetchall()
        for tier in tiers:
            print(f"   - {tier[0]}: {tier[1]} points (x{tier[2]} multiplier)")
        
        print("\n🎁 Current Rewards:")
        cursor.execute("SELECT reward_name, points_required, reward_type FROM loyalty_rewards WHERE user_id = 1 ORDER BY points_required")
        rewards = cursor.fetchall()
        for reward in rewards:
            print(f"   - {reward[0]}: {reward[1]} points ({reward[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_tiers_rewards()

