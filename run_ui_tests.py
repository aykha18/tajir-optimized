#!/usr/bin/env python3
"""
Simple UI Test Runner for Tajir POS
"""

import os
import sys
import subprocess
import time

def install_requirements():
    """Install UI testing requirements"""
    print("Installing UI testing requirements...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "tests/requirements_ui.txt"
        ], check=True)
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install requirements: {e}")
        return False
    return True

def check_chrome_driver():
    """Check if Chrome driver is available"""
    print("Checking Chrome driver...")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.quit()
        print("✓ Chrome driver is working")
        return True
    except Exception as e:
        print(f"✗ Chrome driver issue: {e}")
        print("Please install Chrome browser and ChromeDriver")
        return False

def run_ui_tests():
    """Run the UI test suite"""
    print("Running UI tests...")
    try:
        result = subprocess.run([
            sys.executable, "tests/ui_test_suite.py"
        ], capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"✗ Failed to run tests: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("TAJIR POS - UI TEST RUNNER")
    print("=" * 60)
    
    # Install requirements
    if not install_requirements():
        print("Failed to install requirements. Exiting.")
        return
    
    # Check Chrome driver
    if not check_chrome_driver():
        print("Chrome driver not available. Exiting.")
        return
    
    # Run tests
    print("\nStarting UI tests...")
    success = run_ui_tests()
    
    if success:
        print("\n✓ UI tests completed successfully!")
    else:
        print("\n✗ UI tests failed!")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
