#!/usr/bin/env python3
"""
Test script to investigate Total Spent issue in loyalty system
"""

import requests
import json

def test_total_spent_issue():
    """Test the total spent calculation issue"""
    
    # Test both local and Railway
    base_urls = [
        "http://localhost:5000",
        "https://tajir-pos-production.up.railway.app"
    ]
    
    for base_url in base_urls:
        print(f"\n🔍 TESTING: {base_url}")
        print("=" * 60)
        
        try:
            # 1. Test customer loyalty data
            print("\n1️⃣ Testing customer loyalty data...")
            response = requests.get(f"{base_url}/api/loyalty/customers")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    customers = data.get('customers', [])
                    print(f"   Found {len(customers)} customers")
                    
                    for customer in customers[:3]:  # Show first 3 customers
                        print(f"   Customer: {customer.get('name', 'N/A')}")
                        print(f"     Total Spent: {customer.get('total_spent', 'N/A')}")
                        print(f"     Total Points: {customer.get('total_points', 'N/A')}")
                        print(f"     Available Points: {customer.get('available_points', 'N/A')}")
                        print(f"     Total Purchases: {customer.get('total_purchases', 'N/A')}")
                else:
                    print(f"   Error: {data.get('error', 'Unknown error')}")
            else:
                print(f"   Failed: {response.status_code}")
            
            # 2. Test bills data
            print("\n2️⃣ Testing bills data...")
            response = requests.get(f"{base_url}/api/bills")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    bills = data.get('bills', [])
                    print(f"   Found {len(bills)} bills")
                    
                    # Check bills for customer 28 (from the logs)
                    customer_28_bills = [b for b in bills if b.get('customer_id') == 28]
                    print(f"   Customer 28 has {len(customer_28_bills)} bills")
                    
                    total_spent_28 = sum(float(b.get('total_amount', 0)) for b in customer_28_bills)
                    print(f"   Total spent for customer 28: AED {total_spent_28:.2f}")
                    
                    # Show recent bills
                    for bill in customer_28_bills[:3]:
                        print(f"     Bill {bill.get('bill_id')}: AED {bill.get('total_amount', 0)}")
                else:
                    print(f"   Error: {data.get('error', 'Unknown error')}")
            else:
                print(f"   Failed: {response.status_code}")
            
            # 3. Test specific customer loyalty
            print("\n3️⃣ Testing specific customer loyalty...")
            response = requests.get(f"{base_url}/api/loyalty/customers/28")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    customer = data.get('customer', {})
                    print(f"   Customer: {customer.get('name', 'N/A')}")
                    print(f"     Total Spent: {customer.get('total_spent', 'N/A')}")
                    print(f"     Total Points: {customer.get('total_points', 'N/A')}")
                    print(f"     Available Points: {customer.get('available_points', 'N/A')}")
                    print(f"     Total Purchases: {customer.get('total_purchases', 'N/A')}")
                    print(f"     Last Purchase Date: {customer.get('last_purchase_date', 'N/A')}")
                else:
                    print(f"   Error: {data.get('error', 'Unknown error')}")
            else:
                print(f"   Failed: {response.status_code}")
            
            # 4. Test bill creation (if local)
            if "localhost" in base_url:
                print("\n4️⃣ Testing bill creation...")
                bill_data = {
                    "customer_id": 28,
                    "items": [
                        {
                            "product_id": 39,
                            "quantity": 1,
                            "unit_price": 25.0,
                            "discount": 0.0
                        }
                    ],
                    "payment_mode": "cash",
                    "total_amount": 25.0
                }
                
                response = requests.post(f"{base_url}/api/bills", json=bill_data)
                print(f"   Bill creation status: {response.status_code}")
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        print(f"   Error: {error_data.get('error', 'Unknown error')}")
                    except:
                        print(f"   Error: {response.text[:100]}")
                else:
                    print("   Bill created successfully!")
            
        except Exception as e:
            print(f"   ❌ Error testing {base_url}: {e}")

def test_database_connection():
    """Test database connection to check total_spent data"""
    try:
        import psycopg2
        
        # Connect to Railway database
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        print("\n🔗 DATABASE INVESTIGATION")
        print("=" * 60)
        
        # Check customer_loyalty table
        cursor.execute("""
            SELECT customer_id, total_spent, total_purchases, last_purchase_date 
            FROM customer_loyalty 
            WHERE customer_id = 28
        """)
        loyalty_data = cursor.fetchone()
        
        if loyalty_data:
            print(f"Customer 28 Loyalty Data:")
            print(f"  Total Spent: {loyalty_data[1]}")
            print(f"  Total Purchases: {loyalty_data[2]}")
            print(f"  Last Purchase Date: {loyalty_data[3]}")
        else:
            print("Customer 28 not found in customer_loyalty")
        
        # Check bills table
        cursor.execute("""
            SELECT bill_id, customer_id, total_amount, created_at 
            FROM bills 
            WHERE customer_id = 28 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        bills = cursor.fetchall()
        
        print(f"\nCustomer 28 Bills ({len(bills)} found):")
        total_bill_amount = 0
        for bill in bills:
            print(f"  Bill {bill[0]}: AED {bill[2]} ({bill[3]})")
            total_bill_amount += float(bill[2] or 0)
        
        print(f"Total bill amount: AED {total_bill_amount:.2f}")
        
        # Check if there's a mismatch
        if loyalty_data and loyalty_data[1] != total_bill_amount:
            print(f"\n⚠️  MISMATCH DETECTED!")
            print(f"  Loyalty total_spent: {loyalty_data[1]}")
            print(f"  Actual bill total: {total_bill_amount}")
            print(f"  Difference: {total_bill_amount - (loyalty_data[1] or 0)}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    print("🔍 INVESTIGATING TOTAL SPENT ISSUE")
    print("=" * 80)
    
    # Test API endpoints
    test_total_spent_issue()
    
    # Test database directly
    test_database_connection()
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("This test will help identify why total_spent is not updating correctly.")
    print("Check the results above for any mismatches between bill amounts and loyalty data.")

