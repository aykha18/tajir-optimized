#!/usr/bin/env python3
"""
Test if shop-settings.js is loading properly
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_js_loading():
    print("🧪 Testing JavaScript Loading")
    
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
        
        # Step 2: Check if shop-settings.js is loaded
        print("\n🔍 Step 2: Checking if shop-settings.js is loaded...")
        
        # Check if the function exists
        load_shop_settings_exists = driver.execute_script("return typeof loadShopSettings === 'function'")
        print(f"   loadShopSettings function exists: {load_shop_settings_exists}")
        
        # Check if we can call it manually
        if load_shop_settings_exists:
            print("\n🔄 Step 3: Manually calling loadShopSettings...")
            try:
                driver.execute_script("loadShopSettings()")
                time.sleep(2)
                print("   ✅ loadShopSettings called successfully")
            except Exception as e:
                print(f"   ❌ Error calling loadShopSettings: {e}")
        
        # Step 4: Check console logs
        print("\n📋 Step 4: Checking console logs...")
        logs = driver.get_log('browser')
        
        for log in logs:
            if log['level'] == 'SEVERE':
                print(f"   ❌ {log['message']}")
            elif 'shop-settings' in log['message'].lower() or 'loadShopSettings' in log['message']:
                print(f"   📝 {log['message']}")
        
        # Step 5: Check if the script tag exists
        print("\n🔍 Step 5: Checking if script tag exists...")
        script_tags = driver.find_elements(By.CSS_SELECTOR, "script[src*='shop-settings.js']")
        print(f"   Found {len(script_tags)} shop-settings.js script tags")
        
        for i, script in enumerate(script_tags):
            src = script.get_attribute('src')
            print(f"   Script {i+1}: {src}")
        
        print("\n✅ JavaScript loading test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_js_loading()