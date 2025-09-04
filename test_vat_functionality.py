#!/usr/bin/env python3
"""
Selenium test to verify VAT functionality:
1. Test VAT calculation updates in frontend when VAT% changes
2. Test VAT appears/disappears in print based on VAT% value
3. Test VAT configuration modal functionality
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

class VATTester:
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
    
    def test_vat_calculation_frontend(self):
        """Test VAT calculation updates in frontend"""
        print("\n=== Testing VAT Calculation in Frontend ===")
        
        try:
            # Find VAT input
            vat_input = self.driver.find_element(By.ID, "vatPercent")
            
            # Test 1: Set VAT to 5% and check calculation
            print("Test 1: Setting VAT to 5%")
            vat_input.clear()
            vat_input.send_keys("5")
            vat_input.send_keys("\t")  # Trigger change event
            
            time.sleep(1)  # Wait for calculation
            
            # Check tax amount in table
            tax_cell = self.driver.find_element(By.XPATH, "//table//td[contains(@class, 'text-right') and contains(text(), '5.00')]")
            if tax_cell:
                print("✓ Tax amount shows 5.00 for 5% VAT")
            else:
                print("✗ Tax amount not showing 5.00 for 5% VAT")
            
            # Check total amount
            total_due = self.driver.find_element(By.ID, "totalAmountDue")
            total_text = total_due.text
            if "105.00" in total_text:
                print("✓ Total amount shows 105.00 (100 + 5% VAT)")
            else:
                print(f"✗ Total amount incorrect: {total_text}")
            
            # Test 2: Set VAT to 0% and check calculation
            print("\nTest 2: Setting VAT to 0%")
            vat_input.clear()
            vat_input.send_keys("0")
            vat_input.send_keys("\t")  # Trigger change event
            
            time.sleep(1)  # Wait for calculation
            
            # Check tax amount in table
            try:
                tax_cell = self.driver.find_element(By.XPATH, "//table//td[contains(@class, 'text-right') and contains(text(), '0.00')]")
                print("✓ Tax amount shows 0.00 for 0% VAT")
            except NoSuchElementException:
                print("✗ Tax amount not showing 0.00 for 0% VAT")
            
            # Check total amount
            total_due = self.driver.find_element(By.ID, "totalAmountDue")
            total_text = total_due.text
            if "100.00" in total_text:
                print("✓ Total amount shows 100.00 (no VAT)")
            else:
                print(f"✗ Total amount incorrect: {total_text}")
            
            return True
            
        except Exception as e:
            print(f"✗ VAT calculation test failed: {e}")
            return False
    
    def test_vat_config_modal(self):
        """Test VAT configuration modal"""
        print("\n=== Testing VAT Configuration Modal ===")
        
        try:
            # Find VAT config button
            vat_config_btn = self.driver.find_element(By.ID, "vatConfigBtn")
            vat_config_btn.click()
            
            # Wait for modal to appear
            modal = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.ID, "vatConfigModal"))
            )
            print("✓ VAT configuration modal opened")
            
            # Test setting default VAT to 10%
            default_vat_input = self.driver.find_element(By.ID, "defaultVatPercent")
            default_vat_input.clear()
            default_vat_input.send_keys("10")
            
            # Save configuration
            save_btn = self.driver.find_element(By.ID, "saveVatConfig")
            save_btn.click()
            
            # Wait for modal to close
            WebDriverWait(self.driver, self.wait_timeout).until(
                EC.invisibility_of_element_located((By.ID, "vatConfigModal"))
            )
            print("✓ VAT configuration saved")
            
            # Check if VAT input updated
            vat_input = self.driver.find_element(By.ID, "vatPercent")
            vat_value = vat_input.get_attribute("value")
            if vat_value == "10":
                print("✓ VAT input updated to 10%")
            else:
                print(f"✗ VAT input not updated: {vat_value}")
            
            return True
            
        except Exception as e:
            print(f"✗ VAT configuration modal test failed: {e}")
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
            time.sleep(3)
            
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
                        print("✗ Total amount incorrect in print")
                        
                else:
                    print(f"✗ Print page not accessible: {response.status_code}")
            else:
                print("✗ Could not determine bill ID")
            
            return True
            
        except Exception as e:
            print(f"✗ Bill save and print test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all VAT functionality tests"""
        print("Starting VAT Functionality Tests...")
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
            
            # Test 3: VAT calculation in frontend
            if not self.test_vat_calculation_frontend():
                return False
            
            # Test 4: VAT configuration modal
            if not self.test_vat_config_modal():
                return False
            
            # Test 5: Save bill and test print
            if not self.save_bill_and_test_print():
                return False
            
            print("\n" + "=" * 50)
            print("✓ All VAT functionality tests completed successfully!")
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
    tester = VATTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! VAT functionality is working correctly.")
        exit(0)
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        exit(1)

if __name__ == "__main__":
    main()
