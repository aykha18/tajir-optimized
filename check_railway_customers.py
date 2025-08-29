#!/usr/bin/env python3
"""
Check Railway customers and loyalty data
"""

import psycopg2

def check_railway_customers():
    """Check what customers exist in Railway"""
    try:
        # Connect to Railway database
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        print("🔍 CHECKING RAILWAY CUSTOMERS")
        print("=" * 50)
        
        # Check customers table
        cursor.execute("SELECT customer_id, name, phone FROM customers ORDER BY customer_id LIMIT 10")
        customers = cursor.fetchall()
        
        print(f"📋 Customers in Railway ({len(customers)} shown):")
        for customer in customers:
            print(f"   ID {customer[0]}: {customer[1]} ({customer[2]})")
        
        # Check customer_loyalty table
        cursor.execute("SELECT customer_id, tier_level, total_spent, total_purchases FROM customer_loyalty ORDER BY customer_id LIMIT 10")
        loyalty_customers = cursor.fetchall()
        
        print(f"\n🎯 Customers in Loyalty Program ({len(loyalty_customers)} found):")
        for customer in loyalty_customers:
            print(f"   ID {customer[0]}: Tier {customer[1]}, Spent AED {customer[2]}, Purchases {customer[3]}")
        
        # Check bills table
        cursor.execute("SELECT customer_id, COUNT(*), SUM(total_amount) FROM bills GROUP BY customer_id ORDER BY SUM(total_amount) DESC LIMIT 10")
        bill_summary = cursor.fetchall()
        
        print(f"\n💰 Bills Summary:")
        for summary in bill_summary:
            print(f"   Customer {summary[0]}: {summary[1]} bills, Total AED {summary[2] or 0}")
        
        # Find a customer with bills but no loyalty enrollment
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
        
        print(f"\n⚠️  Customers with bills but NOT enrolled in loyalty:")
        for customer in unenrolled_customers:
            print(f"   ID {customer[0]}: {customer[1]} - {customer[2]} bills, AED {customer[3] or 0}")
        
        conn.close()
        
        # Return the first customer with bills for testing
        if unenrolled_customers:
            return unenrolled_customers[0][0]
        elif loyalty_customers:
            return loyalty_customers[0][0]
        else:
            return None
            
    except Exception as e:
        print(f"❌ Error checking customers: {e}")
        return None

def test_customer_loyalty(customer_id):
    """Test loyalty data for a specific customer"""
    try:
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        print(f"\n🧪 TESTING CUSTOMER {customer_id}")
        print("=" * 50)
        
        # Get customer info
        cursor.execute("SELECT name, phone FROM customers WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()
        if customer:
            print(f"Customer: {customer[0]} ({customer[1]})")
        
        # Get loyalty info
        cursor.execute("SELECT tier_level, total_spent, total_purchases FROM customer_loyalty WHERE customer_id = %s", (customer_id,))
        loyalty = cursor.fetchone()
        if loyalty:
            print(f"Loyalty: Tier {loyalty[0]}, Spent AED {loyalty[1]}, Purchases {loyalty[2]}")
        else:
            print("Loyalty: Not enrolled")
        
        # Get bills info
        cursor.execute("SELECT COUNT(*), SUM(total_amount) FROM bills WHERE customer_id = %s", (customer_id,))
        bills = cursor.fetchone()
        if bills:
            print(f"Bills: {bills[0]} bills, Total AED {bills[1] or 0}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error testing customer: {e}")

if __name__ == "__main__":
    print("🔍 RAILWAY CUSTOMER ANALYSIS")
    print("=" * 80)
    
    # Check customers
    test_customer_id = check_railway_customers()
    
    if test_customer_id:
        print(f"\n🎯 Recommended test customer: {test_customer_id}")
        test_customer_loyalty(test_customer_id)
    else:
        print("\n❌ No suitable customers found for testing")
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("This analysis shows the current state of customers and loyalty data in Railway.")
    print("Use the recommended customer ID for testing the total spent functionality.")

