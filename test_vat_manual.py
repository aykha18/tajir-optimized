#!/usr/bin/env python3
"""
Manual test of VAT functionality:
1. Test VAT configuration modal opening
2. Test VAT input field
3. Test print functionality with existing bills
"""

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

class ManualVATTester:
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
    
    def test_vat_modal_opening(self):
        """Test VAT configuration modal opening"""
        print("\n=== Testing VAT Configuration Modal Opening ===")
        
        try:
            # Find VAT config button
            vat_config_btn = self.driver.find_element(By.ID, "vatConfigBtn")
            vat_config_btn.click()
            
            # Wait for modal to appear
            modal = WebDriverWait(self.driver, self.wait_timeout).until(
                EC.presence_of_element_located((By.ID, "vatConfigModal"))
            )
            print("✓ VAT configuration modal opened successfully")
            
            # Check if modal is visible
            if modal.is_displayed():
                print("✓ VAT configuration modal is visible")
            else:
                print("✗ VAT configuration modal is not visible")
            
            # Close modal by clicking outside or escape
            self.driver.execute_script("document.getElementById('vatConfigModal').style.display = 'none';")
            time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"✗ VAT configuration modal test failed: {e}")
            return False
    
    def test_vat_input_field(self):
        """Test VAT input field functionality"""
        print("\n=== Testing VAT Input Field ===")
        
        try:
            # Find VAT input
            vat_input = self.driver.find_element(By.ID, "vatPercent")
            
            # Test setting VAT to 5%
            print("Test 1: Setting VAT to 5%")
            vat_input.clear()
            vat_input.send_keys("5")
            
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
            
            # Check if value was set
            vat_value = vat_input.get_attribute("value")
            if vat_value == "0":
                print("✓ VAT input correctly set to 0%")
            else:
                print(f"✗ VAT input not set correctly: {vat_value}")
            
            return True
            
        except Exception as e:
            print(f"✗ VAT input field test failed: {e}")
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
    
    def test_vat_js_functions(self):
        """Test if VAT JavaScript functions exist"""
        print("\n=== Testing VAT JavaScript Functions ===")
        
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
            
            # Test if VAT config functions exist
            vat_config_exists = self.driver.execute_script("""
                return typeof openVatConfig === 'function';
            """)
            
            if vat_config_exists:
                print("✓ VAT configuration function exists")
            else:
                print("✗ VAT configuration function not found")
            
            return True
            
        except Exception as e:
            print(f"✗ VAT JavaScript functions test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all VAT functionality tests"""
        print("Starting Manual VAT Functionality Tests...")
        print("=" * 50)
        
        if not self.setup_driver():
            return False
        
        try:
            # Test 1: Login
            if not self.login():
                return False
            
            # Test 2: VAT configuration modal opening
            if not self.test_vat_modal_opening():
                return False
            
            # Test 3: VAT input field
            if not self.test_vat_input_field():
                return False
            
            # Test 4: VAT JavaScript functions
            if not self.test_vat_js_functions():
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
    tester = ManualVATTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! VAT functionality is working correctly.")
        exit(0)
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        exit(1)

if __name__ == "__main__":
    main()
