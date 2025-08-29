#!/usr/bin/env python3
"""
Fix Railway loyalty calculation by enrolling customers and updating their data
"""

import requests
import psycopg2

def fix_railway_loyalty_calculation():
    """Fix Railway loyalty calculation"""
    try:
        print("🔧 FIXING RAILWAY LOYALTY CALCULATION")
        print("=" * 50)
        
        # Connect to Railway database
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database")
        
        # Find customers with bills but no loyalty enrollment
        cursor.execute("""
            SELECT c.customer_id, c.name, COUNT(b.bill_id) as bill_count, SUM(b.total_amount) as total_spent
            FROM customers c
            LEFT JOIN bills b ON c.customer_id = b.customer_id
            LEFT JOIN customer_loyalty cl ON c.customer_id = cl.customer_id
            WHERE cl.customer_id IS NULL AND b.bill_id IS NOT NULL
            GROUP BY c.customer_id, c.name
            ORDER BY total_spent DESC
            LIMIT 10
        """)
        unenrolled_customers = cursor.fetchall()
        
        print(f"Found {len(unenrolled_customers)} customers with bills but no loyalty enrollment")
        
        for customer in unenrolled_customers:
            customer_id = customer[0]
            name = customer[1]
            bill_count = customer[2]
            total_spent = customer[3] or 0
            
            print(f"\n📝 Processing {name} (ID: {customer_id})")
            print(f"   Bills: {bill_count}, Total Spent: AED {total_spent}")
            
            # Determine tier
            tier = 'Gold' if total_spent >= 5000 else 'Silver' if total_spent >= 1000 else 'Bronze'
            
            # Enroll customer in loyalty
            cursor.execute("""
                INSERT INTO customer_loyalty (
                    user_id, customer_id, tier_level, available_points, 
                    total_points, total_purchases, total_spent, is_active
                ) VALUES (1, %s, %s, %s, %s, %s, %s, true)
            """, (customer_id, tier, int(total_spent), int(total_spent), bill_count, total_spent))
            
            print(f"   ✅ Enrolled as {tier} tier with {int(total_spent)} points")
        
        # Also update existing loyalty customers with correct data
        print(f"\n🔄 UPDATING EXISTING LOYALTY CUSTOMERS")
        cursor.execute("""
            SELECT cl.customer_id, c.name, cl.total_spent as current_total
            FROM customer_loyalty cl
            JOIN customers c ON cl.customer_id = c.customer_id
            WHERE cl.total_spent = 0 OR cl.total_spent IS NULL
        """)
        zero_spent_customers = cursor.fetchall()
        
        print(f"Found {len(zero_spent_customers)} loyalty customers with 0 total spent")
        
        for customer in zero_spent_customers:
            customer_id = customer[0]
            name = customer[1]
            current_total = customer[2]
            
            print(f"\n📝 Updating {name} (ID: {customer_id})")
            
            # Get actual bills total
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
                
                print(f"   ✅ Updated: AED {total_spent}, {bill_count} bills, {int(total_spent)} points")
            else:
                print(f"   ⚠️ No bills found")
        
        conn.commit()
        print(f"\n✅ Fixed {len(unenrolled_customers)} new enrollments and {len(zero_spent_customers)} updates")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_railway_after_fix():
    """Test Railway API after fix"""
    try:
        print(f"\n🧪 TESTING RAILWAY AFTER FIX")
        print("=" * 50)
        
        response = requests.get("https://tajir.up.railway.app/api/loyalty/customers", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                customers = data.get('customers', [])
                
                # Show customers with non-zero total spent
                non_zero_customers = [c for c in customers if c.get('total_spent') and c.get('total_spent') > 0]
                print(f"✅ Found {len(non_zero_customers)} customers with spending data")
                
                for i, customer in enumerate(non_zero_customers[:5]):
                    print(f"   {i+1}. {customer.get('name')}: AED {customer.get('total_spent')} - {customer.get('available_points')} points - {customer.get('tier_level')}")
                
                # Check specific customers
                for customer in customers:
                    if 'Abdullah Al Falasi' in customer.get('name', ''):
                        print(f"\n✅ Abdullah Al Falasi:")
                        print(f"   Total Spent: {customer.get('total_spent')}")
                        print(f"   Available Points: {customer.get('available_points')}")
                        print(f"   Tier Level: {customer.get('tier_level')}")
                        break
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Failed: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_railway_loyalty_calculation()
    test_railway_after_fix()

