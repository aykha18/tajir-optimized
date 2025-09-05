#!/usr/bin/env python3
"""
Test the navigation fix
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_navigation_fix():
    print("🧪 Testing Navigation Fix")
    
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
        
        # Step 2: Check initial section visibility
        print("\n🔍 Step 2: Checking initial section visibility...")
        sections = driver.execute_script("""
        const sections = ['billingSec', 'dashSec', 'productsSec', 'customerSec', 'employeeSec', 'loyaltySec', 'shopSettingsSec'];
        const results = {};
        
        sections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) {
                results[sectionId] = {
                    exists: true,
                    hidden: section.classList.contains('hidden'),
                    visible: section.offsetParent !== null
                };
            } else {
                results[sectionId] = { exists: false };
            }
        });
        
        return results;
        """)
        
        print(f"   📝 Section visibility: {sections}")
        
        # Step 3: Click shop settings button
        print("\n⚙️ Step 3: Clicking shop settings button...")
        shop_settings_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-go='shopSettingsSec']"))
        )
        shop_settings_btn.click()
        time.sleep(2)
        
        # Step 4: Check section visibility after click
        print("\n🔍 Step 4: Checking section visibility after click...")
        sections_after = driver.execute_script("""
        const sections = ['billingSec', 'dashSec', 'productsSec', 'customerSec', 'employeeSec', 'loyaltySec', 'shopSettingsSec'];
        const results = {};
        
        sections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) {
                results[sectionId] = {
                    exists: true,
                    hidden: section.classList.contains('hidden'),
                    visible: section.offsetParent !== null
                };
            } else {
                results[sectionId] = { exists: false };
            }
        });
        
        return results;
        """)
        
        print(f"   📝 Section visibility after click: {sections_after}")
        
        # Step 5: Check console logs
        print("\n📋 Step 5: Checking console logs...")
        logs = driver.get_log('browser')
        
        navigation_logs = []
        for log in logs:
            if any(keyword in log['message'] for keyword in ['Navigated to', 'initializeShopSettings', 'Save button found during setup', 'Setting up save button event listener']):
                navigation_logs.append(log['message'])
        
        if navigation_logs:
            print("   📝 Navigation logs:")
            for log in navigation_logs:
                print(f"   {log}")
        else:
            print("   ⚠️ No navigation logs found")
        
        # Step 6: Check if save button is accessible
        print("\n🔍 Step 6: Checking save button accessibility...")
        save_btn_info = driver.execute_script("""
        const saveBtn = document.getElementById('saveShopSettingsBtn');
        return {
            exists: saveBtn !== null,
            visible: saveBtn ? saveBtn.offsetParent !== null : false,
            dataBound: saveBtn ? saveBtn.getAttribute('data-bound') : 'N/A'
        };
        """)
        
        print(f"   📝 Save button info: {save_btn_info}")
        
        # Step 7: Try clicking save button
        print("\n💾 Step 7: Clicking save button...")
        try:
            save_btn = driver.find_element(By.ID, "saveShopSettingsBtn")
            save_btn.click()
            time.sleep(2)
            print("   ✅ Save button clicked")
        except Exception as e:
            print(f"   ❌ Error clicking save button: {e}")
        
        # Step 8: Check console logs after clicking save
        print("\n📋 Step 8: Checking console logs after clicking save...")
        logs_after = driver.get_log('browser')
        
        new_logs = []
        for log in logs_after:
            if any(keyword in log['message'] for keyword in ['Save button click event triggered', 'Save button clicked, form found', 'Calling handleShopSettingsSubmit', 'Form is null']):
                if log not in logs:  # Only new logs
                    new_logs.append(log['message'])
        
        if new_logs:
            print("   📝 New logs after clicking save:")
            for log in new_logs:
                print(f"   {log}")
        else:
            print("   ⚠️ No new logs after clicking save")
        
        print("\n✅ Navigation fix test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_navigation_fix()
