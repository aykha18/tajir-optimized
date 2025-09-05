#!/usr/bin/env python3
"""
Test checkbox visibility issues
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def test_checkbox_visibility():
    """Test checkbox visibility issues"""
    
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
        
        # Find checkboxes
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        print(f"📋 Found {len(checkboxes)} checkboxes")
        
        # Test each checkbox visibility
        for i, checkbox in enumerate(checkboxes):
            name = checkbox.get_attribute('name')
            if not name:
                continue
                
            print(f"\n🔍 Testing checkbox {i+1}: {name}")
            
            # Check if element is in viewport
            in_viewport = driver.execute_script("""
                var rect = arguments[0].getBoundingClientRect();
                return (
                    rect.top >= 0 &&
                    rect.left >= 0 &&
                    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                );
            """, checkbox)
            
            # Check if element has any size
            has_size = driver.execute_script("""
                var rect = arguments[0].getBoundingClientRect();
                return rect.width > 0 && rect.height > 0;
            """, checkbox)
            
            # Check parent elements
            parent_hidden = driver.execute_script("""
                var element = arguments[0];
                var parent = element.parentElement;
                while (parent && parent !== document.body) {
                    var style = window.getComputedStyle(parent);
                    if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
                        return true;
                    }
                    parent = parent.parentElement;
                }
                return false;
            """, checkbox)
            
            print(f"  In viewport: {in_viewport}")
            print(f"  Has size: {has_size}")
            print(f"  Parent hidden: {parent_hidden}")
            
            # Get element position and size
            rect = driver.execute_script("return arguments[0].getBoundingClientRect();", checkbox)
            print(f"  Position: x={rect['x']}, y={rect['y']}, width={rect['width']}, height={rect['height']}")
            
            # Try to force visibility
            if not in_viewport or not has_size:
                print(f"  Trying to force visibility...")
                driver.execute_script("""
                    arguments[0].style.display = 'block';
                    arguments[0].style.visibility = 'visible';
                    arguments[0].style.opacity = '1';
                    arguments[0].style.position = 'relative';
                    arguments[0].style.zIndex = '9999';
                """, checkbox)
                
                time.sleep(0.5)
                
                # Check again
                new_in_viewport = driver.execute_script("""
                    var rect = arguments[0].getBoundingClientRect();
                    return (
                        rect.top >= 0 &&
                        rect.left >= 0 &&
                        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                    );
                """, checkbox)
                
                new_has_size = driver.execute_script("""
                    var rect = arguments[0].getBoundingClientRect();
                    return rect.width > 0 && rect.height > 0;
                """, checkbox)
                
                print(f"  After force - In viewport: {new_in_viewport}, Has size: {new_has_size}")
                
                # Try to click
                if new_in_viewport and new_has_size:
                    print(f"  Trying to click...")
                    driver.execute_script("arguments[0].click();", checkbox)
                    time.sleep(0.5)
                    
                    new_checked = checkbox.is_selected()
                    print(f"  After click - Checked: {new_checked}")
        
        # Take screenshot
        driver.save_screenshot("checkbox_visibility_test.png")
        print("📸 Screenshot saved as checkbox_visibility_test.png")
        
        # Wait a bit
        time.sleep(2)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        print("🔚 Browser closed")

if __name__ == "__main__":
    test_checkbox_visibility()
