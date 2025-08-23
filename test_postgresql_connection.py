#!/usr/bin/env python3
"""
Test PostgreSQL Connection for Tajir POS
This script tests if PostgreSQL is available and can be connected to
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_postgresql_connection():
    """Test PostgreSQL connection"""
    try:
        import psycopg2
        print("✅ psycopg2 is installed")
    except ImportError:
        print("❌ psycopg2 is not installed. Please install it with:")
        print("   pip install psycopg2-binary")
        return False
    
    # Get configuration
    config = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'database': os.getenv('POSTGRES_DB', 'tajir_pos'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'password')
    }
    
    print(f"\n🔧 PostgreSQL Configuration:")
    print(f"   Host: {config['host']}")
    print(f"   Port: {config['port']}")
    print(f"   Database: {config['database']}")
    print(f"   User: {config['user']}")
    print(f"   Password: {'*' * len(config['password'])}")
    
    # Test connection
    try:
        print(f"\n🔌 Testing connection...")
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Test a simple query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL connection successful!")
        print(f"   Version: {version[0]}")
        
        # Test if database exists and is accessible
        cursor.execute("SELECT current_database();")
        current_db = cursor.fetchone()
        print(f"   Current database: {current_db[0]}")
        
        # Test if we can create a table (permissions test)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS connection_test (
                id SERIAL PRIMARY KEY,
                test_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print(f"   Permissions: ✅ Can create tables")
        
        # Clean up test table
        cursor.execute("DROP TABLE IF EXISTS connection_test;")
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 PostgreSQL is ready for migration!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print(f"\n🔧 Troubleshooting:")
        print(f"   1. Make sure PostgreSQL is installed and running")
        print(f"   2. Check if the database '{config['database']}' exists")
        print(f"   3. Verify username and password")
        print(f"   4. Check if port {config['port']} is accessible")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_postgresql_installation():
    """Check if PostgreSQL is installed"""
    print("🔍 Checking PostgreSQL installation...")
    
    # Check if psql command is available
    import subprocess
    try:
        result = subprocess.run(['psql', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ PostgreSQL CLI found: {result.stdout.strip()}")
            return True
        else:
            print("❌ PostgreSQL CLI not found")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ PostgreSQL CLI not found in PATH")
        print("   This might mean PostgreSQL is not installed or not in PATH")
        return False

def main():
    """Main function"""
    print("🚀 PostgreSQL Connection Test for Tajir POS")
    print("=" * 50)
    
    # Check installation
    pg_installed = check_postgresql_installation()
    
    if not pg_installed:
        print(f"\n📋 Installation Status:")
        print(f"   PostgreSQL CLI: ❌ Not found")
        print(f"   Please install PostgreSQL first:")
        print(f"   - Download from: https://www.postgresql.org/download/windows/")
        print(f"   - Or follow the guide in: postgresql_installation_guide.md")
        return False
    
    # Test connection
    connection_success = test_postgresql_connection()
    
    if connection_success:
        print(f"\n🎯 Next Steps:")
        print(f"   1. Run the migration script: python migration_setup.py")
        print(f"   2. Update app.py to use PostgreSQL")
        print(f"   3. Test the application")
    else:
        print(f"\n🔧 Setup Required:")
        print(f"   1. Install PostgreSQL (see postgresql_installation_guide.md)")
        print(f"   2. Create database: CREATE DATABASE tajir_pos;")
        print(f"   3. Set environment variables in .env file")
        print(f"   4. Run this test again")
    
    return connection_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
