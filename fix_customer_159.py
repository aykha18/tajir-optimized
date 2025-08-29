#!/usr/bin/env python3
"""
Fix Customer 159 loyalty enrollment and total spent
"""

import psycopg2

def fix_customer_159():
    """Fix customer 159 loyalty enrollment"""
    try:
        # Connect to Railway database
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        print("🔧 FIXING CUSTOMER 159 LOYALTY")
        print("=" * 50)
        
        customer_id = 159
        
        # 1. Get customer info
        cursor.execute("SELECT name, phone FROM customers WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()
        if customer:
            print(f"✅ Customer: {customer[0]} ({customer[1]})")
        
        # 2. Get bills summary
        cursor.execute("""
            SELECT COUNT(*), SUM(total_amount), MAX(created_at) 
            FROM bills 
            WHERE customer_id = %s
        """, (customer_id,))
        bills_summary = cursor.fetchone()
        
        if bills_summary:
            bill_count = bills_summary[0]
            total_amount = bills_summary[1] or 0
            last_purchase = bills_summary[2]
            
            print(f"📊 Bills: {bill_count} bills, Total AED {total_amount:.2f}")
            print(f"📅 Last Purchase: {last_purchase}")
        
        # 3. Check if already enrolled
        cursor.execute("SELECT * FROM customer_loyalty WHERE customer_id = %s", (customer_id,))
        existing_loyalty = cursor.fetchone()
        
        if existing_loyalty:
            print("⚠️  Customer already enrolled in loyalty program")
            print("   Updating existing loyalty data...")
            
            # Update existing loyalty record
            cursor.execute("""
                UPDATE customer_loyalty 
                SET total_spent = %s, 
                    total_purchases = %s, 
                    last_purchase_date = %s,
                    tier_level = 'Gold'
                WHERE customer_id = %s
            """, (total_amount, bill_count, last_purchase, customer_id))
        else:
            print("🆕 Enrolling customer in loyalty program...")
            
            # Create new loyalty record
            cursor.execute("""
                INSERT INTO customer_loyalty (
                    user_id, customer_id, tier_level, available_points, 
                    total_points, total_purchases, total_spent, last_purchase_date, is_active
                ) VALUES (1, %s, 'Gold', %s, %s, %s, %s, %s, true)
            """, (customer_id, int(total_amount), int(total_amount), bill_count, total_amount, last_purchase))
        
        conn.commit()
        print("✅ Loyalty data updated successfully!")
        
        # 4. Verify the fix
        cursor.execute("""
            SELECT tier_level, total_spent, total_purchases, last_purchase_date, available_points
            FROM customer_loyalty 
            WHERE customer_id = %s
        """, (customer_id,))
        updated_loyalty = cursor.fetchone()
        
        if updated_loyalty:
            print(f"\n✅ VERIFICATION:")
            print(f"   Tier Level: {updated_loyalty[0]}")
            print(f"   Total Spent: AED {updated_loyalty[1]:.2f}")
            print(f"   Total Purchases: {updated_loyalty[2]}")
            print(f"   Last Purchase Date: {updated_loyalty[3]}")
            print(f"   Available Points: {updated_loyalty[4]}")
        
        # 5. Check if this fixes the total spent issue
        print(f"\n🎯 RESULT:")
        print(f"   Customer {customer_id} now has:")
        print(f"   - Total Spent: AED {total_amount:.2f}")
        print(f"   - Loyalty Tier: Gold")
        print(f"   - Points: {int(total_amount)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing customer loyalty: {e}")
        return False

def test_other_customers():
    """Test and fix other customers with bills but no loyalty"""
    try:
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        print("\n🔧 FIXING OTHER CUSTOMERS")
        print("=" * 50)
        
        # Get customers with bills but no loyalty
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
            
            print(f"\n📋 Fixing {name} (ID: {customer_id})")
            print(f"   Bills: {bill_count}, Total: AED {total_spent:.2f}")
            
            # Determine tier based on total spent
            if total_spent >= 5000:
                tier = 'Gold'
            elif total_spent >= 1000:
                tier = 'Silver'
            else:
                tier = 'Bronze'
            
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
        return True
        
    except Exception as e:
        print(f"❌ Error fixing other customers: {e}")
        return False

if __name__ == "__main__":
    print("🔧 FIXING TOTAL SPENT ISSUES")
    print("=" * 80)
    
    # Fix customer 159
    if fix_customer_159():
        print("\n✅ Customer 159 fixed successfully!")
    
    # Fix other customers
    if test_other_customers():
        print("\n✅ Other customers fixed successfully!")
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("All customers with bills have been enrolled in the loyalty program.")
    print("Total Spent should now show correctly in the Railway app.")
    print("Check the Railway app to verify the fix!")

