#!/usr/bin/env python3
"""
Test for console errors
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_console_errors():
    print("🧪 Console Errors Test")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
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
        
        email_input.send_keys("tumd@tajir.com")
        password_input.send_keys("demo123")
        login_button.click()
        
        # Wait for redirect to app
        WebDriverWait(driver, 10).until(
            EC.url_contains("/app")
        )
        print("   ✅ Login successful")
        
        # Step 2: Check all console logs
        print("\n📋 Step 2: Checking all console logs...")
        logs = driver.get_log('browser')
        
        print(f"   📝 Total console logs: {len(logs)}")
        
        for log in logs:
            print(f"   📝 {log['level']}: {log['message']}")
        
        # Step 3: Check for JavaScript errors
        print("\n🔍 Step 3: Checking for JavaScript errors...")
        error_logs = [log for log in logs if log['level'] == 'SEVERE']
        if error_logs:
            print("   ❌ JavaScript errors found:")
            for log in error_logs:
                print(f"   {log['message']}")
        else:
            print("   ✅ No JavaScript errors found")
        
        # Step 4: Check for warnings
        print("\n⚠️ Step 4: Checking for warnings...")
        warning_logs = [log for log in logs if log['level'] == 'WARNING']
        if warning_logs:
            print("   ⚠️ Warnings found:")
            for log in warning_logs:
                print(f"   {log['message']}")
        else:
            print("   ✅ No warnings found")
        
        print("\n✅ Console errors test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_console_errors()
