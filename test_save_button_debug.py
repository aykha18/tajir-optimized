#!/usr/bin/env python3
"""
Test the save button with detailed debugging
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_save_button_debug():
    print("🧪 Testing Save Button with Detailed Debugging")
    
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
        
        # Step 2: Navigate to Shop Settings
        print("\n⚙️ Step 2: Navigating to Shop Settings...")
        shop_settings_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-go='shopSettingsSec']"))
        )
        shop_settings_btn.click()
        time.sleep(3)
        print("   ✅ Shop Settings section loaded")
        
        # Step 3: Check if the save button exists and is bound
        print("\n🔍 Step 3: Checking save button...")
        save_btn = driver.find_element(By.ID, "saveShopSettingsBtn")
        print(f"   📝 Save button found: {save_btn is not None}")
        print(f"   📝 Save button text: {save_btn.text}")
        print(f"   📝 Save button data-bound: {save_btn.get_attribute('data-bound')}")
        
        # Step 4: Check if the JavaScript functions exist
        print("\n🔍 Step 4: Checking JavaScript functions...")
        functions_exist = driver.execute_script("""
        return {
            handleShopSettingsSubmit: typeof handleShopSettingsSubmit === 'function',
            loadShopSettings: typeof loadShopSettings === 'function',
            initializeShopSettings: typeof initializeShopSettings === 'function'
        };
        """)
        print(f"   📝 Functions exist: {functions_exist}")
        
        # Step 5: Check if the form exists
        print("\n🔍 Step 5: Checking form...")
        form = driver.find_element(By.ID, "shopSettingsForm")
        print(f"   📝 Form found: {form is not None}")
        
        # Step 6: Toggle a checkbox
        print("\n🔄 Step 6: Toggling a checkbox...")
        checkbox = driver.find_element(By.ID, "bcEnableTrialDate")
        initial_state = checkbox.is_selected()
        checkbox.click()
        new_state = checkbox.is_selected()
        print(f"   🔄 Trial Date: {initial_state} → {new_state}")
        
        # Step 7: Try to manually call the save function
        print("\n🔄 Step 7: Manually calling save function...")
        try:
            result = driver.execute_script("""
            if (typeof handleShopSettingsSubmit === 'function') {
                console.log('Calling handleShopSettingsSubmit...');
                const event = new Event('submit');
                handleShopSettingsSubmit(event);
                return 'Function called successfully';
            } else {
                return 'Function not found';
            }
            """)
            print(f"   📝 Manual save result: {result}")
        except Exception as e:
            print(f"   ❌ Error calling save function: {e}")
        
        # Step 8: Check console logs
        print("\n📋 Step 8: Checking console logs...")
        logs = driver.get_log('browser')
        
        for log in logs:
            if any(keyword in log['message'] for keyword in ['handleShopSettingsSubmit', 'save', 'submit', 'Form data being sent', 'getFieldChecked', 'API response', 'Error']):
                print(f"   📝 {log['message']}")
        
        # Step 9: Check if there are any JavaScript errors
        print("\n🔍 Step 9: Checking for JavaScript errors...")
        error_logs = [log for log in logs if log['level'] == 'SEVERE']
        if error_logs:
            print("   ❌ JavaScript errors found:")
            for log in error_logs:
                print(f"   {log['message']}")
        else:
            print("   ✅ No JavaScript errors found")
        
        # Step 10: Try clicking the save button
        print("\n💾 Step 10: Clicking save button...")
        save_btn.click()
        time.sleep(2)
        
        # Check console logs after clicking
        print("\n📋 Step 11: Checking console logs after clicking save...")
        logs_after = driver.get_log('browser')
        
        new_logs = []
        for log in logs_after:
            if any(keyword in log['message'] for keyword in ['handleShopSettingsSubmit', 'save', 'submit', 'Form data being sent', 'getFieldChecked', 'API response', 'Error']):
                if log not in logs:  # Only new logs
                    new_logs.append(log['message'])
        
        if new_logs:
            print("   📝 New logs after clicking save:")
            for log in new_logs:
                print(f"   {log}")
        else:
            print("   ⚠️ No new logs after clicking save")
        
        print("\n✅ Save button debug test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_save_button_debug()
