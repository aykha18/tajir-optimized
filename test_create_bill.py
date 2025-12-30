import requests
import json
import random

def test_create_bill():
    url = "http://localhost:5000/api/bills"
    
    # Random phone number to avoid conflicts/easy identification
    random_phone = f"50{random.randint(100000, 999999)}"
    country_code = "965" # Kuwait
    
    # Form Data payload
    data = {
        'customer_name': 'Test Country Code',
        'customer_phone': random_phone,
        'country_code': country_code,
        'customer_city': 'Kuwait City',
        'customer_area': 'Salmiya',
        'bill_date': '2025-12-28',
        'delivery_date': '2025-12-31',
        'payment_method': 'Cash',
        'items': json.dumps([
            {
                'name': 'Test Item',
                'qty': 1,
                'rate': 100,
                'amount': 100
            }
        ])
    }
    
    print(f"Sending request to {url}")
    print(f"Phone: {random_phone}, Country Code: {country_code}")
    
    try:
        response = requests.post(url, data=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Response JSON:", json.dumps(result, indent=2))
            
            bill_id = result.get('bill_id')
            if bill_id:
                print(f"Bill created with ID: {bill_id}")
                
                # Verify the created bill
                verify_url = f"http://localhost:5000/api/bills/{bill_id}"
                verify_response = requests.get(verify_url)
                
                if verify_response.status_code == 200:
                    bill_response = verify_response.json()
                    bill_details = bill_response.get('bill', {})
                    customer_phone = bill_details.get('customer_phone')
                    print(f"Stored Customer Phone: {customer_phone}")
                    
                    expected_phone = f"+{country_code}{random_phone}"
                    if customer_phone == expected_phone:
                        print("SUCCESS: Country code correctly stored!")
                    else:
                        print(f"FAILURE: Expected {expected_phone}, got {customer_phone}")
                else:
                    print("Failed to fetch bill details for verification")
        else:
            print("Failed to create bill")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_create_bill()
