#!/usr/bin/env python3
"""
Test the specific elements you provided
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_specific_elements():
    print("🧪 Testing Specific Elements")
    
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
        
        # Step 3: Check the specific checkboxes you mentioned
        print("\n🔍 Step 3: Checking specific checkboxes...")
        
        # Check each checkbox by the exact IDs you provided
        checkboxes_to_check = [
            ("bcEnableTrialDate", "enable_trial_date"),
            ("bcEnableDeliveryDate", "enable_delivery_date"), 
            ("bcEnableAdvancePayment", "enable_advance_payment"),
            ("useDynamicInvoiceTemplate", "use_dynamic_invoice_template"),
            ("enableCustomerNotes", "enable_customer_notes"),
            ("enableEmployeeAssignment", "enable_employee_assignment")
        ]
        
        for checkbox_id, name in checkboxes_to_check:
            try:
                checkbox = driver.find_element(By.ID, checkbox_id)
                checked = checkbox.is_selected()
                status = "✅" if checked else "❌"
                print(f"   {status} {checkbox_id} ({name}): checked={checked}")
                
                # Also check the value attribute
                value = checkbox.get_attribute('value')
                print(f"      Value attribute: {value}")
                
            except Exception as e:
                print(f"   ❌ {checkbox_id}: ERROR - {e}")
        
        # Step 4: Check the number inputs
        print("\n🔍 Step 4: Checking number inputs...")
        number_inputs = [
            ("defaultTrialDays", "default_trial_days"),
            ("defaultDeliveryDaysCfg", "default_delivery_days")
        ]
        
        for input_id, name in number_inputs:
            try:
                input_field = driver.find_element(By.ID, input_id)
                value = input_field.get_attribute('value')
                print(f"   📝 {input_id} ({name}): value={value}")
            except Exception as e:
                print(f"   ❌ {input_id}: ERROR - {e}")
        
        # Step 5: Check console logs
        print("\n📋 Step 5: Checking console logs...")
        logs = driver.get_log('browser')
        
        shop_settings_logs = []
        for log in logs:
            if any(keyword in log['message'] for keyword in ['populateShopSettingsForm', 'Setting checkbox', 'API response', 'loadShopSettings']):
                shop_settings_logs.append(log['message'])
        
        if shop_settings_logs:
            print("   📝 Shop Settings related logs:")
            for log in shop_settings_logs:
                print(f"   {log}")
        else:
            print("   ⚠️ No shop settings logs found")
        
        # Step 6: Manually call the API to see what it returns
        print("\n🔄 Step 6: Manually calling API...")
        api_result = driver.execute_script("""
        return fetch('/api/shop-settings?' + Date.now(), {
            cache: 'no-cache',
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Manual API call result:', data);
            return data;
        })
        .catch(error => {
            console.error('Manual API call error:', error);
            return {error: error.message};
        });
        """)
        
        time.sleep(2)
        
        # Get the result
        api_result = driver.execute_script("return window.manualApiResult;")
        if api_result and 'settings' in api_result:
            settings = api_result['settings']
            user_id = settings.get('user_id')
            print(f"   📊 API returned user_id: {user_id}")
            
            boolean_fields = [
                "enable_trial_date", "enable_delivery_date", "enable_advance_payment",
                "enable_customer_notes", "enable_employee_assignment", "use_dynamic_invoice_template"
            ]
            
            print("   📝 API boolean values:")
            for field in boolean_fields:
                value = settings.get(field, False)
                status = "✅" if value else "❌"
                print(f"     {status} {field}: {value}")
        else:
            print(f"   ❌ API call failed: {api_result}")
        
        # Step 7: Try to manually populate the form
        print("\n🔄 Step 7: Manually populating form...")
        populate_script = """
        if (window.manualApiResult && window.manualApiResult.settings) {
            const settings = window.manualApiResult.settings;
            
            // Set checkbox values using the exact IDs
            const checkboxMappings = [
                ['bcEnableTrialDate', 'enable_trial_date'],
                ['bcEnableDeliveryDate', 'enable_delivery_date'],
                ['bcEnableAdvancePayment', 'enable_advance_payment'],
                ['useDynamicInvoiceTemplate', 'use_dynamic_invoice_template'],
                ['enableCustomerNotes', 'enable_customer_notes'],
                ['enableEmployeeAssignment', 'enable_employee_assignment']
            ];
            
            checkboxMappings.forEach(([id, name]) => {
                const checkbox = document.getElementById(id);
                if (checkbox) {
                    checkbox.checked = Boolean(settings[name]);
                    console.log(`🔲 Manually set ${id} (${name}): ${checkbox.checked}`);
                } else {
                    console.log(`❌ Checkbox ${id} not found`);
                }
            });
            
            // Set number inputs
            const numberMappings = [
                ['defaultTrialDays', 'default_trial_days'],
                ['defaultDeliveryDaysCfg', 'default_delivery_days']
            ];
            
            numberMappings.forEach(([id, name]) => {
                const input = document.getElementById(id);
                if (input) {
                    input.value = settings[name] || 0;
                    console.log(`🔢 Manually set ${id} (${name}): ${input.value}`);
                } else {
                    console.log(`❌ Input ${id} not found`);
                }
            });
            
            console.log('✅ Manual form population completed');
        }
        """
        
        driver.execute_script(populate_script)
        time.sleep(1)
        
        # Step 8: Check checkbox states after manual population
        print("\n🔍 Step 8: Checking checkbox states after manual population...")
        for checkbox_id, name in checkboxes_to_check:
            try:
                checkbox = driver.find_element(By.ID, checkbox_id)
                checked = checkbox.is_selected()
                status = "✅" if checked else "❌"
                print(f"   {status} {checkbox_id} ({name}): checked={checked}")
            except Exception as e:
                print(f"   ❌ {checkbox_id}: ERROR - {e}")
        
        print("\n✅ Specific elements test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_specific_elements()
