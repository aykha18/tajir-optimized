#!/usr/bin/env python3
"""
Debug checkbox data not being saved
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def debug_checkbox_data():
    print("🔍 Debugging Checkbox Data Not Being Saved")
    
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
        
        # Step 4: Debug what data will be sent
        print("\n🔍 Step 4: Debugging what data will be sent...")
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
        
        // Get ALL checkbox values (including unchecked ones)
        const checkboxes = form.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            data[checkbox.name] = checkbox.checked;
        });
        
        // Also get number inputs
        const numberInputs = form.querySelectorAll('input[type="number"]');
        numberInputs.forEach(input => {
            data[input.name] = input.value;
        });
        
        return data;
        """)
        
        print("   📝 Form data that will be sent:")
        for key, value in form_data.items():
            print(f"     {key}: {value}")
        
        # Step 5: Save and check console logs
        print("\n💾 Step 5: Saving and checking console logs...")
        save_btn = driver.find_element(By.ID, "saveShopSettingsBtn")
        save_btn.click()
        time.sleep(3)
        
        # Check console logs
        logs = driver.get_log('browser')
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
        
        # Step 6: Check database values after save
        print("\n🔄 Step 6: Checking database values after save...")
        db_check = driver.execute_script("""
        return fetch('/api/shop-settings?' + Date.now(), {
            cache: 'no-cache'
        })
        .then(response => response.json())
        .then(data => {
            console.log('Database check result:', data);
            return data;
        })
        .catch(error => {
            console.log('Database check error:', error);
            return {error: error.message};
        });
        """)
        
        time.sleep(2)
        
        # Get the result
        db_result = driver.execute_script("return window.manualApiResult;")
        if db_result and 'settings' in db_result:
            settings = db_result['settings']
            print("   📊 Database values after save:")
            
            boolean_fields = [
                "enable_trial_date", "enable_delivery_date", "enable_advance_payment",
                "enable_customer_notes", "enable_employee_assignment", "use_dynamic_invoice_template"
            ]
            
            for field in boolean_fields:
                value = settings.get(field, False)
                status = "✅" if value else "❌"
                print(f"     {status} {field}: {value}")
        else:
            print(f"   ❌ Database check failed: {db_result}")
        
        print("\n✅ Checkbox data debug completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_checkbox_data()
