#!/usr/bin/env python3
"""
Test PostgreSQL Connection using DATABASE_URL
"""

import os
import psycopg2
from urllib.parse import urlparse

def test_database_url():
    """Test PostgreSQL connection using DATABASE_URL"""
    
    print("=== Testing DATABASE_URL Connection ===")
    
    # Get DATABASE_URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print(f"DATABASE_URL: {database_url}")
    
    try:
        # Parse the URL to show the components
        parsed = urlparse(database_url)
        print(f"Host: {parsed.hostname}")
        print(f"Port: {parsed.port}")
        print(f"Database: {parsed.path[1:]}")  # Remove leading slash
        print(f"User: {parsed.username}")
        print(f"Password: {'*' * len(parsed.password)}")
        
        # Try connection using DATABASE_URL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connection successful!")
        print(f"PostgreSQL version: {version[0]}")
        
        # Test if database is empty
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
        table_count = cursor.fetchone()[0]
        print(f"Number of tables in database: {table_count}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_database_url()
