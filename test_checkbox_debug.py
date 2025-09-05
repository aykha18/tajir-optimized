#!/usr/bin/env python3
"""
Test script to debug checkbox styling issues in shop settings
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_checkbox_styling():
    """Test checkbox styling in shop settings"""
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        # Initialize driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("http://localhost:5000")
        
        # Wait for page to load
        time.sleep(2)
        
        # Login
        email_input = driver.find_element(By.ID, "email")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        email_input.send_keys("dressme@tajir.com")
        password_input.send_keys("password123")
        login_button.click()
        
        # Wait for login
        time.sleep(3)
        
        # Navigate to shop settings
        settings_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-tab='settings']"))
        )
        settings_tab.click()
        
        # Wait for settings to load
        time.sleep(2)
        
        # Find checkboxes
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        print(f"Found {len(checkboxes)} checkboxes")
        
        for i, checkbox in enumerate(checkboxes):
            name = checkbox.get_attribute('name')
            checked = checkbox.is_selected()
            classes = checkbox.get_attribute('class')
            
            # Get computed styles
            bg_color = driver.execute_script("return window.getComputedStyle(arguments[0]).backgroundColor", checkbox)
            border_color = driver.execute_script("return window.getComputedStyle(arguments[0]).borderColor", checkbox)
            display = driver.execute_script("return window.getComputedStyle(arguments[0]).display", checkbox)
            visibility = driver.execute_script("return window.getComputedStyle(arguments[0]).visibility", checkbox)
            
            print(f"\nCheckbox {i+1}: {name}")
            print(f"  Checked: {checked}")
            print(f"  Classes: {classes}")
            print(f"  Background: {bg_color}")
            print(f"  Border: {border_color}")
            print(f"  Display: {display}")
            print(f"  Visibility: {visibility}")
            
            # Check if custom class is applied
            has_custom_class = 'custom-checkbox-styled' in classes
            print(f"  Has custom class: {has_custom_class}")
            
            # Test clicking
            print(f"  Testing click...")
            checkbox.click()
            time.sleep(0.5)
            
            new_checked = checkbox.is_selected()
            new_bg_color = driver.execute_script("return window.getComputedStyle(arguments[0]).backgroundColor", checkbox)
            print(f"  After click - Checked: {new_checked}, Background: {new_bg_color}")
            
            # Click again to reset
            checkbox.click()
            time.sleep(0.5)
        
        # Check if there are any duplicate checkboxes
        all_inputs = driver.find_elements(By.CSS_SELECTOR, "input")
        checkbox_inputs = [inp for inp in all_inputs if inp.get_attribute('type') == 'checkbox']
        print(f"\nTotal checkbox inputs found: {len(checkbox_inputs)}")
        
        # Check for any hidden elements
        hidden_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox'][style*='display: none'], input[type='checkbox'][style*='visibility: hidden']")
        print(f"Hidden checkbox elements: {len(hidden_elements)}")
        
        # Take screenshot
        driver.save_screenshot("checkbox_debug.png")
        print("\nScreenshot saved as checkbox_debug.png")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    test_checkbox_styling()
