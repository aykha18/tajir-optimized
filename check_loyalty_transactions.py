#!/usr/bin/env python3
"""
Check loyalty_transactions table structure and data
"""
import psycopg2

def check_loyalty_transactions():
    """Check loyalty_transactions table structure and data"""
    try:
        print("🔍 CHECKING LOYALTY TRANSACTIONS")
        print("=" * 50)
        
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database")
        
        # Check table structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'loyalty_transactions' 
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        print(f"📊 loyalty_transactions table structure:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        # Check data
        cursor.execute("SELECT * FROM loyalty_transactions ORDER BY created_at DESC")
        transactions = cursor.fetchall()
        
        print(f"\n📝 Found {len(transactions)} transactions:")
        for i, trans in enumerate(transactions):
            print(f"  {i+1}. {trans}")
        
        # Check points by transaction type
        cursor.execute("""
            SELECT transaction_type, SUM(points_amount) as total_points, COUNT(*) as count
            FROM loyalty_transactions 
            GROUP BY transaction_type
        """)
        summary = cursor.fetchall()
        
        print(f"\n📊 Points Summary by Type:")
        for row in summary:
            print(f"  - {row[0]}: {row[1]} points ({row[2]} transactions)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_loyalty_transactions()

