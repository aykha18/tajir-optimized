#!/usr/bin/env python3
"""
Simple test script for catalog scanner functionality
"""

import requests
import json
import os
import sys

def test_catalog_scanner():
    """Test the catalog scanner API endpoints"""
    
    base_url = "http://localhost:5000"
    
    # Test file path - use your actual CSV file
    csv_file_path = "my_catalog.csv"
    
    print("🔍 Testing Catalog Scanner Functionality")
    print("=" * 50)
    
    # Check if file exists
    try:
        if not os.path.exists(csv_file_path):
            # Try alternative path with different encoding
            alt_path = r"C:\Users\Khana\OneDrive\Tài liệu\my_catalog.csv"
            if os.path.exists(alt_path):
                csv_file_path = alt_path
            else:
                print(f"❌ File not found: {csv_file_path}")
                print(f"❌ Alternative path also not found: {alt_path}")
                return False
    except Exception as e:
        print(f"❌ Error checking file: {e}")
        return False
    
    print(f"✅ Found CSV file: {csv_file_path}")
    
    # Test 1: Scan catalog
    print("\n📋 Test 1: Scanning catalog...")
    try:
        # Read CSV file and convert to catalog data
        import csv
        catalog_data = []
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                catalog_data.append({
                    'name': row.get('name', ''),
                    'price': float(row.get('price', 0)),
                    'category': row.get('category', ''),
                    'description': row.get('description', '')
                })
        
        print(f"   - Loaded {len(catalog_data)} products from CSV")
        
        # Send as JSON data
        response = requests.post(
            f"{base_url}/api/catalog/scan", 
            json={'catalog': catalog_data}, 
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Catalog scan successful!")
                print(f"   - Found {len(result.get('suggestions', {}).get('product_types', []))} product types")
                total_products = sum(len(t.get('products', [])) for t in result.get('suggestions', {}).get('product_types', []))
                print(f"   - Found {total_products} products")
                
                # Store suggestions for next test
                suggestions = result.get('suggestions', {})
                
                # Test 2: Check duplicates
                print("\n🔍 Test 2: Checking for duplicates...")
                duplicate_response = requests.post(
                    f"{base_url}/api/catalog/check-duplicates",
                    json={'suggestions': suggestions},
                    timeout=30
                )
                
                if duplicate_response.status_code == 200:
                    duplicate_result = duplicate_response.json()
                    if duplicate_result.get('success'):
                        analysis = duplicate_result.get('analysis', {})
                        print("✅ Duplicate check successful!")
                        print(f"   - Total types: {analysis.get('total_types', 0)}")
                        print(f"   - Total products: {analysis.get('total_products', 0)}")
                        print(f"   - Existing types: {analysis.get('existing_types', 0)}")
                        print(f"   - Existing products: {analysis.get('existing_products', 0)}")
                        print(f"   - New types: {analysis.get('new_types', 0)}")
                        print(f"   - New products: {analysis.get('new_products', 0)}")
                        print(f"   - Duplicate percentage: {analysis.get('duplicate_percentage', 0):.1f}%")
                        
                        # Show some existing items if any
                        existing_items = duplicate_result.get('existing_items', {})
                        if existing_items.get('product_types'):
                            print("\n📝 Existing Product Types:")
                            for type_name, info in existing_items['product_types'].items():
                                if info.get('exists'):
                                    print(f"   - {type_name}")
                        
                        if existing_items.get('products'):
                            print("\n📝 Existing Products:")
                            for product_name, info in existing_items['products'].items():
                                if info.get('exists'):
                                    print(f"   - {product_name} (Current: {info.get('current_rate', 'N/A')}, New: {info.get('new_rate', 'N/A')})")
                        
                        # Show similar products if any
                        similar_products = duplicate_result.get('similar_products', {})
                        if similar_products:
                            print("\n🔍 Similar Products Found:")
                            for product_name, similar_list in similar_products.items():
                                if similar_list:
                                    print(f"   - '{product_name}' similar to:")
                                    for similar in similar_list[:3]:  # Show top 3
                                        print(f"     * '{similar['product_name']}' (similarity: {similar['similarity']:.2f})")
                        
                        return True
                    else:
                        print(f"❌ Duplicate check failed: {duplicate_result.get('error', 'Unknown error')}")
                else:
                    print(f"❌ Duplicate check failed with status {duplicate_response.status_code}")
                    print(f"   Response: {duplicate_response.text}")
                
            else:
                print(f"❌ Catalog scan failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Catalog scan failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Flask app is running on localhost:5000")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

def test_auto_create():
    """Test auto-create functionality (will not actually create products)"""
    print("\n🚀 Test 3: Testing auto-create (dry run)...")
    print("⚠️  This will not actually create products, just test the endpoint")
    
    # Create sample suggestions for testing
    sample_suggestions = {
        "product_types": [
            {
                "name": "Test Category",
                "description": "Test category for testing",
                "products": [
                    {
                        "name": "Test Product 1",
                        "rate": 100.0,
                        "description": "Test product 1"
                    },
                    {
                        "name": "Test Product 2", 
                        "rate": 200.0,
                        "description": "Test product 2"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/catalog/auto-create",
            json={'suggestions': sample_suggestions},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Auto-create endpoint working!")
                print(f"   - Created {len(result.get('created_types', []))} types")
                print(f"   - Created {len(result.get('created_products', []))} products")
            else:
                print(f"❌ Auto-create failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Auto-create failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing auto-create: {e}")

if __name__ == "__main__":
    print("Starting Catalog Scanner Tests...")
    print("Make sure the Flask app is running on localhost:5000")
    print()
    
    success = test_catalog_scanner()
    
    if success:
        test_auto_create()
    
    print("\n" + "=" * 50)
    print("Test completed!")



