#!/usr/bin/env python3
"""
Debug PostgreSQL Connection on Railway
"""

import os
import sys

def debug_connection():
    """Debug PostgreSQL connection issues"""
    
    print("=== Railway PostgreSQL Connection Debug ===")
    print()
    
    # Check all environment variables
    print("All environment variables containing 'PG' or 'POSTGRES':")
    for key, value in os.environ.items():
        if 'PG' in key.upper() or 'POSTGRES' in key.upper():
            if 'PASSWORD' in key.upper():
                print(f"  {key}: {'*' * len(value)}")
            else:
                print(f"  {key}: {value}")
    
    print()
    print("=== Connection Test ===")
    
    # Try to import psycopg2
    try:
        import psycopg2
        print("✅ psycopg2 imported successfully")
    except ImportError as e:
        print(f"❌ psycopg2 import failed: {e}")
        return
    
    # Test different connection configurations
    configs = [
        {
            'name': 'DATABASE_URL (Railway standard)',
            'config': None,  # Special case for DATABASE_URL
            'database_url': os.getenv('DATABASE_URL')
        },
        {
            'name': 'Railway PG_ variables',
            'config': {
                'host': os.getenv('PGHOST'),
                'port': os.getenv('PGPORT'),
                'database': os.getenv('PGDATABASE'),
                'user': os.getenv('PGUSER'),
                'password': os.getenv('PGPASSWORD')
            }
        },
        {
            'name': 'Custom POSTGRES_ variables',
            'config': {
                'host': os.getenv('POSTGRES_HOST'),
                'port': os.getenv('POSTGRES_PORT'),
                'database': os.getenv('POSTGRES_DB'),
                'user': os.getenv('POSTGRES_USER'),
                'password': os.getenv('POSTGRES_PASSWORD')
            }
        },
        {
            'name': 'Combined (PG_ first, then POSTGRES_)',
            'config': {
                'host': os.getenv('PGHOST') or os.getenv('POSTGRES_HOST'),
                'port': os.getenv('PGPORT') or os.getenv('POSTGRES_PORT'),
                'database': os.getenv('PGDATABASE') or os.getenv('POSTGRES_DB'),
                'user': os.getenv('PGUSER') or os.getenv('POSTGRES_USER'),
                'password': os.getenv('PGPASSWORD') or os.getenv('POSTGRES_PASSWORD')
            }
        }
    ]
    
    for config_info in configs:
        print(f"\n--- Testing {config_info['name']} ---")
        
        if config_info['name'] == 'DATABASE_URL (Railway standard)':
            database_url = config_info['database_url']
            if not database_url:
                print("❌ DATABASE_URL not found")
                continue
            
            print(f"DATABASE_URL: {database_url}")
            
            # Try connection using DATABASE_URL
            try:
                conn = psycopg2.connect(database_url)
                cursor = conn.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"✅ Connection successful!")
                print(f"PostgreSQL version: {version[0]}")
                cursor.close()
                conn.close()
                return True
            except Exception as e:
                print(f"❌ Connection failed: {e}")
        else:
            config = config_info['config']
            
            # Check if all required values are present
            missing = [k for k, v in config.items() if not v]
            if missing:
                print(f"❌ Missing values: {missing}")
                continue
            
            print(f"Host: {config['host']}")
            print(f"Port: {config['port']}")
            print(f"Database: {config['database']}")
            print(f"User: {config['user']}")
            print(f"Password: {'*' * len(config['password'])}")
            
            # Try connection
            try:
                conn = psycopg2.connect(**config)
                cursor = conn.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"✅ Connection successful!")
                print(f"PostgreSQL version: {version[0]}")
                cursor.close()
                conn.close()
                return True
            except Exception as e:
                print(f"❌ Connection failed: {e}")
    
    print("\n=== Summary ===")
    print("All connection attempts failed. Please check:")
    print("1. PostgreSQL service is properly added to Railway")
    print("2. PostgreSQL service is linked to this application")
    print("3. Environment variables are correctly set")
    return False

if __name__ == "__main__":
    debug_connection()
