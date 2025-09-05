#!/usr/bin/env python3
"""
Test complete flow for user_id 35 - frontend to backend
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import requests
import json

def test_user_35_complete_flow():
    print("🧪 Testing Complete Flow for User ID 35")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Step 1: Login as user 35
        print("\n🔐 Step 1: Logging in as user 35...")
        driver.get("http://localhost:5000/login")
        
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "signin-email"))
        )
        password_input = driver.find_element(By.ID, "signin-password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        email_input.send_keys("td@tajir.com")
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
        time.sleep(2)
        print("   ✅ Shop Settings section loaded")
        
        # Step 3: Check if we can find any checkboxes
        print("\n🔍 Step 3: Looking for checkboxes...")
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        print(f"   Found {len(checkboxes)} checkboxes")
        
        for i, checkbox in enumerate(checkboxes):
            name = checkbox.get_attribute('name')
            id_attr = checkbox.get_attribute('id')
            checked = checkbox.is_selected()
            displayed = checkbox.is_displayed()
            print(f"   Checkbox {i+1}: name='{name}', id='{id_attr}', checked={checked}, displayed={displayed}")
        
        # Step 4: Test backend API directly
        print("\n🌐 Step 4: Testing backend API directly...")
        session = requests.Session()
        
        # Login via API
        login_data = {
            "method": "email",
            "email": "td@tajir.com",
            "password": "demo123"
        }
        response = session.post("http://localhost:5000/api/auth/login", json=login_data)
        if response.status_code == 200:
            print("   ✅ API login successful")
            
            # Get current settings
            response = session.get("http://localhost:5000/api/shop-settings")
            if response.status_code == 200:
                settings = response.json()
                print("   ✅ API settings retrieved")
                
                # Check key boolean fields
                boolean_fields = [
                    "enable_trial_date", "enable_delivery_date", "enable_advance_payment",
                    "enable_customer_notes", "enable_employee_assignment"
                ]
                
                print("   📊 Current API settings:")
                for field in boolean_fields:
                    value = settings['settings'].get(field, False)
                    status = "✅" if value else "❌"
                    print(f"   {status} {field}: {value}")
                
                # Test updating settings
                print("\n💾 Step 5: Testing API update...")
                test_update = {
                    "shop_name": "Tumble Dry",
                    "enable_trial_date": True,
                    "enable_delivery_date": True,
                    "enable_advance_payment": True,
                    "enable_customer_notes": True,
                    "enable_employee_assignment": True,
                    "default_trial_days": 3,
                    "default_delivery_days": 5
                }
                
                response = session.put("http://localhost:5000/api/shop-settings", json=test_update)
                if response.status_code == 200:
                    print("   ✅ API update successful")
                    
                    # Verify the update
                    response = session.get("http://localhost:5000/api/shop-settings")
                    if response.status_code == 200:
                        updated_settings = response.json()
                        print("   📊 Updated settings:")
                        for field in boolean_fields:
                            value = updated_settings['settings'].get(field, False)
                            status = "✅" if value else "❌"
                            print(f"   {status} {field}: {value}")
                else:
                    print(f"   ❌ API update failed: {response.status_code}")
                    print(f"   Response: {response.text}")
            else:
                print(f"   ❌ API settings retrieval failed: {response.status_code}")
        else:
            print(f"   ❌ API login failed: {response.status_code}")
        
        # Step 6: Check console logs for any frontend errors
        print("\n📋 Step 6: Checking console logs...")
        logs = driver.get_log('browser')
        error_count = 0
        for log in logs:
            if log['level'] == 'SEVERE':
                error_count += 1
                print(f"   ❌ {log['message']}")
        
        if error_count == 0:
            print("   ✅ No JavaScript errors found")
        
        print("\n✅ Complete flow test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_user_35_complete_flow()
