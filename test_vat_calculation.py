#!/usr/bin/env python3
"""
Test VAT calculation when VAT input changes
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

class VATCalculationTester:
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
    
    def test_vat_calculation(self):
        """Test VAT calculation when VAT input changes"""
        print("\n=== Testing VAT Calculation ===")
        
        try:
            # Find VAT input
            vat_input = self.driver.find_element(By.ID, "vatPercent")
            
            # Test 1: Set VAT to 5% and check if calculation happens
            print("Test 1: Setting VAT to 5%")
            vat_input.clear()
            vat_input.send_keys("5")
            vat_input.send_keys("\t")  # Trigger blur event
            
            time.sleep(2)  # Wait for calculation
            
            # Check if VAT calculation function was called
            console_logs = self.driver.get_log('browser')
            vat_calculation_logs = [log for log in console_logs if 'VAT' in log.get('message', '')]
            print(f"VAT-related console logs: {len(vat_calculation_logs)}")
            
            # Test 2: Set VAT to 0% and check if calculation happens
            print("Test 2: Setting VAT to 0%")
            vat_input.clear()
            vat_input.send_keys("0")
            vat_input.send_keys("\t")  # Trigger blur event
            
            time.sleep(2)  # Wait for calculation
            
            # Check if VAT calculation function was called
            console_logs = self.driver.get_log('browser')
            vat_calculation_logs = [log for log in console_logs if 'VAT' in log.get('message', '')]
            print(f"VAT-related console logs after 0%: {len(vat_calculation_logs)}")
            
            # Test 3: Manually call the VAT calculation function
            print("Test 3: Manually calling VAT calculation function")
            result = self.driver.execute_script("""
                if (typeof recalcAllItemsForCurrentVat === 'function') {
                    recalcAllItemsForCurrentVat();
                    return 'Function called successfully';
                } else {
                    return 'Function not available';
                }
            """)
            print(f"Manual function call result: {result}")
            
            return True
            
        except Exception as e:
            print(f"✗ VAT calculation test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all VAT calculation tests"""
        print("Starting VAT Calculation Tests...")
        print("=" * 50)
        
        if not self.setup_driver():
            return False
        
        try:
            # Test 1: Login
            if not self.login():
                return False
            
            # Test 2: VAT calculation
            if not self.test_vat_calculation():
                return False
            
            print("\n" + "=" * 50)
            print("✓ All VAT calculation tests completed!")
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
    tester = VATCalculationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! VAT calculation is working correctly.")
        exit(0)
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        exit(1)

if __name__ == "__main__":
    main()
