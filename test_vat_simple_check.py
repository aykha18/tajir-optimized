#!/usr/bin/env python3
"""
Simple VAT check - just test the existing item
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

class SimpleVATChecker:
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
    
    def get_vat_values(self):
        """Get current VAT values from the page"""
        try:
            # Get VAT input value
            vat_input = self.driver.find_element(By.ID, "vatPercent")
            vat_percent = vat_input.get_attribute("value")
            
            # Get tax amount from table (first item)
            tax_cell = self.driver.find_element(By.CSS_SELECTOR, "tr[data-index='0'] td:nth-child(6)")
            tax_amount = tax_cell.text.strip()
            
            # Get total amount from table (first item)
            total_cell = self.driver.find_element(By.CSS_SELECTOR, "tr[data-index='0'] td:nth-child(7)")
            item_total = total_cell.text.strip()
            
            # Get subtotal from summary
            subtotal_element = self.driver.find_element(By.ID, "subTotal")
            subtotal = subtotal_element.text.strip()
            
            # Get total amount due from summary
            total_due_element = self.driver.find_element(By.ID, "amountDue")
            total_due = total_due_element.text.strip()
            
            # Check if VAT summary row is visible
            vat_summary_row = self.driver.find_element(By.ID, "vatSummaryRow")
            vat_summary_visible = vat_summary_row.is_displayed()
            
            return {
                'vat_percent': vat_percent,
                'tax_amount': tax_amount,
                'item_total': item_total,
                'subtotal': subtotal,
                'total_due': total_due,
                'vat_summary_visible': vat_summary_visible
            }
            
        except Exception as e:
            print(f"✗ Failed to get VAT values: {e}")
            return None
    
    def test_vat_change(self):
        """Test VAT change like a human would"""
        print("\n=== Testing VAT Change ===")
        
        try:
            # Check initial state
            print("\n--- Initial State ---")
            values = self.get_vat_values()
            if not values:
                return False
                
            print(f"VAT Input: {values['vat_percent']}%")
            print(f"Tax Amount: {values['tax_amount']}")
            print(f"Item Total: {values['item_total']}")
            print(f"Subtotal: {values['subtotal']}")
            print(f"Total Due: {values['total_due']}")
            print(f"VAT Summary Visible: {values['vat_summary_visible']}")
            
            # Change VAT to 0%
            print("\n--- Changing VAT to 0% ---")
            vat_input = self.driver.find_element(By.ID, "vatPercent")
            vat_input.clear()
            vat_input.send_keys("0")
            vat_input.send_keys("\t")  # Trigger blur event
            
            time.sleep(3)  # Wait for calculation
            
            # Check final state
            print("\n--- After VAT Change ---")
            values = self.get_vat_values()
            if not values:
                return False
                
            print(f"VAT Input: {values['vat_percent']}%")
            print(f"Tax Amount: {values['tax_amount']}")
            print(f"Item Total: {values['item_total']}")
            print(f"Subtotal: {values['subtotal']}")
            print(f"Total Due: {values['total_due']}")
            print(f"VAT Summary Visible: {values['vat_summary_visible']}")
            
            # Check if VAT calculation worked
            if values['tax_amount'] == "0.00" and values['total_due'] == values['subtotal']:
                print("\n✅ VAT calculation working correctly!")
                return True
            else:
                print("\n❌ VAT calculation NOT working!")
                print(f"Expected: Tax=0.00, Total Due={values['subtotal']}")
                print(f"Actual: Tax={values['tax_amount']}, Total Due={values['total_due']}")
                return False
            
        except Exception as e:
            print(f"✗ VAT change test failed: {e}")
            return False
    
    def run_test(self):
        """Run the test"""
        print("Starting Simple VAT Check...")
        print("=" * 50)
        
        if not self.setup_driver():
            return False
        
        try:
            # Login
            if not self.login():
                return False
            
            # Test VAT change
            if not self.test_vat_change():
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
    tester = SimpleVATChecker()
    success = tester.run_test()
    
    if success:
        print("\n🎉 VAT calculation is working correctly!")
        exit(0)
    else:
        print("\n❌ VAT calculation is NOT working correctly!")
        exit(1)

if __name__ == "__main__":
    main()
