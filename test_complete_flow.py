#!/usr/bin/env python3
"""
Test the complete flow from UI to database
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_complete_flow():
    print("🧪 Testing Complete Flow from UI to Database")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Step 1: Login
        print("\n🔐 Step 1: Logging in...")
        driver.get("http://localhost:5000/login")
        
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "signin-email"))
        )
        password_input = driver.find_element(By.ID, "signin-password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        email_input.send_keys("td@tajir.com")
        password_input.send_keys("demo123")
        login_button.click()
        
        WebDriverWait(driver, 10).until(EC.url_contains("/app"))
        print("   ✅ Login successful")
        
        # Step 2: Navigate to shop settings
        print("\n⚙️ Step 2: Navigating to shop settings...")
        shop_settings_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-go='shopSettingsSec']"))
        )
        shop_settings_btn.click()
        time.sleep(2)
        print("   ✅ Shop settings section loaded")
        
        # Step 3: Set specific checkbox values
        print("\n🔧 Step 3: Setting specific checkbox values...")
        checkboxes_to_set = [
            ("bcEnableTrialDate", "enable_trial_date", True),
            ("bcEnableDeliveryDate", "enable_delivery_date", False),
            ("bcEnableAdvancePayment", "enable_advance_payment", True),
            ("useDynamicInvoiceTemplate", "use_dynamic_invoice_template", False),
            ("enableCustomerNotes", "enable_customer_notes", True),
            ("enableEmployeeAssignment", "enable_employee_assignment", False)
        ]
        
        for checkbox_id, name, target_state in checkboxes_to_set:
            try:
                checkbox = driver.find_element(By.ID, checkbox_id)
                current_state = checkbox.is_selected()
                if current_state != target_state:
                    checkbox.click()  # Toggle to target state
                final_state = checkbox.is_selected()
                status = "✅" if final_state == target_state else "❌"
                print(f"   {status} {checkbox_id} ({name}): {current_state} → {final_state} (target: {target_state})")
            except Exception as e:
                print(f"   ❌ Error setting {checkbox_id}: {e}")
        
        time.sleep(1)
        
        # Step 4: Save the settings
        print("\n💾 Step 4: Saving settings...")
        try:
            save_btn = driver.find_element(By.ID, "saveShopSettingsBtn")
            save_btn.click()
            time.sleep(3)  # Wait for save to complete
            
            # Handle the alert
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text
                print(f"   📝 Alert: {alert_text}")
                alert.accept()
            except:
                print("   ⚠️ No alert found")
                
        except Exception as e:
            print(f"   ❌ Error saving: {e}")
        
        # Step 5: Refresh the page to test if values persist
        print("\n🔄 Step 5: Refreshing page to test persistence...")
        driver.refresh()
        time.sleep(3)
        
        # Navigate back to shop settings
        shop_settings_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-go='shopSettingsSec']"))
        )
        shop_settings_btn.click()
        time.sleep(2)
        
        # Step 6: Check if values persisted
        print("\n🔍 Step 6: Checking if values persisted after refresh...")
        persistence_results = []
        
        for checkbox_id, name, expected_state in checkboxes_to_set:
            try:
                checkbox = driver.find_element(By.ID, checkbox_id)
                actual_state = checkbox.is_selected()
                matches = actual_state == expected_state
                persistence_results.append(matches)
                status = "✅" if matches else "❌"
                print(f"   {status} {checkbox_id} ({name}): {actual_state} (expected: {expected_state})")
            except Exception as e:
                print(f"   ❌ Error checking {checkbox_id}: {e}")
                persistence_results.append(False)
        
        # Step 7: Summary
        print("\n📊 Step 7: Summary...")
        total_checks = len(persistence_results)
        passed_checks = sum(persistence_results)
        
        print(f"   📝 Total checkbox checks: {total_checks}")
        print(f"   ✅ Passed: {passed_checks}")
        print(f"   ❌ Failed: {total_checks - passed_checks}")
        
        if passed_checks == total_checks:
            print("   🎉 SUCCESS: All values persisted correctly!")
        else:
            print("   ⚠️ ISSUE: Some values did not persist")
        
        print("\n✅ Complete flow test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_complete_flow()
