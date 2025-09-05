#!/usr/bin/env python3
"""
Test the frontend directly to see what's happening
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_frontend_direct():
    print("🧪 Testing Frontend Directly")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Step 1: Login with correct credentials
        print("\n🔐 Step 1: Logging in with tumd@tajir.com...")
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
        
        # Step 3: Check console logs for debugging info
        print("\n📋 Step 3: Checking console logs...")
        logs = driver.get_log('browser')
        
        shop_settings_logs = []
        for log in logs:
            if any(keyword in log['message'] for keyword in ['populateShopSettingsForm', 'Setting checkbox', 'API response']):
                shop_settings_logs.append(log['message'])
        
        if shop_settings_logs:
            print("   📝 Shop Settings related logs:")
            for log in shop_settings_logs:
                print(f"   {log}")
        else:
            print("   ⚠️ No shop settings logs found")
        
        # Step 4: Manually call the API to see what it returns
        print("\n🔄 Step 4: Manually calling API...")
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
        
        # Wait for the promise to resolve
        time.sleep(2)
        
        # Get the result
        api_result = driver.execute_script("return window.manualApiResult;")
        if api_result:
            print("   📊 Manual API call result:")
            if 'settings' in api_result:
                settings = api_result['settings']
                user_id = settings.get('user_id')
                print(f"   📝 User ID: {user_id}")
                
                boolean_fields = [
                    "enable_trial_date", "enable_delivery_date", "enable_advance_payment",
                    "enable_customer_notes", "enable_employee_assignment"
                ]
                
                print("   📝 Boolean values from API:")
                for field in boolean_fields:
                    value = settings.get(field, False)
                    status = "✅" if value else "❌"
                    print(f"     {status} {field}: {value}")
            else:
                print(f"   ❌ API error: {api_result}")
        else:
            print("   ❌ No API result found")
        
        # Step 5: Check checkbox states in the UI
        print("\n🔍 Step 5: Checking checkbox states in UI...")
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
                status = "✅" if checked else "❌"
                print(f"   {status} {name}: checked={checked}")
            except Exception as e:
                print(f"   ❌ {name}: ERROR - {e}")
        
        # Step 6: Check if there's a mismatch between API and UI
        print("\n🔍 Step 6: Analyzing the issue...")
        if api_result and 'settings' in api_result:
            api_user_id = api_result['settings'].get('user_id')
            if api_user_id == 35:
                print("   ✅ API returns user_id 35 (correct)")
                api_values = [api_result['settings'].get(field, False) for field in boolean_fields]
                if all(api_values):
                    print("   ✅ API returns all True values (correct)")
                    print("   ❌ ISSUE: API is correct but UI shows False values")
                    print("   🔧 The problem is in the frontend JavaScript loading/population")
                else:
                    print("   ❌ API returns False values (incorrect)")
            else:
                print(f"   ❌ API returns user_id {api_user_id} (incorrect)")
        
        print("\n✅ Frontend test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_frontend_direct()
