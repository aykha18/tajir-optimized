#!/usr/bin/env python3
"""
Debug what form data is being sent
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_debug_form_data():
    print("🔍 Debugging Form Data Being Sent")
    
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
        
        # Step 4: Debug what data will be sent
        print("\n🔍 Step 4: Debugging form data...")
        form_data = driver.execute_script("""
        const form = document.getElementById('shopSettingsForm');
        if (!form) {
            return { error: 'Form not found' };
        }
        
        // Collect all form data
        const formData = new FormData(form);
        const data = {};
        
        // Get all form fields
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        // Get checkbox values
        const checkboxes = form.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            data[checkbox.name] = checkbox.checked;
        });
        
        return data;
        """)
        
        print("   📝 Form data that will be sent:")
        for key, value in form_data.items():
            print(f"     {key}: {value}")
        
        # Step 5: Save and check console logs
        print("\n💾 Step 5: Saving and checking console logs...")
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
        
        # Step 6: Check console logs
        print("\n📋 Step 6: Checking console logs...")
        logs = driver.get_log('browser')
        
        # Look for save-related logs
        save_logs = []
        for log in logs:
            if any(keyword in log['message'] for keyword in ['💾', 'Form data collected', 'Save successful', 'Save failed', 'Save error']):
                save_logs.append(log)
        
        if save_logs:
            print("   📝 Save operation logs:")
            for log in save_logs:
                print(f"   {log['message']}")
        else:
            print("   ⚠️ No save operation logs found")
        
        print("\n✅ Form data debug completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_debug_form_data()
