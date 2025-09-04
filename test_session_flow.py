#!/usr/bin/env python3
"""
Test Session Flow for AI Dashboard
This script tests the complete session flow to identify authentication issues
"""

import requests
import json

def test_session_flow():
    """Test the complete session flow"""
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    print("🚀 Testing AI Dashboard Session Flow")
    print("=" * 50)
    
    # Test 1: Try to access AI dashboard without login
    print("\n📋 Test 1: Access AI Dashboard (Unauthenticated)")
    print("-" * 50)
    
    try:
        response = session.get(f"{base_url}/ai-dashboard", allow_redirects=False)
        print(f"Status Code: {response.status_code}")
        print(f"Response URL: {response.url}")
        
        if response.status_code == 302:  # Redirect
            print("✅ SUCCESS: Redirected as expected")
            print(f"Redirect Location: {response.headers.get('Location', 'Not set')}")
        else:
            print(f"❌ UNEXPECTED: Got status {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 2: Try to access main app without login
    print("\n📋 Test 2: Access Main App (Unauthenticated)")
    print("-" * 50)
    
    try:
        response = session.get(f"{base_url}/app", allow_redirects=False)
        print(f"Status Code: {response.status_code}")
        print(f"Response URL: {response.url}")
        
        if response.status_code == 302:  # Redirect
            print("✅ SUCCESS: Redirected as expected")
            print(f"Redirect Location: {response.headers.get('Location', 'Not set')}")
        else:
            print(f"❌ UNEXPECTED: Got status {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 3: Login
    print("\n📋 Test 3: Login Process")
    print("-" * 50)
    
    try:
        login_data = {
            "method": "email",
            "email": "admin@tailorpos.com",
            "password": "admin123"
        }
        
        response = session.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            login_response = response.json()
            print("✅ SUCCESS: Login successful")
            print(f"Response: {json.dumps(login_response, indent=2)}")
            
            # Check if redirect field is present
            if 'redirect' in login_response:
                print("✅ SUCCESS: Redirect field found in response")
                print(f"Redirect URL: {login_response['redirect']}")
            else:
                print("❌ ISSUE: Redirect field missing from response")
                print("This means the session['next'] was not set properly")
                
        else:
            print(f"❌ FAILED: Login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 4: Try to access AI dashboard after login
    print("\n📋 Test 4: Access AI Dashboard (Authenticated)")
    print("-" * 50)
    
    try:
        response = session.get(f"{base_url}/ai-dashboard", allow_redirects=False)
        print(f"Status Code: {response.status_code}")
        print(f"Response URL: {response.url}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: AI Dashboard accessible after login")
            # Check if it's actually the dashboard or still login page
            if "AI Business Intelligence" in response.text:
                print("✅ SUCCESS: Dashboard content loaded correctly")
            else:
                print("❌ ISSUE: Dashboard content not loaded (might be login page)")
                print("First 200 chars of response:", response.text[:200])
        elif response.status_code == 302:
            print("❌ ISSUE: Still getting redirected after login")
            print(f"Redirect Location: {response.headers.get('Location', 'Not set')}")
        else:
            print(f"❌ UNEXPECTED: Got status {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 5: Check session cookies
    print("\n📋 Test 5: Session Cookies")
    print("-" * 50)
    
    cookies = session.cookies
    print(f"Number of cookies: {len(cookies)}")
    
    for cookie in cookies:
        print(f"Cookie: {cookie.name} = {cookie.value}")
        print(f"  Domain: {cookie.domain}")
        print(f"  Path: {cookie.path}")
        print(f"  Expires: {cookie.expires}")
    
    if not cookies:
        print("❌ ISSUE: No session cookies found")
        print("This suggests the session is not being maintained")
    
    # Test 6: Try to access main app after login
    print("\n📋 Test 6: Access Main App (Authenticated)")
    print("-" * 50)
    
    try:
        response = session.get(f"{base_url}/app", allow_redirects=False)
        print(f"Status Code: {response.status_code}")
        print(f"Response URL: {response.url}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Main app accessible after login")
            # Check if it's actually the app or still login page
            if "AI Insights" in response.text:
                print("✅ SUCCESS: Main app content loaded correctly")
            else:
                print("❌ ISSUE: Main app content not loaded (might be login page)")
                print("First 200 chars of response:", response.text[:200])
        elif response.status_code == 302:
            print("❌ ISSUE: Still getting redirected after login")
            print(f"Redirect Location: {response.headers.get('Location', 'Not set')}")
        else:
            print(f"❌ UNEXPECTED: Got status {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS SUMMARY")
    print("=" * 50)
    
    # Analyze the results
    if "AI Business Intelligence" in response.text:
        print("✅ SUCCESS: AI Dashboard is working correctly!")
        print("✅ Authentication flow is working!")
        print("✅ Session management is working!")
    else:
        print("❌ ISSUES DETECTED:")
        print("   - Session not being maintained between requests")
        print("   - Login successful but no redirect to intended page")
        print("   - Possible Flask session configuration issue")
        
        print("\n🔍 Possible Solutions:")
        print("1. Check Flask secret key configuration")
        print("2. Verify session cookie settings")
        print("3. Check if session middleware is properly configured")
        print("4. Verify the session['next'] is being set correctly")

if __name__ == "__main__":
    test_session_flow()

