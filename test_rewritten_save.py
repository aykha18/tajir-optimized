#!/usr/bin/env python3
"""
Test the completely rewritten save functionality
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_rewritten_save():
    print("🧪 Testing Completely Rewritten Save Functionality")
    
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
        
        # Step 3: Check initial checkbox states
        print("\n🔍 Step 3: Checking initial checkbox states...")
        checkboxes_to_check = [
            ("bcEnableTrialDate", "enable_trial_date"),
            ("bcEnableDeliveryDate", "enable_delivery_date"), 
            ("bcEnableAdvancePayment", "enable_advance_payment"),
            ("useDynamicInvoiceTemplate", "use_dynamic_invoice_template"),
            ("enableCustomerNotes", "enable_customer_notes"),
            ("enableEmployeeAssignment", "enable_employee_assignment")
        ]
        
        initial_states = {}
        for checkbox_id, name in checkboxes_to_check:
            try:
                checkbox = driver.find_element(By.ID, checkbox_id)
                checked = checkbox.is_selected()
                initial_states[checkbox_id] = checked
                status = "✅" if checked else "❌"
                print(f"   {status} {checkbox_id} ({name}): checked={checked}")
            except Exception as e:
                print(f"   ❌ {checkbox_id}: ERROR - {e}")
        
        # Step 4: Change some checkbox values
        print("\n🔄 Step 4: Changing some checkbox values...")
        
        # Toggle a few checkboxes
        toggles = [
            ("bcEnableTrialDate", "Trial Date"),
            ("bcEnableAdvancePayment", "Advance Payment"),
            ("enableCustomerNotes", "Customer Notes")
        ]
        
        for checkbox_id, label in toggles:
            try:
                checkbox = driver.find_element(By.ID, checkbox_id)
                current_state = checkbox.is_selected()
                checkbox.click()  # Toggle the checkbox
                new_state = checkbox.is_selected()
                print(f"   🔄 {label}: {current_state} → {new_state}")
            except Exception as e:
                print(f"   ❌ Error toggling {checkbox_id}: {e}")
        
        time.sleep(1)
        
        # Step 5: Check states after toggling
        print("\n🔍 Step 5: Checking states after toggling...")
        for checkbox_id, name in checkboxes_to_check:
            try:
                checkbox = driver.find_element(By.ID, checkbox_id)
                checked = checkbox.is_selected()
                status = "✅" if checked else "❌"
                print(f"   {status} {checkbox_id} ({name}): checked={checked}")
            except Exception as e:
                print(f"   ❌ {checkbox_id}: ERROR - {e}")
        
        # Step 6: Click Save Settings
        print("\n💾 Step 6: Clicking Save Settings...")
        try:
            save_btn = driver.find_element(By.ID, "saveShopSettingsBtn")
            print("   📝 Save button found, clicking...")
            save_btn.click()
            print("   ✅ Save button clicked")
            time.sleep(3)  # Wait for save to complete
        except Exception as e:
            print(f"   ❌ Error clicking save button: {e}")
        
        # Step 7: Check console logs for save operation
        print("\n📋 Step 7: Checking console logs for save operation...")
        logs = driver.get_log('browser')
        
        # Look for save-related logs
        save_logs = []
        for log in logs:
            if any(keyword in log['message'] for keyword in ['💾', 'Save button clicked', 'Form data collected', 'Save successful', 'Save failed', 'Save error']):
                save_logs.append(log)
        
        if save_logs:
            print("   📝 Save operation logs:")
            for log in save_logs:
                print(f"   {log['message']}")
        else:
            print("   ⚠️ No save operation logs found")
        
        # Step 8: Check checkbox states after save
        print("\n🔍 Step 8: Checking checkbox states after save...")
        for checkbox_id, name in checkboxes_to_check:
            try:
                checkbox = driver.find_element(By.ID, checkbox_id)
                checked = checkbox.is_selected()
                status = "✅" if checked else "❌"
                print(f"   {status} {checkbox_id} ({name}): checked={checked}")
            except Exception as e:
                print(f"   ❌ {checkbox_id}: ERROR - {e}")
        
        # Step 9: Check if alert appeared (success/error message)
        print("\n🔍 Step 9: Checking for alert messages...")
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"   📝 Alert message: {alert_text}")
            alert.accept()  # Close the alert
        except:
            print("   ⚠️ No alert message found")
        
        print("\n✅ Rewritten save functionality test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_rewritten_save()
