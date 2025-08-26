#!/usr/bin/env python3
"""
Test PostgreSQL Connection
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def test_postgresql_connection():
    """Test PostgreSQL connection with current environment variables"""
    
    # Get PostgreSQL configuration from environment variables
    pg_config = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'database': os.getenv('POSTGRES_DB', 'tajir_pos'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'password')
    }
    
    print("Testing PostgreSQL connection with:")
    print(f"Host: {pg_config['host']}")
    print(f"Port: {pg_config['port']}")
    print(f"Database: {pg_config['database']}")
    print(f"User: {pg_config['user']}")
    print(f"Password: {'*' * len(pg_config['password'])}")
    print("-" * 50)
    
    try:
        # Test connection
        conn = psycopg2.connect(**pg_config)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL connection successful!")
        print(f"PostgreSQL version: {version[0]}")
        
        # Test if database is empty
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
        table_count = cursor.fetchone()[0]
        print(f"Number of tables in database: {table_count}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

if __name__ == "__main__":
    test_postgresql_connection()
