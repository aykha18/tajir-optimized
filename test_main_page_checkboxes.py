#!/usr/bin/env python3
"""
Test checkboxes on main page
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def test_main_page_checkboxes():
    """Test checkboxes on main page"""
    
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
        driver.save_screenshot("main_page_checkboxes.png")
        print("📸 Screenshot saved as main_page_checkboxes.png")
        
        # Find all checkboxes
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        print(f"📋 Found {len(checkboxes)} checkboxes on main page")
        
        # Test each checkbox
        for i, checkbox in enumerate(checkboxes):
            name = checkbox.get_attribute('name')
            id_attr = checkbox.get_attribute('id')
            class_attr = checkbox.get_attribute('class')
            
            print(f"\n🔍 Testing checkbox {i+1}:")
            print(f"  Name: {name}")
            print(f"  ID: {id_attr}")
            print(f"  Class: {class_attr}")
            
            # Get initial state
            initial_checked = checkbox.is_selected()
            print(f"  Initial state: {'checked' if initial_checked else 'unchecked'}")
            
            # Get computed styles
            bg_color = driver.execute_script("return window.getComputedStyle(arguments[0]).backgroundColor", checkbox)
            border_color = driver.execute_script("return window.getComputedStyle(arguments[0]).borderColor", checkbox)
            display = driver.execute_script("return window.getComputedStyle(arguments[0]).display", checkbox)
            visibility = driver.execute_script("return window.getComputedStyle(arguments[0]).visibility", checkbox)
            
            print(f"  Background: {bg_color}")
            print(f"  Border: {border_color}")
            print(f"  Display: {display}")
            print(f"  Visibility: {visibility}")
            
            # Check if it's visible and clickable
            is_displayed = checkbox.is_displayed()
            is_enabled = checkbox.is_enabled()
            print(f"  Is displayed: {is_displayed}")
            print(f"  Is enabled: {is_enabled}")
            
            # Try to click if it's visible
            if is_displayed and is_enabled:
                print(f"  Clicking checkbox...")
                try:
                    # Scroll to element
                    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                    time.sleep(0.5)
                    
                    # Click using JavaScript
                    driver.execute_script("arguments[0].click();", checkbox)
                    time.sleep(1)
                    
                    # Check new state
                    new_checked = checkbox.is_selected()
                    new_bg_color = driver.execute_script("return window.getComputedStyle(arguments[0]).backgroundColor", checkbox)
                    new_border_color = driver.execute_script("return window.getComputedStyle(arguments[0]).borderColor", checkbox)
                    
                    print(f"  After click - Checked: {new_checked}")
                    print(f"  After click - Background: {new_bg_color}")
                    print(f"  After click - Border: {new_border_color}")
                    
                    # Click again to reset
                    driver.execute_script("arguments[0].click();", checkbox)
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"  Error clicking: {e}")
            else:
                print(f"  Skipping click - not visible or enabled")
        
        # Check for duplicate checkboxes
        print(f"\n🔍 Checking for duplicates...")
        all_inputs = driver.find_elements(By.CSS_SELECTOR, "input")
        checkbox_inputs = [inp for inp in all_inputs if inp.get_attribute('type') == 'checkbox']
        print(f"Total checkbox inputs found: {len(checkbox_inputs)}")
        
        # Check for hidden elements
        hidden_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][style*='display: none'], input[type='checkbox'][style*='visibility: hidden']")
        print(f"Hidden checkbox elements: {len(hidden_elements)}")
        
        # Check console logs
        print(f"\n📝 Checking console logs...")
        logs = driver.get_log('browser')
        for log in logs[-20:]:  # Last 20 logs
            if 'shop-settings' in log['message'] or 'checkbox' in log['message'].lower():
                print(f"  {log['level']}: {log['message']}")
        
        # Wait a bit to see the result
        time.sleep(2)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        print("🔚 Browser closed")

if __name__ == "__main__":
    test_main_page_checkboxes()
