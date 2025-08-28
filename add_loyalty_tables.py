#!/usr/bin/env python3
"""
Add Customer Loyalty Program Tables
This script adds comprehensive loyalty program tables to the database.
"""

import sqlite3
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

def get_db_connection():
    """Get database connection based on environment."""
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # PostgreSQL via single URL
        return psycopg2.connect(database_url)

    # Try explicit PostgreSQL variables
    pg_host = os.getenv('POSTGRES_HOST') or os.getenv('PGHOST')
    pg_port = os.getenv('POSTGRES_PORT') or os.getenv('PGPORT') or '5432'
    pg_db = os.getenv('POSTGRES_DB') or os.getenv('PGDATABASE')
    pg_user = os.getenv('POSTGRES_USER') or os.getenv('PGUSER')
    pg_password = os.getenv('POSTGRES_PASSWORD') or os.getenv('PGPASSWORD')

    if pg_host and pg_db and pg_user and pg_password:
        return psycopg2.connect(
            host=pg_host,
            port=pg_port,
            dbname=pg_db,
            user=pg_user,
            password=pg_password,
        )

    # Fallback to SQLite (local dev)
    return sqlite3.connect('pos_tailor.db')

def add_loyalty_tables():
    """Add loyalty program tables to the database."""
    
    print("🎯 Adding Customer Loyalty Program Tables...")
    
    try:
        # Load env so POSTGRES_* are available when running standalone
        load_dotenv()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if we're using PostgreSQL or SQLite
        is_postgresql = hasattr(conn, 'server_version')
        
        if is_postgresql:
            print("📊 Using PostgreSQL database")
            
            # 1. Loyalty Program Configuration Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS loyalty_config (
                    config_id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    program_name VARCHAR(255) DEFAULT 'Loyalty Program',
                    is_active BOOLEAN DEFAULT TRUE,
                    points_per_aed DECIMAL(5,2) DEFAULT 1.00,
                    aed_per_point DECIMAL(5,2) DEFAULT 0.01,
                    min_points_redemption INTEGER DEFAULT 100,
                    max_points_redemption_percent INTEGER DEFAULT 20,
                    birthday_bonus_points INTEGER DEFAULT 50,
                    anniversary_bonus_points INTEGER DEFAULT 100,
                    referral_bonus_points INTEGER DEFAULT 200,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
            
            # 2. Customer Loyalty Profiles Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customer_loyalty (
                    loyalty_id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    customer_id INTEGER NOT NULL,
                    total_points INTEGER DEFAULT 0,
                    available_points INTEGER DEFAULT 0,
                    lifetime_points INTEGER DEFAULT 0,
                    tier_level VARCHAR(20) DEFAULT 'Bronze' CHECK (tier_level IN ('Bronze', 'Silver', 'Gold', 'Platinum')),
                    tier_points_threshold INTEGER DEFAULT 0,
                    join_date DATE DEFAULT CURRENT_DATE,
                    last_purchase_date DATE,
                    total_purchases INTEGER DEFAULT 0,
                    total_spent DECIMAL(10,2) DEFAULT 0.00,
                    referral_code VARCHAR(20) UNIQUE,
                    referred_by INTEGER,
                    birthday DATE,
                    anniversary_date DATE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
                    FOREIGN KEY (referred_by) REFERENCES customer_loyalty(loyalty_id) ON DELETE SET NULL
                )
            """)
            
            # 3. Loyalty Tiers Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS loyalty_tiers (
                    tier_id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    tier_name VARCHAR(50) NOT NULL,
                    tier_level VARCHAR(20) NOT NULL CHECK (tier_level IN ('Bronze', 'Silver', 'Gold', 'Platinum')),
                    points_threshold INTEGER NOT NULL,
                    discount_percent DECIMAL(5,2) DEFAULT 0.00,
                    bonus_points_multiplier DECIMAL(3,2) DEFAULT 1.00,
                    free_delivery BOOLEAN DEFAULT FALSE,
                    priority_service BOOLEAN DEFAULT FALSE,
                    exclusive_offers BOOLEAN DEFAULT FALSE,
                    color_code VARCHAR(7) DEFAULT '#CD7F32',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    UNIQUE(user_id, tier_level)
                )
            """)
            
            # 4. Points Transactions Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS loyalty_transactions (
                    transaction_id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    loyalty_id INTEGER NOT NULL,
                    bill_id INTEGER,
                    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('earned', 'redeemed', 'expired', 'bonus', 'referral', 'birthday', 'anniversary')),
                    points_amount INTEGER NOT NULL,
                    aed_amount DECIMAL(10,2) DEFAULT 0.00,
                    description TEXT,
                    expiry_date DATE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (loyalty_id) REFERENCES customer_loyalty(loyalty_id) ON DELETE CASCADE,
                    FOREIGN KEY (bill_id) REFERENCES bills(bill_id) ON DELETE SET NULL
                )
            """)
            
            # 5. Loyalty Rewards Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS loyalty_rewards (
                    reward_id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    reward_name VARCHAR(255) NOT NULL,
                    reward_type VARCHAR(20) NOT NULL CHECK (reward_type IN ('discount', 'free_item', 'points_bonus', 'free_delivery', 'priority_service')),
                    points_cost INTEGER DEFAULT 0,
                    discount_percent DECIMAL(5,2) DEFAULT 0.00,
                    discount_amount DECIMAL(10,2) DEFAULT 0.00,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            """)
            
            # 6. Customer Rewards Redemption Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reward_redemptions (
                    redemption_id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    loyalty_id INTEGER NOT NULL,
                    reward_id INTEGER NOT NULL,
                    bill_id INTEGER,
                    points_used INTEGER NOT NULL,
                    discount_amount DECIMAL(10,2) DEFAULT 0.00,
                    redemption_date DATE DEFAULT CURRENT_DATE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (loyalty_id) REFERENCES customer_loyalty(loyalty_id) ON DELETE CASCADE,
                    FOREIGN KEY (reward_id) REFERENCES loyalty_rewards(reward_id) ON DELETE CASCADE,
                    FOREIGN KEY (bill_id) REFERENCES bills(bill_id) ON DELETE SET NULL
                )
            """)
            
            # 7. Personalized Offers Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS personalized_offers (
                    offer_id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    loyalty_id INTEGER NOT NULL,
                    offer_title VARCHAR(255) NOT NULL,
                    offer_description TEXT,
                    offer_type VARCHAR(20) NOT NULL CHECK (offer_type IN ('discount', 'points_bonus', 'free_item', 'birthday', 'anniversary', 'referral')),
                    discount_percent DECIMAL(5,2) DEFAULT 0.00,
                    points_bonus INTEGER DEFAULT 0,
                    min_purchase_amount DECIMAL(10,2) DEFAULT 0.00,
                    valid_from DATE NOT NULL,
                    valid_until DATE NOT NULL,
                    is_used BOOLEAN DEFAULT FALSE,
                    used_date DATE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (loyalty_id) REFERENCES customer_loyalty(loyalty_id) ON DELETE CASCADE
                )
            """)
            
        else:
            print("📊 Using SQLite database")
            
            # 1. Loyalty Program Configuration Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS loyalty_config (
                    config_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    program_name TEXT DEFAULT 'Loyalty Program',
                    is_active BOOLEAN DEFAULT 1,
                    points_per_aed REAL DEFAULT 1.00,
                    aed_per_point REAL DEFAULT 0.01,
                    min_points_redemption INTEGER DEFAULT 100,
                    max_points_redemption_percent INTEGER DEFAULT 20,
                    birthday_bonus_points INTEGER DEFAULT 50,
                    anniversary_bonus_points INTEGER DEFAULT 100,
                    referral_bonus_points INTEGER DEFAULT 200,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # 2. Customer Loyalty Profiles Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customer_loyalty (
                    loyalty_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    customer_id INTEGER NOT NULL,
                    total_points INTEGER DEFAULT 0,
                    available_points INTEGER DEFAULT 0,
                    lifetime_points INTEGER DEFAULT 0,
                    tier_level TEXT DEFAULT 'Bronze' CHECK (tier_level IN ('Bronze', 'Silver', 'Gold', 'Platinum')),
                    tier_points_threshold INTEGER DEFAULT 0,
                    join_date DATE DEFAULT CURRENT_DATE,
                    last_purchase_date DATE,
                    total_purchases INTEGER DEFAULT 0,
                    total_spent REAL DEFAULT 0.00,
                    referral_code TEXT UNIQUE,
                    referred_by INTEGER,
                    birthday DATE,
                    anniversary_date DATE,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                    FOREIGN KEY (referred_by) REFERENCES customer_loyalty(loyalty_id)
                )
            """)
            
            # 3. Loyalty Tiers Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS loyalty_tiers (
                    tier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    tier_name TEXT NOT NULL,
                    tier_level TEXT NOT NULL CHECK (tier_level IN ('Bronze', 'Silver', 'Gold', 'Platinum')),
                    points_threshold INTEGER NOT NULL,
                    discount_percent REAL DEFAULT 0.00,
                    bonus_points_multiplier REAL DEFAULT 1.00,
                    free_delivery BOOLEAN DEFAULT 0,
                    priority_service BOOLEAN DEFAULT 0,
                    exclusive_offers BOOLEAN DEFAULT 0,
                    color_code TEXT DEFAULT '#CD7F32',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    UNIQUE(user_id, tier_level)
                )
            """)
            
            # 4. Points Transactions Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS loyalty_transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    loyalty_id INTEGER NOT NULL,
                    bill_id INTEGER,
                    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('earned', 'redeemed', 'expired', 'bonus', 'referral', 'birthday', 'anniversary')),
                    points_amount INTEGER NOT NULL,
                    aed_amount REAL DEFAULT 0.00,
                    description TEXT,
                    expiry_date DATE,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (loyalty_id) REFERENCES customer_loyalty(loyalty_id),
                    FOREIGN KEY (bill_id) REFERENCES bills(bill_id)
                )
            """)
            
            # 5. Loyalty Rewards Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS loyalty_rewards (
                    reward_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    reward_name TEXT NOT NULL,
                    reward_type TEXT NOT NULL CHECK (reward_type IN ('discount', 'free_item', 'points_bonus', 'free_delivery', 'priority_service')),
                    points_cost INTEGER DEFAULT 0,
                    discount_percent REAL DEFAULT 0.00,
                    discount_amount REAL DEFAULT 0.00,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # 6. Customer Rewards Redemption Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reward_redemptions (
                    redemption_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    loyalty_id INTEGER NOT NULL,
                    reward_id INTEGER NOT NULL,
                    bill_id INTEGER,
                    points_used INTEGER NOT NULL,
                    discount_amount REAL DEFAULT 0.00,
                    redemption_date DATE DEFAULT CURRENT_DATE,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (loyalty_id) REFERENCES customer_loyalty(loyalty_id),
                    FOREIGN KEY (reward_id) REFERENCES loyalty_rewards(reward_id),
                    FOREIGN KEY (bill_id) REFERENCES bills(bill_id)
                )
            """)
            
            # 7. Personalized Offers Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS personalized_offers (
                    offer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    loyalty_id INTEGER NOT NULL,
                    offer_title TEXT NOT NULL,
                    offer_description TEXT,
                    offer_type TEXT NOT NULL CHECK (offer_type IN ('discount', 'points_bonus', 'free_item', 'birthday', 'anniversary', 'referral')),
                    discount_percent REAL DEFAULT 0.00,
                    points_bonus INTEGER DEFAULT 0,
                    min_purchase_amount REAL DEFAULT 0.00,
                    valid_from DATE NOT NULL,
                    valid_until DATE NOT NULL,
                    is_used BOOLEAN DEFAULT 0,
                    used_date DATE,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (loyalty_id) REFERENCES customer_loyalty(loyalty_id)
                )
            """)
        
        # Add loyalty settings to shop_settings table
        if is_postgresql:
            cursor.execute("""
                ALTER TABLE shop_settings 
                ADD COLUMN IF NOT EXISTS enable_loyalty_program BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS loyalty_program_name TEXT DEFAULT 'Loyalty Program',
                ADD COLUMN IF NOT EXISTS loyalty_points_per_aed DECIMAL(5,2) DEFAULT 1.00,
                ADD COLUMN IF NOT EXISTS loyalty_aed_per_point DECIMAL(5,2) DEFAULT 0.01
            """)
        else:
            cursor.execute("""
                ALTER TABLE shop_settings 
                ADD COLUMN enable_loyalty_program BOOLEAN DEFAULT 0
            """)
            cursor.execute("""
                ALTER TABLE shop_settings 
                ADD COLUMN loyalty_program_name TEXT DEFAULT 'Loyalty Program'
            """)
            cursor.execute("""
                ALTER TABLE shop_settings 
                ADD COLUMN loyalty_points_per_aed REAL DEFAULT 1.00
            """)
            cursor.execute("""
                ALTER TABLE shop_settings 
                ADD COLUMN loyalty_aed_per_point REAL DEFAULT 0.01
            """)
        
        conn.commit()
        print("✅ Loyalty tables created successfully!")
        
        # Insert default loyalty tiers
        print("🎯 Creating default loyalty tiers...")
        
        default_tiers = [
            ('Bronze', 0, 0.0, 1.0, False, False, False, '#CD7F32'),
            ('Silver', 1000, 5.0, 1.1, False, False, False, '#C0C0C0'),
            ('Gold', 5000, 10.0, 1.25, True, False, True, '#FFD700'),
            ('Platinum', 15000, 15.0, 1.5, True, True, True, '#E5E4E2')
        ]
        
        for tier in default_tiers:
            tier_level, threshold, discount, multiplier, free_delivery, priority, exclusive, color = tier
            if is_postgresql:
                cursor.execute(
                    """
                    INSERT INTO loyalty_tiers (
                        user_id, tier_name, tier_level, points_threshold, discount_percent,
                        bonus_points_multiplier, free_delivery, priority_service, exclusive_offers, color_code
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id, tier_level) DO NOTHING
                    """,
                    (1, tier_level, tier_level, threshold, discount, multiplier, free_delivery, priority, exclusive, color),
                )
            else:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO loyalty_tiers (
                        user_id, tier_name, tier_level, points_threshold, discount_percent,
                        bonus_points_multiplier, free_delivery, priority_service, exclusive_offers, color_code)
                    VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (tier_level, tier_level, threshold, discount, multiplier, free_delivery, priority, exclusive, color),
                )
        
        conn.commit()
        print("✅ Default loyalty tiers created!")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n🎉 Customer Loyalty Program Tables Added Successfully!")
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
        
    except Exception as e:
        print(f"❌ Error creating loyalty tables: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    add_loyalty_tables()
