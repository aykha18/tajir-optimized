#!/usr/bin/env python3
"""
OCR Feature Test Script

This script tests the OCR (Optical Character Recognition) functionality by creating
sample images and testing the API endpoints for text extraction.

Features:
- Creates test images with known text content
- Tests single image OCR endpoint
- Tests batch image OCR endpoint
- Validates authentication and error handling
- Provides detailed test results and recommendations

Usage:
    python test_ocr.py

Requirements:
    - Flask app running on localhost:5000
    - requests library installed
    - Pillow library installed
    - Tesseract OCR installed (for backend processing)

@author Tajir POS Team
@version 1.0.0
"""

import requests
import base64
from PIL import Image, ImageDraw, ImageFont
import io
import os
import sys
from typing import List, Dict, Optional

# Test configuration
API_BASE_URL = 'http://localhost:5000'
OCR_SINGLE_ENDPOINT = f'{API_BASE_URL}/api/ocr/extract'
OCR_BATCH_ENDPOINT = f'{API_BASE_URL}/api/ocr/extract-batch'

# Test image configuration
TEST_IMAGE_PATH = "test_ocr_image.png"
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 400
FONT_SIZE = 24


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


def create_test_image() -> str:
    """
    Create a test image with text for OCR testing.
    
    Returns:
        str: Path to the created test image
    """
    print("🖼️  Creating test image...")
    
    # Create a new image with white background
    image = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a system font, fallback to default if not available
    font = None
    font_paths = [
        "arial.ttf",
        "/System/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/arial.ttf"
    ]
    
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, FONT_SIZE)
            print(f"   Using font: {font_path}")
            break
        except:
            continue
    
    if font is None:
        font = ImageFont.load_default()
        print("   Using default font")
    
    # Add text to the image
    text_lines = [
        "OCR Test Image",
        "This is a sample text for testing OCR functionality.",
        "Product: Linen Shirt",
        "Price: AED 120.00",
        "Category: Clothing",
        "Description: High-quality linen shirt with modern fit",
        "Additional Information:",
        "- Material: 100% Linen",
        "- Size: Medium",
        "- Color: Natural"
    ]
    
    y_position = 30
    for line in text_lines:
        draw.text((30, y_position), line, fill='black', font=font)
        y_position += 35
    
    # Save the image
    image.save(TEST_IMAGE_PATH)
    print(f"✅ Test image created: {TEST_IMAGE_PATH}")
    return TEST_IMAGE_PATH


