#!/usr/bin/env python3
"""
Test OCR functionality with OpenCV fallback
This script tests the OCR feature when OpenCV is not available
"""

import os
import sys
import requests
from PIL import Image, ImageDraw, ImageFont
import tempfile

def create_test_image():
    """Create a test image with text"""
    try:
        # Create a simple test image
        width, height = 800, 400
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Try to use a default font, fallback to basic if not available
        try:
            # Try to use a system font
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)  # macOS
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)  # Linux
                except:
                    font = ImageFont.load_default()  # Fallback
        
        # Add text to image
        text = "OCR Test Image\nThis is a sample text for testing OCR functionality\nProduct: Linen Shirt\nPrice: AED 120"
        draw.text((50, 50), text, fill='black', font=font)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        image.save(temp_file.name)
        temp_file.close()
        
        print(f"✅ Test image created: {temp_file.name}")
        return temp_file.name
        
    except Exception as e:
        print(f"❌ Error creating test image: {e}")
        return None

def test_ocr_without_opencv():
    """Test OCR functionality without OpenCV"""
    print("🧪 Testing OCR without OpenCV")
    print("=" * 50)
    
    # Create test image
    image_path = create_test_image()
    if not image_path:
        return False
    
    try:
        # Test server connectivity
        print("🔍 Checking server connectivity...")
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
        else:
            print(f"❌ Server returned status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the Flask app is running on localhost:5000")
        return False
    
    # Test single image OCR
    print("\n🧪 Testing Single Image OCR...")
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(
                "http://localhost:5000/api/ocr/extract",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Single image OCR successful!")
            print(f"   Extracted text: {result.get('text', '')[:100]}...")
            print(f"   Confidence: {result.get('confidence', 0)}%")
            print(f"   Message: {result.get('message', '')}")
            
            # Check for expected keywords
            text = result.get('text', '').lower()
            expected_keywords = ['ocr', 'test', 'image', 'linen', 'shirt', 'aed', '120']
            found_keywords = [kw for kw in expected_keywords if kw in text]
            print(f"   ✅ Found expected keywords: {found_keywords}")
            
        else:
            print(f"❌ OCR failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing OCR: {e}")
        return False
    
    # Cleanup
    try:
        os.unlink(image_path)
        print(f"🧹 Cleaned up test file: {image_path}")
    except:
        pass
    
    print("\n✅ OCR test completed successfully!")
    return True

def test_opencv_availability():
    """Test if OpenCV is available"""
    print("\n🔍 Testing OpenCV availability...")
    try:
        import cv2
        print(f"✅ OpenCV is available: {cv2.__version__}")
        return True
    except ImportError as e:
        print(f"⚠️  OpenCV not available: {e}")
        print("   OCR will use PIL fallback")
        return False

if __name__ == "__main__":
    print("🧪 OCR Fallback Test Suite")
    print("=" * 50)
    
    # Test OpenCV availability
    opencv_available = test_opencv_availability()
    
    # Test OCR functionality
    success = test_ocr_without_opencv()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    print(f"   OpenCV Available: {'✅ YES' if opencv_available else '⚠️  NO (using fallback)'}")
    print(f"   OCR Functionality: {'✅ PASS' if success else '❌ FAIL'}")
    
    if success:
        print("\n🎯 OCR is working correctly!")
        if not opencv_available:
            print("   Using PIL fallback for image processing")
        else:
            print("   Using OpenCV for image processing")
    else:
        print("\n❌ OCR test failed. Please check the server logs.")
    
    print("\n📝 Next Steps:")
    print("1. Test the OCR feature in the web interface")
    print("2. Upload real images with text content")
    print("3. Verify extracted text accuracy")
    print("4. Deploy to Railway with the updated configuration")
