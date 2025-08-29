#!/usr/bin/env python3
"""
Check customer loyalty enrollment
"""

import requests

def check_customer_loyalty():
    """Check if customer is enrolled in loyalty program"""
    try:
        print("🔍 CHECKING CUSTOMER LOYALTY ENROLLMENT")
        print("=" * 50)
        
        base_url = "https://tajir.up.railway.app"
        
        # Get customer 63 (Abdullah Al Falasi)
        customer_id = 63
        
        # Check loyalty data
        response = requests.get(f"{base_url}/api/loyalty/customers", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                customers = data.get('customers', [])
                
                # Find our customer
                customer_loyalty = None
                for cust in customers:
                    if cust.get('customer_id') == customer_id:
                        customer_loyalty = cust
                        break
                
                if customer_loyalty:
                    print(f"✅ Customer {customer_id} is enrolled in loyalty program")
                    print(f"   Name: {customer_loyalty.get('name')}")
                    print(f"   Tier: {customer_loyalty.get('tier_level')}")
                    print(f"   Total Spent: AED {customer_loyalty.get('total_spent')}")
                    print(f"   Available Points: {customer_loyalty.get('available_points')}")
                    print(f"   Total Purchases: {customer_loyalty.get('total_purchases')}")
                    print(f"   Join Date: {customer_loyalty.get('join_date')}")
                    print(f"   Is Active: {customer_loyalty.get('is_active')}")
                else:
                    print(f"❌ Customer {customer_id} is NOT enrolled in loyalty program")
                    
                    # Check if customer exists in customers table
                    customers_response = requests.get(f"{base_url}/api/customers", timeout=10)
                    if customers_response.status_code == 200:
                        all_customers = customers_response.json()
                        for cust in all_customers:
                            if cust.get('customer_id') == customer_id:
                                print(f"   Customer exists in customers table: {cust.get('name')}")
                                break
                        else:
                            print(f"   Customer {customer_id} not found in customers table")
            else:
                print(f"❌ Failed to get loyalty data: {data.get('error')}")
        else:
            print(f"❌ Failed to get loyalty data: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_customer_loyalty()

