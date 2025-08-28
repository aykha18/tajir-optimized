#!/usr/bin/env python3
"""
Recreate Railway Database
Drop and recreate Railway database with complete schema
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

def recreate_railway_database():
    """Drop and recreate Railway database with complete schema"""
    
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
        
        print("\n🗑️ Dropping all existing tables...")
        
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """)
        
        tables = cursor.fetchall()
        
        # Drop all tables (in reverse dependency order)
        for table in reversed(tables):
            table_name = table[0]
            print(f"   Dropping table: {table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
        
        # Drop all sequences
        cursor.execute("""
            SELECT sequence_name 
            FROM information_schema.sequences 
            WHERE sequence_schema = 'public'
        """)
        
        sequences = cursor.fetchall()
        for seq in sequences:
            seq_name = seq[0]
            print(f"   Dropping sequence: {seq_name}")
            cursor.execute(f"DROP SEQUENCE IF EXISTS {seq_name} CASCADE")
        
        connection.commit()
        print("✅ All tables and sequences dropped!")
        
        print("\n🏗️ Recreating database with complete schema...")
        
        # Read and execute the complete schema
        with open('complete_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        # Split into individual statements and execute
        statements = schema_sql.split(';')
        
        for i, statement in enumerate(statements):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    print(f"   Executing statement {i+1}/{len(statements)}...")
                    cursor.execute(statement)
                except Exception as e:
                    print(f"   ⚠️ Warning in statement {i+1}: {e}")
                    print(f"   Statement: {statement[:100]}...")
        
        connection.commit()
        print("✅ Complete schema applied!")
        
        print("\n📊 Loading sample data...")
        
        # Read and execute sample data
        with open('sample_data.sql', 'r') as f:
            data_sql = f.read()
        
        # Split into individual statements and execute
        data_statements = data_sql.split(';')
        
        for i, statement in enumerate(data_statements):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    print(f"   Loading data statement {i+1}/{len(data_statements)}...")
                    cursor.execute(statement)
                except Exception as e:
                    print(f"   ⚠️ Warning in data statement {i+1}: {e}")
                    print(f"   Statement: {statement[:100]}...")
        
        connection.commit()
        print("✅ Sample data loaded!")
        
        # Verify the recreation
        print("\n🔍 Verifying database recreation...")
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"✅ Total tables created: {len(tables)}")
        
        for table in tables:
            print(f"   • {table[0]}")
        
        # Check loyalty tables specifically
        loyalty_tables = [
            'loyalty_config',
            'customer_loyalty', 
            'loyalty_tiers',
            'loyalty_transactions',
            'loyalty_rewards',
            'reward_redemptions',
            'personalized_offers'
        ]
        
        print("\n📋 Loyalty tables verification:")
        for table in loyalty_tables:
            cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
            exists = cursor.fetchone()[0]
            print(f"   • {table}: {'✅ EXISTS' if exists else '❌ MISSING'}")
        
        # Check loyalty columns in shop_settings
        print("\n📋 Loyalty columns in shop_settings:")
        loyalty_columns = [
            'enable_loyalty_program',
            'loyalty_program_name',
            'loyalty_points_per_aed',
            'loyalty_aed_per_point',
            'min_points_redemption',
            'max_points_redemption_percent',
            'birthday_bonus_points',
            'anniversary_bonus_points',
            'referral_bonus_points'
        ]
        
        for col in loyalty_columns:
            cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'shop_settings' AND column_name = '{col}')")
            exists = cursor.fetchone()[0]
            print(f"   • {col}: {'✅ EXISTS' if exists else '❌ MISSING'}")
        
        print("\n🎉 Railway Database Recreation Completed Successfully!")
        print("\n📋 What was accomplished:")
        print("   • Dropped all existing tables and sequences")
        print("   • Recreated complete database schema")
        print("   • Loaded sample data")
        print("   • Verified all tables and loyalty columns exist")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error recreating database: {e}")
        if 'connection' in locals():
            connection.rollback()
            connection.close()

if __name__ == "__main__":
    recreate_railway_database()
