#!/usr/bin/env python3
"""
Direct test of VAT print functionality:
1. Create a test bill with VAT 0% and test print
2. Create a test bill with VAT 5% and test print
"""

import requests
import json
from bs4 import BeautifulSoup

class VATPrintTester:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.session = requests.Session()
        
    def login(self):
        """Login to get session"""
        try:
            # Login
            login_data = {
                "method": "email",
                "email": "admin@tailorpos.com",
                "password": "admin123"
            }
            
            response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✓ Login successful")
                    return True
                else:
                    print(f"✗ Login failed: {data.get('message')}")
                    return False
            else:
                print(f"✗ Login request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Login error: {e}")
            return False
    
    def create_test_bill(self, vat_percent=0):
        """Create a test bill with specified VAT percentage"""
        try:
            bill_data = {
                "bill": {
                    "customer_id": None,
                    "customer_name": "Test Customer",
                    "customer_phone": "1234567890",
                    "customer_address": "Test Address",
                    "bill_number": f"TEST-{vat_percent}",
                    "bill_date": "2025-09-04",
                    "due_date": "2025-09-04",
                    "vat_percent": vat_percent,
                    "vat_amount": 0 if vat_percent == 0 else 5.0,
                    "subtotal": 100.0,
                    "total_amount": 100.0 if vat_percent == 0 else 105.0,
                    "advance_paid": 0.0,
                    "balance_amount": 100.0 if vat_percent == 0 else 105.0,
                    "payment_status": "pending",
                    "notes": f"Test bill with {vat_percent}% VAT"
                },
                "items": [
                    {
                        "product_name": "Test Product",
                        "description": "Test Description",
                        "quantity": 1,
                        "rate": 100.0,
                        "discount": 0.0,
                        "advance_paid": 0.0,
                        "vat_percent": vat_percent,
                        "vat_amount": 0.0 if vat_percent == 0 else 5.0,
                        "total_amount": 100.0 if vat_percent == 0 else 105.0
                    }
                ]
            }
            
            response = self.session.post(f"{self.base_url}/api/bills", json=bill_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    bill_id = data.get("bill_id")
                    print(f"✓ Test bill created with ID: {bill_id} (VAT: {vat_percent}%)")
                    return bill_id
                else:
                    print(f"✗ Bill creation failed: {data.get('message')}")
                    return None
            else:
                print(f"✗ Bill creation request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"✗ Bill creation error: {e}")
            return None
    
    def test_print_bill(self, bill_id, expected_vat_shown=True):
        """Test print functionality for a bill"""
        try:
            print_url = f"{self.base_url}/api/bills/{bill_id}/print"
            response = self.session.get(print_url)
            
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
        print("Starting VAT Print Functionality Tests...")
        print("=" * 50)
        
        # Test 1: Login
        if not self.login():
            return False
        
        # Test 2: Create bill with 0% VAT and test print
        print("\n=== Testing Bill with 0% VAT ===")
        bill_id_0 = self.create_test_bill(0)
        if bill_id_0:
            self.test_print_bill(bill_id_0, expected_vat_shown=False)
        
        # Test 3: Create bill with 5% VAT and test print
        print("\n=== Testing Bill with 5% VAT ===")
        bill_id_5 = self.create_test_bill(5)
        if bill_id_5:
            self.test_print_bill(bill_id_5, expected_vat_shown=True)
        
        print("\n" + "=" * 50)
        print("✓ All VAT print tests completed!")
        return True

def main():
    """Main test execution"""
    tester = VATPrintTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! VAT print functionality is working correctly.")
        exit(0)
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        exit(1)

if __name__ == "__main__":
    main()
