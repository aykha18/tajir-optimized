#!/usr/bin/env python3
"""
Simple Mobile Billing Test
"""

import requests
import re

def test_mobile_billing_elements():
    """Test if mobile billing HTML elements are present"""
    
    print("Testing Mobile Billing Elements...")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000/app")
        if response.status_code != 200:
            print("❌ Server not responding")
            return
    except:
        print("❌ Cannot connect to server")
        return
    
    print("✅ Server is running")
    
    # Get the HTML content
    html_content = response.text
    
    # Check for mobile billing elements
    elements_to_check = [
        ("mobileBillingBannerBtn", "Mobile billing banner button"),
        ("mobileBillingToggleV3", "Mobile billing toggle button"),
        ("mobile-billing-v3-overlay", "Mobile billing overlay"),
        ("mobile-billing-v3.js", "Mobile billing JavaScript file"),
        ("mobile-billing-v3.css", "Mobile billing CSS file")
    ]
    
    all_found = True
    for element_id, description in elements_to_check:
        if element_id in html_content:
            print(f"✅ {description} found")
        else:
            print(f"❌ {description} not found")
            all_found = False
    
    # Check for event listeners
    if "addEventListener" in html_content and "mobileBilling" in html_content:
        print("✅ Mobile billing event listeners found")
    else:
        print("❌ Mobile billing event listeners not found")
        all_found = False
    
    print("\n" + "=" * 50)
    if all_found:
        print("✅ All mobile billing elements are present!")
        print("\nTo test the mobile billing interface:")
        print("1. Open http://localhost:5000/app in your browser")
        print("2. Look for the '📱 Mobile Billing V3' button")
        print("3. Click it to open the mobile billing interface")
        print("4. If it doesn't work, check the browser console for errors")
    else:
        print("❌ Some mobile billing elements are missing")
        print("The mobile billing interface may not work properly")

if __name__ == "__main__":
    test_mobile_billing_elements()

