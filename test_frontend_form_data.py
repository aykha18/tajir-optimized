#!/usr/bin/env python3
"""
Test script to check what data the frontend is actually sending
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json

def test_frontend_form_data():
    print("🧪 Testing Frontend Form Data Submission")
    
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
        time.sleep(2)
        print("   ✅ Shop Settings section loaded")
        
        # Step 3: Click on Billing Configuration tab
        print("\n⚙️ Step 3: Clicking Billing Configuration tab...")
        billing_config_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "tabBillingConfig"))
        )
        billing_config_tab.click()
        time.sleep(1)
        print("   ✅ Billing Configuration tab opened")
        
        # Step 4: Check current checkbox states
        print("\n🔍 Step 4: Checking current checkbox states...")
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
                print(f"   {name}: checked={checkbox.is_selected()}, displayed={checkbox.is_displayed()}")
            except Exception as e:
                print(f"   {name}: ERROR - {e}")
        
        # Step 5: Click some checkboxes
        print("\n🖱️ Step 5: Clicking checkboxes...")
        trial_checkbox = driver.find_element(By.NAME, "enable_trial_date")
        delivery_checkbox = driver.find_element(By.NAME, "enable_delivery_date")
        
        print(f"   Before: trial={trial_checkbox.is_selected()}, delivery={delivery_checkbox.is_selected()}")
        
        trial_checkbox.click()
        delivery_checkbox.click()
        
        print(f"   After: trial={trial_checkbox.is_selected()}, delivery={delivery_checkbox.is_selected()}")
        
        # Step 6: Check what data would be sent
        print("\n📋 Step 6: Checking form data...")
        
        # Get all form fields
        form = driver.find_element(By.ID, "shopSettingsForm")
        form_data = {}
        
        # Get text inputs
        text_inputs = form.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='number']")
        for input_elem in text_inputs:
            name = input_elem.get_attribute('name')
            if name:
                form_data[name] = input_elem.get_attribute('value')
        
        # Get checkboxes
        checkbox_inputs = form.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        for checkbox in checkbox_inputs:
            name = checkbox.get_attribute('name')
            if name:
                form_data[name] = checkbox.is_selected()
        
        print("   Form data that would be sent:")
        for key, value in form_data.items():
            print(f"   {key}: {value} (type: {type(value)})")
        
        # Step 7: Try to save and see what happens
        print("\n💾 Step 7: Attempting to save...")
        save_btn = driver.find_element(By.ID, "saveShopSettingsBtn")
        save_btn.click()
        time.sleep(2)
        
        # Check console logs for any errors
        print("\n📋 Step 8: Checking console logs...")
        logs = driver.get_log('browser')
        for log in logs:
            if log['level'] == 'SEVERE':
                print(f"   ❌ {log['message']}")
        
        print("\n✅ Frontend form data test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_frontend_form_data()
