#!/usr/bin/env python3
"""
Tajir POS - Comprehensive Test Suite
Pre-PostgreSQL Migration Testing

This test suite covers all major features of the Tajir POS application
to ensure functionality is preserved during the PostgreSQL migration.
"""

import unittest
import json
import sqlite3
import tempfile
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import requests
from io import BytesIO

# Add the parent directory to the path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, get_db_connection, setup_database, get_current_user_id

class TajirPOSTestCase(unittest.TestCase):
    """Base test case for Tajir POS application"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Create a temporary database for testing
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # Configure app for testing
        app.config['TESTING'] = True
        app.config['DATABASE'] = self.db_path
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        # Create test client
        self.client = app.test_client()
        
        # Setup test database
        self.setup_test_database()
        
        # Create test user
        self.create_test_user()
        
        # Login test user
        self.login_test_user()
    
    def tearDown(self):
        """Clean up after each test"""
        # Close and remove temporary database
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def setup_test_database(self):
        """Setup test database with schema"""
        conn = sqlite3.connect(self.db_path)
        
        # Read and execute schema
        with open('database_schema.sql', 'r') as f:
            schema = f.read()
            conn.executescript(schema)
        
        conn.close()
    
    def create_test_user(self):
        """Create a test user for testing"""
        conn = sqlite3.connect(self.db_path)
        
        # Create test user
        conn.execute('''
            INSERT INTO users (email, mobile, shop_code, password_hash, shop_name, shop_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('test@tajir.com', '1234567890', 'TEST001', 'hashed_password', 'Test Shop', 'tailor'))
        
        user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        
        # Create user plan
        conn.execute('''
            INSERT INTO user_plans (user_id, plan_type, plan_start_date, plan_end_date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, 'pro', datetime.now().date(), None))
        
        # Create shop settings
        conn.execute('''
            INSERT INTO shop_settings (user_id, shop_name, address, trn)
            VALUES (?, ?, ?, ?)
        ''', (user_id, 'Test Shop', 'Test Address', '123456789'))
        
        conn.commit()
        conn.close()
        
        self.test_user_id = user_id
    
    def login_test_user(self):
        """Login test user and get session"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_user_id
            sess['email'] = 'test@tajir.com'
            sess['shop_name'] = 'Test Shop'

