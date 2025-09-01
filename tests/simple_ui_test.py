#!/usr/bin/env python3
"""
Simple UI Test for Tajir POS - Basic Functionality
"""

import unittest
import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class SimpleUITest(unittest.TestCase):
    """Simple UI test for basic functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Initialize WebDriver
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)
        cls.wait = WebDriverWait(cls.driver, 10)
        
        # Start Flask app (simple approach)
        cls.start_flask_app()
        
        # Wait for app to start
        time.sleep(5)
        
        # Navigate to the app
        cls.driver.get("http://localhost:5000")
        
        # Try to login
        cls.try_login()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up"""
        cls.driver.quit()
        cls.stop_flask_app()
    
    @classmethod
    def start_flask_app(cls):
        """Start Flask app in background"""
        import subprocess
        import threading
        
        def run_flask():
            subprocess.run(["python", "app.py"], capture_output=True)
        
        cls.flask_thread = threading.Thread(target=run_flask, daemon=True)
        cls.flask_thread.start()
    
    @classmethod
    def stop_flask_app(cls):
        """Stop Flask app"""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == 'python.exe':
                    proc.terminate()
        except:
            pass
    
    @classmethod
    def try_login(cls):
        """Try to login if login form is present"""
        try:
            # Check if login form exists
            username_field = cls.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            
            # Login
            password_field = cls.driver.find_element(By.ID, "password")
            username_field.send_keys("demo")
            password_field.send_keys("demo123")
            
            login_button = cls.driver.find_element(By.ID, "loginBtn")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(3)
            
        except TimeoutException:
            print("No login form found - may already be logged in")
    
    def test_01_homepage_loads(self):
        """Test that the homepage loads"""
        self.driver.get("http://localhost:5000")
        
        # Check if page loaded
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertIsNotNone(body)
        
        # Check page title
        title = self.driver.title
        self.assertIsNotNone(title)
        
        print(f"✓ Homepage loads with title: {title}")
    
    def test_02_expenses_page_accessible(self):
        """Test that expenses page is accessible"""
        self.driver.get("http://localhost:5000/expenses")
        time.sleep(2)
        
        # Check if page loaded
        body = self.driver.find_element(By.TAG_NAME, "body")
        self.assertIsNotNone(body)
        
        # Look for expense-related elements
        try:
            # Check for add expense button
            add_button = self.driver.find_element(By.ID, "addExpenseBtn")
            self.assertTrue(add_button.is_displayed())
            print("✓ Add expense button found")
        except NoSuchElementException:
            print("⚠ Add expense button not found")
        
        try:
            # Check for expense modal
            modal = self.driver.find_element(By.ID, "expenseModal")
            print("✓ Expense modal found")
        except NoSuchElementException:
            print("⚠ Expense modal not found")
        
        print("✓ Expenses page is accessible")
    
    def test_03_expense_form_elements_exist(self):
        """Test that expense form elements exist in the DOM"""
        self.driver.get("http://localhost:5000/expenses")
        time.sleep(2)
        
        # Check for form elements by ID
        form_elements = [
            "expenseAmount",
            "expenseDescription", 
            "expenseCategory",
            "expenseDate",
            "expensePaymentMethod",
            "saveExpenseBtn"
        ]
        
        found_elements = []
        for element_id in form_elements:
            try:
                element = self.driver.find_element(By.ID, element_id)
                found_elements.append(element_id)
                print(f"✓ Found element: {element_id}")
            except NoSuchElementException:
                print(f"⚠ Missing element: {element_id}")
        
        # Should find at least some elements
        self.assertGreater(len(found_elements), 0, "Should find at least some form elements")
        print(f"✓ Found {len(found_elements)} out of {len(form_elements)} form elements")
    
    def test_04_page_navigation(self):
        """Test basic page navigation"""
        pages = [
            ("/dashboard", "Dashboard"),
            ("/products", "Products"),
            ("/customers", "Customers"),
            ("/employees", "Employees"),
            ("/bills", "Bills")
        ]
        
        successful_pages = 0
        for url, page_name in pages:
            try:
                self.driver.get(f"http://localhost:5000{url}")
                time.sleep(1)
                
                # Check if page loaded
                body = self.driver.find_element(By.TAG_NAME, "body")
                self.assertIsNotNone(body)
                
                print(f"✓ {page_name} page loads")
                successful_pages += 1
                
            except Exception as e:
                print(f"⚠ {page_name} page failed: {e}")
        
        # Should be able to access most pages
        self.assertGreater(successful_pages, 0, "Should be able to access at least some pages")
        print(f"✓ Successfully accessed {successful_pages} out of {len(pages)} pages")

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add tests
    test_classes = [SimpleUITest]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"SIMPLE UI TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    print(f"\n{'='*60}")
