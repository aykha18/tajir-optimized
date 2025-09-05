#!/usr/bin/env python3
"""
Check what user is logged in via browser session
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def check_browser_session():
    print("🔍 Checking Browser Session")
    
    # Setup Chrome options - NOT headless so we can see what's happening
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Step 1: Go to the app page directly (assuming you're already logged in)
        print("\n🌐 Step 1: Going to app page...")
        driver.get("http://localhost:5000/app")
        time.sleep(3)
        
        # Step 2: Check if we're redirected to login
        current_url = driver.current_url
        print(f"   Current URL: {current_url}")
        
        if "login" in current_url:
            print("   ❌ Redirected to login - not logged in")
            return
        
        # Step 3: Navigate to Shop Settings
        print("\n⚙️ Step 2: Navigating to Shop Settings...")
        try:
            shop_settings_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-go='shopSettingsSec']"))
            )
            shop_settings_btn.click()
            time.sleep(3)
            print("   ✅ Shop Settings section loaded")
        except Exception as e:
            print(f"   ❌ Could not navigate to Shop Settings: {e}")
            return
        
        # Step 4: Check what user we're logged in as
        print("\n🔍 Step 3: Checking logged-in user...")
        user_info = driver.execute_script("""
        // Check if there's user info in the page
        const userElements = document.querySelectorAll('[data-user-id], .user-id, #user-id');
        let userInfo = {};
        
        userElements.forEach(el => {
            if (el.dataset.userId) userInfo.user_id = el.dataset.userId;
            if (el.textContent && el.textContent.includes('user')) userInfo.text = el.textContent;
        });
        
        // Also check localStorage/sessionStorage
        userInfo.localStorage = {};
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key.includes('user') || key.includes('id')) {
                userInfo.localStorage[key] = localStorage.getItem(key);
            }
        }
        
        return userInfo;
        """)
        
        print(f"   📊 User info from page: {user_info}")
        
        # Step 5: Call API to check user
        print("\n🔄 Step 4: Calling API to check user...")
        api_result = driver.execute_script("""
        return fetch('/api/shop-settings')
        .then(response => response.json())
        .then(data => {
            console.log('API result:', data);
            return data;
        })
        .catch(error => {
            console.error('API error:', error);
            return {error: error.message};
        });
        """)
        
        time.sleep(2)
        
        # Get the result
        api_result = driver.execute_script("return window.manualApiResult || 'No result';")
        print(f"   📊 API result: {api_result}")
        
        # Step 6: Check checkbox states
        print("\n🔍 Step 5: Checking checkbox states...")
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
        
        # Step 7: Check console logs
        print("\n📋 Step 6: Checking console logs...")
        logs = driver.get_log('browser')
        
        for log in logs:
            if any(keyword in log['message'] for keyword in ['populateShopSettingsForm', 'Setting checkbox', 'API response', 'user_id']):
                print(f"   📝 {log['message']}")
        
        print("\n✅ Browser session check completed!")
        print("\n💡 If you see this browser window, please check:")
        print("   1. Are you logged in as the correct user?")
        print("   2. Do the checkboxes show as checked or unchecked?")
        print("   3. What do the console logs show?")
        
        # Keep browser open for manual inspection
        input("\nPress Enter to close the browser...")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    check_browser_session()
