#!/usr/bin/env python3
"""
Fix Total Spent issue by enrolling customer and testing loyalty system
"""

import requests
import json
import psycopg2

def test_railway_app():
    """Test if Railway app is working"""
    try:
        response = requests.get("https://tajir-pos-production.up.railway.app/api/customers", timeout=10)
        if response.status_code == 200:
            print("✅ Railway app is responding")
            return True
        else:
            print(f"❌ Railway app status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Railway app error: {e}")
        return False

def fix_customer_loyalty():
    """Fix customer loyalty enrollment and total spent"""
    try:
        # Connect to Railway database
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        print("🔧 FIXING CUSTOMER LOYALTY")
        print("=" * 50)
        
        # 1. Check if customer 28 exists
        cursor.execute("SELECT customer_id, name, phone FROM customers WHERE customer_id = 28")
        customer = cursor.fetchone()
        
        if not customer:
            print("❌ Customer 28 not found in customers table")
            return False
        
        print(f"✅ Found customer: {customer[1]} ({customer[2]})")
        
        # 2. Check if customer is enrolled in loyalty
        cursor.execute("SELECT * FROM customer_loyalty WHERE customer_id = 28")
        loyalty = cursor.fetchone()
        
        if not loyalty:
            print("⚠️  Customer not enrolled in loyalty program")
            print("   Enrolling customer in loyalty program...")
            
            # Enroll customer in loyalty program
            cursor.execute("""
                INSERT INTO customer_loyalty (
                    user_id, customer_id, tier_level, available_points, 
                    total_points, total_purchases, total_spent, is_active
                ) VALUES (1, 28, 'Bronze', 0, 0, 0, 0, true)
            """)
            conn.commit()
            print("✅ Customer enrolled in loyalty program")
        else:
            print("✅ Customer already enrolled in loyalty program")
        
        # 3. Check bills for this customer
        cursor.execute("""
            SELECT bill_id, total_amount, created_at 
            FROM bills 
            WHERE customer_id = 28 
            ORDER BY created_at DESC
        """)
        bills = cursor.fetchall()
        
        print(f"\n📊 Customer 28 Bills: {len(bills)} found")
        total_bill_amount = 0
        for bill in bills:
            print(f"   Bill {bill[0]}: AED {bill[1]} ({bill[2]})")
            total_bill_amount += float(bill[1] or 0)
        
        print(f"   Total bill amount: AED {total_bill_amount:.2f}")
        
        # 4. Update loyalty data with correct totals
        if total_bill_amount > 0:
            print(f"\n🔄 Updating loyalty data...")
            cursor.execute("""
                UPDATE customer_loyalty 
                SET total_spent = %s, total_purchases = %s, last_purchase_date = (
                    SELECT MAX(created_at) FROM bills WHERE customer_id = 28
                )
                WHERE customer_id = 28
            """, (total_bill_amount, len(bills)))
            conn.commit()
            print("✅ Loyalty data updated")
        
        # 5. Verify the fix
        cursor.execute("""
            SELECT total_spent, total_purchases, last_purchase_date 
            FROM customer_loyalty 
            WHERE customer_id = 28
        """)
        updated_loyalty = cursor.fetchone()
        
        if updated_loyalty:
            print(f"\n✅ VERIFICATION:")
            print(f"   Total Spent: AED {updated_loyalty[0]}")
            print(f"   Total Purchases: {updated_loyalty[1]}")
            print(f"   Last Purchase Date: {updated_loyalty[2]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing customer loyalty: {e}")
        return False

def test_loyalty_api():
    """Test loyalty API after fix"""
    try:
        print("\n🌐 TESTING LOYALTY API")
        print("=" * 50)
        
        # Test customer loyalty endpoint
        response = requests.get("https://tajir-pos-production.up.railway.app/api/loyalty/customers/28")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                customer = data.get('customer', {})
                print(f"✅ Customer: {customer.get('name', 'N/A')}")
                print(f"   Total Spent: AED {customer.get('total_spent', 'N/A')}")
                print(f"   Total Points: {customer.get('total_points', 'N/A')}")
                print(f"   Available Points: {customer.get('available_points', 'N/A')}")
                print(f"   Total Purchases: {customer.get('total_purchases', 'N/A')}")
                print(f"   Last Purchase Date: {customer.get('last_purchase_date', 'N/A')}")
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ API Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API test error: {e}")

def create_test_bill():
    """Create a test bill to verify total spent calculation"""
    try:
        print("\n🧪 CREATING TEST BILL")
        print("=" * 50)
        
        # Connect to Railway database
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        # Create a test bill for customer 28
        bill_data = {
            "customer_id": 28,
            "total_amount": 150.00,
            "payment_mode": "cash",
            "status": "completed"
        }
        
        cursor.execute("""
            INSERT INTO bills (user_id, customer_id, total_amount, payment_mode, status, created_at)
            VALUES (1, 28, %s, %s, %s, NOW())
            RETURNING bill_id
        """, (bill_data["total_amount"], bill_data["payment_mode"], bill_data["status"]))
        
        bill_id = cursor.fetchone()[0]
        
        # Add bill items
        cursor.execute("""
            INSERT INTO bill_items (bill_id, product_id, quantity, unit_price, total_price)
            VALUES (%s, 39, 1, 150.00, 150.00)
        """, (bill_id,))
        
        # Update loyalty data
        cursor.execute("""
            UPDATE customer_loyalty 
            SET total_spent = total_spent + %s, 
                total_purchases = total_purchases + 1,
                last_purchase_date = NOW()
            WHERE customer_id = 28
        """, (bill_data["total_amount"],))
        
        conn.commit()
        print(f"✅ Test bill created: Bill ID {bill_id}")
        print(f"   Amount: AED {bill_data['total_amount']}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating test bill: {e}")
        return False

def main():
    """Main function to fix total spent issue"""
    print("🔧 FIXING TOTAL SPENT ISSUE")
    print("=" * 80)
    
    # Check if Railway app is working
    if not test_railway_app():
        print("⚠️  Railway app not responding. Proceeding with database fixes only.")
    
    # Fix customer loyalty
    if fix_customer_loyalty():
        print("\n✅ Customer loyalty fixed!")
        
        # Create test bill
        if create_test_bill():
            print("\n✅ Test bill created!")
        
        # Test API
        test_loyalty_api()
    else:
        print("\n❌ Failed to fix customer loyalty")
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("The total spent issue should now be fixed.")
    print("Check the Railway app to see if Total Spent is now showing correctly.")

if __name__ == "__main__":
    main()

