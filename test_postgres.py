import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

def test_connection():
    print("Testing PostgreSQL connection...")
    
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print(f"Using DATABASE_URL: {database_url[:20]}...")
    else:
        print("Using individual environment variables:")
        print(f"PGHOST: {os.getenv('PGHOST') or os.getenv('POSTGRES_HOST')}")
        print(f"PGPORT: {os.getenv('PGPORT') or os.getenv('POSTGRES_PORT')}")
        print(f"PGDATABASE: {os.getenv('PGDATABASE') or os.getenv('POSTGRES_DB')}")
        print(f"PGUSER: {os.getenv('PGUSER') or os.getenv('POSTGRES_USER')}")

    try:
        from db.connection import get_db_connection, execute_query
        
        conn = get_db_connection()
        print("✅ Connection successful!")
        
        # Test query
        print("Running test query...")
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL Version: {version['version'] if isinstance(version, dict) else version[0]}")
        
        # Test users table
        print("Checking users table...")
        cursor.execute("SELECT count(*) FROM users")
        count = cursor.fetchone()
        print(f"User count: {count['count'] if isinstance(count, dict) else count[0]}")
        
        conn.close()
        return True
        
    except ImportError as e:
        print(f"❌ ImportError: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
