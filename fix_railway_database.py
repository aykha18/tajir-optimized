#!/usr/bin/env python3
"""
Fix the Railway database that the app is actually using
"""

import psycopg2

def fix_railway_database():
    """Fix the Railway database that the app is actually using"""
    try:
        print("🔧 FIXING RAILWAY DATABASE")
        print("=" * 50)
        
        # Connect to the Railway database that the app is actually using
        # Based on Railway variables: postgres-uhnv.railway.internal
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@postgres-uhnv.railway.internal:5432/tajir_pos"
        )
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database")
        
        # Check if Abdullah Al Marri exists
        cursor.execute("""
            SELECT customer_id, name FROM customers WHERE name ILIKE '%Abdullah Al Marri%'
        """)
        abdullah = cursor.fetchone()
        
        if abdullah:
            customer_id = abdullah[0]
            print(f"Found Abdullah Al Marri (ID: {customer_id})")
            
            # Get bills total
            cursor.execute("""
                SELECT COUNT(*), SUM(total_amount) FROM bills WHERE customer_id = %s
            """, (customer_id,))
            bills = cursor.fetchone()
            
            if bills and bills[1]:
                total_spent = bills[1]
                bill_count = bills[0]
                
                # Check if already in loyalty
                cursor.execute("""
                    SELECT * FROM customer_loyalty WHERE customer_id = %s
                """, (customer_id,))
                existing = cursor.fetchone()
                
                if existing:
                    print("Abdullah already in loyalty program - updating...")
                    
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
                else:
                    print("Abdullah not in loyalty program - enrolling...")
                    
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
                print(f"✅ Updated Abdullah Al Marri's data:")
                print(f"   Total Spent: AED {total_spent}")
                print(f"   Total Purchases: {bill_count}")
                print(f"   Points: {int(total_spent)}")
                print(f"   Tier: Gold")
            else:
                print("No bills found for Abdullah Al Marri")
        else:
            print("Abdullah Al Marri not found in Railway database")
        
        # Also fix other customers with bills but no loyalty
        print(f"\n🔧 FIXING OTHER CUSTOMERS")
        cursor.execute("""
            SELECT c.customer_id, c.name, COUNT(b.bill_id) as bill_count, SUM(b.total_amount) as total_spent
            FROM customers c
            LEFT JOIN bills b ON c.customer_id = b.customer_id
            LEFT JOIN customer_loyalty cl ON c.customer_id = cl.customer_id
            WHERE cl.customer_id IS NULL AND b.bill_id IS NOT NULL
            GROUP BY c.customer_id, c.name
            ORDER BY total_spent DESC
            LIMIT 5
        """)
        unenrolled_customers = cursor.fetchall()
        
        for customer in unenrolled_customers:
            customer_id = customer[0]
            name = customer[1]
            bill_count = customer[2]
            total_spent = customer[3] or 0
            
            print(f"Enrolling {name} (ID: {customer_id})")
            
            # Determine tier
            tier = 'Gold' if total_spent >= 5000 else 'Silver' if total_spent >= 1000 else 'Bronze'
            
            # Enroll customer
            cursor.execute("""
                INSERT INTO customer_loyalty (
                    user_id, customer_id, tier_level, available_points, 
                    total_points, total_purchases, total_spent, is_active
                ) VALUES (1, %s, %s, %s, %s, %s, %s, true)
            """, (customer_id, tier, int(total_spent), int(total_spent), bill_count, total_spent))
            
            print(f"   ✅ Enrolled as {tier} tier with {int(total_spent)} points")
        
        conn.commit()
        print(f"\n✅ Fixed {len(unenrolled_customers)} customers")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_railway_database()

