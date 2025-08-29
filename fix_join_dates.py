#!/usr/bin/env python3
"""
Fix join_date for existing loyalty customers
"""

import psycopg2

def fix_join_dates():
    """Fix join_date for existing loyalty customers"""
    try:
        print("🔧 FIXING JOIN DATES")
        print("=" * 50)
        
        # Connect to Railway database
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database")
        
        # Find customers with NULL join_date
        cursor.execute("""
            SELECT cl.customer_id, c.name, cl.join_date
            FROM customer_loyalty cl
            JOIN customers c ON cl.customer_id = c.customer_id
            WHERE cl.join_date IS NULL
        """)
        customers_without_join_date = cursor.fetchall()
        
        print(f"Found {len(customers_without_join_date)} customers without join_date")
        
        for customer in customers_without_join_date:
            customer_id = customer[0]
            name = customer[1]
            current_join_date = customer[2]
            
            print(f"📝 Fixing {name} (ID: {customer_id})")
            
            # Set join_date to current date
            cursor.execute("""
                UPDATE customer_loyalty 
                SET join_date = CURRENT_DATE
                WHERE customer_id = %s
            """, (customer_id,))
            
            print(f"   ✅ Set join_date to CURRENT_DATE")
        
        conn.commit()
        print(f"\n✅ Fixed join_date for {len(customers_without_join_date)} customers")
        
        # Also check for customers with join_date but no enrollment_date
        cursor.execute("""
            SELECT cl.customer_id, c.name, cl.join_date, cl.enrollment_date
            FROM customer_loyalty cl
            JOIN customers c ON cl.customer_id = c.customer_id
            WHERE cl.enrollment_date IS NULL AND cl.join_date IS NOT NULL
        """)
        customers_without_enrollment_date = cursor.fetchall()
        
        if customers_without_enrollment_date:
            print(f"\n🔄 FIXING ENROLLMENT DATES")
            print(f"Found {len(customers_without_enrollment_date)} customers without enrollment_date")
            
            for customer in customers_without_enrollment_date:
                customer_id = customer[0]
                name = customer[1]
                join_date = customer[2]
                
                print(f"📝 Fixing {name} (ID: {customer_id})")
                
                # Set enrollment_date to join_date
                cursor.execute("""
                    UPDATE customer_loyalty 
                    SET enrollment_date = join_date
                    WHERE customer_id = %s
                """, (customer_id,))
                
                print(f"   ✅ Set enrollment_date to {join_date}")
            
            conn.commit()
            print(f"✅ Fixed enrollment_date for {len(customers_without_enrollment_date)} customers")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_join_dates()

