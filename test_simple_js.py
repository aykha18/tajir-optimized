#!/usr/bin/env python3
"""
Test simple JavaScript execution
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_simple_js():
    print("🧪 Testing Simple JavaScript Execution")
    
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
        
        # Step 3: Test simple JavaScript
        print("\n🔧 Step 3: Testing simple JavaScript...")
        simple_test = driver.execute_script("""
        console.log('Simple JS test - this should work');
        return 'Simple JS executed successfully';
        """)
        print(f"   📝 Simple JS result: {simple_test}")
        
        # Step 4: Test form data collection
        print("\n🔧 Step 4: Testing form data collection...")
        form_test = driver.execute_script("""
        const form = document.getElementById('shopSettingsForm');
        if (form) {
            const checkboxes = form.querySelectorAll('input[type="checkbox"]');
            const data = {};
            checkboxes.forEach(checkbox => {
                if (checkbox.name) {
                    data[checkbox.name] = checkbox.checked;
                }
            });
            console.log('Form data test:', data);
            return data;
        } else {
            return {error: 'Form not found'};
        }
        """)
        print(f"   📝 Form test result: {form_test}")
        
        # Step 5: Test API call
        print("\n🔧 Step 5: Testing API call...")
        api_test = driver.execute_script("""
        return fetch('/api/shop-settings', {
            method: 'GET',
            cache: 'no-cache'
        })
        .then(response => {
            console.log('API test - response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('API test - data received:', data);
            return data;
        })
        .catch(error => {
            console.log('API test - error:', error);
            return {error: error.message};
        });
        """)
        
        time.sleep(2)
        
        # Get the API result
        api_result = driver.execute_script("return window.manualApiResult;")
        if api_result:
            print(f"   📝 API test result: {api_result}")
        else:
            print("   ⚠️ No API test result")
        
        # Step 6: Check console logs
        print("\n🔍 Step 6: Checking console logs...")
        logs = driver.get_log('browser')
        if logs:
            print("   📝 Console logs:")
            for log in logs:
                print(f"   {log['level']}: {log['message']}")
        else:
            print("   ⚠️ No console logs found")
        
        print("\n✅ Simple JavaScript test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_simple_js()
