#!/usr/bin/env python3
"""
Test to see what the login page looks like
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def test_login_page():
    """Test login page structure"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        print("🌐 Opening login page...")
        driver.get("http://localhost:5000/login")
        
        # Wait for page to load
        time.sleep(3)
        
        # Take screenshot
        driver.save_screenshot("login_page.png")
        print("📸 Screenshot saved as login_page.png")
        
        # Get page source
        page_source = driver.page_source
        with open("login_page_source.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        print("📄 Page source saved as login_page_source.html")
        
        # Look for any input elements
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"📋 Found {len(inputs)} input elements:")
        for i, inp in enumerate(inputs):
            inp_type = inp.get_attribute('type')
            inp_id = inp.get_attribute('id')
            inp_name = inp.get_attribute('name')
            inp_placeholder = inp.get_attribute('placeholder')
            print(f"  {i+1}. Type: {inp_type}, ID: {inp_id}, Name: {inp_name}, Placeholder: {inp_placeholder}")
        
        # Look for any buttons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"🔘 Found {len(buttons)} button elements:")
        for i, btn in enumerate(buttons):
            btn_type = btn.get_attribute('type')
            btn_text = btn.text
            btn_class = btn.get_attribute('class')
            print(f"  {i+1}. Type: {btn_type}, Text: '{btn_text}', Class: {btn_class}")
        
        # Wait a bit
        time.sleep(2)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    test_login_page()
