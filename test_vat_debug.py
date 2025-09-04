#!/usr/bin/env python3
"""
Debug VAT function calls
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

class VATDebugger:
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
    
    def debug_vat_function(self):
        """Debug VAT function availability and calls"""
        print("\n=== Debugging VAT Function ===")
        
        try:
            # Check if function exists
            function_exists = self.driver.execute_script("""
                return typeof recalcAllItemsForCurrentVat === 'function';
            """)
            print(f"recalcAllItemsForCurrentVat function exists: {function_exists}")
            
            # Check if bill array exists
            bill_info = self.driver.execute_script("""
                if (typeof bill !== 'undefined' && Array.isArray(bill)) {
                    return {exists: true, length: bill.length, items: bill};
                } else if (typeof window.bill !== 'undefined' && Array.isArray(window.bill)) {
                    return {exists: true, length: window.bill.length, items: window.bill};
                } else {
                    return {exists: false, available: Object.keys(window).filter(k => k.includes('bill'))};
                }
            """)
            print(f"Bill array info: {bill_info}")
            
            # Check VAT input
            vat_input = self.driver.find_element(By.ID, "vatPercent")
            vat_value = vat_input.get_attribute("value")
            print(f"VAT input value: {vat_value}")
            
            # Change VAT to 0 and check console logs
            print("\n--- Changing VAT to 0% ---")
            vat_input.clear()
            vat_input.send_keys("0")
            vat_input.send_keys("\t")  # Trigger blur event
            
            time.sleep(3)  # Wait for any calculations
            
            # Get console logs
            console_logs = self.driver.get_log('browser')
            vat_logs = [log for log in console_logs if 'VAT' in log.get('message', '') or 'recalc' in log.get('message', '')]
            print(f"VAT-related console logs: {len(vat_logs)}")
            for log in vat_logs:
                print(f"  {log['message']}")
            
            # Manually call the function and check result
            print("\n--- Manually calling VAT function ---")
            result = self.driver.execute_script("""
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
            print(f"Manual function call result: {result}")
            
            # Check console logs after manual call
            console_logs = self.driver.get_log('browser')
            vat_logs = [log for log in console_logs if 'VAT' in log.get('message', '') or 'recalc' in log.get('message', '')]
            print(f"VAT-related console logs after manual call: {len(vat_logs)}")
            for log in vat_logs:
                print(f"  {log['message']}")
            
            return True
            
        except Exception as e:
            print(f"✗ Debug failed: {e}")
            return False
    
    def run_debug(self):
        """Run the debug"""
        print("Starting VAT Debug...")
        print("=" * 50)
        
        if not self.setup_driver():
            return False
        
        try:
            # Login
            if not self.login():
                return False
            
            # Debug VAT function
            if not self.debug_vat_function():
                return False
            
            print("\n" + "=" * 50)
            print("✓ Debug completed!")
            return True
            
        except Exception as e:
            print(f"✗ Debug execution failed: {e}")
            return False
        
        finally:
            if self.driver:
                self.driver.quit()
                print("✓ Browser closed")

def main():
    """Main debug execution"""
    debugger = VATDebugger()
    success = debugger.run_debug()
    
    if success:
        print("\n🎉 Debug completed!")
        exit(0)
    else:
        print("\n❌ Debug failed!")
        exit(1)

if __name__ == "__main__":
    main()
