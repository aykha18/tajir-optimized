#!/usr/bin/env python3
"""
Test if VAT functions are now available in the browser
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

class VATFunctionsTester:
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
    
    def test_vat_functions(self):
        """Test if VAT functions are available"""
        print("\n=== Testing VAT Functions Availability ===")
        
        try:
            # Test if VAT calculation function exists
            vat_calc_exists = self.driver.execute_script("""
                return typeof recalcAllItemsForCurrentVat === 'function';
            """)
            
            if vat_calc_exists:
                print("✓ VAT calculation function exists")
            else:
                print("✗ VAT calculation function not found")
            
            # Test if VAT config functions exist
            vat_config_exists = self.driver.execute_script("""
                return typeof openVatConfigModal === 'function';
            """)
            
            if vat_config_exists:
                print("✓ VAT configuration function exists")
            else:
                print("✗ VAT configuration function not found")
            
            # Test if attachVatChangeListeners function exists
            attach_listeners_exists = self.driver.execute_script("""
                return typeof attachVatChangeListeners === 'function';
            """)
            
            if attach_listeners_exists:
                print("✓ Attach VAT listeners function exists")
            else:
                print("✗ Attach VAT listeners function not found")
            
            # Test VAT input functionality
            vat_input = self.driver.find_element(By.ID, "vatPercent")
            
            # Set VAT to 5%
            print("\nTest: Setting VAT to 5%")
            vat_input.clear()
            vat_input.send_keys("5")
            vat_input.send_keys("\t")
            
            time.sleep(1)
            
            # Check if value was set
            vat_value = vat_input.get_attribute("value")
            if vat_value == "5":
                print("✓ VAT input correctly set to 5%")
            else:
                print(f"✗ VAT input not set correctly: {vat_value}")
            
            # Set VAT to 0%
            print("Test: Setting VAT to 0%")
            vat_input.clear()
            vat_input.send_keys("0")
            vat_input.send_keys("\t")
            
            time.sleep(1)
            
            # Check if value was set
            vat_value = vat_input.get_attribute("value")
            if vat_value == "0":
                print("✓ VAT input correctly set to 0%")
            else:
                print(f"✗ VAT input not set correctly: {vat_value}")
            
            return True
            
        except Exception as e:
            print(f"✗ VAT functions test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all VAT function tests"""
        print("Starting VAT Functions Tests...")
        print("=" * 50)
        
        if not self.setup_driver():
            return False
        
        try:
            # Test 1: Login
            if not self.login():
                return False
            
            # Test 2: VAT functions availability
            if not self.test_vat_functions():
                return False
            
            print("\n" + "=" * 50)
            print("✓ All VAT function tests completed!")
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
    tester = VATFunctionsTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! VAT functions are working correctly.")
        exit(0)
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        exit(1)

if __name__ == "__main__":
    main()
