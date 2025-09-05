#!/usr/bin/env python3
"""
Test checkbox HTML structure
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def test_checkbox_structure():
    print("🧪 Testing Checkbox HTML Structure")
    
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
        
        # Step 3: Check checkbox structure
        print("\n🔍 Step 3: Checking checkbox structure...")
        checkbox_info = driver.execute_script("""
        const form = document.getElementById('shopSettingsForm');
        if (!form) {
            return {error: 'Form not found'};
        }
        
        const checkboxes = form.querySelectorAll('input[type="checkbox"]');
        const info = {
            totalCheckboxes: checkboxes.length,
            checkboxes: []
        };
        
        checkboxes.forEach((checkbox, index) => {
            info.checkboxes.push({
                index: index,
                id: checkbox.id,
                name: checkbox.name,
                checked: checkbox.checked,
                value: checkbox.value
            });
        });
        
        return info;
        """)
        
        print(f"   📝 Checkbox info: {checkbox_info}")
        
        # Step 4: Check specific checkboxes
        print("\n🔍 Step 4: Checking specific checkboxes...")
        specific_checkboxes = [
            "bcEnableTrialDate",
            "bcEnableDeliveryDate", 
            "bcEnableAdvancePayment",
            "useDynamicInvoiceTemplate",
            "enableCustomerNotes",
            "enableEmployeeAssignment"
        ]
        
        for checkbox_id in specific_checkboxes:
            try:
                checkbox = driver.find_element(By.ID, checkbox_id)
                name = checkbox.get_attribute("name")
                checked = checkbox.is_selected()
                print(f"   📝 {checkbox_id}: name='{name}', checked={checked}")
            except Exception as e:
                print(f"   ❌ {checkbox_id}: ERROR - {e}")
        
        # Step 5: Test form data collection with specific names
        print("\n🔧 Step 5: Testing form data collection with specific names...")
        form_data = driver.execute_script("""
        const data = {};
        
        // Get specific checkbox values
        const checkboxNames = [
            'enable_trial_date',
            'enable_delivery_date', 
            'enable_advance_payment',
            'use_dynamic_invoice_template',
            'enable_customer_notes',
            'enable_employee_assignment'
        ];
        
        checkboxNames.forEach(name => {
            const checkbox = document.querySelector(`input[name="${name}"]`);
            if (checkbox) {
                data[name] = checkbox.checked;
            } else {
                data[name] = 'NOT_FOUND';
            }
        });
        
        return data;
        """)
        
        print(f"   📝 Form data with specific names: {form_data}")
        
        print("\n✅ Checkbox structure test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_checkbox_structure()
