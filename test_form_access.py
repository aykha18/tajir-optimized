#!/usr/bin/env python3
"""
Test if the form is accessible
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_form_access():
    print("🧪 Testing Form Access")
    
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
        
        # Step 2: Navigate to Shop Settings
        print("\n⚙️ Step 2: Navigating to Shop Settings...")
        shop_settings_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-go='shopSettingsSec']"))
        )
        shop_settings_btn.click()
        time.sleep(3)
        print("   ✅ Shop Settings section loaded")
        
        # Step 3: Check if form is accessible
        print("\n🔍 Step 3: Checking form accessibility...")
        form_info = driver.execute_script("""
        const form = document.getElementById('shopSettingsForm');
        return {
            exists: form !== null,
            visible: form ? form.offsetParent !== null : false,
            display: form ? window.getComputedStyle(form).display : 'N/A',
            visibility: form ? window.getComputedStyle(form).visibility : 'N/A',
            className: form ? form.className : 'N/A',
            id: form ? form.id : 'N/A'
        };
        """)
        
        print(f"   📝 Form info: {form_info}")
        
        # Step 4: Check if save button is accessible
        print("\n🔍 Step 4: Checking save button accessibility...")
        save_btn_info = driver.execute_script("""
        const saveBtn = document.getElementById('saveShopSettingsBtn');
        return {
            exists: saveBtn !== null,
            visible: saveBtn ? saveBtn.offsetParent !== null : false,
            display: saveBtn ? window.getComputedStyle(saveBtn).display : 'N/A',
            visibility: saveBtn ? window.getComputedStyle(saveBtn).visibility : 'N/A',
            className: saveBtn ? saveBtn.className : 'N/A',
            id: saveBtn ? saveBtn.id : 'N/A'
        };
        """)
        
        print(f"   📝 Save button info: {save_btn_info}")
        
        # Step 5: Try to manually find the form
        print("\n🔍 Step 5: Manually finding form...")
        form_found = driver.execute_script("""
        // Try different ways to find the form
        const methods = {
            byId: document.getElementById('shopSettingsForm'),
            byQuerySelector: document.querySelector('#shopSettingsForm'),
            byQuerySelectorAll: document.querySelectorAll('#shopSettingsForm')[0],
            byTagName: document.getElementsByTagName('form')[0]
        };
        
        const results = {};
        for (const [method, element] of Object.entries(methods)) {
            results[method] = {
                found: element !== null,
                id: element ? element.id : 'N/A',
                tagName: element ? element.tagName : 'N/A'
            };
        }
        
        return results;
        """)
        
        print(f"   📝 Form search results: {form_found}")
        
        # Step 6: Check if the form is in the DOM
        print("\n🔍 Step 6: Checking DOM structure...")
        dom_info = driver.execute_script("""
        const forms = document.querySelectorAll('form');
        const results = [];
        
        forms.forEach((form, index) => {
            results.push({
                index: index,
                id: form.id || 'no-id',
                className: form.className || 'no-class',
                visible: form.offsetParent !== null
            });
        });
        
        return results;
        """)
        
        print(f"   📝 All forms in DOM: {dom_info}")
        
        print("\n✅ Form access test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_form_access()
