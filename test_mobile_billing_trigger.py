#!/usr/bin/env python3
"""
Test Mobile Billing Trigger
"""

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_mobile_billing_trigger():
    """Test if mobile billing interface can be triggered"""
    
    print("Testing Mobile Billing Trigger...")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000/api/products")
        if response.status_code != 200:
            print("❌ Server not responding")
            return
    except:
        print("❌ Cannot connect to server")
        return
    
    print("✅ Server is running")
    
    # Set up Chrome options for headless testing
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ Chrome driver initialized")
        
        # Navigate to the app
        driver.get("http://localhost:5000/app")
        print("✅ Navigated to app page")
        
        # Wait for page to load
        time.sleep(3)
        
        # Check if mobile billing buttons exist
        try:
            # Look for mobile billing banner button
            banner_btn = driver.find_element(By.ID, "mobileBillingBannerBtn")
            print("✅ Mobile billing banner button found")
            
            # Look for mobile billing toggle button
            toggle_btn = driver.find_element(By.ID, "mobileBillingToggleV3")
            print("✅ Mobile billing toggle button found")
            
            # Check if mobile billing overlay exists
            overlay = driver.find_element(By.ID, "mobile-billing-v3-overlay")
            print("✅ Mobile billing overlay found")
            
            # Check if it's hidden initially
            if "hidden" in overlay.get_attribute("class"):
                print("✅ Mobile billing overlay is hidden initially (correct)")
            else:
                print("⚠️ Mobile billing overlay is visible initially")
            
            # Try to click the toggle button
            toggle_btn.click()
            print("✅ Clicked mobile billing toggle button")
            
            # Wait a moment for the interface to show
            time.sleep(2)
            
            # Check if overlay is now visible
            if "hidden" not in overlay.get_attribute("class"):
                print("✅ Mobile billing overlay is now visible")
            else:
                print("❌ Mobile billing overlay did not show")
            
        except Exception as e:
            print(f"❌ Error finding mobile billing elements: {e}")
        
        driver.quit()
        print("✅ Test completed")
        
    except Exception as e:
        print(f"❌ Error with browser test: {e}")
        print("Note: This test requires Chrome browser and ChromeDriver")
        print("You can manually test by:")
        print("1. Opening http://localhost:5000/app in your browser")
        print("2. Looking for '📱 Mobile Billing V3' button")
        print("3. Clicking it to open the mobile billing interface")

if __name__ == "__main__":
    test_mobile_billing_trigger()

