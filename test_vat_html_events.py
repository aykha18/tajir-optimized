#!/usr/bin/env python3
"""
Test HTML event handlers directly
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

class HTMLVATTester:
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
    
    def test_html_events(self):
        """Test HTML event handlers"""
        print("\n=== Testing HTML Event Handlers ===")
        
        try:
            # Check VAT input element
            vat_input = self.driver.find_element(By.ID, "vatPercent")
            print(f"VAT input found: {vat_input}")
            print(f"VAT input value: {vat_input.get_attribute('value')}")
            
            # Check if HTML event handlers are present
            onchange = vat_input.get_attribute('onchange')
            oninput = vat_input.get_attribute('oninput')
            onblur = vat_input.get_attribute('onblur')
            
            print(f"onchange attribute: {onchange}")
            print(f"oninput attribute: {oninput}")
            print(f"onblur attribute: {onblur}")
            
            # Test direct JavaScript execution
            print("\n--- Testing direct JavaScript execution ---")
            result = self.driver.execute_script("""
                const vatInput = document.getElementById('vatPercent');
                if (vatInput) {
                    vatInput.value = '0';
                    vatInput.dispatchEvent(new Event('change', { bubbles: true }));
                    vatInput.dispatchEvent(new Event('input', { bubbles: true }));
                    vatInput.dispatchEvent(new Event('blur', { bubbles: true }));
                    return 'Events dispatched';
                } else {
                    return 'VAT input not found';
                }
            """)
            print(f"Direct event dispatch result: {result}")
            
            time.sleep(2)  # Wait for any processing
            
            # Check console logs
            console_logs = self.driver.get_log('browser')
            vat_logs = [log for log in console_logs if 'VAT' in log.get('message', '') or 'recalc' in log.get('message', '')]
            print(f"VAT-related console logs: {len(vat_logs)}")
            for log in vat_logs:
                print(f"  {log['message']}")
            
            # Test manual function call
            print("\n--- Testing manual function call ---")
            manual_result = self.driver.execute_script("""
                if (typeof recalcAllItemsForCurrentVat === 'function') {
                    try {
                        recalcAllItemsForCurrentVat();
                        return 'Function called successfully';
                    } catch (error) {
                        return 'Function call failed: ' + error.message;
                    }
                } else {
                    return 'Function not available';
                }
            """)
            print(f"Manual function call result: {manual_result}")
            
            # Check console logs after manual call
            console_logs = self.driver.get_log('browser')
            vat_logs = [log for log in console_logs if 'VAT' in log.get('message', '') or 'recalc' in log.get('message', '')]
            print(f"VAT-related console logs after manual call: {len(vat_logs)}")
            for log in vat_logs:
                print(f"  {log['message']}")
            
            return True
            
        except Exception as e:
            print(f"✗ HTML event test failed: {e}")
            return False
    
    def run_test(self):
        """Run the test"""
        print("Starting HTML Event Handler Test...")
        print("=" * 50)
        
        if not self.setup_driver():
            return False
        
        try:
            # Login
            if not self.login():
                return False
            
            # Test HTML events
            if not self.test_html_events():
                return False
            
            print("\n" + "=" * 50)
            print("✓ Test completed!")
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
    tester = HTMLVATTester()
    success = tester.run_test()
    
    if success:
        print("\n🎉 Test completed!")
        exit(0)
    else:
        print("\n❌ Test failed!")
        exit(1)

if __name__ == "__main__":
    main()
