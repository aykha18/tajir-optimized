#!/usr/bin/env python3
"""
Check and fix database schema and loyalty data
"""

import psycopg2

def check_schema():
    """Check the actual database schema"""
    try:
        print("🔍 CHECKING DATABASE SCHEMA")
        print("=" * 50)
        
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        # Check customer_loyalty table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'customer_loyalty' 
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        print("customer_loyalty table columns:")
        for col in columns:
            print(f"   {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        # Check customers table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'customers' 
            ORDER BY ordinal_position
        """)
        customer_columns = cursor.fetchall()
        
        print("\ncustomers table columns:")
        for col in customer_columns:
            print(f"   {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Schema check error: {e}")

def check_loyalty_data():
    """Check loyalty data with correct schema"""
    try:
        print("\n🔍 CHECKING LOYALTY DATA")
        print("=" * 50)
        
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        # Join customers and loyalty tables
        cursor.execute("""
            SELECT c.customer_id, c.name, cl.total_spent, cl.available_points, cl.tier_level 
            FROM customers c
            LEFT JOIN customer_loyalty cl ON c.customer_id = cl.customer_id
            WHERE cl.customer_id IS NOT NULL
            ORDER BY cl.total_spent DESC 
            LIMIT 5
        """)
        loyalty_customers = cursor.fetchall()
        
        print(f"Top 5 Loyalty Customers:")
        for customer in loyalty_customers:
            print(f"   {customer[1]}: AED {customer[2]}, {customer[3]} points, {customer[4]} tier")
        
        # Check Abdullah specifically
        cursor.execute("""
            SELECT c.customer_id, c.name, cl.total_spent, cl.available_points, cl.tier_level
            FROM customers c
            LEFT JOIN customer_loyalty cl ON c.customer_id = cl.customer_id
            WHERE c.name ILIKE '%Abdullah%' AND cl.customer_id IS NOT NULL
        """)
        abdullah = cursor.fetchone()
        
        if abdullah:
            print(f"\n✅ Abdullah found: {abdullah[1]} - AED {abdullah[2]}, {abdullah[3]} points, {abdullah[4]} tier")
        else:
            print(f"\n❌ Abdullah not found in loyalty program")
            
            # Check if Abdullah exists in customers
            cursor.execute("""
                SELECT customer_id, name FROM customers WHERE name ILIKE '%Abdullah%'
            """)
            abdullah_customer = cursor.fetchone()
            if abdullah_customer:
                print(f"   But Abdullah exists in customers: {abdullah_customer[1]} (ID: {abdullah_customer[0]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Loyalty data check error: {e}")

def fix_abdullah_loyalty():
    """Fix Abdullah's loyalty data"""
    try:
        print("\n🔧 FIXING ABDULLAH LOYALTY")
        print("=" * 50)
        
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        # Find Abdullah in customers
        cursor.execute("""
            SELECT customer_id, name FROM customers WHERE name ILIKE '%Abdullah%'
        """)
        abdullah = cursor.fetchone()
        
        if abdullah:
            customer_id = abdullah[0]
            print(f"Found Abdullah: {abdullah[1]} (ID: {customer_id})")
            
            # Check if already in loyalty
            cursor.execute("""
                SELECT * FROM customer_loyalty WHERE customer_id = %s
            """, (customer_id,))
            existing = cursor.fetchone()
            
            if existing:
                print("Abdullah already in loyalty program")
                
                # Get bills total
                cursor.execute("""
                    SELECT COUNT(*), SUM(total_amount) FROM bills WHERE customer_id = %s
                """, (customer_id,))
                bills = cursor.fetchone()
                
                if bills and bills[1]:
                    total_spent = bills[1]
                    bill_count = bills[0]
                    
                    # Update loyalty data
                    cursor.execute("""
                        UPDATE customer_loyalty 
                        SET total_spent = %s,
                            total_purchases = %s,
                            available_points = %s,
                            total_points = %s,
                            tier_level = CASE 
                                WHEN %s >= 5000 THEN 'Gold'
                                WHEN %s >= 1000 THEN 'Silver'
                                ELSE 'Bronze'
                            END
                        WHERE customer_id = %s
                    """, (total_spent, bill_count, int(total_spent), int(total_spent), total_spent, total_spent, customer_id))
                    
                    conn.commit()
                    print(f"✅ Updated Abdullah's loyalty data:")
                    print(f"   Total Spent: AED {total_spent}")
                    print(f"   Total Purchases: {bill_count}")
                    print(f"   Points: {int(total_spent)}")
                else:
                    print("No bills found for Abdullah")
            else:
                print("Abdullah not in loyalty program - enrolling...")
                
                # Get bills total
                cursor.execute("""
                    SELECT COUNT(*), SUM(total_amount) FROM bills WHERE customer_id = %s
                """, (customer_id,))
                bills = cursor.fetchone()
                
                if bills and bills[1]:
                    total_spent = bills[1]
                    bill_count = bills[0]
                    
                    # Enroll in loyalty
                    cursor.execute("""
                        INSERT INTO customer_loyalty (
                            user_id, customer_id, tier_level, available_points, 
                            total_points, total_purchases, total_spent, is_active
                        ) VALUES (1, %s, %s, %s, %s, %s, %s, true)
                    """, (customer_id, 
                          'Gold' if total_spent >= 5000 else 'Silver' if total_spent >= 1000 else 'Bronze',
                          int(total_spent), int(total_spent), bill_count, total_spent))
                    
                    conn.commit()
                    print(f"✅ Enrolled Abdullah in loyalty program:")
                    print(f"   Total Spent: AED {total_spent}")
                    print(f"   Total Purchases: {bill_count}")
                    print(f"   Points: {int(total_spent)}")
                else:
                    print("No bills found for Abdullah")
        else:
            print("Abdullah not found in customers table")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fix error: {e}")

if __name__ == "__main__":
    check_schema()
    check_loyalty_data()
    fix_abdullah_loyalty()

