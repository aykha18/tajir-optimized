#!/usr/bin/env python3
"""
Simple Session Test
Test if Flask session is working properly
"""

import requests
import json

def test_simple_session():
    """Test basic session functionality"""
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    print("🚀 Testing Simple Session Flow")
    print("=" * 50)
    
    # Test 1: Check if we can access the root route
    print("\n📋 Test 1: Access Root Route")
    print("-" * 50)
    
    try:
        response = session.get(f"{base_url}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response URL: {response.url}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Root route accessible")
        else:
            print(f"❌ FAILED: Root route returned {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 2: Try to access main app (should redirect to login)
    print("\n📋 Test 2: Access Main App (Unauthenticated)")
    print("-" * 50)
    
    try:
        response = session.get(f"{base_url}/app", allow_redirects=False)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 302:
            print("✅ SUCCESS: Redirected to login as expected")
            redirect_location = response.headers.get('Location', 'Not set')
            print(f"Redirect Location: {redirect_location}")
        else:
            print(f"❌ UNEXPECTED: Got status {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 3: Try to access AI dashboard (should redirect to login)
    print("\n📋 Test 3: Access AI Dashboard (Unauthenticated)")
    print("-" * 50)
    
    try:
        response = session.get(f"{base_url}/ai-dashboard", allow_redirects=False)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 302:
            print("✅ SUCCESS: Redirected to login as expected")
            redirect_location = response.headers.get('Location', 'Not set')
            print(f"Redirect Location: {redirect_location}")
        else:
            print(f"❌ UNEXPECTED: Got status {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 4: Login
    print("\n📋 Test 4: Login Process")
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
        else:
            print(f"❌ FAILED: Login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 5: Check session cookies after login
    print("\n📋 Test 5: Session Cookies After Login")
    print("-" * 50)
    
    cookies = session.cookies
    print(f"Number of cookies: {len(cookies)}")
    
    for cookie in cookies:
        print(f"Cookie: {cookie.name} = {cookie.value}")
        print(f"  Domain: {cookie.domain}")
        print(f"  Path: {cookie.path}")
    
    # Test 6: Try to access main app after login
    print("\n📋 Test 6: Access Main App (Authenticated)")
    print("-" * 50)
    
    try:
        response = session.get(f"{base_url}/app", allow_redirects=False)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Main app accessible after login")
            # Check content
            if "AI Insights" in response.text:
                print("✅ SUCCESS: Main app content loaded correctly")
            else:
                print("❌ ISSUE: Main app content not loaded correctly")
        elif response.status_code == 302:
            print("❌ ISSUE: Still getting redirected after login")
            redirect_location = response.headers.get('Location', 'Not set')
            print(f"Redirect Location: {redirect_location}")
        else:
            print(f"❌ UNEXPECTED: Got status {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 7: Try to access AI dashboard after login
    print("\n📋 Test 7: Access AI Dashboard (Authenticated)")
    print("-" * 50)
    
    try:
        response = session.get(f"{base_url}/ai-dashboard", allow_redirects=False)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: AI Dashboard accessible after login")
            # Check content
            if "AI Business Intelligence" in response.text:
                print("✅ SUCCESS: AI Dashboard content loaded correctly")
            else:
                print("❌ ISSUE: AI Dashboard content not loaded correctly")
                print("First 200 chars:", response.text[:200])
        elif response.status_code == 302:
            print("❌ ISSUE: Still getting redirected after login")
            redirect_location = response.headers.get('Location', 'Not set')
            print(f"Redirect Location: {redirect_location}")
        else:
            print(f"❌ UNEXPECTED: Got status {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test 8: Check if session cookie is being sent
    print("\n📋 Test 8: Session Cookie Verification")
    print("-" * 50)
    
    # Make another request to see if cookies are being sent
    try:
        response = session.get(f"{base_url}/app")
        print(f"Status Code: {response.status_code}")
        
        # Check if the session cookie is still there
        session_cookie = session.cookies.get('session')
        if session_cookie:
            print(f"✅ Session cookie present: {session_cookie[:50]}...")
        else:
            print("❌ Session cookie missing")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 FINAL DIAGNOSIS")
    print("=" * 50)
    
    # Final analysis
    if "AI Business Intelligence" in response.text:
        print("✅ SUCCESS: Everything is working correctly!")
    else:
        print("❌ ISSUES DETECTED:")
        print("   - Session not being maintained between requests")
        print("   - Possible Flask session configuration issue")
        print("   - Check if session middleware is working")

if __name__ == "__main__":
    test_simple_session()

