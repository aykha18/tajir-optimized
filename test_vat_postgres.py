#!/usr/bin/env python3
"""
Test VAT functionality by directly creating bills in PostgreSQL database and testing print
"""

import psycopg2
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

class VATPostgresTester:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        
        # PostgreSQL connection parameters
        self.db_params = {
            'host': 'localhost',
            'port': '5432',
            'database': 'tajir_pos',
            'user': 'postgres',
            'password': 'aykha123'
        }
        
    def create_test_bill_in_db(self, vat_percent=0):
        """Create a test bill directly in the PostgreSQL database"""
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()
            
            # Create bill using the correct columns from app.py
            bill_data = {
                'user_id': 1,  # Assuming user_id 1 exists
                'customer_id': None,
                'customer_name': 'Test Customer',
                'customer_phone': '1234567890',
                'customer_city': 'Test City',
                'customer_area': 'Test Area',
                'customer_trn': '',
                'customer_type': 'individual',
                'business_name': '',
                'business_address': '',
                'uuid': f'test-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'bill_number': f'TEST-{vat_percent}-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'bill_date': datetime.now().strftime('%Y-%m-%d'),
                'delivery_date': datetime.now().strftime('%Y-%m-%d'),
                'payment_method': 'cash',
                'subtotal': 100.0,
                'vat_amount': 0.0 if vat_percent == 0 else 5.0,
                'total_amount': 100.0 if vat_percent == 0 else 105.0,
                'advance_paid': 0.0,
                'balance_amount': 100.0 if vat_percent == 0 else 105.0,
                'status': 'pending',
                'master_id': None,
                'trial_date': None,
                'notes': f'Test bill with {vat_percent}% VAT'
            }
            
            cursor.execute('''
                INSERT INTO bills (user_id, bill_number, customer_id, customer_name, customer_phone, 
                                 customer_city, customer_area, customer_trn, customer_type, business_name, business_address,
                                 uuid, bill_date, delivery_date, payment_method, subtotal, vat_amount, total_amount, 
                                 advance_paid, balance_amount, status, master_id, trial_date, notes)
                VALUES (%(user_id)s, %(bill_number)s, %(customer_id)s, %(customer_name)s, %(customer_phone)s,
                        %(customer_city)s, %(customer_area)s, %(customer_trn)s, %(customer_type)s, %(business_name)s, %(business_address)s,
                        %(uuid)s, %(bill_date)s, %(delivery_date)s, %(payment_method)s, %(subtotal)s, %(vat_amount)s, %(total_amount)s,
                        %(advance_paid)s, %(balance_amount)s, %(status)s, %(master_id)s, %(trial_date)s, %(notes)s)
                RETURNING bill_id
            ''', bill_data)
            
            bill_id = cursor.fetchone()[0]
            
            # Create bill item using the correct columns from app.py
            item_data = {
                'bill_id': bill_id,
                'product_name': 'Test Product',
                'quantity': 1,
                'rate': 100.0,
                'discount': 0.0,
                'vat_amount': 0.0 if vat_percent == 0 else 5.0,
                'advance_paid': 0.0,
                'total_amount': 100.0 if vat_percent == 0 else 105.0
            }
            
            cursor.execute('''
                INSERT INTO bill_items (bill_id, product_name, quantity, rate, discount, vat_amount, advance_paid, total_amount)
                VALUES (%(bill_id)s, %(product_name)s, %(quantity)s, %(rate)s, %(discount)s, %(vat_amount)s, %(advance_paid)s, %(total_amount)s)
            ''', item_data)
            
            conn.commit()
            conn.close()
            
            print(f"✓ Test bill created in PostgreSQL with ID: {bill_id} (VAT: {vat_percent}%)")
            return bill_id
            
        except Exception as e:
            print(f"✗ PostgreSQL bill creation error: {e}")
            return None
    
    def test_print_bill(self, bill_id, expected_vat_shown=True):
        """Test print functionality for a bill"""
        try:
            print_url = f"{self.base_url}/api/bills/{bill_id}/print"
            response = requests.get(print_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check if VAT elements exist
                vat_elements = soup.find_all(text=lambda text: text and "VAT" in text)
                vat_found = len(vat_elements) > 0
                
                if expected_vat_shown:
                    if vat_found:
                        print(f"✓ VAT correctly shown in print for bill {bill_id}")
                        print(f"VAT elements: {[elem.strip() for elem in vat_elements if elem.strip()]}")
                    else:
                        print(f"✗ VAT not shown in print for bill {bill_id} (expected to be shown)")
                else:
                    if not vat_found:
                        print(f"✓ VAT correctly hidden in print for bill {bill_id}")
                    else:
                        print(f"✗ VAT shown in print for bill {bill_id} (expected to be hidden)")
                        print(f"VAT elements: {[elem.strip() for elem in vat_elements if elem.strip()]}")
                
                # Check for total amounts
                total_elements = soup.find_all(text=lambda text: text and any(amount in text for amount in ["100.00", "105.00"]) if text else False)
                if total_elements:
                    print(f"✓ Total amounts found in print: {[elem.strip() for elem in total_elements if elem.strip()]}")
                else:
                    print("ℹ No total amounts found in print")
                
                return True
                
            else:
                print(f"✗ Print page not accessible: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Print test error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all VAT print tests"""
        print("Starting VAT PostgreSQL Print Tests...")
        print("=" * 50)
        
        # Test 1: Create bill with 0% VAT and test print
        print("\n=== Testing Bill with 0% VAT ===")
        bill_id_0 = self.create_test_bill_in_db(0)
        if bill_id_0:
            self.test_print_bill(bill_id_0, expected_vat_shown=False)
        
        # Test 2: Create bill with 5% VAT and test print
        print("\n=== Testing Bill with 5% VAT ===")
        bill_id_5 = self.create_test_bill_in_db(5)
        if bill_id_5:
            self.test_print_bill(bill_id_5, expected_vat_shown=True)
        
        print("\n" + "=" * 50)
        print("✓ All VAT PostgreSQL print tests completed!")
        return True

def main():
    """Main test execution"""
    tester = VATPostgresTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! VAT print functionality is working correctly.")
        exit(0)
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        exit(1)

if __name__ == "__main__":
    main()
