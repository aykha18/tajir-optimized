#!/usr/bin/env python3
"""
Test if shop-settings.js is loading from network
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_js_network():
    print("🧪 Testing JavaScript Network Loading")
    
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
        
        # Wait for redirect to app
        WebDriverWait(driver, 10).until(
            EC.url_contains("/app")
        )
        print("   ✅ Login successful")
        
        # Step 2: Check if shop-settings.js is loaded by testing the URL directly
        print("\n🔍 Step 2: Testing shop-settings.js URL directly...")
        
        # Get the script src
        script_tags = driver.find_elements(By.CSS_SELECTOR, "script[src*='shop-settings.js']")
        if script_tags:
            script_src = script_tags[0].get_attribute('src')
            print(f"   📝 Script src: {script_src}")
            
            # Test if the URL is accessible
            try:
                driver.get(script_src)
                page_source = driver.page_source
                if 'loadShopSettings' in page_source:
                    print("   ✅ shop-settings.js is accessible and contains loadShopSettings function")
                else:
                    print("   ❌ shop-settings.js is accessible but doesn't contain loadShopSettings function")
                    print(f"   📝 Content preview: {page_source[:200]}...")
            except Exception as e:
                print(f"   ❌ Error accessing shop-settings.js: {e}")
        else:
            print("   ❌ No shop-settings.js script tag found")
        
        # Step 3: Check if the function exists in the global scope
        print("\n🔍 Step 3: Checking global scope...")
        
        # Check if the function exists
        load_shop_settings_exists = driver.execute_script("return typeof loadShopSettings === 'function'")
        print(f"   loadShopSettings function exists: {load_shop_settings_exists}")
        
        # Check if the module is loaded
        shop_settings_module_exists = driver.execute_script("return typeof window.shopSettings !== 'undefined'")
        print(f"   shopSettings module exists: {shop_settings_module_exists}")
        
        # Check if we can access the function through the module
        if shop_settings_module_exists:
            module_function_exists = driver.execute_script("return typeof window.shopSettings.loadShopSettings === 'function'")
            print(f"   shopSettings.loadShopSettings function exists: {module_function_exists}")
        
        # Step 4: Try to manually call the function
        print("\n🔄 Step 4: Trying to manually call loadShopSettings...")
        try:
            driver.execute_script("if (typeof loadShopSettings === 'function') { loadShopSettings(); } else { console.log('loadShopSettings function not found'); }")
            time.sleep(2)
            print("   ✅ Manual call attempted")
        except Exception as e:
            print(f"   ❌ Error calling loadShopSettings: {e}")
        
        # Step 5: Check console logs
        print("\n📋 Step 5: Checking console logs...")
        logs = driver.get_log('browser')
        
        for log in logs:
            if log['level'] == 'SEVERE':
                print(f"   ❌ {log['message']}")
            elif 'shop-settings' in log['message'].lower() or 'loadShopSettings' in log['message']:
                print(f"   📝 {log['message']}")
        
        print("\n✅ JavaScript network test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_js_network()
