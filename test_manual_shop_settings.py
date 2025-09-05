#!/usr/bin/env python3
"""
Test manual shop settings loading
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_manual_shop_settings():
    print("🧪 Testing Manual Shop Settings Loading")
    
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
        time.sleep(3)
        print("   ✅ Shop Settings section loaded")
        
        # Step 3: Manually call the API to load settings
        print("\n🔄 Step 3: Manually calling API to load settings...")
        
        # Execute JavaScript to manually call the API
        api_call_script = """
        fetch('/api/shop-settings?' + Date.now(), {
            cache: 'no-cache',
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('📡 Manual API call result:', data);
            window.manualApiResult = data;
        })
        .catch(error => {
            console.error('❌ Manual API call error:', error);
        });
        """
        
        driver.execute_script(api_call_script)
        time.sleep(2)
        
        # Check the result
        result = driver.execute_script("return window.manualApiResult;")
        if result:
            print("   ✅ Manual API call successful")
            print(f"   📊 Settings: {result}")
            
            # Check the boolean values
            if 'settings' in result:
                settings = result['settings']
                boolean_fields = [
                    "enable_trial_date", "enable_delivery_date", "enable_advance_payment",
                    "enable_customer_notes", "enable_employee_assignment"
                ]
                
                print("\n📋 Step 4: Checking API response values...")
                for field in boolean_fields:
                    value = settings.get(field, False)
                    status = "✅" if value else "❌"
                    print(f"   {status} {field}: {value}")
        else:
            print("   ❌ Manual API call failed")
        
        # Step 4: Manually populate the form
        print("\n🔄 Step 5: Manually populating form...")
        
        populate_script = """
        if (window.manualApiResult && window.manualApiResult.settings) {
            const settings = window.manualApiResult.settings;
            const form = document.getElementById('shopSettingsForm');
            
            if (form) {
                // Set checkbox values
                const booleanFields = [
                    'enable_trial_date', 'enable_delivery_date', 'enable_advance_payment',
                    'enable_customer_notes', 'enable_employee_assignment'
                ];
                
                booleanFields.forEach(field => {
                    const checkbox = form.querySelector(`[name="${field}"]`);
                    if (checkbox) {
                        checkbox.checked = Boolean(settings[field]);
                        console.log(`🔲 Set ${field}: ${checkbox.checked}`);
                    }
                });
                
                console.log('✅ Form populated manually');
            } else {
                console.log('❌ Form not found');
            }
        }
        """
        
        driver.execute_script(populate_script)
        time.sleep(1)
        
        # Step 5: Check checkbox states after manual population
        print("\n🔍 Step 6: Checking checkbox states after manual population...")
        checkboxes = [
            ("enable_trial_date", "bcEnableTrialDate"),
            ("enable_delivery_date", "bcEnableDeliveryDate"),
            ("enable_advance_payment", "bcEnableAdvancePayment"),
            ("enable_customer_notes", "enableCustomerNotes"),
            ("enable_employee_assignment", "enableEmployeeAssignment")
        ]
        
        all_checked = True
        for name, id in checkboxes:
            try:
                checkbox = driver.find_element(By.NAME, name)
                checked = checkbox.is_selected()
                status = "✅" if checked else "❌"
                print(f"   {status} {name}: checked={checked}")
                if not checked:
                    all_checked = False
            except Exception as e:
                print(f"   ❌ {name}: ERROR - {e}")
                all_checked = False
        
        # Step 6: Summary
        print("\n📊 Step 7: Summary...")
        if all_checked:
            print("   🎉 SUCCESS: All checkboxes are checked correctly!")
            print("   ✅ Manual population works - the issue is with automatic loading")
        else:
            print("   ❌ ISSUE: Some checkboxes are still not checked")
            print("   🔧 Manual population also failed")
        
        print("\n✅ Manual shop settings test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_manual_shop_settings()
