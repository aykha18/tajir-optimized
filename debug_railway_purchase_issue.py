#!/usr/bin/env python3
"""
Debug Railway purchase amount issue
"""

import requests
import psycopg2

def check_railway_bills():
    """Check bills in Railway database"""
    try:
        print("🔍 CHECKING RAILWAY BILLS")
        print("=" * 50)
        
        # Test bills endpoint
        response = requests.get("https://tajir.up.railway.app/api/bills", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'bills' in data:
                bills = data['bills']
                print(f"✅ Found {len(bills)} bills in Railway")
                
                # Show recent bills
                for i, bill in enumerate(bills[:5]):
                    print(f"   {i+1}. Bill #{bill.get('bill_id')}: AED {bill.get('total_amount')} - Customer: {bill.get('customer_name', 'N/A')}")
                
                # Check if any bills have customers
                bills_with_customers = [b for b in bills if b.get('customer_id')]
                print(f"   Bills with customers: {len(bills_with_customers)}")
                
                if bills_with_customers:
                    # Check customer loyalty for these customers
                    print(f"\n🔍 CHECKING CUSTOMER LOYALTY")
                    for bill in bills_with_customers[:3]:
                        customer_id = bill.get('customer_id')
                        customer_name = bill.get('customer_name', 'Unknown')
                        print(f"   Customer {customer_id} ({customer_name}): AED {bill.get('total_amount')}")
                        
                        # Check loyalty data
                        loyalty_response = requests.get(f"https://tajir.up.railway.app/api/loyalty/customers/{customer_id}", timeout=10)
                        if loyalty_response.status_code == 200:
                            loyalty_data = loyalty_response.json()
                            if loyalty_data.get('success'):
                                customer = loyalty_data.get('customer', {})
                                print(f"     Loyalty: AED {customer.get('total_spent')} - {customer.get('available_points')} points")
                            else:
                                print(f"     Loyalty: Not enrolled")
                        else:
                            print(f"     Loyalty: Error {loyalty_response.status_code}")
            else:
                print("❌ No bills found in response")
        else:
            print(f"❌ Bills endpoint failed: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def check_railway_customers_with_bills():
    """Check customers who have bills but show 0 total spent"""
    try:
        print(f"\n🔍 CHECKING CUSTOMERS WITH BILLS")
        print("=" * 50)
        
        # Get all customers
        response = requests.get("https://tajir.up.railway.app/api/customers", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'customers' in data:
                customers = data['customers']
                
                # Get loyalty customers
                loyalty_response = requests.get("https://tajir.up.railway.app/api/loyalty/customers", timeout=10)
                if loyalty_response.status_code == 200:
                    loyalty_data = loyalty_response.json()
                    if loyalty_data.get('success'):
                        loyalty_customers = loyalty_data.get('customers', [])
                        
                        # Find customers with 0 total spent
                        zero_spent_customers = []
                        for customer in loyalty_customers:
                            if customer.get('total_spent') == 0 or customer.get('total_spent') is None:
                                zero_spent_customers.append(customer)
                        
                        print(f"Found {len(zero_spent_customers)} customers with 0 total spent")
                        
                        # Check if these customers have bills
                        for customer in zero_spent_customers[:5]:
                            customer_id = customer.get('customer_id')
                            customer_name = customer.get('name')
                            print(f"\n   Customer: {customer_name} (ID: {customer_id})")
                            
                            # Check if this customer has bills
                            bills_response = requests.get(f"https://tajir.up.railway.app/api/bills", timeout=10)
                            if bills_response.status_code == 200:
                                bills_data = bills_response.json()
                                if 'bills' in bills_data:
                                    customer_bills = [b for b in bills_data['bills'] if b.get('customer_id') == customer_id]
                                    if customer_bills:
                                        total_bills = sum(b.get('total_amount', 0) for b in customer_bills)
                                        print(f"     Has {len(customer_bills)} bills totaling AED {total_bills}")
                                        print(f"     But loyalty shows: AED {customer.get('total_spent')}")
                                    else:
                                        print(f"     No bills found")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def create_test_bill_and_check():
    """Create a test bill and check if loyalty updates"""
    try:
        print(f"\n🧪 CREATING TEST BILL")
        print("=" * 50)
        
        # First, get a customer
        response = requests.get("https://tajir.up.railway.app/api/customers", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'customers' in data and data['customers']:
                customer = data['customers'][0]
                customer_id = customer.get('customer_id')
                customer_name = customer.get('name')
                
                print(f"Using customer: {customer_name} (ID: {customer_id})")
                
                # Get a product
                products_response = requests.get("https://tajir.up.railway.app/api/products", timeout=10)
                if products_response.status_code == 200:
                    products_data = products_response.json()
                    if 'products' in products_data and products_data['products']:
                        product = products_data['products'][0]
                        product_id = product.get('product_id')
                        
                        # Create bill
                        bill_data = {
                            "customer_id": customer_id,
                            "items": [
                                {
                                    "product_id": product_id,
                                    "quantity": 1,
                                    "unit_price": 150.0,
                                    "discount": 0.0
                                }
                            ],
                            "payment_mode": "cash",
                            "total_amount": 150.0
                        }
                        
                        print(f"Creating bill for AED 150.0...")
                        bill_response = requests.post("https://tajir.up.railway.app/api/bills", json=bill_data, timeout=10)
                        
                        if bill_response.status_code == 200:
                            print("✅ Bill created successfully!")
                            
                            # Check loyalty after bill creation
                            print(f"Checking loyalty for {customer_name}...")
                            loyalty_response = requests.get(f"https://tajir.up.railway.app/api/loyalty/customers", timeout=10)
                            if loyalty_response.status_code == 200:
                                loyalty_data = loyalty_response.json()
                                if loyalty_data.get('success'):
                                    customers = loyalty_data.get('customers', [])
                                    for cust in customers:
                                        if cust.get('customer_id') == customer_id:
                                            print(f"   Total Spent: AED {cust.get('total_spent')}")
                                            print(f"   Available Points: {cust.get('available_points')}")
                                            print(f"   Tier Level: {cust.get('tier_level')}")
                                            break
                        else:
                            print(f"❌ Bill creation failed: {bill_response.status_code}")
                            print(f"   Error: {bill_response.text[:100]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_railway_bills()
    check_railway_customers_with_bills()
    create_test_bill_and_check()

