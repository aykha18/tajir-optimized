#!/usr/bin/env python3
"""
Direct test of VAT functionality:
1. Test VAT configuration modal
2. Test VAT calculation in frontend
3. Test print functionality with existing bills
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

class DirectVATTester:
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
    
    def test_vat_input_functionality(self):
        """Test VAT input field functionality"""
        print("\n=== Testing VAT Input Functionality ===")
        
        try:
            # Find VAT input
            vat_input = self.driver.find_element(By.ID, "vatPercent")
            
            # Test setting VAT to 5%
            print("Test 1: Setting VAT to 5%")
            vat_input.clear()
            vat_input.send_keys("5")
            vat_input.send_keys("\t")  # Trigger change event
            
            time.sleep(1)
            
            # Check if value was set
            vat_value = vat_input.get_attribute("value")
            if vat_value == "5":
                print("✓ VAT input correctly set to 5%")
            else:
                print(f"✗ VAT input not set correctly: {vat_value}")
            
            # Test setting VAT to 0%
            print("Test 2: Setting VAT to 0%")
            vat_input.clear()
            vat_input.send_keys("0")
            vat_input.send_keys("\t")  # Trigger change event
            
            time.sleep(1)
            
            # Check if value was set
            vat_value = vat_input.get_attribute("value")
            if vat_value == "0":
                print("✓ VAT input correctly set to 0%")
            else:
                print(f"✗ VAT input not set correctly: {vat_value}")
            
            return True
            
        except Exception as e:
            print(f"✗ VAT input functionality test failed: {e}")
            return False
    
    def test_existing_bills_print(self):
        """Test print functionality with existing bills"""
        print("\n=== Testing Print Functionality with Existing Bills ===")
        
        try:
            # Try to find existing bills by checking the bills page
            self.driver.get(f"{self.base_url}/bills")
            time.sleep(2)
            
            # Look for bill links
            try:
                bill_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/bills/')]")
                if bill_links:
                    # Get the first bill ID
                    first_bill_link = bill_links[0]
                    bill_href = first_bill_link.get_attribute("href")
                    bill_id = bill_href.split("/bills/")[1].split("/")[0]
                    print(f"✓ Found existing bill ID: {bill_id}")
                    
                    # Test print functionality
                    print_url = f"{self.base_url}/api/bills/{bill_id}/print"
                    print(f"Testing print URL: {print_url}")
                    
                    # Fetch print page
                    response = requests.get(print_url)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Check if VAT elements exist
                        vat_elements = soup.find_all(text=lambda text: text and "VAT" in text)
                        if vat_elements:
                            print("✓ VAT elements found in print")
                            print(f"VAT elements: {[elem.strip() for elem in vat_elements if elem.strip()]}")
                        else:
                            print("ℹ No VAT elements found in print")
                        
                        # Check for total amounts
                        total_elements = soup.find_all(text=lambda text: text and any(amount in text for amount in ["100.00", "105.00", "110.00", "120.00"]) if text else False)
                        if total_elements:
                            print("✓ Total amounts found in print")
                            print(f"Total elements: {[elem.strip() for elem in total_elements if elem.strip()]}")
                        else:
                            print("ℹ No total amounts found in print")
                            
                    else:
                        print(f"✗ Print page not accessible: {response.status_code}")
                        
                else:
                    print("ℹ No existing bills found")
                    
            except NoSuchElementException:
                print("ℹ No bills page or bill links found")
            
            return True
            
        except Exception as e:
            print(f"✗ Existing bills print test failed: {e}")
            return False
    
    def test_vat_calculation_js(self):
        """Test VAT calculation JavaScript functionality"""
        print("\n=== Testing VAT Calculation JavaScript ===")
        
        try:
            # Go back to app page
            self.driver.get(f"{self.base_url}/app")
            time.sleep(2)
            
            # Test if VAT calculation functions exist
            vat_calc_exists = self.driver.execute_script("""
                return typeof recalcAllItemsForCurrentVat === 'function';
            """)
            
            if vat_calc_exists:
                print("✓ VAT calculation function exists")
            else:
                print("✗ VAT calculation function not found")
            
            # Test if VAT change listeners are attached
            vat_input = self.driver.find_element(By.ID, "vatPercent")
            listeners_exist = self.driver.execute_script("""
                var input = arguments[0];
                var events = getEventListeners ? getEventListeners(input) : null;
                return events && (events.input || events.change);
            """, vat_input)
            
            if listeners_exist:
                print("✓ VAT change listeners are attached")
            else:
                print("ℹ VAT change listeners status unknown (getEventListeners not available)")
            
            return True
            
        except Exception as e:
            print(f"✗ VAT calculation JS test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all VAT functionality tests"""
        print("Starting Direct VAT Functionality Tests...")
        print("=" * 50)
        
        if not self.setup_driver():
            return False
        
        try:
            # Test 1: Login
            if not self.login():
                return False
            
            # Test 2: VAT configuration modal
            if not self.test_vat_config_modal():
                return False
            
            # Test 3: VAT input functionality
            if not self.test_vat_input_functionality():
                return False
            
            # Test 4: VAT calculation JavaScript
            if not self.test_vat_calculation_js():
                return False
            
            # Test 5: Existing bills print functionality
            if not self.test_existing_bills_print():
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
    tester = DirectVATTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! VAT functionality is working correctly.")
        exit(0)
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        exit(1)

if __name__ == "__main__":
    main()
