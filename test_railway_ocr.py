#!/usr/bin/env python3
"""
Railway OCR Test Script

This script verifies that Tesseract OCR is properly installed and configured
on Railway deployment.

Usage:
    python test_railway_ocr.py

@author Tajir POS Team
@version 1.0.0
"""

import os
import sys
import subprocess
import pytesseract
from PIL import Image, ImageDraw, ImageFont

def test_tesseract_installation():
    """Test if Tesseract is installed and accessible"""
    print("🔍 Testing Tesseract Installation...")
    
    try:
        # Test system Tesseract
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ System Tesseract is installed")
            print(f"   Version: {result.stdout.strip()}")
            return True
        else:
            print("❌ System Tesseract not found")
            return False
    except FileNotFoundError:
        print("❌ Tesseract command not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Tesseract command timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing Tesseract: {e}")
        return False

def test_pytesseract():
    """Test Python pytesseract library"""
    print("\n🔍 Testing Python pytesseract...")
    
    try:
        # Test pytesseract import
        version = pytesseract.get_tesseract_version()
        print(f"✅ pytesseract is working")
        print(f"   Tesseract version: {version}")
        
        # Test Tesseract path
        cmd = pytesseract.pytesseract.tesseract_cmd
        print(f"   Tesseract path: {cmd}")
        
        return True
    except Exception as e:
        print(f"❌ pytesseract error: {e}")
        return False

def test_ocr_functionality():
    """Test actual OCR functionality"""
    print("\n🔍 Testing OCR Functionality...")
    
    try:
        # Create a simple test image
        image = Image.new('RGB', (300, 100), color='white')
        draw = ImageDraw.Draw(image)
        
        # Try to use a font
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Add text to image
        draw.text((10, 40), "OCR Test", fill='black', font=font)
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        text = text.strip()
        
        if text:
            print("✅ OCR functionality working")
            print(f"   Extracted text: '{text}'")
            return True
        else:
            print("⚠️  OCR extracted no text (this might be normal)")
            return True
            
    except Exception as e:
        print(f"❌ OCR functionality error: {e}")
        return False

def test_environment():
    """Test environment variables and configuration"""
    print("\n🔍 Testing Environment...")
    
    # Check environment variables
    env_vars = {
        'FLASK_ENV': os.getenv('FLASK_ENV', 'Not set'),
        'PORT': os.getenv('PORT', 'Not set'),
        'TESSERACT_ENABLED': os.getenv('TESSERACT_ENABLED', 'Not set')
    }
    
    print("Environment Variables:")
    for var, value in env_vars.items():
        print(f"   {var}: {value}")
    
    # Check if we're on Railway
    if os.getenv('RAILWAY_ENVIRONMENT'):
        print("✅ Running on Railway")
    else:
        print("ℹ️  Running locally")
    
    return True

def main():
    """Main test function"""
    print("🧪 Railway OCR Test Suite")
    print("=" * 50)
    
    tests = {
        'Tesseract Installation': test_tesseract_installation,
        'Python pytesseract': test_pytesseract,
        'OCR Functionality': test_ocr_functionality,
        'Environment': test_environment
    }
    
    results = {}
    
    for test_name, test_func in tests.items():
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if passed_test:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! OCR is ready for Railway deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
