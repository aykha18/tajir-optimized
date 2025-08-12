#!/usr/bin/env python3
"""
Test script to verify reports API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_reports_api():
    print("🧪 Testing Reports API...")
    
    # Test 1: Get invoices report
    print("\n1. Testing GET /api/reports/invoices")
    try:
        response = requests.get(f"{BASE_URL}/api/reports/invoices")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success - Data received")
            if isinstance(data, dict):
                print(f"   Records: {data.get('total_records', 'N/A')}")
            elif isinstance(data, list):
                print(f"   Records: {len(data)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Get employees report
    print("\n2. Testing GET /api/reports/employees")
    try:
        response = requests.get(f"{BASE_URL}/api/reports/employees")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success - Data received")
            if isinstance(data, dict):
                print(f"   Records: {data.get('total_records', 'N/A')}")
            elif isinstance(data, list):
                print(f"   Records: {len(data)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Get products report
    print("\n3. Testing GET /api/reports/products")
    try:
        response = requests.get(f"{BASE_URL}/api/reports/products")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success - Data received")
            if isinstance(data, dict):
                print(f"   Records: {data.get('total_records', 'N/A')}")
            elif isinstance(data, list):
                print(f"   Records: {len(data)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Test with filters
    print("\n4. Testing GET /api/reports/invoices with filters")
    try:
        params = {
            'from_date': '2024-01-01',
            'to_date': '2024-12-31',
            'status': 'All'
        }
        response = requests.get(f"{BASE_URL}/api/reports/invoices", params=params)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success - Filtered data received")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_reports_api()
