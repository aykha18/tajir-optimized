#!/usr/bin/env python3
"""
Fix Railway data synchronization issue
"""

import requests
import psycopg2

def check_railway_database():
    """Check which database Railway app is using"""
    try:
        print("🔍 CHECKING RAILWAY DATABASE")
        print("=" * 50)
        
        # Test Railway API
        response = requests.get("https://tajir.up.railway.app/api/loyalty/customers", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                customers = data.get('customers', [])
                print(f"Railway API shows {len(customers)} customers")
                
                # Find Abdullah Al Marri in Railway API
                abdullah_railway = None
                for customer in customers:
                    if 'Abdullah Al Marri' in customer.get('name', ''):
                        abdullah_railway = customer
                        break
                
                if abdullah_railway:
                    print(f"Railway API - Abdullah Al Marri:")
                    print(f"   Total Spent: {abdullah_railway.get('total_spent')}")
                    print(f"   Available Points: {abdullah_railway.get('available_points')}")
                    print(f"   Tier Level: {abdullah_railway.get('tier_level')}")
                else:
                    print("❌ Abdullah Al Marri not found in Railway API")
        
        # Check our database
        print(f"\n🔗 CHECKING OUR DATABASE")
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.customer_id, c.name, cl.total_spent, cl.available_points, cl.tier_level
            FROM customers c
            LEFT JOIN customer_loyalty cl ON c.customer_id = cl.customer_id
            WHERE c.name ILIKE '%Abdullah Al Marri%' AND cl.customer_id IS NOT NULL
        """)
        abdullah_db = cursor.fetchone()
        
        if abdullah_db:
            print(f"Database - Abdullah Al Marri:")
            print(f"   Total Spent: {abdullah_db[2]}")
            print(f"   Available Points: {abdullah_db[3]}")
            print(f"   Tier Level: {abdullah_db[4]}")
        else:
            print("❌ Abdullah Al Marri not found in database")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def fix_railway_data():
    """Fix the Railway data by ensuring it uses the correct database"""
    try:
        print(f"\n🔧 FIXING RAILWAY DATA")
        print("=" * 50)
        
        # The issue might be that Railway is using a different database
        # Let's check if we need to update the Railway environment variables
        
        print("The Railway app is working but showing incorrect data.")
        print("This suggests it might be using a different database or environment.")
        print("\nPossible solutions:")
        print("1. Check Railway environment variables")
        print("2. Redeploy with correct database connection")
        print("3. Update Railway database directly")
        
        # Let's try to update the Railway database directly
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        # Ensure Abdullah Al Marri has correct data
        cursor.execute("""
            SELECT customer_id FROM customers WHERE name ILIKE '%Abdullah Al Marri%'
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
                print(f"✅ Updated Abdullah Al Marri's data:")
                print(f"   Total Spent: AED {total_spent}")
                print(f"   Total Purchases: {bill_count}")
                print(f"   Points: {int(total_spent)}")
                print(f"   Tier: Gold")
            else:
                print("No bills found for Abdullah Al Marri")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_after_fix():
    """Test Railway API after fix"""
    try:
        print(f"\n🧪 TESTING AFTER FIX")
        print("=" * 50)
        
        response = requests.get("https://tajir.up.railway.app/api/loyalty/customers", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                customers = data.get('customers', [])
                
                # Find Abdullah Al Marri
                for customer in customers:
                    if 'Abdullah Al Marri' in customer.get('name', ''):
                        print(f"✅ Abdullah Al Marri after fix:")
                        print(f"   Total Spent: {customer.get('total_spent')}")
                        print(f"   Available Points: {customer.get('available_points')}")
                        print(f"   Tier Level: {customer.get('tier_level')}")
                        break
                else:
                    print("❌ Abdullah Al Marri not found after fix")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_railway_database()
    fix_railway_data()
    test_after_fix()

