#!/usr/bin/env python3
"""
Local Loyalty Tables Migration Script
This script runs the loyalty tables migration for the local database
"""

import os
import sys
import sqlite3
from dotenv import load_dotenv

def get_local_db_connection():
    """Get local SQLite connection"""
    try:
        # Use local SQLite database
        DATABASE_PATH = "pos_tailor.db"
        
        print(f"🔗 Connecting to local SQLite database...")
        print(f"   Database: {DATABASE_PATH}")
        
        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row
        
        # Test connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT sqlite_version();")
            version = cursor.fetchone()[0]
            print(f"✅ Connected successfully!")
            print(f"   SQLite version: {version}")
        
        return connection
        
    except Exception as e:
        print(f"❌ Failed to connect to local database: {e}")
        return None

def create_loyalty_tables(connection):
    """Create loyalty program tables in local SQLite"""
    try:
        cursor = connection.cursor()
        
        print("\n🎯 Creating loyalty program tables...")
        
        # 1. Add loyalty configuration to shop_settings
        print("📝 Adding loyalty configuration to shop_settings...")
        cursor.execute("""
            ALTER TABLE shop_settings 
            ADD COLUMN enable_loyalty_program BOOLEAN DEFAULT 0
        """)
        cursor.execute("""
            ALTER TABLE shop_settings 
            ADD COLUMN loyalty_program_name VARCHAR(100) DEFAULT 'Loyalty Program'
        """)
        cursor.execute("""
            ALTER TABLE shop_settings 
            ADD COLUMN loyalty_points_per_aed DECIMAL(10,2) DEFAULT 1.0
        """)
        cursor.execute("""
            ALTER TABLE shop_settings 
            ADD COLUMN loyalty_aed_per_point DECIMAL(10,2) DEFAULT 0.01
        """)
        cursor.execute("""
            ALTER TABLE shop_settings 
            ADD COLUMN min_points_redemption INTEGER DEFAULT 100
        """)
        cursor.execute("""
            ALTER TABLE shop_settings 
            ADD COLUMN max_points_redemption_percent INTEGER DEFAULT 20
        """)
        cursor.execute("""
            ALTER TABLE shop_settings 
            ADD COLUMN birthday_bonus_points INTEGER DEFAULT 50
        """)
        cursor.execute("""
            ALTER TABLE shop_settings 
            ADD COLUMN anniversary_bonus_points INTEGER DEFAULT 100
        """)
        cursor.execute("""
            ALTER TABLE shop_settings 
            ADD COLUMN referral_bonus_points INTEGER DEFAULT 200
        """)
        cursor.execute("""
            ALTER TABLE shop_settings 
            ADD COLUMN points_per_currency DECIMAL(10,2) DEFAULT 1.0
        """)
        cursor.execute("""
            ALTER TABLE shop_settings 
            ADD COLUMN min_purchase_amount DECIMAL(10,2) DEFAULT 0.0
        """)
        cursor.execute("""
            ALTER TABLE shop_settings 
            ADD COLUMN points_expiry_days INTEGER DEFAULT 365
        """)
        
        # 2. Create loyalty_config table
        print("📝 Creating loyalty_config table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loyalty_config (
                config_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                loyalty_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
            )
        """)
        
        # 4. Create loyalty_tiers table
        print("📝 Creating loyalty_tiers table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loyalty_tiers (
                tier_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                loyalty_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                transaction_type VARCHAR(20) NOT NULL,
                points_change INTEGER NOT NULL,
                bill_id INTEGER,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (loyalty_id) REFERENCES customer_loyalty(loyalty_id) ON DELETE CASCADE
            )
        """)
        
        # 6. Create loyalty_rewards table
        print("📝 Creating loyalty_rewards table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loyalty_rewards (
                reward_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                reward_name VARCHAR(100) NOT NULL,
                description TEXT,
                points_required INTEGER NOT NULL,
                discount_amount DECIMAL(10,2),
                discount_percentage DECIMAL(5,2),
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 7. Create reward_redemptions table
        print("📝 Creating reward_redemptions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reward_redemptions (
                redemption_id INTEGER PRIMARY KEY AUTOINCREMENT,
                loyalty_id INTEGER NOT NULL,
                reward_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                bill_id INTEGER,
                points_used INTEGER NOT NULL,
                discount_applied DECIMAL(10,2),
                redeemed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (loyalty_id) REFERENCES customer_loyalty(loyalty_id) ON DELETE CASCADE,
                FOREIGN KEY (reward_id) REFERENCES loyalty_rewards(reward_id) ON DELETE CASCADE
            )
        """)
        
        # 8. Create personalized_offers table
        print("📝 Creating personalized_offers table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS personalized_offers (
                offer_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
            )
        """)
        
        connection.commit()
        print("✅ All loyalty tables created successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating loyalty tables: {e}")
        connection.rollback()
        return False

def create_default_tiers(connection):
    """Create default loyalty tiers"""
    try:
        cursor = connection.cursor()
        
        print("\n🎯 Creating default loyalty tiers...")
        
        # Check if tiers already exist
        cursor.execute("SELECT COUNT(*) FROM loyalty_tiers")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print("✅ Default tiers already exist, skipping...")
            return True
        
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
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tier_id, 1, name, min_points, multiplier, discount, benefits))
        
        connection.commit()
        print("✅ Default loyalty tiers created!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating default tiers: {e}")
        connection.rollback()
        return False

def main():
    """Main migration function"""
    print("🚀 Local Loyalty Tables Migration")
    print("=" * 50)
    
    # Connect to local SQLite
    connection = get_local_db_connection()
    if not connection:
        print("❌ Cannot proceed without database connection")
        sys.exit(1)
    
    try:
        # Create loyalty tables
        if create_loyalty_tables(connection):
            # Create default tiers
            create_default_tiers(connection)
            
            print("\n🎉 Local Loyalty Tables Migration Completed Successfully!")
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
        else:
            print("❌ Migration failed!")
            sys.exit(1)
            
    finally:
        connection.close()

if __name__ == "__main__":
    main()

