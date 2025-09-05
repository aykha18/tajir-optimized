#!/usr/bin/env python3
"""
Test script to debug the trial date checkbox specifically
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_trial_date_checkbox():
    print("🧪 Testing Trial Date Checkbox Specifically")
    
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
        
        # Wait for shop settings section to be visible
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "shopSettingsSec"))
        )
        print("   ✅ Shop Settings section loaded")
        
        # Step 2.5: Click on Billing Configuration tab
        print("\n⚙️ Step 2.5: Clicking Billing Configuration tab...")
        billing_config_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "tabBillingConfig"))
        )
        billing_config_tab.click()
        time.sleep(1)
        print("   ✅ Billing Configuration tab opened")
        
        # Step 3: Find the trial date checkbox specifically
        print("\n🔍 Step 3: Finding trial date checkbox...")
        trial_checkbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "enableTrialDate"))
        )
        
        print(f"   Checkbox ID: {trial_checkbox.get_attribute('id')}")
        print(f"   Checkbox name: {trial_checkbox.get_attribute('name')}")
        print(f"   Is displayed: {trial_checkbox.is_displayed()}")
        print(f"   Is enabled: {trial_checkbox.is_enabled()}")
        print(f"   Initial checked state: {trial_checkbox.is_selected()}")
        print(f"   Initial style: {trial_checkbox.get_attribute('style')}")
        
        # Check if it has custom styling
        has_custom_styling = "appearance: none" in trial_checkbox.get_attribute('style')
        print(f"   Has custom styling: {has_custom_styling}")
        
        # Step 4: Click the checkbox and observe changes
        print("\n🖱️ Step 4: Clicking trial date checkbox...")
        initial_checked = trial_checkbox.is_selected()
        print(f"   Before click - checked: {initial_checked}")
        
        # Click the checkbox
        trial_checkbox.click()
        time.sleep(1)  # Give time for JS to process
        
        after_click_checked = trial_checkbox.is_selected()
        after_click_style = trial_checkbox.get_attribute('style')
        
        print(f"   After click - checked: {after_click_checked}")
        print(f"   After click - style: {after_click_style}")
        
        # Check if the visual state changed
        if after_click_checked != initial_checked:
            print("   ✅ Checkbox state changed successfully")
        else:
            print("   ❌ Checkbox state did not change")
        
        # Check for visual indicators
        if after_click_checked:
            has_blue_bg = "rgb(59, 130, 246)" in after_click_style or "#3b82f6" in after_click_style
            has_checkmark = "background-image: url(\"data:image/svg+xml" in after_click_style
            print(f"   Has blue background: {has_blue_bg}")
            print(f"   Has checkmark: {has_checkmark}")
        else:
            has_dark_bg = "rgb(31, 41, 55)" in after_click_style or "#1f2937" in after_click_style
            has_no_checkmark = "background-image: none" in after_click_style
            print(f"   Has dark background: {has_dark_bg}")
            print(f"   Has no checkmark: {has_no_checkmark}")
        
        # Step 5: Check console logs for any errors
        print("\n📋 Step 5: Checking console logs...")
        logs = driver.get_log('browser')
        error_logs = [log for log in logs if log['level'] == 'SEVERE']
        
        if error_logs:
            print(f"   Found {len(error_logs)} error logs:")
            for log in error_logs:
                print(f"   ❌ {log['message']}")
        else:
            print("   ✅ No JavaScript errors found")
        
        # Step 6: Try clicking again to toggle back
        print("\n🔄 Step 6: Clicking again to toggle back...")
        trial_checkbox.click()
        time.sleep(1)
        
        final_checked = trial_checkbox.is_selected()
        final_style = trial_checkbox.get_attribute('style')
        
        print(f"   Final checked state: {final_checked}")
        print(f"   Final style: {final_style}")
        
        if final_checked == initial_checked:
            print("   ✅ Checkbox toggled back successfully")
        else:
            print("   ❌ Checkbox did not toggle back properly")
        
        print("\n✅ Trial date checkbox test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()

if __name__ == "__main__":
    test_trial_date_checkbox()
