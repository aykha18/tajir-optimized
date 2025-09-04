#!/usr/bin/env python3
"""
Selenium Test for AI Insights Functionality
This script will test the complete flow from login to AI dashboard access
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """Setup Chrome driver with options"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    # Uncomment the line below if you want to run headless
    # chrome_options.add_argument("--headless")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def test_ai_insights_flow():
    """Test the complete AI Insights flow"""
    driver = setup_driver()
    
    try:
        print("🚀 Starting AI Insights Test...")
        print("=" * 50)
        
        # Test 1: Direct access to AI dashboard (should redirect to login)
        print("\n📋 Test 1: Direct AI Dashboard Access (Unauthenticated)")
        print("-" * 50)
        
        driver.get("http://127.0.0.1:5000/ai-dashboard")
        time.sleep(2)
        
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        if "login" in current_url:
            print("✅ SUCCESS: Redirected to login page as expected")
        else:
            print(f"❌ FAILED: Expected login redirect, got: {current_url}")
        
        # Test 2: Login process
        print("\n📋 Test 2: Login Process")
        print("-" * 50)
        
        # Wait for login form to be visible
        wait = WebDriverWait(driver, 10)
        email_input = wait.until(EC.presence_of_element_located((By.ID, "signin-email")))
        password_input = driver.find_element(By.ID, "signin-email")
        password_input = driver.find_element(By.ID, "signin-password")
        
        print("Found login form elements")
        
        # Fill in login credentials (using admin account from logs)
        email_input.clear()
        email_input.send_keys("admin@tailorpos.com")
        
        password_input.clear()
        password_input.send_keys("admin123")
        
        print("Filled login credentials")
        
        # Submit login form
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        print("Clicked login button")
        
        # Wait for redirect or success message
        time.sleep(5)
        
        current_url = driver.current_url
        print(f"Current URL after login: {current_url}")
        
        if "ai-dashboard" in current_url:
            print("✅ SUCCESS: Directly redirected to AI dashboard after login")
        elif "app" in current_url:
            print("ℹ️  INFO: Redirected to main app (will test AI Insights button next)")
        else:
            print(f"❌ UNEXPECTED: Login resulted in URL: {current_url}")
        
        # Test 3: Access AI Insights from main app
        print("\n📋 Test 3: AI Insights Button from Main App")
        print("-" * 50)
        
        if "app" in current_url:
            # Look for AI Insights button
            try:
                ai_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'AI Insights')]")))
                print("Found AI Insights button")
                
                # Click AI Insights button
                ai_button.click()
                print("Clicked AI Insights button")
                
                time.sleep(3)
                current_url = driver.current_url
                print(f"Current URL after clicking AI Insights: {current_url}")
                
                if "ai-dashboard" in current_url:
                    print("✅ SUCCESS: AI Insights button works correctly!")
                else:
                    print(f"❌ FAILED: AI Insights button didn't redirect to dashboard: {current_url}")
                    
            except Exception as e:
                print(f"❌ ERROR: Could not find or click AI Insights button: {e}")
        
        # Test 4: AI Dashboard Functionality
        print("\n📋 Test 4: AI Dashboard Functionality")
        print("-" * 50)
        
        if "ai-dashboard" in current_url:
            print("Testing AI dashboard features...")
            
            # Check if dashboard loaded
            try:
                # Look for key elements
                dashboard_title = wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'AI Business Intelligence')]")))
                print("✅ Dashboard title found")
                
                # Look for customer segmentation section
                segmentation_section = driver.find_element(By.ID, "customerSegmentation")
                print("✅ Customer segmentation section found")
                
                # Look for refresh button
                refresh_button = driver.find_element(By.ID, "refreshSegmentationBtn")
                print("✅ Refresh button found")
                
                # Test refresh functionality
                print("Testing refresh functionality...")
                refresh_button.click()
                time.sleep(2)
                
                # Check for loading state
                loading_element = driver.find_element(By.ID, "segmentationLoading")
                if loading_element.is_displayed():
                    print("✅ Loading state displayed")
                else:
                    print("ℹ️  Loading state not visible (may have completed quickly)")
                
                time.sleep(3)
                
                # Check for results
                try:
                    cards_element = driver.find_element(By.ID, "segmentationCards")
                    if cards_element.is_displayed():
                        print("✅ Segmentation results displayed")
                    else:
                        print("ℹ️  Segmentation results not visible yet")
                except:
                    print("ℹ️  Segmentation results section not found (may be loading)")
                
            except Exception as e:
                print(f"❌ ERROR testing dashboard functionality: {e}")
        else:
            print("⚠️  Skipping dashboard functionality test - not on dashboard page")
        
        # Test 5: Check for JavaScript errors
        print("\n📋 Test 5: JavaScript Console Errors")
        print("-" * 50)
        
        logs = driver.get_log('browser')
        if logs:
            print(f"Found {len(logs)} console messages:")
            for log in logs:
                if log['level'] == 'SEVERE':
                    print(f"❌ ERROR: {log['message']}")
                elif log['level'] == 'WARNING':
                    print(f"⚠️  WARNING: {log['message']}")
                else:
                    print(f"ℹ️  INFO: {log['message']}")
        else:
            print("✅ No console errors found")
        
        # Final status
        print("\n" + "=" * 50)
        print("🎯 TEST SUMMARY")
        print("=" * 50)
        
        if "ai-dashboard" in current_url:
            print("✅ SUCCESS: AI Insights functionality is working!")
            print("✅ Users can access AI dashboard after login")
            print("✅ Authentication flow is working correctly")
        else:
            print("❌ ISSUES DETECTED:")
            print(f"   - Final URL: {current_url}")
            print("   - Check the detailed test results above")
        
        print("\n🔍 Next Steps:")
        print("1. Review any error messages above")
        print("2. Check browser console for JavaScript errors")
        print("3. Verify database connection and data")
        print("4. Test with different user accounts")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Keep browser open for manual inspection
        print("\n🔍 Browser will remain open for manual inspection...")
        print("Press Enter to close browser...")
        input()
        driver.quit()

if __name__ == "__main__":
    test_ai_insights_flow()

