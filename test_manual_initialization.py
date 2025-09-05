#!/usr/bin/env python3
"""
Test manual initialization of shop settings
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_manual_initialization():
    print("🧪 Manual Initialization Test")
    
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
        
        # Step 2: Navigate to shop settings
        print("\n⚙️ Step 2: Navigating to shop settings...")
        shop_settings_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-go='shopSettingsSec']"))
        )
        shop_settings_btn.click()
        time.sleep(2)
        
        # Step 3: Check if functions are available
        print("\n🔍 Step 3: Checking if functions are available...")
        functions_available = driver.execute_script("""
        return {
            initializeShopSettings: typeof window.initializeShopSettings === 'function',
            handleShopSettingsSubmit: typeof window.handleShopSettingsSubmit === 'function',
            loadShopSettings: typeof window.loadShopSettings === 'function'
        };
        """)
        
        print(f"   📝 Functions available: {functions_available}")
        
        # Step 4: Manually call initializeShopSettings
        print("\n🔧 Step 4: Manually calling initializeShopSettings...")
        init_result = driver.execute_script("""
        if (window.initializeShopSettings) {
            try {
                window.initializeShopSettings();
                return 'initializeShopSettings called successfully';
            } catch (e) {
                return 'Error calling initializeShopSettings: ' + e.message;
            }
        } else {
            return 'initializeShopSettings not available';
        }
        """)
        
        print(f"   📝 Initialize result: {init_result}")
        
        # Step 5: Check if save button is bound
        print("\n🔍 Step 5: Checking if save button is bound...")
        save_btn_info = driver.execute_script("""
        const saveBtn = document.getElementById('saveShopSettingsBtn');
        if (saveBtn) {
            return {
                exists: true,
                dataBound: saveBtn.getAttribute('data-bound'),
                visible: saveBtn.offsetParent !== null
            };
        } else {
            return { exists: false };
        }
        """)
        
        print(f"   📝 Save button info: {save_btn_info}")
        
        # Step 6: Try clicking save button
        print("\n💾 Step 6: Clicking save button...")
        try:
            save_btn = driver.find_element(By.ID, "saveShopSettingsBtn")
            save_btn.click()
            time.sleep(2)
            print("   ✅ Save button clicked")
        except Exception as e:
            print(f"   ❌ Error clicking save button: {e}")
        
        # Step 7: Check console logs
        print("\n📋 Step 7: Checking console logs...")
        logs = driver.get_log('browser')
        
        for log in logs:
            if any(keyword in log['message'] for keyword in ['Save button click event triggered', 'Save button clicked, form found', 'Calling handleShopSettingsSubmit', 'Form is null', 'initializeShopSettings', 'Setting up save button event listener']):
                print(f"   📝 {log['message']}")
        
        print("\n✅ Manual initialization test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_manual_initialization()