class AuthenticationTests(TajirPOSTestCase):
    """Test authentication and user management features"""
    
    def test_user_login(self):
        """Test user login functionality"""
        response = self.client.post('/api/auth/login', json={
            'email': 'test@tajir.com',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 200)
    
    def test_plan_status(self):
        """Test plan status API"""
        response = self.client.get('/api/plan/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('plan_type', data)
    
    def test_feature_access(self):
        """Test feature access control"""
        response = self.client.get('/api/plan/check-feature/dashboard')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('enabled', data)

class ProductManagementTests(TajirPOSTestCase):
    """Test product management features"""
    
    def setUp(self):
        super().setUp()
        self.create_test_product_type()
    
    def create_test_product_type(self):
        """Create test product type"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO product_types (user_id, type_name, description)
            VALUES (?, ?, ?)
        ''', (self.test_user_id, 'Test Type', 'Test Description'))
        self.product_type_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.commit()
        conn.close()
    
    def test_get_product_types(self):
        """Test getting product types"""
        response = self.client.get('/api/product-types')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_create_product_type(self):
        """Test creating product type"""
        response = self.client.post('/api/product-types', json={
            'name': 'New Type',
            'description': 'New Description'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('id', data)
    
    def test_create_product(self):
        """Test creating product"""
        response = self.client.post('/api/products', json={
            'type_id': self.product_type_id,
            'name': 'Test Product',
            'rate': 100.00,
            'description': 'Test Product Description'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('id', data)
    
    def test_get_products(self):
        """Test getting products"""
        response = self.client.get('/api/products')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

class CustomerManagementTests(TajirPOSTestCase):
    """Test customer management features"""
    
    def test_create_customer(self):
        """Test creating customer"""
        response = self.client.post('/api/customers', json={
            'name': 'Test Customer',
            'phone': '9876543210',
            'city': 'Dubai',
            'area': 'Downtown',
            'email': 'customer@test.com',
            'address': 'Test Address'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('id', data)
    
    def test_get_customers(self):
        """Test getting customers"""
        response = self.client.get('/api/customers')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_get_recent_customers(self):
        """Test getting recent customers"""
        response = self.client.get('/api/customers/recent')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

class BillingSystemTests(TajirPOSTestCase):
    """Test billing system features"""
    
    def setUp(self):
        super().setUp()
        self.create_test_customer()
        self.create_test_product()
    
    def create_test_customer(self):
        """Create test customer"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO customers (user_id, name, phone, city, area, email)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.test_user_id, 'Test Customer', '9876543210', 'Dubai', 'Downtown', 'customer@test.com'))
        self.customer_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.commit()
        conn.close()
    
    def create_test_product(self):
        """Create test product"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO products (user_id, type_id, product_name, rate, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.test_user_id, 1, 'Test Product', 100.00, 'Test Description'))
        self.product_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.commit()
        conn.close()
    
    def test_create_bill(self):
        """Test creating bill"""
        response = self.client.post('/api/bills', json={
            'customer_id': self.customer_id,
            'customer_name': 'Test Customer',
            'customer_phone': '9876543210',
            'customer_city': 'Dubai',
            'customer_area': 'Downtown',
            'bill_date': datetime.now().strftime('%Y-%m-%d'),
            'delivery_date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'payment_method': 'advance',
            'items': [{
                'product_id': self.product_id,
                'product_name': 'Test Product',
                'quantity': 1,
                'rate': 100.00,
                'discount': 0,
                'advance_paid': 50.00,
                'total_amount': 100.00
            }],
            'subtotal': 100.00,
            'vat_amount': 5.00,
            'total_amount': 105.00,
            'advance_paid': 50.00,
            'balance_amount': 55.00,
            'status': 'pending',
            'master_id': 1,
            'trial_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'notes': 'Test bill'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('bill_id', data)
    
    def test_get_bills(self):
        """Test getting bills"""
        response = self.client.get('/api/bills')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_get_next_bill_number(self):
        """Test getting next bill number"""
        response = self.client.get('/api/next-bill-number')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('next_number', data)

class AnalyticsTests(TajirPOSTestCase):
    """Test analytics and reporting features"""
    
    def test_dashboard_analytics(self):
        """Test dashboard analytics"""
        response = self.client.get('/api/dashboard')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('revenue', data)
        self.assertIn('bills', data)
        self.assertIn('customers', data)
    
    def test_financial_overview(self):
        """Test financial overview analytics"""
        response = self.client.get('/api/analytics/financial-overview?from_date=2025-01-01&to_date=2025-12-31')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('revenue', data)
        self.assertIn('expenses', data)
        self.assertIn('profitability', data)
    
    def test_expense_breakdown(self):
        """Test expense breakdown analytics"""
        response = self.client.get('/api/analytics/expense-breakdown?from_date=2025-01-01&to_date=2025-12-31')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('category_breakdown', data)

class ReportsTests(TajirPOSTestCase):
    """Test reporting features"""
    
    def test_invoice_reports(self):
        """Test invoice reports"""
        response = self.client.get('/api/reports/invoices?from_date=2025-01-01&to_date=2025-12-31')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('invoices', data)
    
    def test_employee_reports(self):
        """Test employee reports"""
        response = self.client.get('/api/reports/employees?from_date=2025-01-01&to_date=2025-12-31')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('employees', data)
    
    def test_product_reports(self):
        """Test product reports"""
        response = self.client.get('/api/reports/products?from_date=2025-01-01&to_date=2025-12-31')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('products', data)

class ConfigurationTests(TajirPOSTestCase):
    """Test configuration and settings features"""
    
    def test_get_shop_settings(self):
        """Test getting shop settings"""
        response = self.client.get('/api/shop-settings')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('shop_name', data)
    
    def test_update_shop_settings(self):
        """Test updating shop settings"""
        response = self.client.put('/api/shop-settings', json={
            'shop_name': 'Updated Shop Name',
            'address': 'Updated Address',
            'trn': '123456789'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
    
    def test_get_vat_rates(self):
        """Test getting VAT rates"""
        response = self.client.get('/api/vat-rates')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

class EmployeeManagementTests(TajirPOSTestCase):
    """Test employee management features"""
    
    def test_create_employee(self):
        """Test creating employee"""
        response = self.client.post('/api/employees', json={
            'name': 'Test Employee',
            'mobile': '1234567890',
            'address': 'Employee Address'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('id', data)
    
    def test_get_employees(self):
        """Test getting employees"""
        response = self.client.get('/api/employees')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

class ExpenseManagementTests(TajirPOSTestCase):
    """Test expense management features"""
    
    def test_create_expense(self):
        """Test creating expense"""
        response = self.client.post('/api/expenses', json={
            'category': 'Test Category',
            'amount': 100.00,
            'description': 'Test Expense',
            'date': datetime.now().strftime('%Y-%m-%d')
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('id', data)
    
    def test_get_expenses(self):
        """Test getting expenses"""
        response = self.client.get('/api/expenses')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

class IntegrationTests(TajirPOSTestCase):
    """Test integration between different modules"""
    
    def test_complete_billing_workflow(self):
        """Test complete billing workflow from customer to bill"""
        # 1. Create customer
        customer_response = self.client.post('/api/customers', json={
            'name': 'Integration Customer',
            'phone': '1111111111',
            'city': 'Dubai',
            'area': 'Downtown'
        })
        self.assertEqual(customer_response.status_code, 200)
        customer_data = json.loads(customer_response.data)
        customer_id = customer_data['id']
        
        # 2. Create product
        product_response = self.client.post('/api/products', json={
            'type_id': 1,
            'name': 'Integration Product',
            'rate': 200.00
        })
        self.assertEqual(product_response.status_code, 200)
        product_data = json.loads(product_response.data)
        product_id = product_data['id']
        
        # 3. Create bill
        bill_response = self.client.post('/api/bills', json={
            'customer_id': customer_id,
            'customer_name': 'Integration Customer',
            'customer_phone': '1111111111',
            'customer_city': 'Dubai',
            'customer_area': 'Downtown',
            'bill_date': datetime.now().strftime('%Y-%m-%d'),
            'delivery_date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'payment_method': 'advance',
            'items': [{
                'product_id': product_id,
                'product_name': 'Integration Product',
                'quantity': 2,
                'rate': 200.00,
                'discount': 0,
                'advance_paid': 200.00,
                'total_amount': 400.00
            }],
            'subtotal': 400.00,
            'vat_amount': 20.00,
            'total_amount': 420.00,
            'advance_paid': 200.00,
            'balance_amount': 220.00,
            'status': 'pending'
        })
        self.assertEqual(bill_response.status_code, 200)
        bill_data = json.loads(bill_response.data)
        bill_id = bill_data['bill_id']
        
        # 4. Verify bill exists
        bills_response = self.client.get('/api/bills')
        self.assertEqual(bills_response.status_code, 200)
        bills_data = json.loads(bills_response.data)
        self.assertTrue(any(bill['bill_id'] == bill_id for bill in bills_data))
        
        # 5. Check dashboard reflects new data
        dashboard_response = self.client.get('/api/dashboard')
        self.assertEqual(dashboard_response.status_code, 200)
        dashboard_data = json.loads(dashboard_response.data)
        self.assertGreater(dashboard_data['revenue']['total_revenue'], 0)

class PerformanceTests(TajirPOSTestCase):
    """Test performance characteristics"""
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        # Create multiple test records
        conn = sqlite3.connect(self.db_path)
        
        # Create 100 test customers
        for i in range(100):
            conn.execute('''
                INSERT INTO customers (user_id, name, phone, city, area)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.test_user_id, f'Customer {i}', f'123456789{i:02d}', 'Dubai', 'Downtown'))
        
        conn.commit()
        conn.close()
        
        # Test getting customers (should handle large dataset)
        start_time = datetime.now()
        response = self.client.get('/api/customers')
        end_time = datetime.now()
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 100)
        
        # Performance check (should complete within 1 second)
        duration = (end_time - start_time).total_seconds()
        self.assertLess(duration, 1.0)

class SecurityTests(TajirPOSTestCase):
    """Test security features"""
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        # Test with malicious input
        response = self.client.post('/api/customers', json={
            'name': "'; DROP TABLE customers; --",
            'phone': '1234567890',
            'city': 'Dubai',
            'area': 'Downtown'
        })
        
        # Should handle gracefully (either reject or escape)
        self.assertNotEqual(response.status_code, 500)
    
    def test_xss_prevention(self):
        """Test XSS prevention"""
        # Test with script injection
        response = self.client.post('/api/customers', json={
            'name': '<script>alert("xss")</script>',
            'phone': '1234567890',
            'city': 'Dubai',
            'area': 'Downtown'
        })
        
        # Should handle gracefully
        self.assertNotEqual(response.status_code, 500)
    
    def test_unauthorized_access(self):
        """Test unauthorized access prevention"""
        # Test without login
        with self.client.session_transaction() as sess:
            sess.clear()
        
        response = self.client.get('/api/customers')
        self.assertIn(response.status_code, [401, 302])  # Should redirect or return unauthorized

class DatabaseTests(TajirPOSTestCase):
    """Test database operations and integrity"""
    
    def test_database_connection(self):
        """Test database connection"""
        conn = get_db_connection()
        self.assertIsNotNone(conn)
        
        # Test basic query
        cursor = conn.execute('SELECT 1')
        result = cursor.fetchone()
        self.assertEqual(result[0], 1)
        
        conn.close()
    
    def test_foreign_key_integrity(self):
        """Test foreign key integrity"""
        # Try to create bill with non-existent customer
        response = self.client.post('/api/bills', json={
            'customer_id': 99999,  # Non-existent customer
            'customer_name': 'Test Customer',
            'customer_phone': '1234567890',
            'customer_city': 'Dubai',
            'customer_area': 'Downtown',
            'bill_date': datetime.now().strftime('%Y-%m-%d'),
            'delivery_date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'payment_method': 'advance',
            'items': [],
            'subtotal': 0,
            'vat_amount': 0,
            'total_amount': 0,
            'advance_paid': 0,
            'balance_amount': 0,
            'status': 'pending'
        })
        
        # Should handle gracefully (either reject or handle error)
        self.assertNotEqual(response.status_code, 500)

def run_test_suite():
    """Run the complete test suite"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        AuthenticationTests,
        ProductManagementTests,
        CustomerManagementTests,
        BillingSystemTests,
        AnalyticsTests,
        ReportsTests,
        ConfigurationTests,
        EmployeeManagementTests,
        ExpenseManagementTests,
        IntegrationTests,
        PerformanceTests,
        SecurityTests,
        DatabaseTests
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"TEST SUITE SUMMARY")
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
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_test_suite()
    sys.exit(0 if success else 1)