def test_ocr_single_image(image_path: str) -> bool:
    """
    Test single image OCR endpoint.
    
    Args:
        image_path (str): Path to the test image
        
    Returns:
        bool: True if successful, False otherwise
    """
    print("\n🧪 Testing Single Image OCR...")
    print(f"   Endpoint: {OCR_SINGLE_ENDPOINT}")
    print(f"   Image: {image_path}")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(OCR_SINGLE_ENDPOINT, files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("✅ Single image OCR successful!")
                print(f"   Extracted text: {result.get('text', 'No text')[:100]}...")
                print(f"   Confidence: {result.get('confidence', 0):.1f}%")
                print(f"   Message: {result.get('message', '')}")
                
                # Validate extracted text
                expected_keywords = ['OCR', 'Test', 'Image', 'Linen', 'Shirt', 'AED', '120']
                extracted_text = result.get('text', '').lower()
                found_keywords = [kw for kw in expected_keywords if kw.lower() in extracted_text]
                
                if len(found_keywords) >= 3:
                    print(f"   ✅ Found expected keywords: {found_keywords}")
                else:
                    print(f"   ⚠️  Limited keyword detection: {found_keywords}")
                
                return True
            else:
                print(f"❌ OCR failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Single image OCR failed with status {response.status_code}")
            print(f"   Response: {response.text}")
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


def test_ocr_batch_images(image_path: str) -> bool:
    """
    Test batch image OCR endpoint.
    
    Args:
        image_path (str): Path to the test image
        
    Returns:
        bool: True if successful, False otherwise
    """
    print("\n🧪 Testing Batch Image OCR...")
    print(f"   Endpoint: {OCR_BATCH_ENDPOINT}")
    print(f"   Images: 2 copies of {image_path}")
    
    try:
        with open(image_path, 'rb') as f1, open(image_path, 'rb') as f2:
            files = [
                ('images', ('test1.png', f1, 'image/png')),
                ('images', ('test2.png', f2, 'image/png'))
            ]
            response = requests.post(OCR_BATCH_ENDPOINT, files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("✅ Batch image OCR successful!")
                print(f"   Processed {len(result.get('results', []))} images")
                
                success_count = 0
                for i, img_result in enumerate(result.get('results', [])):
                    print(f"\n   Image {i+1}: {img_result.get('filename', 'Unknown')}")
                    print(f"   Success: {img_result.get('success', False)}")
                    
                    if img_result.get('success'):
                        success_count += 1
                        print(f"   Text: {img_result.get('text', 'No text')[:50]}...")
                        print(f"   Confidence: {img_result.get('confidence', 0):.1f}%")
                    else:
                        print(f"   Error: {img_result.get('error', 'Unknown error')}")
                
                if success_count == len(result.get('results', [])):
                    print(f"   ✅ All {success_count} images processed successfully")
                    return True
                else:
                    print(f"   ⚠️  {success_count}/{len(result.get('results', []))} images processed successfully")
                    return False
            else:
                print(f"❌ Batch OCR failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Batch image OCR failed with status {response.status_code}")
            print(f"   Response: {response.text}")
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


def test_ocr_without_authentication() -> bool:
    """
    Test OCR endpoints without authentication to ensure proper security.
    
    Returns:
        bool: True if authentication check works correctly, False otherwise
    """
    print("\n🧪 Testing Authentication...")
    
    # Create a simple test image in memory
    image = Image.new('RGB', (200, 100), color='white')
    draw = ImageDraw.Draw(image)
    draw.text((10, 40), "Test", fill='black')
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    try:
        files = {'image': ('test.png', img_byte_arr, 'image/png')}
        response = requests.post(OCR_SINGLE_ENDPOINT, files=files, timeout=10)
        
        if response.status_code == 401:
            print("✅ Authentication check working correctly")
            return True
        else:
            print(f"❌ Authentication check failed - got status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing authentication: {e}")
        return False


def test_invalid_file_type() -> bool:
    """
    Test OCR with invalid file type to ensure proper validation.
    
    Returns:
        bool: True if file type validation works correctly, False otherwise
    """
    print("\n🧪 Testing File Type Validation...")
    
    try:
        # Create a text file instead of image
        files = {'image': ('test.txt', io.BytesIO(b'This is not an image'), 'text/plain')}
        response = requests.post(OCR_SINGLE_ENDPOINT, files=files, timeout=10)
        
        if response.status_code == 400:
            result = response.json()
            if 'Invalid file type' in result.get('error', ''):
                print("✅ File type validation working correctly")
                return True
            else:
                print(f"❌ Unexpected error message: {result.get('error')}")
                return False
        else:
            print(f"❌ File type validation failed - got status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing file type validation: {e}")
        return False


def test_large_file_handling() -> bool:
    """
    Test OCR with a large file to ensure proper size validation.
    
    Returns:
        bool: True if size validation works correctly, False otherwise
    """
    print("\n🧪 Testing File Size Validation...")
    
    try:
        # Create a large image (simulate large file)
        large_image = Image.new('RGB', (4000, 3000), color='white')
        draw = ImageDraw.Draw(large_image)
        draw.text((100, 100), "Large Test Image", fill='black')
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        large_image.save(img_byte_arr, format='PNG', quality=95)
        img_byte_arr.seek(0)
        
        files = {'image': ('large_test.png', img_byte_arr, 'image/png')}
        response = requests.post(OCR_SINGLE_ENDPOINT, files=files, timeout=30)
        
        # Large files should either be processed or rejected gracefully
        if response.status_code in [200, 400, 413]:
            print("✅ File size handling working correctly")
            return True
        else:
            print(f"❌ Unexpected response for large file: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing large file handling: {e}")
        return False


def cleanup_test_files(image_path: str) -> None:
    """
    Clean up test files created during testing.
    
    Args:
        image_path (str): Path to the test image to remove
    """
    try:
        if os.path.exists(image_path):
            os.remove(image_path)
            print(f"\n🧹 Cleaned up test file: {image_path}")
    except Exception as e:
        print(f"⚠️  Could not clean up test file: {e}")


def main():
    """
    Main test function that orchestrates all tests.
    """
    print("🧪 OCR Feature Test Suite")
    print("=" * 60)
    
    # Check server connectivity
    print("🔍 Checking server connectivity...")
    if not check_server_connectivity():
        print("\n❌ Cannot connect to server.")
        print("   Please make sure the Flask app is running on localhost:5000")
        print("   Run: python app.py")
        sys.exit(1)
    
    print("✅ Server is running and accessible")
    
    # Create test image
    image_path = create_test_image()
    
    # Run tests
    test_results = {
        'single_image_ocr': False,
        'batch_image_ocr': False,
        'authentication': False,
        'file_type_validation': False,
        'file_size_handling': False
    }
    
    try:
        # Test single image OCR
        test_results['single_image_ocr'] = test_ocr_single_image(image_path)
        
        # Test batch image OCR
        test_results['batch_image_ocr'] = test_ocr_batch_images(image_path)
        
        # Test authentication
        test_results['authentication'] = test_ocr_without_authentication()
        
        # Test file type validation
        test_results['file_type_validation'] = test_invalid_file_type()
        
        # Test file size handling
        test_results['file_size_handling'] = test_large_file_handling()
        
    finally:
        # Clean up
        cleanup_test_files(image_path)
    
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
        print("🎉 All tests passed! OCR feature is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the server logs and try again.")
    
    print("\n📝 Next Steps:")
    print("1. Install Tesseract OCR if not already installed")
    print("2. Test the OCR feature in the web interface")
    print("3. Upload real images with text content")
    print("4. Check the logs for any errors")
    print("5. Verify extracted text accuracy")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error in main: {e}")
        sys.exit(1)
