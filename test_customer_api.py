import sqlite3
import requests
import json

def test_customer_api():
    try:
        # Test the API directly
        print("Testing customer API...")
        response = requests.get('http://localhost:5000/api/customers')
        print(f"API Response Status: {response.status_code}")
        print(f"API Response: {response.text}")
        
        # Check database directly
        print("\nChecking database directly...")
        conn = sqlite3.connect('pos_tailor.db')
        cursor = conn.execute('SELECT * FROM customers WHERE user_id = 1')
        customers = cursor.fetchall()
        print(f"Customers in database: {len(customers)}")
        for customer in customers:
            print(f"  {customer}")
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_customer_api()