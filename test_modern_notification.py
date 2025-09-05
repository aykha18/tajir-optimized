#!/usr/bin/env python3
"""
Test the modern notification system
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_modern_notification():
    print("🧪 Testing Modern Notification System")
    
    # Setup Chrome options (keep visible to see the notification)
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    # Keep browser visible to see the notification
    
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
        
        WebDriverWait(driver, 10).until(EC.url_contains("/app"))
        print("   ✅ Login successful")
        
        # Step 2: Navigate to shop settings
        print("\n⚙️ Step 2: Navigating to shop settings...")
        shop_settings_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-go='shopSettingsSec']"))
        )
        shop_settings_btn.click()
        time.sleep(2)
        print("   ✅ Shop settings section loaded")
        
        # Step 3: Change a checkbox value
        print("\n🔄 Step 3: Changing a checkbox value...")
        checkbox = driver.find_element(By.ID, "bcEnableTrialDate")
        current_state = checkbox.is_selected()
        checkbox.click()  # Toggle the checkbox
        new_state = checkbox.is_selected()
        print(f"   🔄 Trial Date: {current_state} → {new_state}")
        
        # Step 4: Save and watch for modern notification
        print("\n💾 Step 4: Saving and watching for modern notification...")
        print("   👀 Watch for the modern notification in the top-right corner!")
        
        save_btn = driver.find_element(By.ID, "saveShopSettingsBtn")
        save_btn.click()
        
        # Wait and check for notification
        time.sleep(2)
        
        # Check if modern notification appeared
        notification = driver.find_element(By.CSS_SELECTOR, ".modern-notification")
        if notification:
            print("   ✅ Modern notification found!")
            
            # Check notification content
            notification_text = notification.find_element(By.CSS_SELECTOR, "p").text
            print(f"   📝 Notification text: {notification_text}")
            
            # Check if it has the success styling
            notification_div = notification.find_element(By.CSS_SELECTOR, "div")
            classes = notification_div.get_attribute("class")
            if "bg-green-500" in classes:
                print("   ✅ Success styling applied (green background)")
            else:
                print(f"   ⚠️ Unexpected styling: {classes}")
            
            # Wait for auto-removal
            print("   ⏳ Waiting for notification to auto-remove (4 seconds)...")
            time.sleep(5)
            
            # Check if notification was removed
            try:
                driver.find_element(By.CSS_SELECTOR, ".modern-notification")
                print("   ⚠️ Notification still present after 5 seconds")
            except:
                print("   ✅ Notification auto-removed successfully")
                
        else:
            print("   ❌ Modern notification not found")
        
        print("\n✅ Modern notification test completed!")
        print("   🎉 The notification should have appeared in the top-right corner with a smooth slide-in animation!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        input("Press Enter to close browser...")
        driver.quit()

if __name__ == "__main__":
    test_modern_notification()
