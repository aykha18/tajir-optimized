#!/usr/bin/env python3
"""
Debug login process to see what's actually happening
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def debug_login():
    print("🔧 Setting up Chrome driver...")
    
    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("🌐 Opening login page...")
        driver.get("http://localhost:5000/login")
        
        print("🔐 Logging in...")
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "signin-email"))
        )
        password_input = driver.find_element(By.ID, "signin-password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        email_input.send_keys("td@tajir.com")
        password_input.send_keys("demo123")
        login_button.click()
        
        print("⏳ Waiting for login to complete...")
        time.sleep(3)  # Wait a bit longer
        
        print("🔍 Checking current URL...")
        current_url = driver.current_url
        print(f"   Current URL: {current_url}")
        
        print("🔍 Checking page title...")
        page_title = driver.title
        print(f"   Page title: {page_title}")
        
        print("🔍 Looking for common elements...")
        elements_to_check = [
            ("#app", "App element"),
            ("#shopSettingsSec", "Shop Settings section"),
            ("input[type='checkbox']", "Any checkbox"),
            ("body", "Body element"),
            (".page", "Page class"),
            ("[data-tab='settings']", "Settings tab")
        ]
        
        for selector, description in elements_to_check:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"   {description} ({selector}): {len(elements)} found")
                if elements:
                    first_element = elements[0]
                    print(f"      - Is displayed: {first_element.is_displayed()}")
                    print(f"      - Is enabled: {first_element.is_enabled()}")
                    if selector == "input[type='checkbox']":
                        print(f"      - Is selected: {first_element.is_selected()}")
            except Exception as e:
                print(f"   {description} ({selector}): Error - {e}")
        
        print("🔍 Checking for JavaScript errors...")
        logs = driver.get_log('browser')
        error_count = 0
        for log in logs:
            if log['level'] == 'SEVERE':
                error_count += 1
                print(f"   ❌ {log['message']}")
        
        if error_count == 0:
            print("   ✅ No JavaScript errors found")
        else:
            print(f"   ⚠️  Found {error_count} JavaScript errors")
        
        print("🔍 Taking screenshot...")
        driver.save_screenshot("login_debug.png")
        print("   Screenshot saved as login_debug.png")
        
        print("🔍 Getting page source snippet...")
        page_source = driver.page_source
        print(f"   Page source length: {len(page_source)}")
        
        # Look for specific patterns
        if "app" in page_source.lower():
            print("   ✅ Found 'app' in page source")
        else:
            print("   ❌ 'app' not found in page source")
            
        if "checkbox" in page_source.lower():
            print("   ✅ Found 'checkbox' in page source")
        else:
            print("   ❌ 'checkbox' not found in page source")
            
        if "shopSettingsSec" in page_source:
            print("   ✅ Found 'shopSettingsSec' in page source")
        else:
            print("   ❌ 'shopSettingsSec' not found in page source")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_login()
