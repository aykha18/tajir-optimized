#!/usr/bin/env python3
"""
Test the final save operation
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_final_save_operation():
    print("🧪 Final Save Operation Test")
    
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
        
        email_input.send_keys("tumd@tajir.com")
        password_input.send_keys("demo123")
        login_button.click()
        
        # Wait for redirect to app
        WebDriverWait(driver, 10).until(
            EC.url_contains("/app")
        )
        print("   ✅ Login successful")
        
        # Step 2: Navigate to shop settings
        print("\n⚙️ Step 2: Navigating to shop settings...")
        shop_settings_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-go='shopSettingsSec']"))
        )
        shop_settings_btn.click()
        time.sleep(2)
        
        # Step 3: Toggle a checkbox
        print("\n🔄 Step 3: Toggling a checkbox...")
        checkbox = driver.find_element(By.ID, "bcEnableTrialDate")
        initial_state = checkbox.is_selected()
        checkbox.click()
        new_state = checkbox.is_selected()
        print(f"   🔄 Trial Date: {initial_state} → {new_state}")
        
        # Step 4: Click save button
        print("\n💾 Step 4: Clicking save button...")
        save_btn = driver.find_element(By.ID, "saveShopSettingsBtn")
        save_btn.click()
        time.sleep(3)
        
        # Step 5: Check if the checkbox state changed
        print("\n🔍 Step 5: Checking checkbox state after save...")
        checkbox_after = driver.find_element(By.ID, "bcEnableTrialDate")
        final_state = checkbox_after.is_selected()
        print(f"   📝 Checkbox state after save: {final_state}")
        
        # Step 6: Check console logs
        print("\n📋 Step 6: Checking console logs...")
        logs = driver.get_log('browser')
        
        for log in logs:
            if any(keyword in log['message'] for keyword in ['Save button click event triggered', 'Save button clicked, form found', 'Calling handleShopSettingsSubmit', 'Form is null', 'initializeShopSettings', 'Setting up save button event listener']):
                print(f"   📝 {log['message']}")
        
        # Step 7: Check if there are any JavaScript errors
        print("\n🔍 Step 7: Checking for JavaScript errors...")
        error_logs = [log for log in logs if log['level'] == 'SEVERE']
        if error_logs:
            print("   ❌ JavaScript errors found:")
            for log in error_logs:
                print(f"   {log['message']}")
        else:
            print("   ✅ No JavaScript errors found")
        
        # Step 8: Summary
        print("\n📊 Step 8: Summary...")
        if final_state == new_state:
            print("   ✅ Save operation worked - checkbox state preserved")
        else:
            print("   ❌ Save operation failed - checkbox state reverted")
        
        print("\n✅ Final save operation test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_final_save_operation()
