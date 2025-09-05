#!/usr/bin/env python3
"""
Test frontend with user_id 35 (correct user)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_user_35_frontend():
    print("🧪 Testing Frontend with User ID 35 (Correct User)")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Step 1: Login with correct credentials
        print("\n🔐 Step 1: Logging in with user_id 35 credentials...")
        driver.get("http://localhost:5000/login")
        
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "signin-email"))
        )
        password_input = driver.find_element(By.ID, "signin-password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        email_input.send_keys("tumd@tajir.com")  # Correct email for user_id 35
        password_input.send_keys("demo123")
        login_button.click()
        
        # Wait for redirect to app
        WebDriverWait(driver, 10).until(
            EC.url_contains("/app")
        )
        print("   ✅ Login successful")
        
        # Step 2: Navigate to Shop Settings
        print("\n⚙️ Step 2: Navigating to Shop Settings...")
        shop_settings_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-go='shopSettingsSec']"))
        )
        shop_settings_btn.click()
        time.sleep(3)
        print("   ✅ Shop Settings section loaded")
        
        # Step 3: Check checkbox states
        print("\n🔍 Step 3: Checking checkbox states...")
        checkboxes = [
            ("enable_trial_date", "bcEnableTrialDate"),
            ("enable_delivery_date", "bcEnableDeliveryDate"),
            ("enable_advance_payment", "bcEnableAdvancePayment"),
            ("enable_customer_notes", "enableCustomerNotes"),
            ("enable_employee_assignment", "enableEmployeeAssignment")
        ]
        
        all_checked = True
        for name, id in checkboxes:
            try:
                checkbox = driver.find_element(By.NAME, name)
                checked = checkbox.is_selected()
                status = "✅" if checked else "❌"
                print(f"   {status} {name}: checked={checked}")
                if not checked:
                    all_checked = False
            except Exception as e:
                print(f"   ❌ {name}: ERROR - {e}")
                all_checked = False
        
        # Step 4: Summary
        print("\n📊 Step 4: Summary...")
        if all_checked:
            print("   🎉 SUCCESS: All checkboxes are checked correctly!")
            print("   ✅ The frontend is now loading the correct values from the database")
            print("   ✅ The cache issue is resolved!")
        else:
            print("   ❌ ISSUE: Some checkboxes are still not checked")
            print("   🔧 There may still be a frontend loading issue")
        
        # Step 5: Test save functionality
        print("\n💾 Step 5: Testing save functionality...")
        save_btn = driver.find_element(By.ID, "saveShopSettingsBtn")
        save_btn.click()
        time.sleep(2)
        
        # Check if values are still correct after save
        print("\n🔍 Step 6: Checking values after save...")
        for name, id in checkboxes:
            try:
                checkbox = driver.find_element(By.NAME, name)
                checked = checkbox.is_selected()
                status = "✅" if checked else "❌"
                print(f"   {status} {name}: checked={checked}")
            except Exception as e:
                print(f"   ❌ {name}: ERROR - {e}")
        
        print("\n✅ User ID 35 frontend test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_user_35_frontend()
