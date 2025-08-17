#!/usr/bin/env python3
"""
Test script for the Catalog Scanner feature
"""

import requests
import json

# Test data
test_catalog = [
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
    }
]

def test_catalog_scan():
    """Test the catalog scan endpoint"""
    print("Testing Catalog Scan API...")
    
    try:
        response = requests.post(
            'http://localhost:5000/api/catalog/scan',
            json={'catalog': test_catalog},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Catalog scan successful!")
            print(f"📊 Analysis Results:")
            print(f"   - Total items: {result['analysis']['total_items']}")
            print(f"   - Categories found: {len(result['analysis']['categories'])}")
            print(f"   - Product types suggested: {len(result['suggestions']['product_types'])}")
            
            # Show suggested product types
            print("\n📋 Suggested Product Types:")
            for pt in result['suggestions']['product_types']:
                print(f"   - {pt['name']}: {len(pt['products'])} products")
            
            return result
        else:
            print(f"❌ Catalog scan failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing catalog scan: {e}")
        return None

def test_auto_create(suggestions):
    """Test the auto-create endpoint"""
    if not suggestions:
        print("❌ No suggestions available for auto-create test")
        return
    
    print("\nTesting Auto-Create API...")
    
    try:
        response = requests.post(
            'http://localhost:5000/api/catalog/auto-create',
            json={'suggestions': suggestions},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Auto-create successful!")
            print(f"📝 Created {result['created_types']} product types and {result['created_products']} products")
            print(f"Message: {result['message']}")
        else:
            print(f"❌ Auto-create failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing auto-create: {e}")

def main():
    """Main test function"""
    print("🧪 Testing Catalog Scanner Feature")
    print("=" * 50)
    
    # Test catalog scan
    scan_result = test_catalog_scan()
    
    if scan_result:
        # Test auto-create (commented out to avoid creating test data)
        # test_auto_create(scan_result['suggestions'])
        print("\n⚠️  Auto-create test skipped to avoid creating test data")
        print("   Uncomment the line in main() to test auto-create functionality")
    
    print("\n✅ Catalog Scanner feature test completed!")

if __name__ == "__main__":
    main()
