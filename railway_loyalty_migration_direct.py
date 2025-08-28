#!/usr/bin/env python3
"""
Railway Loyalty Tables Migration Script
Using direct Railway PostgreSQL connection string
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

def create_loyalty_tables():
    """Create loyalty program tables in Railway PostgreSQL"""
    
    # Railway PostgreSQL connection string
    DATABASE_URL = "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
    
    try:
        print("🔗 Connecting to Railway PostgreSQL...")
        print("   Host: hopper.proxy.rlwy.net")
        print("   Port: 46337")
        print("   Database: tajir_pos")
        print("   User: postgres")
        
        connection = psycopg2.connect(DATABASE_URL)
        
        # Test connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ Connected successfully!")
            print(f"   PostgreSQL version: {version}")
        
        cursor = connection.cursor()
        
        print("\n🎯 Creating loyalty program tables...")
        
        # 1. Add loyalty configuration to shop_settings
        print("📝 Adding loyalty configuration to shop_settings...")
        cursor.execute("""
            ALTER TABLE shop_settings 
            ADD COLUMN IF NOT EXISTS enable_loyalty_program BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS loyalty_program_name VARCHAR(100) DEFAULT 'Loyalty Program',
            ADD COLUMN IF NOT EXISTS loyalty_points_per_aed DECIMAL(10,2) DEFAULT 1.0,
            ADD COLUMN IF NOT EXISTS loyalty_aed_per_point DECIMAL(10,2) DEFAULT 0.01,
            ADD COLUMN IF NOT EXISTS min_points_redemption INTEGER DEFAULT 100,
            ADD COLUMN IF NOT EXISTS max_points_redemption_percent INTEGER DEFAULT 20,
            ADD COLUMN IF NOT EXISTS birthday_bonus_points INTEGER DEFAULT 50,
            ADD COLUMN IF NOT EXISTS anniversary_bonus_points INTEGER DEFAULT 100,
            ADD COLUMN IF NOT EXISTS referral_bonus_points INTEGER DEFAULT 200,
            ADD COLUMN IF NOT EXISTS points_per_currency DECIMAL(10,2) DEFAULT 1.0,
            ADD COLUMN IF NOT EXISTS min_purchase_amount DECIMAL(10,2) DEFAULT 0.0,
            ADD COLUMN IF NOT EXISTS points_expiry_days INTEGER DEFAULT 365
        """)
        
        # 2. Create loyalty_config table
        print("📝 Creating loyalty_config table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loyalty_config (
                config_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                points_per_currency DECIMAL(10,2) DEFAULT 1.0,
                min_purchase_amount DECIMAL(10,2) DEFAULT 0.0,
                points_expiry_days INTEGER DEFAULT 365,
                referral_bonus_points INTEGER DEFAULT 100,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. Create customer_loyalty table
        print("📝 Creating customer_loyalty table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_loyalty (
                loyalty_id SERIAL PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                current_points INTEGER DEFAULT 0,
                total_points_earned INTEGER DEFAULT 0,
                total_points_redeemed INTEGER DEFAULT 0,
                tier_id INTEGER DEFAULT 1,
                referral_code VARCHAR(20) UNIQUE,
                referred_by INTEGER,
                enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # 4. Create loyalty_tiers table
        print("📝 Creating loyalty_tiers table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loyalty_tiers (
                tier_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                tier_name VARCHAR(50) NOT NULL,
                min_points INTEGER DEFAULT 0,
                point_multiplier DECIMAL(3,2) DEFAULT 1.0,
                discount_percentage DECIMAL(5,2) DEFAULT 0.0,
                benefits TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 5. Create loyalty_transactions table
        print("📝 Creating loyalty_transactions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loyalty_transactions (
                transaction_id SERIAL PRIMARY KEY,
                loyalty_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                transaction_type VARCHAR(20) NOT NULL,
                points_change INTEGER NOT NULL,
                bill_id INTEGER,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 6. Create loyalty_rewards table
        print("📝 Creating loyalty_rewards table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loyalty_rewards (
                reward_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                reward_name VARCHAR(100) NOT NULL,
                description TEXT,
                points_required INTEGER NOT NULL,
                discount_amount DECIMAL(10,2),
                discount_percentage DECIMAL(5,2),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 7. Create reward_redemptions table
        print("📝 Creating reward_redemptions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reward_redemptions (
                redemption_id SERIAL PRIMARY KEY,
                loyalty_id INTEGER NOT NULL,
                reward_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                bill_id INTEGER,
                points_used INTEGER NOT NULL,
                discount_applied DECIMAL(10,2),
                redeemed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 8. Create personalized_offers table
        print("📝 Creating personalized_offers table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS personalized_offers (
                offer_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                customer_id INTEGER,
                offer_type VARCHAR(50) NOT NULL,
                title VARCHAR(100) NOT NULL,
                description TEXT,
                discount_percentage DECIMAL(5,2),
                discount_amount DECIMAL(10,2),
                min_purchase_amount DECIMAL(10,2),
                valid_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                valid_until TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        connection.commit()
        print("✅ All loyalty tables created successfully!")
        
        # Create default tiers
        print("\n🎯 Creating default loyalty tiers...")
        
        # Check if tiers already exist
        cursor.execute("SELECT COUNT(*) FROM loyalty_tiers")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print("✅ Default tiers already exist, skipping...")
        else:
            # Create default tiers
            default_tiers = [
                (1, "Bronze", 0, 1.0, 0.0, "Basic loyalty member"),
                (2, "Silver", 1000, 1.2, 5.0, "Silver tier with 5% discount"),
                (3, "Gold", 5000, 1.5, 10.0, "Gold tier with 10% discount"),
                (4, "Platinum", 10000, 2.0, 15.0, "Platinum tier with 15% discount")
            ]
            
            for tier_id, name, min_points, multiplier, discount, benefits in default_tiers:
                cursor.execute("""
                    INSERT INTO loyalty_tiers (tier_id, user_id, tier_name, min_points, point_multiplier, discount_percentage, benefits)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (tier_id) DO NOTHING
                """, (tier_id, 1, name, min_points, multiplier, discount, benefits))
            
            connection.commit()
            print("✅ Default loyalty tiers created!")
        
        print("\n🎉 Railway Loyalty Tables Migration Completed Successfully!")
        print("\n📋 Tables Created:")
        print("   • loyalty_config - Program configuration")
        print("   • customer_loyalty - Customer loyalty profiles")
        print("   • loyalty_tiers - Tier definitions")
        print("   • loyalty_transactions - Points transactions")
        print("   • loyalty_rewards - Available rewards")
        print("   • reward_redemptions - Reward redemptions")
        print("   • personalized_offers - AI-driven offers")
        print("\n🎯 Features Available:")
        print("   • Points System with customizable rates")
        print("   • Tiered Rewards (Bronze, Silver, Gold, Platinum)")
        print("   • Personalized Offers based on purchase history")
        print("   • Referral Program with bonus points")
        print("   • Birthday & Anniversary Rewards")
        print("   • Points expiration and redemption tracking")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating loyalty tables: {e}")
        if 'connection' in locals():
            connection.rollback()
        return False
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    create_loyalty_tables()
