#!/usr/bin/env python3
"""
Test to see what happens after login
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def test_after_login():
    """Test what happens after login"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        print("🌐 Opening login page...")
        driver.get("http://localhost:5000/login")
        time.sleep(3)
        
        # Login
        print("🔐 Logging in...")
        email_input = driver.find_element(By.ID, "signin-email")
        password_input = driver.find_element(By.ID, "signin-password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        email_input.clear()
        email_input.send_keys("td@tajir.com")
        password_input.clear()
        password_input.send_keys("demo123")
        login_button.click()
        
        # Wait for login
        time.sleep(5)
        
        # Take screenshot
        driver.save_screenshot("after_login.png")
        print("📸 Screenshot saved as after_login.png")
        
        # Get current URL
        current_url = driver.current_url
        print(f"📍 Current URL: {current_url}")
        
        # Look for any navigation elements
        nav_elements = driver.find_elements(By.CSS_SELECTOR, "[data-tab], .nav-item, .tab, button")
        print(f"🧭 Found {len(nav_elements)} navigation elements:")
        for i, elem in enumerate(nav_elements[:10]):  # First 10
            text = elem.text.strip()
            data_tab = elem.get_attribute('data-tab')
            class_name = elem.get_attribute('class')
            print(f"  {i+1}. Text: '{text}', data-tab: {data_tab}, class: {class_name}")
        
        # Look for any checkboxes
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        print(f"📋 Found {len(checkboxes)} checkboxes on current page")
        
        # Wait a bit
        time.sleep(2)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    test_after_login()
