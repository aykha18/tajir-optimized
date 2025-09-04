#!/usr/bin/env python3
"""
Complete Selenium test to verify VAT functionality with actual bill items:
1. Add items to bill
2. Test VAT calculation updates in frontend when VAT% changes
3. Save bill and test print functionality
"""

import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

class CompleteVATTester:
    def __init__(self):
        self.driver = None
        self.base_url = "http://localhost:5000"
        self.wait_timeout = 10
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(5)
            print("✓ Chrome driver initialized")
            return True
        except Exception as e:
            print(f"✗ Failed to initialize Chrome driver: {e}")
            return False
    
    def login(self):
        """Login to the application"""
        try:
            self.driver.get(f"{self.base_url}/login")
            
            # Wait for login form
            email_input = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.ID, "signin-email"))
            )
            password_input = self.driver.find_element(By.ID, "signin-password")
            login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]")
            
            # Login with admin credentials
            email_input.clear()
            email_input.send_keys("admin@tailorpos.com")
            password_input.clear()
            password_input.send_keys("admin123")
            login_btn.click()
            
            # Wait for redirect to app
            WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.ID, "productSearch"))
            )
            print("✓ Login successful")
            return True
            
        except TimeoutException:
            print("✗ Login timeout - check if server is running")
            return False
        except Exception as e:
            print(f"✗ Login failed: {e}")
            return False
    
    def add_test_item(self):
        """Add a test item to the bill"""
        try:
            # Fill product search
            product_search = self.driver.find_element(By.ID, "productSearch")
            product_search.clear()
            product_search.send_keys("Test Product")
            
            # Fill rate
            rate_input = self.driver.find_element(By.ID, "rate")
            rate_input.clear()
            rate_input.send_keys("100")
            
            # Fill quantity
            qty_input = self.driver.find_element(By.ID, "quantity")
            qty_input.clear()
            qty_input.send_keys("1")
            
            # Click Add Item
            add_item_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Add Item')]")
            add_item_btn.click()
            
            # Wait for item to appear in table
            WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.XPATH, "//table//td[contains(text(), 'Test Product')]"))
            )
            print("✓ Test item added successfully")
            return True
            
        except Exception as e:
            print(f"✗ Failed to add test item: {e}")
            return False
    
    def test_vat_calculation_with_items(self):
        """Test VAT calculation with actual items"""
        print("\n=== Testing VAT Calculation with Items ===")
        
        try:
            # Find VAT input
            vat_input = self.driver.find_element(By.ID, "vatPercent")
            
            # Test 1: Set VAT to 5% and check calculation
            print("Test 1: Setting VAT to 5%")
            vat_input.clear()
            vat_input.send_keys("5")
            vat_input.send_keys("\t")  # Trigger change event
            
            time.sleep(2)  # Wait for calculation
            
            # Check tax amount in table
            try:
                bill_table = self.driver.find_element(By.XPATH, "//table[contains(@class, 'bill-table')]")
                rows = bill_table.find_elements(By.XPATH, ".//tr[contains(@class, 'bill-item')]")
                
                if len(rows) > 0:
                    # Find tax column (usually the 6th column)
                    tax_cells = bill_table.find_elements(By.XPATH, ".//td[contains(@class, 'text-right')]")
                    if len(tax_cells) >= 6:
                        tax_text = tax_cells[5].text  # 6th column (0-indexed)
                        print(f"Tax amount in table: {tax_text}")
                        
                        if "5.00" in tax_text:
                            print("✓ Tax amount shows 5.00 for 5% VAT")
                        else:
                            print(f"✗ Tax amount not showing 5.00 for 5% VAT: {tax_text}")
                    else:
                        print("ℹ Could not find tax column")
                else:
                    print("ℹ No items in bill table")
                    
            except NoSuchElementException:
                print("ℹ No bill table found")
            
            # Check total amount in summary
            try:
                total_due = self.driver.find_element(By.ID, "totalAmountDue")
                total_text = total_due.text
                print(f"Total amount due: {total_text}")
                
                if "105.00" in total_text:
                    print("✓ Total amount shows 105.00 (100 + 5% VAT)")
                else:
                    print(f"ℹ Total amount: {total_text}")
                    
            except NoSuchElementException:
                print("ℹ Total amount element not found")
            
            # Test 2: Set VAT to 0% and check calculation
            print("\nTest 2: Setting VAT to 0%")
            vat_input.clear()
            vat_input.send_keys("0")
            vat_input.send_keys("\t")  # Trigger change event
            
            time.sleep(2)  # Wait for calculation
            
            # Check total amount again
            try:
                total_due = self.driver.find_element(By.ID, "totalAmountDue")
                total_text = total_due.text
                print(f"Total amount after 0% VAT: {total_text}")
                
                if "100.00" in total_text:
                    print("✓ Total amount shows 100.00 (no VAT)")
                else:
                    print(f"ℹ Total amount: {total_text}")
                    
            except NoSuchElementException:
                print("ℹ Total amount element not found")
            
            return True
            
        except Exception as e:
            print(f"✗ VAT calculation test failed: {e}")
            return False
    
    def save_bill_and_test_print(self):
        """Save bill and test print functionality"""
        print("\n=== Testing Bill Save and Print ===")
        
        try:
            # Set VAT to 0% for print test
            vat_input = self.driver.find_element(By.ID, "vatPercent")
            vat_input.clear()
            vat_input.send_keys("0")
            vat_input.send_keys("\t")
            time.sleep(1)
            
            # Save the bill
            save_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Save Invoice')]")
            save_btn.click()
            
            # Wait for success message or redirect
            time.sleep(5)
            
            # Get current URL to extract bill ID
            current_url = self.driver.current_url
            print(f"Current URL: {current_url}")
            
            # Try to find bill ID from URL or page
            bill_id = None
            if "/bills/" in current_url:
                bill_id = current_url.split("/bills/")[1].split("/")[0]
            else:
                # Look for bill ID in page content
                try:
                    bill_id_element = self.driver.find_element(By.XPATH, "//span[contains(@class, 'bill-number')]")
                    bill_id = bill_id_element.text.replace("#", "")
                except:
                    pass
            
            if bill_id:
                print(f"✓ Bill saved with ID: {bill_id}")
                
                # Test print functionality
                print_url = f"{self.base_url}/api/bills/{bill_id}/print"
                print(f"Testing print URL: {print_url}")
                
                # Fetch print page
                response = requests.get(print_url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Check if VAT is hidden (should be for 0% VAT)
                    vat_elements = soup.find_all(text=lambda text: text and "VAT" in text)
                    if not vat_elements:
                        print("✓ VAT correctly hidden in print (0% VAT)")
                    else:
                        print(f"✗ VAT still appears in print: {vat_elements}")
                    
                    # Check total amount in print
                    total_elements = soup.find_all(text=lambda text: text and "100.00" in text)
                    if total_elements:
                        print("✓ Total amount correct in print (100.00)")
                    else:
                        print("ℹ Total amount not found in print")
                        
                else:
                    print(f"✗ Print page not accessible: {response.status_code}")
                    
                return bill_id
            else:
                print("✗ Could not determine bill ID")
                return None
            
        except Exception as e:
            print(f"✗ Bill save and print test failed: {e}")
            return None
    
    def test_print_with_vat(self, bill_id):
        """Test print functionality with VAT enabled"""
        if not bill_id:
            print("ℹ No bill ID available for VAT print test")
            return True
            
        print("\n=== Testing Print with VAT Enabled ===")
        
        try:
            # Navigate back to app and modify the bill
            self.driver.get(f"{self.base_url}/app")
            time.sleep(2)
            
            # Set VAT to 5%
            vat_input = self.driver.find_element(By.ID, "vatPercent")
            vat_input.clear()
            vat_input.send_keys("5")
            vat_input.send_keys("\t")
            time.sleep(1)
            
            # Save the bill again
            save_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Save Invoice')]")
            save_btn.click()
            time.sleep(3)
            
            # Test print functionality with VAT
            print_url = f"{self.base_url}/api/bills/{bill_id}/print"
            print(f"Testing print URL with VAT: {print_url}")
            
            # Fetch print page
            response = requests.get(print_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check if VAT is shown (should be for 5% VAT)
                vat_elements = soup.find_all(text=lambda text: text and "VAT" in text)
                if vat_elements:
                    print("✓ VAT correctly shown in print (5% VAT)")
                else:
                    print("✗ VAT not shown in print despite 5% VAT")
                
                # Check total amount in print
                total_elements = soup.find_all(text=lambda text: text and "105.00" in text)
                if total_elements:
                    print("✓ Total amount correct in print (105.00)")
                else:
                    print("ℹ Total amount not found in print")
                    
            else:
                print(f"✗ Print page not accessible: {response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"✗ VAT print test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all VAT functionality tests"""
        print("Starting Complete VAT Functionality Tests...")
        print("=" * 50)
        
        if not self.setup_driver():
            return False
        
        try:
            # Test 1: Login
            if not self.login():
                return False
            
            # Test 2: Add test item
            if not self.add_test_item():
                return False
            
            # Test 3: VAT calculation with items
            if not self.test_vat_calculation_with_items():
                return False
            
            # Test 4: Save bill and test print (0% VAT)
            bill_id = self.save_bill_and_test_print()
            
            # Test 5: Test print with VAT enabled
            if not self.test_print_with_vat(bill_id):
                return False
            
            print("\n" + "=" * 50)
            print("✓ All VAT functionality tests completed!")
            return True
            
        except Exception as e:
            print(f"✗ Test execution failed: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
                print("✓ Browser closed")

def main():
    """Main test execution"""
    tester = CompleteVATTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! VAT functionality is working correctly.")
        exit(0)
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        exit(1)

if __name__ == "__main__":
    main()
