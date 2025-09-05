#!/usr/bin/env python3
"""
Test if the navigation system is working
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_navigation_system():
    print("🧪 Testing Navigation System")
    
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
        
        # Step 2: Check console logs for navigation system
        print("\n🔍 Step 2: Checking console logs for navigation system...")
        logs = driver.get_log('browser')
        navigation_logs = [log for log in logs if '🚀' in log['message']]
        if navigation_logs:
            print("   📝 Navigation system logs found:")
            for log in navigation_logs:
                print(f"   {log['message']}")
        else:
            print("   ⚠️ No navigation system logs found")
        
        # Step 3: Check if navigation system functions exist
        print("\n🔍 Step 3: Checking if navigation system functions exist...")
        nav_check = driver.execute_script("""
        return {
            initializeShopSettings: typeof window.initializeShopSettings,
            setupSaveButton: typeof window.setupSaveButton,
            showModernNotification: typeof window.showModernNotification
        };
        """)
        print(f"   📝 Function availability: {nav_check}")
        
        # Step 4: Manually call initializeShopSettings
        print("\n🔧 Step 4: Manually calling initializeShopSettings...")
        manual_init = driver.execute_script("""
        if (window.initializeShopSettings) {
            console.log('🔧 Manually calling initializeShopSettings...');
            window.initializeShopSettings();
            return 'initializeShopSettings called manually';
        } else {
            return 'initializeShopSettings not available';
        }
        """)
        print(f"   📝 Manual init result: {manual_init}")
        
        # Step 5: Check console logs after manual call
        print("\n🔍 Step 5: Checking console logs after manual call...")
        logs = driver.get_log('browser')
        manual_logs = [log for log in logs if '🔧' in log['message']]
        if manual_logs:
            print("   📝 Manual call logs:")
            for log in manual_logs:
                print(f"   {log['message']}")
        else:
            print("   ⚠️ No manual call logs found")
        
        # Step 6: Try to navigate to shop settings
        print("\n⚙️ Step 6: Trying to navigate to shop settings...")
        shop_settings_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-go='shopSettingsSec']"))
        )
        shop_settings_btn.click()
        time.sleep(2)
        
        # Check if section is visible
        section_visible = driver.execute_script("""
        const section = document.getElementById('shopSettingsSec');
        return section ? !section.classList.contains('hidden') : false;
        """)
        print(f"   📝 Shop settings section visible: {section_visible}")
        
        # Step 7: Check console logs after navigation
        print("\n🔍 Step 7: Checking console logs after navigation...")
        logs = driver.get_log('browser')
        nav_logs = [log for log in logs if '🚀' in log['message']]
        if nav_logs:
            print("   📝 Navigation logs after click:")
            for log in nav_logs:
                print(f"   {log['message']}")
        else:
            print("   ⚠️ No navigation logs after click")
        
        print("\n✅ Navigation system test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_navigation_system()
