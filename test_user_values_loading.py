#!/usr/bin/env python3
"""
Test if shop settings values are loaded correctly for user td@tajir.com
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_user_values_loading():
    print("🧪 Testing Shop Settings Values Loading for td@tajir.com")
    
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
        print("\n🔐 Step 1: Logging in as td@tajir.com...")
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
        
        # Step 3: Check what values are loaded from the database
        print("\n🔍 Step 3: Checking loaded values from database...")
        api_result = driver.execute_script("""
        return fetch('/api/shop-settings?' + Date.now(), {
            cache: 'no-cache'
        })
        .then(response => response.json())
        .then(data => {
            console.log('API Response:', data);
            return data;
        })
        .catch(error => {
            console.log('API Error:', error);
            return {error: error.message};
        });
        """)
        
        time.sleep(2)
        
        # Get the result
        api_result = driver.execute_script("return window.manualApiResult;")
        if api_result and 'settings' in api_result:
            settings = api_result['settings']
            user_id = settings.get('user_id')
            print(f"   📊 Database values for user_id: {user_id}")
            
            boolean_fields = [
                "enable_trial_date", "enable_delivery_date", "enable_advance_payment",
                "enable_customer_notes", "enable_employee_assignment", "use_dynamic_invoice_template"
            ]
            
            print("   📝 Database boolean values:")
            for field in boolean_fields:
                value = settings.get(field, False)
                status = "✅" if value else "❌"
                print(f"     {status} {field}: {value}")
        else:
            print(f"   ❌ API call failed: {api_result}")
        
        # Step 4: Check what values are displayed in the UI
        print("\n🔍 Step 4: Checking UI checkbox values...")
        checkboxes_to_check = [
            ("bcEnableTrialDate", "enable_trial_date"),
            ("bcEnableDeliveryDate", "enable_delivery_date"), 
            ("bcEnableAdvancePayment", "enable_advance_payment"),
            ("useDynamicInvoiceTemplate", "use_dynamic_invoice_template"),
            ("enableCustomerNotes", "enable_customer_notes"),
            ("enableEmployeeAssignment", "enable_employee_assignment")
        ]
        
        ui_values = {}
        for checkbox_id, name in checkboxes_to_check:
            try:
                checkbox = driver.find_element(By.ID, checkbox_id)
                checked = checkbox.is_selected()
                ui_values[name] = checked
                status = "✅" if checked else "❌"
                print(f"   {status} {checkbox_id} ({name}): checked={checked}")
            except Exception as e:
                print(f"   ❌ {checkbox_id}: ERROR - {e}")
        
        # Step 5: Compare database vs UI values
        print("\n🔍 Step 5: Comparing database vs UI values...")
        if api_result and 'settings' in api_result:
            settings = api_result['settings']
            mismatches = []
            
            for field in boolean_fields:
                db_value = settings.get(field, False)
                ui_value = ui_values.get(field, False)
                
                if db_value != ui_value:
                    mismatches.append(f"{field}: DB={db_value}, UI={ui_value}")
                    print(f"   ❌ MISMATCH: {field} - DB={db_value}, UI={ui_value}")
                else:
                    print(f"   ✅ MATCH: {field} - DB={db_value}, UI={ui_value}")
            
            if mismatches:
                print(f"\n   ⚠️ Found {len(mismatches)} mismatches between database and UI")
            else:
                print(f"\n   ✅ All values match between database and UI")
        
        # Step 6: Check if save button exists and is functional
        print("\n🔍 Step 6: Checking save button functionality...")
        try:
            save_btn = driver.find_element(By.ID, "saveShopSettingsBtn")
            print(f"   📝 Save button exists: {save_btn is not None}")
            print(f"   📝 Save button visible: {save_btn.is_displayed()}")
            print(f"   📝 Save button enabled: {save_btn.is_enabled()}")
            
            # Check if it has event listeners
            has_listeners = driver.execute_script("""
            const saveBtn = document.getElementById('saveShopSettingsBtn');
            if (saveBtn) {
                // Test if clicking triggers any response
                let clicked = false;
                const testHandler = () => { clicked = true; };
                saveBtn.addEventListener('click', testHandler);
                saveBtn.click();
                saveBtn.removeEventListener('click', testHandler);
                return clicked;
            }
            return false;
            """)
            print(f"   📝 Save button has event listeners: {has_listeners}")
            
        except Exception as e:
            print(f"   ❌ Save button error: {e}")
        
        print("\n✅ Values loading test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_user_values_loading()
