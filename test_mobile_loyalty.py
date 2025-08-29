import requests
import json
import time

def test_mobile_loyalty_ahmed():
    print("=== Testing Mobile Billing Loyalty for Ahmed Al Nahyan ===")
    
    # Test 1: Check if Ahmed exists and is enrolled
    print("\n1. Checking Ahmed's loyalty status...")
    try:
        response = requests.get('http://localhost:5000/api/loyalty/customers/108')
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('loyalty_profile'):
                profile = data['loyalty_profile']
                print(f"✓ Ahmed is enrolled in loyalty program")
                print(f"  Customer ID: {profile.get('customer_id')}")
                print(f"  Name: {profile.get('customer_name')}")
                print(f"  Phone: {profile.get('customer_phone')}")
                print(f"  Tier Level: {profile.get('tier_level')}")
                print(f"  Available Points: {profile.get('available_points')}")
                print(f"  Total Spent: {profile.get('total_spent')}")
                print(f"  Join Date: {profile.get('join_date')}")
                print(f"  Loyalty ID: {profile.get('loyalty_id')}")
            else:
                print("✗ Ahmed is not enrolled in loyalty program")
        else:
            print(f"✗ Error getting Ahmed's loyalty data: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Check the main loyalty customers endpoint for Ahmed
    print(f"\n2. Checking main loyalty customers endpoint for Ahmed...")
    try:
        response = requests.get('http://localhost:5000/api/loyalty/customers')
        if response.status_code == 200:
            data = response.json()
            customers = data.get('customers', [])
            ahmed = None
            for customer in customers:
                if customer.get('customer_id') == 108:
                    ahmed = customer
                    break
            
            if ahmed:
                print(f"✓ Ahmed found in main loyalty customers endpoint")
                print(f"  Customer ID: {ahmed.get('customer_id')}")
                print(f"  Name: {ahmed.get('name')}")
                print(f"  Phone: {ahmed.get('phone')}")
                print(f"  Loyalty ID: {ahmed.get('loyalty_id')}")
                print(f"  Tier Level: {ahmed.get('tier_level')}")
                print(f"  Available Points: {ahmed.get('available_points')}")
                print(f"  Total Spent: {ahmed.get('total_spent')}")
                print(f"  Join Date: {ahmed.get('join_date')}")
            else:
                print("✗ Ahmed not found in main loyalty customers endpoint")
        else:
            print(f"✗ Error getting loyalty customers: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Test enrollment attempt (should fail since already enrolled)
    print(f"\n3. Testing enrollment attempt (should fail)...")
    try:
        response = requests.post(
            'http://localhost:5000/api/loyalty/customers/108/enroll',
            headers={'Content-Type': 'application/json'},
            json={}
        )
        if response.status_code == 400:
            data = response.json()
            if 'already enrolled' in data.get('error', ''):
                print("✓ Enrollment correctly rejected - Ahmed is already enrolled")
            else:
                print(f"✗ Unexpected error: {data.get('error')}")
        else:
            print(f"✗ Unexpected response: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")
    
    print(f"\n=== Test Summary ===")
    print("Ahmed Al Nahyan (ID: 108) should be enrolled in the loyalty program.")
    print("The mobile billing interface should:")
    print("1. Hide the 'Enroll Customer in Loyalty Program' button")
    print("2. Show '✓ Customer enrolled in loyalty program' message")
    print("3. Display loyalty details (Tier: Bronze, Points: 0, etc.)")
    print("4. Show tier indicator next to customer name")
    print("\nPlease test the mobile billing interface for Ahmed Al Nahyan (0581183518)")

if __name__ == "__main__":
    test_mobile_loyalty_ahmed()
