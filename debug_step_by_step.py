#!/usr/bin/env python3
"""
Step-by-step debugging with breakpoints
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def debug_step_by_step():
    print("🔍 STEP-BY-STEP DEBUG WITH BREAKPOINTS")
    
    # Setup Chrome with debugging enabled
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    # Keep browser visible for debugging
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("\n🔍 BREAKPOINT 1: Opening login page")
        driver.get("http://localhost:5000/login")
        input("Press Enter when ready to continue...")
        
        print("\n🔍 BREAKPOINT 2: Logging in")
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "signin-email"))
        )
        password_input = driver.find_element(By.ID, "signin-password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        email_input.send_keys("tumd@tajir.com")
        password_input.send_keys("demo123")
        login_button.click()
        
        WebDriverWait(driver, 10).until(EC.url_contains("/app"))
        print("   ✅ Login successful")
        input("Press Enter when ready to continue...")
        
        print("\n🔍 BREAKPOINT 3: Check console for any JavaScript errors")
        logs = driver.get_log('browser')
        print(f"   📝 Current console logs: {len(logs)}")
        for log in logs:
            print(f"   {log['level']}: {log['message']}")
        input("Press Enter when ready to continue...")
        
        print("\n🔍 BREAKPOINT 4: Navigate to shop settings")
        print("   📝 Looking for shop settings button...")
        shop_settings_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-go='shopSettingsSec']"))
        )
        print("   📝 Shop settings button found, clicking...")
        shop_settings_btn.click()
        time.sleep(2)
        print("   ✅ Shop settings button clicked")
        input("Press Enter when ready to continue...")
        
        print("\n🔍 BREAKPOINT 5: Check if shop settings section is visible")
        section_visible = driver.execute_script("""
        const section = document.getElementById('shopSettingsSec');
        return section ? !section.classList.contains('hidden') : false;
        """)
        print(f"   📝 Shop settings section visible: {section_visible}")
        
        print("\n🔍 BREAKPOINT 6: Check console logs after navigation")
        logs = driver.get_log('browser')
        navigation_logs = [log for log in logs if any(keyword in log['message'] for keyword in ['🚀', '🔧', 'Navigated', 'Shop settings'])]
        if navigation_logs:
            print("   📝 Navigation logs found:")
            for log in navigation_logs:
                print(f"   {log['message']}")
        else:
            print("   ⚠️ No navigation logs found")
        input("Press Enter when ready to continue...")
        
        print("\n🔍 BREAKPOINT 7: Check if save button exists and has event listeners")
        save_btn_check = driver.execute_script("""
        const saveBtn = document.getElementById('saveShopSettingsBtn');
        return {
            exists: saveBtn !== null,
            visible: saveBtn ? saveBtn.offsetParent !== null : false,
            dataBound: saveBtn ? saveBtn.getAttribute('data-bound') : null,
            dataManualBound: saveBtn ? saveBtn.getAttribute('data-manual-bound') : null
        };
        """)
        print(f"   📝 Save button check: {save_btn_check}")
        input("Press Enter when ready to continue...")
        
        print("\n🔍 BREAKPOINT 8: Manually trigger save button click via JavaScript")
        click_result = driver.execute_script("""
        const saveBtn = document.getElementById('saveShopSettingsBtn');
        if (saveBtn) {
            console.log('🔧 MANUAL JS CLICK: Clicking save button...');
            saveBtn.click();
            return 'Button clicked via JavaScript';
        }
        return 'Button not found';
        """)
        print(f"   📝 Manual click result: {click_result}")
        time.sleep(2)
        input("Press Enter when ready to continue...")
        
        print("\n🔍 BREAKPOINT 9: Check console logs after manual click")
        logs = driver.get_log('browser')
        click_logs = [log for log in logs if any(keyword in log['message'] for keyword in ['MANUAL JS CLICK', 'MANUAL:', 'Save button clicked'])]
        if click_logs:
            print("   📝 Click logs found:")
            for log in click_logs:
                print(f"   {log['message']}")
        else:
            print("   ⚠️ No click logs found")
        
        print("\n🔍 FINAL ANALYSIS:")
        print("   1. If navigation logs are missing → Navigation system not loaded")
        print("   2. If save button exists but no click logs → Event listener not attached")
        print("   3. If manual JS click works → Original event listener is broken")
        
        input("Press Enter to close browser...")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        input("Press Enter to close browser...")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_step_by_step()
