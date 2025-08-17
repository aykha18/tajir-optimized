#!/usr/bin/env python3
"""
Catalog Scanner Test Script

This script tests the Catalog Scanner feature by sending sample catalog data
to the backend API endpoints and validating the responses.

Features:
- Tests catalog scan endpoint with sample data
- Tests auto-create endpoint (optional)
- Validates API responses and data structure
- Provides detailed test results and recommendations

Usage:
    python test_catalog_scanner.py

Requirements:
    - Flask app running on localhost:5000
    - requests library installed

@author Tajir POS Team
@version 1.0.0
"""

import requests
import json
import sys
from typing import Dict, List, Optional

# Test configuration
API_BASE_URL = 'http://localhost:5000'
CATALOG_SCAN_ENDPOINT = f'{API_BASE_URL}/api/catalog/scan'
AUTO_CREATE_ENDPOINT = f'{API_BASE_URL}/api/catalog/auto-create'

# Sample test catalog data
TEST_CATALOG = [
    {
        "name": "Linen Shirt",
        "price": 120.00,
        "category": "Shirts",
        "description": "High-quality linen shirt with modern fit"
    },
    {
        "name": "Cotton T-Shirt",
        "price": 45.00,
        "category": "Shirts",
        "description": "Comfortable cotton t-shirt"
    },
    {
        "name": "Wool Blazer",
        "price": 350.00,
        "category": "Coats",
        "description": "Professional wool blazer for formal occasions"
    },
    {
        "name": "Silk Dress",
        "price": 280.00,
        "category": "Dresses",
        "description": "Elegant silk dress for special events"
    },
    {
        "name": "Denim Jeans",
        "price": 180.00,
        "category": "Pants",
        "description": "Classic denim jeans with perfect fit"
    },
    {
        "name": "Cotton Kurta",
        "price": 95.00,
        "category": "Traditional",
        "description": "Traditional cotton kurta with embroidery"
    },
    {
        "name": "Silk Saree",
        "price": 450.00,
        "category": "Traditional",
        "description": "Premium silk saree with designer work"
    },
    {
        "name": "Leather Jacket",
        "price": 420.00,
        "category": "Coats",
        "description": "Stylish leather jacket for casual wear"
    },
    {
        "name": "Wool Sweater",
        "price": 150.00,
        "category": "Winter",
        "description": "Warm wool sweater for cold weather"
    },
    {
        "name": "Linen Pants",
        "price": 110.00,
        "category": "Pants",
        "description": "Comfortable linen pants for summer"
    }
]


