#!/usr/bin/env python3
"""
Test if shop-settings.js is loading and executing properly
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_shop_settings_loading():
    print("🧪 Testing Shop Settings JavaScript Loading")
    
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
        time.sleep(3)  # Give more time for JavaScript to load
        print("   ✅ Shop Settings section loaded")
        
        # Step 3: Check if shop-settings.js functions are available
        print("\n🔍 Step 3: Checking if shop-settings.js functions are available...")
        
        # Check if loadShopSettings function exists
        load_shop_settings_exists = driver.execute_script("return typeof loadShopSettings === 'function'")
        print(f"   loadShopSettings function exists: {load_shop_settings_exists}")
        
        # Check if populateShopSettingsForm function exists
        populate_form_exists = driver.execute_script("return typeof populateShopSettingsForm === 'function'")
        print(f"   populateShopSettingsForm function exists: {populate_form_exists}")
        
        # Try to manually call loadShopSettings
        if load_shop_settings_exists:
            print("\n🔄 Step 4: Manually calling loadShopSettings...")
            try:
                driver.execute_script("loadShopSettings()")
                time.sleep(2)
                print("   ✅ loadShopSettings called successfully")
            except Exception as e:
                print(f"   ❌ Error calling loadShopSettings: {e}")
        
        # Step 5: Check checkbox states after manual load
        print("\n🔍 Step 5: Checking checkbox states after manual load...")
        checkboxes = [
            ("enable_trial_date", "bcEnableTrialDate"),
            ("enable_delivery_date", "bcEnableDeliveryDate"),
            ("enable_advance_payment", "bcEnableAdvancePayment"),
            ("enable_customer_notes", "enableCustomerNotes"),
            ("enable_employee_assignment", "enableEmployeeAssignment")
        ]
        
        for name, id in checkboxes:
            try:
                checkbox = driver.find_element(By.NAME, name)
                checked = checkbox.is_selected()
                print(f"   {name}: checked={checked}")
            except Exception as e:
                print(f"   {name}: ERROR - {e}")
        
        # Step 6: Check console logs
        print("\n📋 Step 6: Checking console logs...")
        logs = driver.get_log('browser')
        error_count = 0
        for log in logs:
            if log['level'] == 'SEVERE':
                error_count += 1
                print(f"   ❌ {log['message']}")
            elif 'shop-settings' in log['message'].lower():
                print(f"   📝 {log['message']}")
        
        if error_count == 0:
            print("   ✅ No JavaScript errors found")
        
        print("\n✅ Shop settings loading test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_shop_settings_loading()
