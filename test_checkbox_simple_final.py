#!/usr/bin/env python3
"""
Simple checkbox test - just check if they work when visible
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_checkboxes_simple():
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
        time.sleep(3)
        
        print("🔍 Step 1: Clicking Shop Settings button to make section visible...")
        shop_settings_btn = driver.find_element(By.CSS_SELECTOR, "button[data-go='shopSettingsSec']")
        shop_settings_btn.click()
        time.sleep(1)
        
        print("🔍 Step 2: Finding checkboxes in Shop Settings...")
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "#shopSettingsSec input[type='checkbox']")
        print(f"   Found {len(checkboxes)} checkboxes")
        
        if checkboxes:
            first_checkbox = checkboxes[0]
            print(f"\n📋 Testing first checkbox:")
            print(f"   ID: {first_checkbox.get_attribute('id')}")
            print(f"   Name: {first_checkbox.get_attribute('name')}")
            print(f"   Is displayed: {first_checkbox.is_displayed()}")
            print(f"   Is enabled: {first_checkbox.is_enabled()}")
            print(f"   Is selected: {first_checkbox.is_selected()}")
            
            # Check inline styles
            style = first_checkbox.get_attribute('style')
            print(f"   Inline style: {style}")
            
            # Check if it has custom styling
            has_custom_styling = 'appearance: none' in style and 'background-color' in style
            print(f"   Has custom styling: {has_custom_styling}")
            
            print("\n🔍 Step 3: Testing checkbox interaction...")
            # Get initial state
            initial_checked = first_checkbox.is_selected()
            print(f"   Initial checked state: {initial_checked}")
            
            # Click the checkbox
            first_checkbox.click()
            time.sleep(0.5)
            
            # Check new state
            new_checked = first_checkbox.is_selected()
            print(f"   New checked state: {new_checked}")
            
            # Check if state changed
            if initial_checked != new_checked:
                print("   ✅ Checkbox interaction working")
            else:
                print("   ❌ Checkbox interaction not working")
            
            # Check style after interaction
            style_after_click = first_checkbox.get_attribute('style')
            print(f"   Style after click: {style_after_click}")
            
            # Check if the visual state changed
            has_custom_styling_after = 'appearance: none' in style_after_click and 'background-color' in style_after_click
            print(f"   Has custom styling after click: {has_custom_styling_after}")
            
            # Check if the background color changed based on checked state
            if new_checked:
                has_blue_background = '#3b82f6' in style_after_click or 'rgb(59, 130, 246)' in style_after_click
                print(f"   Has blue background when checked: {has_blue_background}")
            else:
                has_dark_background = '#1f2937' in style_after_click or 'rgb(31, 41, 55)' in style_after_click
                print(f"   Has dark background when unchecked: {has_dark_background}")
        
        print("\n✅ Simple test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()

if __name__ == "__main__":
    test_checkboxes_simple()
