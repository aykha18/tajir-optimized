#!/usr/bin/env python3
"""
Test new bill creation and loyalty updates
"""

import requests
import json

def test_new_bill_loyalty():
    """Test creating a new bill and checking loyalty updates"""
    try:
        print("🧪 TESTING NEW BILL LOYALTY UPDATES")
        print("=" * 50)
        
        base_url = "https://tajir.up.railway.app"
        
        # Step 1: Get a customer
        print("1️⃣ Getting customer...")
        response = requests.get(f"{base_url}/api/customers", timeout=10)
        if response.status_code == 200:
            customers = response.json()
            if customers:
                customer = customers[0]  # Use first customer
                customer_id = customer.get('customer_id')
                customer_name = customer.get('name')
                print(f"   Using customer: {customer_name} (ID: {customer_id})")
                
                # Step 2: Get current loyalty data
                print("2️⃣ Getting current loyalty data...")
                loyalty_response = requests.get(f"{base_url}/api/loyalty/customers", timeout=10)
                if loyalty_response.status_code == 200:
                    loyalty_data = loyalty_response.json()
                    if loyalty_data.get('success'):
                        customers_loyalty = loyalty_data.get('customers', [])
                        
                        # Find our customer
                        current_loyalty = None
                        for cust in customers_loyalty:
                            if cust.get('customer_id') == customer_id:
                                current_loyalty = cust
                                break
                        
                        if current_loyalty:
                            print(f"   Current Total Spent: AED {current_loyalty.get('total_spent')}")
                            print(f"   Current Points: {current_loyalty.get('available_points')}")
                            print(f"   Current Purchases: {current_loyalty.get('total_purchases')}")
                            print(f"   Join Date: {current_loyalty.get('join_date')}")
                        else:
                            print(f"   Customer not found in loyalty program")
                            return
                
                # Step 3: Get a product
                print("3️⃣ Getting product...")
                products_response = requests.get(f"{base_url}/api/products", timeout=10)
                if products_response.status_code == 200:
                    products_data = products_response.json()
                    if isinstance(products_data, list) and products_data:
                        product = products_data[0]
                        product_id = product.get('product_id')
                        product_name = product.get('product_name')
                        print(f"   Using product: {product_name} (ID: {product_id})")
                        
                        # Step 4: Create a test bill
                        print("4️⃣ Creating test bill...")
                        bill_data = {
                            "bill": {
                                "customer_phone": customer.get('phone', ''),
                                "customer_name": customer.get('name', ''),
                                "customer_city": customer.get('city', ''),
                                "customer_area": customer.get('area', ''),
                                "customer_type": customer.get('customer_type', 'Individual'),
                                "payment_method": "Cash",
                                "subtotal": 200.0,
                                "vat_amount": 10.0,
                                "total_amount": 210.0,
                                "advance_paid": 0.0,
                                "balance_amount": 210.0
                            },
                            "items": [
                                {
                                    "product_id": product_id,
                                    "product_name": product_name,
                                    "quantity": 2,
                                    "rate": 100.0,
                                    "discount": 0.0,
                                    "advance_paid": 0.0
                                }
                            ]
                        }
                        
                        print(f"   Customer phone: {customer.get('phone')}")
                        print(f"   Customer name: {customer.get('name')}")
                        
                        bill_response = requests.post(f"{base_url}/api/bills", json=bill_data, timeout=10)
                        print(f"   Bill creation status: {bill_response.status_code}")
                        
                        if bill_response.status_code == 200:
                            bill_result = bill_response.json()
                            bill_id = bill_result.get('bill_id')
                            points_earned = bill_result.get('loyalty_points_earned', 0)
                            print(f"   ✅ Bill created successfully! ID: {bill_id}")
                            print(f"   Points earned: {points_earned}")
                            
                            # Step 5: Check updated loyalty data
                            print("5️⃣ Checking updated loyalty data...")
                            updated_loyalty_response = requests.get(f"{base_url}/api/loyalty/customers", timeout=10)
                            if updated_loyalty_response.status_code == 200:
                                updated_loyalty_data = updated_loyalty_response.json()
                                if updated_loyalty_data.get('success'):
                                    updated_customers = updated_loyalty_data.get('customers', [])
                                    
                                    # Find our customer again
                                    updated_loyalty = None
                                    for cust in updated_customers:
                                        if cust.get('customer_id') == customer_id:
                                            updated_loyalty = cust
                                            break
                                    
                                    if updated_loyalty:
                                        print(f"   ✅ Updated Total Spent: AED {updated_loyalty.get('total_spent')}")
                                        print(f"   ✅ Updated Points: {updated_loyalty.get('available_points')}")
                                        print(f"   ✅ Updated Purchases: {updated_loyalty.get('total_purchases')}")
                                        print(f"   ✅ Join Date: {updated_loyalty.get('join_date')}")
                                        
                                        # Calculate expected values
                                        expected_total_spent = float(current_loyalty.get('total_spent', 0)) + 210.0
                                        expected_points = int(current_loyalty.get('available_points', 0)) + 210
                                        expected_purchases = int(current_loyalty.get('total_purchases', 0)) + 1
                                        
                                        print(f"\n📊 VERIFICATION:")
                                        print(f"   Expected Total Spent: AED {expected_total_spent}")
                                        print(f"   Expected Points: {expected_points}")
                                        print(f"   Expected Purchases: {expected_purchases}")
                                        
                                        # Check if values match
                                        actual_total_spent = float(updated_loyalty.get('total_spent', 0))
                                        actual_points = int(updated_loyalty.get('available_points', 0))
                                        actual_purchases = int(updated_loyalty.get('total_purchases', 0))
                                        
                                        if actual_total_spent == expected_total_spent:
                                            print(f"   ✅ Total Spent: CORRECT")
                                        else:
                                            print(f"   ❌ Total Spent: INCORRECT (Expected: {expected_total_spent}, Got: {actual_total_spent})")
                                        
                                        if actual_points == expected_points:
                                            print(f"   ✅ Points: CORRECT")
                                        else:
                                            print(f"   ❌ Points: INCORRECT (Expected: {expected_points}, Got: {actual_points})")
                                        
                                        if actual_purchases == expected_purchases:
                                            print(f"   ✅ Purchases: CORRECT")
                                        else:
                                            print(f"   ❌ Purchases: INCORRECT (Expected: {expected_purchases}, Got: {actual_purchases})")
                                        
                                        if updated_loyalty.get('join_date') and updated_loyalty.get('join_date') != 'N/A':
                                            print(f"   ✅ Join Date: POPULATED")
                                        else:
                                            print(f"   ❌ Join Date: NOT POPULATED")
                                        
                                    else:
                                        print(f"   ❌ Customer not found in updated loyalty data")
                                else:
                                    print(f"   ❌ Failed to get updated loyalty data")
                            else:
                                print(f"   ❌ Failed to get updated loyalty data: {updated_loyalty_response.status_code}")
                        else:
                            print(f"   ❌ Bill creation failed: {bill_response.text[:200]}")
                    else:
                        print(f"   ❌ No products available")
                else:
                    print(f"   ❌ Failed to get products: {products_response.status_code}")
            else:
                print(f"   ❌ No customers available")
        else:
            print(f"   ❌ Failed to get customers: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_new_bill_loyalty()
