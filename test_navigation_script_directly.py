#!/usr/bin/env python3
"""
Test the navigation script directly
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_navigation_script_directly():
    print("🔍 Testing Navigation Script Directly")
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Login
        driver.get("http://localhost:5000/login")
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
        
        # Test the navigation script directly
        result = driver.execute_script("""
        console.log('🔧 DIRECT TEST: Testing navigation script...');
        
        // Test 1: Check if DOMContentLoaded is already fired
        console.log('🔧 DIRECT TEST: Document ready state:', document.readyState);
        
        // Test 2: Manually execute the navigation system
        try {
            // Hide all sections
            document.querySelectorAll('.page').forEach(section => {
                section.classList.add('hidden');
            });
            
            // Show shop settings section
            const target = document.getElementById('shopSettingsSec');
            if (target) {
                target.classList.remove('hidden');
                console.log('🔧 DIRECT TEST: Shop settings section shown');
                
                // Initialize shop settings
                if (window.initializeShopSettings) {
                    console.log('🔧 DIRECT TEST: Calling initializeShopSettings...');
                    window.initializeShopSettings();
                    console.log('🔧 DIRECT TEST: initializeShopSettings called');
                } else {
                    console.log('🔧 DIRECT TEST: initializeShopSettings not available');
                }
                
                return 'Navigation test completed';
            } else {
                return 'Shop settings section not found';
            }
        } catch (e) {
            console.log('🔧 DIRECT TEST: Error:', e.message);
            return 'Error: ' + e.message;
        }
        """)
        
        print(f"   📝 Direct test result: {result}")
        time.sleep(2)
        
        # Check console logs
        logs = driver.get_log('browser')
        direct_logs = [log for log in logs if 'DIRECT TEST:' in log['message']]
        if direct_logs:
            print("   📝 Direct test logs:")
            for log in direct_logs:
                print(f"   {log['message']}")
        else:
            print("   ⚠️ No direct test logs found")
        
        # Test save button functionality
        save_test_result = driver.execute_script("""
        const saveBtn = document.getElementById('saveShopSettingsBtn');
        if (saveBtn) {
            console.log('🔧 SAVE TEST: Save button found');
            
            // Remove existing listeners and add new one
            const newBtn = saveBtn.cloneNode(true);
            saveBtn.parentNode.replaceChild(newBtn, saveBtn);
            
            newBtn.addEventListener('click', function(e) {
                console.log('🔧 SAVE TEST: Save button clicked!');
                e.preventDefault();
                
                const form = document.getElementById('shopSettingsForm');
                if (form && window.handleShopSettingsSubmit) {
                    console.log('🔧 SAVE TEST: Calling handleShopSettingsSubmit...');
                    window.handleShopSettingsSubmit({ preventDefault: () => {}, target: form });
                } else {
                    console.log('🔧 SAVE TEST: Form or handleShopSettingsSubmit not found');
                }
            });
            
            // Click the button
            newBtn.click();
            
            return 'Save test completed';
        }
        return 'Save button not found';
        """)
        
        print(f"   📝 Save test result: {save_test_result}")
        time.sleep(2)
        
        # Check save test logs
        logs = driver.get_log('browser')
        save_logs = [log for log in logs if 'SAVE TEST:' in log['message']]
        if save_logs:
            print("   📝 Save test logs:")
            for log in save_logs:
                print(f"   {log['message']}")
        else:
            print("   ⚠️ No save test logs found")
        
        print("\n✅ Navigation script test completed!")
        input("Press Enter to close browser...")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        input("Press Enter to close browser...")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_navigation_script_directly()
