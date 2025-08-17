#!/usr/bin/env python3
"""
OCR Feature Test Script
Tests the OCR functionality by creating a sample image and testing the API endpoints
"""

import requests
import base64
from PIL import Image, ImageDraw, ImageFont
import io
import os

def create_test_image():
    """Create a test image with text for OCR testing"""
    # Create a new image with white background
    width, height = 800, 400
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a default font, fallback to basic if not available
    try:
        # Try to use a system font
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            except:
                # Fallback to default font
                font = ImageFont.load_default()
    
    # Add text to the image
    text_lines = [
        "OCR Test Image",
        "This is a sample text for testing OCR functionality.",
        "Product: Linen Shirt",
        "Price: AED 120.00",
        "Category: Clothing",
        "Description: High-quality linen shirt with modern fit"
    ]
    
    y_position = 50
    for line in text_lines:
        draw.text((50, y_position), line, fill='black', font=font)
        y_position += 40
    
    # Save the image
    image_path = "test_ocr_image.png"
    image.save(image_path)
    print(f"Created test image: {image_path}")
    return image_path

def test_ocr_single_image(image_path):
    """Test single image OCR endpoint"""
    print("\n=== Testing Single Image OCR ===")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post('http://localhost:5000/api/ocr/extract', files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Single image OCR successful!")
            print(f"Extracted text: {result.get('text', 'No text')}")
            print(f"Confidence: {result.get('confidence', 0):.1f}%")
            print(f"Message: {result.get('message', '')}")
        else:
            print(f"❌ Single image OCR failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing single image OCR: {e}")

def test_ocr_batch_images(image_path):
    """Test batch image OCR endpoint"""
    print("\n=== Testing Batch Image OCR ===")
    
    try:
        with open(image_path, 'rb') as f1, open(image_path, 'rb') as f2:
            files = [
                ('images', ('test1.png', f1, 'image/png')),
                ('images', ('test2.png', f2, 'image/png'))
            ]
            response = requests.post('http://localhost:5000/api/ocr/extract-batch', files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Batch image OCR successful!")
            print(f"Processed {len(result.get('results', []))} images")
            
            for i, img_result in enumerate(result.get('results', [])):
                print(f"\nImage {i+1}: {img_result.get('filename', 'Unknown')}")
                print(f"Success: {img_result.get('success', False)}")
                print(f"Text: {img_result.get('text', 'No text')}")
                print(f"Confidence: {img_result.get('confidence', 0):.1f}%")
                if img_result.get('error'):
                    print(f"Error: {img_result.get('error')}")
        else:
            print(f"❌ Batch image OCR failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing batch image OCR: {e}")

def test_ocr_without_authentication():
    """Test OCR endpoints without authentication"""
    print("\n=== Testing OCR without Authentication ===")
    
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
        response = requests.post('http://localhost:5000/api/ocr/extract', files=files)
        
        if response.status_code == 401:
            print("✅ Authentication check working correctly")
        else:
            print(f"❌ Authentication check failed - got status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing authentication: {e}")

def test_invalid_file_type():
    """Test OCR with invalid file type"""
    print("\n=== Testing Invalid File Type ===")
    
    try:
        # Create a text file instead of image
        files = {'image': ('test.txt', io.BytesIO(b'This is not an image'), 'text/plain')}
        response = requests.post('http://localhost:5000/api/ocr/extract', files=files)
        
        if response.status_code == 400:
            result = response.json()
            if 'Invalid file type' in result.get('error', ''):
                print("✅ File type validation working correctly")
            else:
                print(f"❌ Unexpected error message: {result.get('error')}")
        else:
            print(f"❌ File type validation failed - got status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing file type validation: {e}")

def cleanup_test_files(image_path):
    """Clean up test files"""
    try:
        if os.path.exists(image_path):
            os.remove(image_path)
            print(f"\n🧹 Cleaned up test file: {image_path}")
    except Exception as e:
        print(f"⚠️ Could not clean up test file: {e}")

def main():
    """Main test function"""
    print("🧪 OCR Feature Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:5000/')
        if response.status_code != 200:
            print("❌ Server is not responding properly")
            return
        print("✅ Server is running")
    except:
        print("❌ Cannot connect to server. Make sure the Flask app is running on localhost:5000")
        return
    
    # Create test image
    image_path = create_test_image()
    
    try:
        # Run tests
        test_ocr_single_image(image_path)
        test_ocr_batch_images(image_path)
        test_ocr_without_authentication()
        test_invalid_file_type()
        
        print("\n" + "=" * 50)
        print("🎉 OCR Feature Test Suite Complete!")
        print("\nNext steps:")
        print("1. Install Tesseract OCR if not already installed")
        print("2. Test the OCR feature in the web interface")
        print("3. Check the logs for any errors")
        
    finally:
        # Clean up
        cleanup_test_files(image_path)

if __name__ == "__main__":
    main()
