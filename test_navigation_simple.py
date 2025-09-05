#!/usr/bin/env python3
"""
Simple test to check if navigation system is working
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_navigation_simple():
    print("🧪 Simple Navigation Test")
    
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
        
        # Step 2: Check if navigation system is loaded
        print("\n🔍 Step 2: Checking if navigation system is loaded...")
        nav_system_loaded = driver.execute_script("""
        // Check if navigation system is working
        const navButtons = document.querySelectorAll('[data-go]');
        console.log('Navigation buttons found:', navButtons.length);
        
        // Try to click a navigation button programmatically
        const shopSettingsBtn = document.querySelector('[data-go="shopSettingsSec"]');
        if (shopSettingsBtn) {
            console.log('Shop settings button found, clicking...');
            shopSettingsBtn.click();
            return 'Button clicked';
        } else {
            return 'Button not found';
        }
        """)
        
        print(f"   📝 Navigation system test: {nav_system_loaded}")
        
        # Step 3: Check console logs
        print("\n📋 Step 3: Checking console logs...")
        logs = driver.get_log('browser')
        
        for log in logs:
            if any(keyword in log['message'] for keyword in ['Navigation buttons found', 'Shop settings button found', 'Button clicked', '🚀', '🔧']):
                print(f"   📝 {log['message']}")
        
        # Step 4: Check if shop settings section is visible
        print("\n🔍 Step 4: Checking if shop settings section is visible...")
        section_visible = driver.execute_script("""
        const section = document.getElementById('shopSettingsSec');
        if (section) {
            return {
                exists: true,
                hidden: section.classList.contains('hidden'),
                visible: section.offsetParent !== null
            };
        } else {
            return { exists: false };
        }
        """)
        
        print(f"   📝 Shop settings section: {section_visible}")
        
        print("\n✅ Simple navigation test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_navigation_simple()