def check_server_connectivity() -> bool:
    """
    Check if the Flask server is running and accessible.
    
    Returns:
        bool: True if server is accessible, False otherwise
    """
    try:
        response = requests.get(API_BASE_URL, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Server connectivity error: {e}")
        return False


def test_catalog_scan() -> Optional[Dict]:
    """
    Test the catalog scan endpoint with sample data.
    
    Returns:
        Optional[Dict]: API response data if successful, None otherwise
    """
    print("🧪 Testing Catalog Scan API...")
    print(f"   Endpoint: {CATALOG_SCAN_ENDPOINT}")
    print(f"   Sample data: {len(TEST_CATALOG)} products")
    
    try:
        response = requests.post(
            CATALOG_SCAN_ENDPOINT,
            json={'catalog': TEST_CATALOG},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("✅ Catalog scan successful!")
                print(f"📊 Analysis Results:")
                print(f"   - Total items: {result['analysis']['total_items']}")
                print(f"   - Categories found: {len(result['analysis']['categories'])}")
                print(f"   - Product types suggested: {len(result['suggestions']['product_types'])}")
                
                # Display categories breakdown
                print("\n📋 Categories Analysis:")
                for category, data in result['analysis']['categories'].items():
                    print(f"   - {category}: {data['count']} items (Avg: AED {data['avg_price']:.2f})")
                
                # Display suggested product types
                print("\n📋 Suggested Product Types:")
                for pt in result['suggestions']['product_types']:
                    print(f"   - {pt['name']}: {len(pt['products'])} products")
                    for product in pt['products'][:3]:  # Show first 3 products
                        print(f"     • {product['name']} - AED {product['rate']}")
                    if len(pt['products']) > 3:
                        print(f"     ... and {len(pt['products']) - 3} more")
                
                # Display recommendations
                if result['suggestions']['recommendations']:
                    print("\n💡 Recommendations:")
                    for rec in result['suggestions']['recommendations'][:5]:  # Show first 5
                        print(f"   - {rec['suggestion']}")
                
                return result
            else:
                print(f"❌ Catalog scan failed: {result.get('error', 'Unknown error')}")
                return None
        else:
            print(f"❌ Catalog scan failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - server may be slow or unresponsive")
        return None
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - check if server is running")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def test_auto_create(suggestions: Dict) -> bool:
    """
    Test the auto-create endpoint with suggestions from catalog scan.
    
    Args:
        suggestions (Dict): Suggestions data from catalog scan
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not suggestions:
        print("❌ No suggestions available for auto-create test")
        return False
    
    print("\n🧪 Testing Auto-Create API...")
    print(f"   Endpoint: {AUTO_CREATE_ENDPOINT}")
    print("   ⚠️  This will create actual products in the database")
    
    # Ask for confirmation
    try:
        confirm = input("   Do you want to proceed? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("   ⏭️  Auto-create test skipped")
            return False
    except KeyboardInterrupt:
        print("\n   ⏭️  Auto-create test cancelled")
        return False
    
    try:
        response = requests.post(
            AUTO_CREATE_ENDPOINT,
            json={'suggestions': suggestions},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("✅ Auto-create successful!")
                print(f"📝 Created {result['created_types']} product types and {result['created_products']} products")
                print(f"Message: {result['message']}")
                
                # Show created items
                if result.get('created_types'):
                    print("\n📋 Created Product Types:")
                    for pt in result['created_types']:
                        print(f"   - {pt['name']} (ID: {pt['type_id']})")
                
                if result.get('created_products'):
                    print("\n📋 Created Products:")
                    for product in result['created_products'][:5]:  # Show first 5
                        print(f"   - {product['name']} (AED {product['rate']}) - {product['type_name']}")
                    if len(result['created_products']) > 5:
                        print(f"   ... and {len(result['created_products']) - 5} more")
                
                return True
            else:
                print(f"❌ Auto-create failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Auto-create failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - server may be slow or unresponsive")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - check if server is running")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_invalid_data() -> bool:
    """
    Test API endpoints with invalid data to ensure proper error handling.
    
    Returns:
        bool: True if error handling works correctly, False otherwise
    """
    print("\n🧪 Testing Error Handling...")
    
    # Test with empty catalog
    try:
        response = requests.post(
            CATALOG_SCAN_ENDPOINT,
            json={'catalog': []},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 400:
            result = response.json()
            if 'No catalog data provided' in result.get('error', ''):
                print("✅ Empty catalog validation working correctly")
            else:
                print(f"❌ Unexpected error message: {result.get('error')}")
                return False
        else:
            print(f"❌ Expected 400 status, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing invalid data: {e}")
        return False
    
    # Test with malformed data
    try:
        response = requests.post(
            CATALOG_SCAN_ENDPOINT,
            json={'catalog': [{'invalid': 'data'}]},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code in [400, 500]:
            print("✅ Malformed data validation working correctly")
        else:
            print(f"❌ Expected error status, got {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing malformed data: {e}")
        return False
    
    return True


def main():
    """
    Main test function that orchestrates all tests.
    """
    print("🧪 Catalog Scanner Feature Test Suite")
    print("=" * 60)
    
    # Check server connectivity
    print("🔍 Checking server connectivity...")
    if not check_server_connectivity():
        print("\n❌ Cannot connect to server.")
        print("   Please make sure the Flask app is running on localhost:5000")
        print("   Run: python app.py")
        sys.exit(1)
    
    print("✅ Server is running and accessible")
    
    # Run tests
    test_results = {
        'catalog_scan': False,
        'error_handling': False,
        'auto_create': False
    }
    
    # Test catalog scan
    scan_result = test_catalog_scan()
    test_results['catalog_scan'] = scan_result is not None
    
    # Test error handling
    test_results['error_handling'] = test_invalid_data()
    
    # Test auto-create (optional)
    if scan_result and scan_result.get('suggestions'):
        test_results['auto_create'] = test_auto_create(scan_result['suggestions'])
    else:
        print("\n⚠️  Auto-create test skipped - no valid suggestions available")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in test_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Catalog Scanner feature is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the server logs and try again.")
    
    print("\n📝 Next Steps:")
    print("1. Test the feature in the web interface")
    print("2. Upload a real catalog CSV file")
    print("3. Verify created products in the Products section")
    print("4. Check the logs for any errors")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error in main: {e}")
        sys.exit(1)
