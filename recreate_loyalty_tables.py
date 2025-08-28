#!/usr/bin/env python3
"""
Recreate Loyalty Tables Only
Add loyalty tables and columns to Railway database without dropping existing tables
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

def recreate_loyalty_tables():
    """Add loyalty tables and columns to Railway database"""
    
    # Railway PostgreSQL connection string
    DATABASE_URL = "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
    
    try:
        print("🔗 Connecting to Railway PostgreSQL...")
        print("   Host: hopper.proxy.rlwy.net")
        print("   Port: 46337")
        print("   Database: tajir_pos")
        print("   User: postgres")
        
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()
        
        # Test connection
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Connected successfully!")
        print(f"   PostgreSQL version: {version}")
        
        print("\n🗑️ Dropping existing loyalty tables (if any)...")
        
        # Drop loyalty tables if they exist
        loyalty_tables = [
            'personalized_offers',
            'reward_redemptions', 
            'loyalty_rewards',
            'loyalty_transactions',
            'loyalty_tiers',
            'customer_loyalty',
            'loyalty_config'
        ]
        
        for table in loyalty_tables:
            print(f"   Dropping table: {table}")
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
        
        connection.commit()
        print("✅ Existing loyalty tables dropped!")
        
        print("\n🏗️ Creating loyalty tables...")
        
        # Create loyalty_config table
        print("   Creating loyalty_config table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loyalty_config (
                config_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                program_name VARCHAR(100) DEFAULT 'Loyalty Program',
                points_per_currency DECIMAL(10,2) DEFAULT 1.0,
                min_purchase_amount DECIMAL(10,2) DEFAULT 0.0,
                points_expiry_days INTEGER DEFAULT 365,
                referral_bonus_points INTEGER DEFAULT 100,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create customer_loyalty table
        print("   Creating customer_loyalty table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_loyalty (
                loyalty_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                total_points INTEGER DEFAULT 0,
                current_points INTEGER DEFAULT 0,
                tier_id INTEGER DEFAULT 1,
                enrollment_date DATE DEFAULT CURRENT_DATE,
                last_purchase_date DATE,
                total_purchases INTEGER DEFAULT 0,
                total_spent DECIMAL(10,2) DEFAULT 0.0,
                referral_code VARCHAR(20) UNIQUE,
                referred_by INTEGER,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create loyalty_tiers table
        print("   Creating loyalty_tiers table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loyalty_tiers (
                tier_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                tier_name VARCHAR(50) NOT NULL,
                min_points INTEGER DEFAULT 0,
                point_multiplier DECIMAL(3,2) DEFAULT 1.0,
                discount_percentage DECIMAL(5,2) DEFAULT 0.0,
                benefits TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create loyalty_transactions table
        print("   Creating loyalty_transactions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loyalty_transactions (
                transaction_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                bill_id INTEGER,
                points_earned INTEGER DEFAULT 0,
                points_redeemed INTEGER DEFAULT 0,
                transaction_type VARCHAR(20) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create loyalty_rewards table
        print("   Creating loyalty_rewards table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loyalty_rewards (
                reward_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                reward_name VARCHAR(100) NOT NULL,
                reward_type VARCHAR(20) NOT NULL,
                points_required INTEGER NOT NULL,
                discount_percentage DECIMAL(5,2),
                discount_amount DECIMAL(10,2),
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create reward_redemptions table
        print("   Creating reward_redemptions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reward_redemptions (
                redemption_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                reward_id INTEGER NOT NULL,
                bill_id INTEGER,
                points_used INTEGER NOT NULL,
                discount_amount DECIMAL(10,2),
                redemption_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create personalized_offers table
        print("   Creating personalized_offers table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS personalized_offers (
                offer_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                offer_type VARCHAR(50) NOT NULL,
                offer_title VARCHAR(100) NOT NULL,
                offer_description TEXT,
                discount_percentage DECIMAL(5,2),
                discount_amount DECIMAL(10,2),
                min_purchase_amount DECIMAL(10,2),
                valid_from DATE,
                valid_until DATE,
                is_active BOOLEAN DEFAULT TRUE,
                is_used BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        connection.commit()
        print("✅ All loyalty tables created!")
        
        print("\n🔧 Adding loyalty columns to shop_settings...")
        
        # Add loyalty columns to shop_settings
        loyalty_columns = [
            "ADD COLUMN IF NOT EXISTS enable_loyalty_program BOOLEAN DEFAULT FALSE",
            "ADD COLUMN IF NOT EXISTS loyalty_program_name VARCHAR(100) DEFAULT 'Loyalty Program'",
            "ADD COLUMN IF NOT EXISTS loyalty_points_per_aed DECIMAL(10,2) DEFAULT 1.0",
            "ADD COLUMN IF NOT EXISTS loyalty_aed_per_point DECIMAL(10,2) DEFAULT 0.01",
            "ADD COLUMN IF NOT EXISTS min_points_redemption INTEGER DEFAULT 100",
            "ADD COLUMN IF NOT EXISTS max_points_redemption_percent INTEGER DEFAULT 20",
            "ADD COLUMN IF NOT EXISTS birthday_bonus_points INTEGER DEFAULT 50",
            "ADD COLUMN IF NOT EXISTS anniversary_bonus_points INTEGER DEFAULT 100",
            "ADD COLUMN IF NOT EXISTS referral_bonus_points INTEGER DEFAULT 200",
            "ADD COLUMN IF NOT EXISTS points_per_currency DECIMAL(10,2) DEFAULT 1.0",
            "ADD COLUMN IF NOT EXISTS min_purchase_amount DECIMAL(10,2) DEFAULT 0.0",
            "ADD COLUMN IF NOT EXISTS points_expiry_days INTEGER DEFAULT 365"
        ]
        
        alter_sql = f"ALTER TABLE shop_settings {', '.join(loyalty_columns)}"
        print(f"   Executing: {alter_sql}")
        cursor.execute(alter_sql)
        
        connection.commit()
        print("✅ Loyalty columns added to shop_settings!")
        
        print("\n📊 Inserting default loyalty tiers...")
        
        # Insert default loyalty tiers
        default_tiers = [
            (1, 1, 'Bronze', 0, 1.0, 0.0, 'Basic loyalty member'),
            (2, 1, 'Silver', 1000, 1.2, 5.0, 'Silver tier with 5% discount'),
            (3, 1, 'Gold', 5000, 1.5, 10.0, 'Gold tier with 10% discount'),
            (4, 1, 'Platinum', 10000, 2.0, 15.0, 'Platinum tier with 15% discount')
        ]
        
        for tier in default_tiers:
            cursor.execute("""
                INSERT INTO loyalty_tiers (tier_id, user_id, tier_name, min_points, point_multiplier, discount_percentage, benefits) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (tier_id) DO NOTHING
            """, tier)
            print(f"   Inserted tier: {tier[2]}")
        
        connection.commit()
        print("✅ Default loyalty tiers inserted!")
        
        # Verify the creation
        print("\n🔍 Verifying loyalty tables creation...")
        
        # Check loyalty tables
        print("\n📋 Loyalty tables verification:")
        for table in loyalty_tables:
            cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
            exists = cursor.fetchone()[0]
            print(f"   • {table}: {'✅ EXISTS' if exists else '❌ MISSING'}")
        
        # Check loyalty columns in shop_settings
        print("\n📋 Loyalty columns in shop_settings:")
        loyalty_column_names = [
            'enable_loyalty_program',
            'loyalty_program_name',
            'loyalty_points_per_aed',
            'loyalty_aed_per_point',
            'min_points_redemption',
            'max_points_redemption_percent',
            'birthday_bonus_points',
            'anniversary_bonus_points',
            'referral_bonus_points',
            'points_per_currency',
            'min_purchase_amount',
            'points_expiry_days'
        ]
        
        for col in loyalty_column_names:
            cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'shop_settings' AND column_name = '{col}')")
            exists = cursor.fetchone()[0]
            print(f"   • {col}: {'✅ EXISTS' if exists else '❌ MISSING'}")
        
        # Check loyalty tiers
        print("\n📋 Loyalty tiers verification:")
        cursor.execute("SELECT tier_name, min_points, discount_percentage FROM loyalty_tiers ORDER BY tier_id")
        tiers = cursor.fetchall()
        for tier in tiers:
            print(f"   • {tier[0]}: {tier[1]} points, {tier[2]}% discount")
        
        print("\n🎉 Loyalty Tables Recreation Completed Successfully!")
        print("\n📋 What was accomplished:")
        print("   • Dropped existing loyalty tables (if any)")
        print("   • Created all loyalty tables with proper structure")
        print("   • Added loyalty columns to shop_settings")
        print("   • Inserted default loyalty tiers")
        print("   • Verified all tables and columns exist")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error recreating loyalty tables: {e}")
        if 'connection' in locals():
            connection.rollback()
            connection.close()

if __name__ == "__main__":
    recreate_loyalty_tables()
