#!/usr/bin/env python3
"""
Systematic debugging of save button functionality
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def debug_save_button_systematic():
    print("🔍 SYSTEMATIC DEBUG: Save Button Functionality")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # STEP 1: Login
        print("\n🔍 STEP 1: Login")
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
        
        # STEP 2: Navigate to shop settings
        print("\n🔍 STEP 2: Navigate to shop settings")
        shop_settings_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-go='shopSettingsSec']"))
        )
        shop_settings_btn.click()
        time.sleep(2)
        print("   ✅ Shop settings section shown")
        
        # STEP 3: Check if save button exists and is accessible
        print("\n🔍 STEP 3: Check save button existence and accessibility")
        save_btn = driver.find_element(By.ID, "saveShopSettingsBtn")
        print(f"   📝 Save button found: {save_btn is not None}")
        print(f"   📝 Save button visible: {save_btn.is_displayed()}")
        print(f"   📝 Save button enabled: {save_btn.is_enabled()}")
        print(f"   📝 Save button data-bound: {save_btn.get_attribute('data-bound')}")
        
        # STEP 4: Check if event listeners are attached
        print("\n🔍 STEP 4: Check if event listeners are attached")
        event_listeners = driver.execute_script("""
        const saveBtn = document.getElementById('saveShopSettingsBtn');
        if (saveBtn) {
            // Check if the button has any event listeners by testing click
            let clickHandled = false;
            const testHandler = () => { clickHandled = true; };
            saveBtn.addEventListener('click', testHandler);
            saveBtn.click();
            saveBtn.removeEventListener('click', testHandler);
            
            return {
                hasListeners: clickHandled,
                buttonExists: true
            };
        }
        return { error: 'Save button not found' };
        """)
        print(f"   📝 Event listeners: {event_listeners}")
        
        # STEP 5: Manually attach event listener and test
        print("\n🔍 STEP 5: Manually attach event listener and test")
        manual_listener_result = driver.execute_script("""
        const saveBtn = document.getElementById('saveShopSettingsBtn');
        if (saveBtn) {
            // Remove any existing listeners
            const newBtn = saveBtn.cloneNode(true);
            saveBtn.parentNode.replaceChild(newBtn, saveBtn);
            
            // Add manual event listener
            newBtn.addEventListener('click', function(e) {
                console.log('🔧 MANUAL: Save button clicked!');
                e.preventDefault();
                
                // Get form data
                const form = document.getElementById('shopSettingsForm');
                if (form) {
                    console.log('🔧 MANUAL: Form found, collecting data...');
                    
                    // Collect checkbox data
                    const checkboxes = form.querySelectorAll('input[type="checkbox"]');
                    const checkboxData = {};
                    checkboxes.forEach(cb => {
                        checkboxData[cb.name] = cb.checked;
                        console.log('🔧 MANUAL: Checkbox', cb.name, '=', cb.checked);
                    });
                    
                    // Send to API
                    fetch('/api/shop-settings', {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(checkboxData)
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log('🔧 MANUAL: API response:', data);
                    })
                    .catch(error => {
                        console.log('🔧 MANUAL: API error:', error);
                    });
                } else {
                    console.log('🔧 MANUAL: Form not found');
                }
            });
            
            return 'Manual event listener attached';
        }
        return 'Save button not found';
        """)
        print(f"   📝 Manual listener result: {manual_listener_result}")
        
        # STEP 6: Toggle a checkbox
        print("\n🔍 STEP 6: Toggle a checkbox")
        checkbox = driver.find_element(By.ID, "bcEnableTrialDate")
        initial_state = checkbox.is_selected()
        checkbox.click()
        new_state = checkbox.is_selected()
        print(f"   📝 Trial Date: {initial_state} → {new_state}")
        
        # STEP 7: Click save button (get fresh reference)
        print("\n🔍 STEP 7: Click save button")
        save_btn = driver.find_element(By.ID, "saveShopSettingsBtn")  # Get fresh reference
        save_btn.click()
        time.sleep(3)
        print("   ✅ Save button clicked")
        
        # STEP 8: Check console logs
        print("\n🔍 STEP 8: Check console logs")
        logs = driver.get_log('browser')
        print(f"   📝 Total console logs: {len(logs)}")
        
        manual_logs = [log for log in logs if 'MANUAL:' in log['message']]
        if manual_logs:
            print("   📝 Manual event logs:")
            for log in manual_logs:
                print(f"   {log['message']}")
        else:
            print("   ⚠️ No manual event logs found")
            
        # Check all logs for any relevant information
        all_relevant_logs = [log for log in logs if any(keyword in log['message'] for keyword in ['click', 'save', 'button', 'form', 'API', 'error'])]
        if all_relevant_logs:
            print("   📝 All relevant logs:")
            for log in all_relevant_logs:
                print(f"   {log['level']}: {log['message']}")
        
        # STEP 9: Check checkbox state after save
        print("\n🔍 STEP 9: Check checkbox state after save")
        checkbox_after = driver.find_element(By.ID, "bcEnableTrialDate")
        final_state = checkbox_after.is_selected()
        print(f"   📝 Final checkbox state: {final_state}")
        
        # STEP 10: Check API response
        print("\n🔍 STEP 10: Check API response")
        api_response = driver.execute_script("""
        return fetch('/api/shop-settings?' + Date.now(), {
            cache: 'no-cache'
        })
        .then(response => response.json())
        .then(data => {
            console.log('🔧 API Response:', data);
            return data;
        })
        .catch(error => {
            console.log('🔧 API Error:', error);
            return {error: error.message};
        });
        """)
        time.sleep(2)
        
        api_result = driver.execute_script("return window.manualApiResult;")
        if api_result:
            print(f"   📝 API result: {api_result}")
        else:
            print("   ⚠️ No API result")
        
        print("\n✅ SYSTEMATIC DEBUG COMPLETED!")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_save_button_systematic()
