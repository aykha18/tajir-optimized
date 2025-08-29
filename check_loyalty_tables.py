#!/usr/bin/env python3
"""
Check loyalty tables in Railway database
"""
import psycopg2

def check_loyalty_tables():
    """Check what loyalty tables exist in Railway database"""
    try:
        print("🔍 CHECKING LOYALTY TABLES")
        print("=" * 50)
        
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database")
        
        # Check for loyalty tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%loyalty%'
            ORDER BY table_name
        """)
        loyalty_tables = cursor.fetchall()
        
        print(f"Found {len(loyalty_tables)} loyalty tables:")
        for table in loyalty_tables:
            print(f"  - {table[0]}")
        
        # Check if loyalty_transactions table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'loyalty_transactions'
            )
        """)
        transactions_exists = cursor.fetchone()[0]
        
        if transactions_exists:
            print(f"\n✅ loyalty_transactions table exists")
            # Check if it has data
            cursor.execute("SELECT COUNT(*) FROM loyalty_transactions")
            count = cursor.fetchone()[0]
            print(f"   Records: {count}")
        else:
            print(f"\n❌ loyalty_transactions table does NOT exist")
            print(f"   This is why analytics show 0 points!")
        
        # Check customer_loyalty table structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'customer_loyalty' 
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        print(f"\n📊 customer_loyalty table structure:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_loyalty_tables()
