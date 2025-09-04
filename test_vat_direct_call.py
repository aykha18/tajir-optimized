#!/usr/bin/env python3
"""
Test direct function call with console logging
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

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
    
    def test_direct_function_call(self):
        """Test direct function call with console logging"""
        print("\n=== Testing Direct Function Call ===")
        
        try:
            # Clear console logs first
            self.driver.get_log('browser')
            
            # Test direct function call
            print("--- Calling function directly ---")
            result = self.driver.execute_script("""
                console.log('🧪 Starting direct function call test...');
                
                if (typeof recalcAllItemsForCurrentVat === 'function') {
                    console.log('✓ Function exists, calling it...');
                    try {
                        recalcAllItemsForCurrentVat();
                        console.log('✓ Function called successfully');
                        return 'Function called successfully';
                    } catch (error) {
                        console.error('❌ Function call failed:', error);
                        return 'Function call failed: ' + error.message;
                    }
                } else {
                    console.error('❌ Function not available');
                    return 'Function not available';
                }
            """)
            print(f"Direct function call result: {result}")
            
            time.sleep(2)  # Wait for any processing
            
            # Get all console logs
            console_logs = self.driver.get_log('browser')
            print(f"Total console logs: {len(console_logs)}")
            
            for log in console_logs:
                message = log.get('message', '')
                if any(keyword in message for keyword in ['VAT', 'recalc', '🚀', '🔄', '✓', '❌', '🧪']):
                    print(f"  {message}")
            
            # Test if function is accessible from window
            window_test = self.driver.execute_script("""
                return {
                    windowFunction: typeof window.recalcAllItemsForCurrentVat,
                    globalFunction: typeof recalcAllItemsForCurrentVat,
                    functionExists: typeof recalcAllItemsForCurrentVat === 'function'
                };
            """)
            print(f"Window function test: {window_test}")
            
            return True
            
        except Exception as e:
            print(f"✗ Direct function call test failed: {e}")
            return False
    
    def run_test(self):
        """Run the test"""
        print("Starting Direct Function Call Test...")
        print("=" * 50)
        
        if not self.setup_driver():
            return False
        
        try:
            # Login
            if not self.login():
                return False
            
            # Test direct function call
            if not self.test_direct_function_call():
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
    tester = DirectVATTester()
    success = tester.run_test()
    
    if success:
        print("\n🎉 Test completed!")
        exit(0)
    else:
        print("\n❌ Test failed!")
        exit(1)

if __name__ == "__main__":
    main()
