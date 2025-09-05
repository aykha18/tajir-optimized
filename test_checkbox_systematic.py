#!/usr/bin/env python3
"""
Systematic checkbox test to verify the styling is working correctly
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_checkboxes_systematically():
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
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "app"))
        )
        
        print("🔍 Step 1: Checking if Shop Settings section is visible...")
        shop_settings_section = driver.find_element(By.ID, "shopSettingsSec")
        is_visible = shop_settings_section.is_displayed()
        print(f"   Shop Settings section visible: {is_visible}")
        
        if not is_visible:
            print("🔧 Step 2: Clicking Shop Settings button to make section visible...")
            shop_settings_btn = driver.find_element(By.CSS_SELECTOR, "button[data-go='shopSettingsSec']")
            shop_settings_btn.click()
            time.sleep(1)
            
            # Check again
            is_visible = shop_settings_section.is_displayed()
            print(f"   Shop Settings section visible after click: {is_visible}")
        
        print("🔍 Step 3: Finding all checkboxes in Shop Settings...")
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "#shopSettingsSec input[type='checkbox']")
        print(f"   Found {len(checkboxes)} checkboxes")
        
        for i, checkbox in enumerate(checkboxes):
            print(f"\n📋 Checkbox {i+1}:")
            print(f"   ID: {checkbox.get_attribute('id')}")
            print(f"   Name: {checkbox.get_attribute('name')}")
            print(f"   Is displayed: {checkbox.is_displayed()}")
            print(f"   Is enabled: {checkbox.is_enabled()}")
            print(f"   Is selected: {checkbox.is_selected()}")
            
            # Check inline styles
            style = checkbox.get_attribute('style')
            print(f"   Inline style: {style[:100]}..." if len(style) > 100 else f"   Inline style: {style}")
            
            # Check if it has the custom styling
            has_custom_styling = 'appearance: none' in style and 'background-color' in style
            print(f"   Has custom styling: {has_custom_styling}")
            
            # Check computed styles
            computed_style = driver.execute_script("""
                var element = arguments[0];
                var computed = window.getComputedStyle(element);
                return {
                    appearance: computed.appearance,
                    backgroundColor: computed.backgroundColor,
                    borderColor: computed.borderColor,
                    width: computed.width,
                    height: computed.height
                };
            """, checkbox)
            
            print(f"   Computed appearance: {computed_style['appearance']}")
            print(f"   Computed background: {computed_style['backgroundColor']}")
            print(f"   Computed border: {computed_style['borderColor']}")
            print(f"   Computed size: {computed_style['width']} x {computed_style['height']}")
        
        print("\n🔍 Step 4: Testing JavaScript function availability...")
        js_functions = [
            'updateCheckboxVisualState',
            'initializeShopSettings',
            'setupCheckboxVisualHandlers'
        ]
        
        for func_name in js_functions:
            exists = driver.execute_script(f"return typeof {func_name} === 'function';")
            print(f"   {func_name}: {'✅ Exists' if exists else '❌ Missing'}")
        
        print("\n🔍 Step 5: Testing manual checkbox styling...")
        if checkboxes:
            first_checkbox = checkboxes[0]
            print(f"   Testing checkbox: {first_checkbox.get_attribute('name')}")
            
            # Try to manually call the styling function
            try:
                result = driver.execute_script("""
                    var checkbox = arguments[0];
                    if (typeof updateCheckboxVisualState === 'function') {
                        updateCheckboxVisualState(checkbox);
                        return 'Function called successfully';
                    } else {
                        return 'Function not available';
                    }
                """, first_checkbox)
                print(f"   Manual styling result: {result}")
            except Exception as e:
                print(f"   Manual styling error: {e}")
            
            # Check style after manual call
            style_after = first_checkbox.get_attribute('style')
            print(f"   Style after manual call: {style_after[:100]}..." if len(style_after) > 100 else f"   Style after manual call: {style_after}")
        
        print("\n🔍 Step 6: Checking console errors...")
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
        
        print("\n🔍 Step 7: Testing checkbox interaction...")
        if checkboxes:
            first_checkbox = checkboxes[0]
            print(f"   Testing checkbox: {first_checkbox.get_attribute('name')}")
            
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
            print(f"   Style after click: {style_after_click[:100]}..." if len(style_after_click) > 100 else f"   Style after click: {style_after_click}")
        
        print("\n✅ Systematic test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()

if __name__ == "__main__":
    test_checkboxes_systematically()
