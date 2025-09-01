#!/usr/bin/env python3
"""
Tajir POS - Comprehensive Regression Test Suite
Complete functionality testing from Add Product Type to Billing

This test suite covers all major features of the Tajir POS application
to ensure functionality is preserved and working correctly.
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

from app import app, get_db_connection, get_current_user_id

class TajirPOSRegressionTestCase(unittest.TestCase):
    """Base test case for Tajir POS regression testing"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Configure app for testing with PostgreSQL
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        # Create test client
        self.client = app.test_client()
        
        # Get demo user ID from database
        self.get_demo_user()
        
        # Login demo user
        self.login_demo_user()
    
    def tearDown(self):
        """Clean up after each test"""
        # No cleanup needed for PostgreSQL
        pass
    
    def get_demo_user(self):
        """Get demo user ID from database"""
        # Use the existing demo user with user_id = 2
        self.test_user_id = 2
    
    def login_demo_user(self):
        """Login demo user and get session"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_user_id

class ProductTypeTests(TajirPOSRegressionTestCase):
    """Test Product Type Management"""
    
    def test_01_get_product_types(self):
        """Test getting product types"""
        response = self.client.get('/api/product-types')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        # API returns list directly, not wrapped in 'product_types' key
        self.assertIsInstance(data, list)
        if len(data) > 0:
            self.assertIn('type_id', data[0])
            self.assertIn('type_name', data[0])
    
    def test_02_create_product_type(self):
        """Test creating a new product type"""
        product_type_data = {
            'name': 'Test Shirt',
            'description': 'Test shirt type'
        }
        response = self.client.post('/api/product-types', 
                                  data=json.dumps(product_type_data),
                                  content_type='application/json')
        
        # Check if creation was successful (either 201 or 200)
        self.assertIn(response.status_code, [200, 201])
        data = json.loads(response.data)
        # API returns: {'id': type_id, 'name': name, 'description': description, 'message': 'Product type added successfully'}
        self.assertEqual(data['name'], 'Test Shirt')
        self.assertIn('id', data)
    
    def test_03_delete_product_type(self):
        """Test deleting a product type"""
        # First create a product type
        product_type_data = {
            'name': 'Test Delete Type',
            'description': 'Type to be deleted'
        }
        create_response = self.client.post('/api/product-types', 
                                         data=json.dumps(product_type_data),
                                         content_type='application/json')
        
        # Get the type_id from response
        create_data = json.loads(create_response.data)
        type_id = create_data['id']
        
        # Then delete it
        response = self.client.delete(f'/api/product-types/{type_id}')
        self.assertEqual(response.status_code, 200)

class ProductTests(TajirPOSRegressionTestCase):
    """Test Product Management"""
    
    def test_04_get_products(self):
        """Test getting products"""
        response = self.client.get('/api/products')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('products', data)
    
    def test_05_create_product(self):
        """Test creating a new product"""
        product_data = {
            'product_name': 'Test Product',
            'product_type_id': 1,
            'rate': 100.00,
            'description': 'Test product description'
        }
        response = self.client.post('/api/products', 
                                  data=json.dumps(product_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('product', data)
        self.assertEqual(data['product']['product_name'], 'Test Product')
    
    def test_06_get_single_product(self):
        """Test getting a single product"""
        # First create a product
        product_data = {
            'product_name': 'Test Single Product',
            'product_type_id': 1,
            'rate': 150.00,
            'description': 'Test single product'
        }
        create_response = self.client.post('/api/products', 
                                         data=json.dumps(product_data),
                                         content_type='application/json')
        product_id = json.loads(create_response.data)['product']['product_id']
        
        # Then get it
        response = self.client.get(f'/api/products/{product_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('product', data)
        self.assertEqual(data['product']['product_name'], 'Test Single Product')
    
    def test_07_update_product(self):
        """Test updating a product"""
        # First create a product
        product_data = {
            'product_name': 'Test Update Product',
            'product_type_id': 1,
            'rate': 200.00,
            'description': 'Test update product'
        }
        create_response = self.client.post('/api/products', 
                                         data=json.dumps(product_data),
                                         content_type='application/json')
        product_id = json.loads(create_response.data)['product']['product_id']
        
        # Then update it
        update_data = {
            'product_name': 'Updated Product',
            'rate': 250.00
        }
        response = self.client.put(f'/api/products/{product_id}', 
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['product']['product_name'], 'Updated Product')
        self.assertEqual(data['product']['rate'], 250.00)
    
    def test_08_delete_product(self):
        """Test deleting a product"""
        # First create a product
        product_data = {
            'product_name': 'Test Delete Product',
            'product_type_id': 1,
            'rate': 300.00,
            'description': 'Product to be deleted'
        }
        create_response = self.client.post('/api/products', 
                                         data=json.dumps(product_data),
                                         content_type='application/json')
        product_id = json.loads(create_response.data)['product']['product_id']
        
        # Then delete it
        response = self.client.delete(f'/api/products/{product_id}')
        self.assertEqual(response.status_code, 200)

class CustomerTests(TajirPOSRegressionTestCase):
    """Test Customer Management"""
    
    def test_09_get_customers(self):
        """Test getting customers"""
        response = self.client.get('/api/customers')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('customers', data)
    
    def test_10_create_customer(self):
        """Test creating a new customer"""
        customer_data = {
            'name': 'Test Customer',
            'phone': '9876543210',
            'email': 'test@customer.com',
            'city': 'Test City',
            'area': 'Test Area'
        }
        response = self.client.post('/api/customers', 
                                  data=json.dumps(customer_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('customer', data)
        self.assertEqual(data['customer']['name'], 'Test Customer')
    
    def test_11_get_single_customer(self):
        """Test getting a single customer"""
        # First create a customer
        customer_data = {
            'name': 'Test Single Customer',
            'phone': '9876543211',
            'email': 'single@customer.com',
            'city': 'Test City',
            'area': 'Test Area'
        }
        create_response = self.client.post('/api/customers', 
                                         data=json.dumps(customer_data),
                                         content_type='application/json')
        customer_id = json.loads(create_response.data)['customer']['customer_id']
        
        # Then get it
        response = self.client.get(f'/api/customers/{customer_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('customer', data)
        self.assertEqual(data['customer']['name'], 'Test Single Customer')
    
    def test_12_update_customer(self):
        """Test updating a customer"""
        # First create a customer
        customer_data = {
            'name': 'Test Update Customer',
            'phone': '9876543212',
            'email': 'update@customer.com',
            'city': 'Test City',
            'area': 'Test Area'
        }
        create_response = self.client.post('/api/customers', 
                                         data=json.dumps(customer_data),
                                         content_type='application/json')
        customer_id = json.loads(create_response.data)['customer']['customer_id']
        
        # Then update it
        update_data = {
            'name': 'Updated Customer',
            'phone': '9876543213'
        }
        response = self.client.put(f'/api/customers/{customer_id}', 
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['customer']['name'], 'Updated Customer')
        self.assertEqual(data['customer']['phone'], '9876543213')
    
    def test_13_delete_customer(self):
        """Test deleting a customer"""
        # First create a customer
        customer_data = {
            'name': 'Test Delete Customer',
            'phone': '9876543214',
            'email': 'delete@customer.com',
            'city': 'Test City',
            'area': 'Test Area'
        }
        create_response = self.client.post('/api/customers', 
                                         data=json.dumps(customer_data),
                                         content_type='application/json')
        customer_id = json.loads(create_response.data)['customer']['customer_id']
        
        # Then delete it
        response = self.client.delete(f'/api/customers/{customer_id}')
        self.assertEqual(response.status_code, 200)

class EmployeeTests(TajirPOSRegressionTestCase):
    """Test Employee Management"""
    
    def test_14_get_employees(self):
        """Test getting employees"""
        response = self.client.get('/api/employees')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('employees', data)
    
    def test_15_create_employee(self):
        """Test creating a new employee"""
        employee_data = {
            'name': 'Test Employee',
            'phone': '9876543215',
            'email': 'test@employee.com',
            'role': 'Tailor'
        }
        response = self.client.post('/api/employees', 
                                  data=json.dumps(employee_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('employee', data)
        self.assertEqual(data['employee']['name'], 'Test Employee')
    
    def test_16_get_single_employee(self):
        """Test getting a single employee"""
        # First create an employee
        employee_data = {
            'name': 'Test Single Employee',
            'phone': '9876543216',
            'email': 'single@employee.com',
            'role': 'Tailor'
        }
        create_response = self.client.post('/api/employees', 
                                         data=json.dumps(employee_data),
                                         content_type='application/json')
        employee_id = json.loads(create_response.data)['employee']['employee_id']
        
        # Then get it
        response = self.client.get(f'/api/employees/{employee_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('employee', data)
        self.assertEqual(data['employee']['name'], 'Test Single Employee')
    
    def test_17_update_employee(self):
        """Test updating an employee"""
        # First create an employee
        employee_data = {
            'name': 'Test Update Employee',
            'phone': '9876543217',
            'email': 'update@employee.com',
            'role': 'Tailor'
        }
        create_response = self.client.post('/api/employees', 
                                         data=json.dumps(employee_data),
                                         content_type='application/json')
        employee_id = json.loads(create_response.data)['employee']['employee_id']
        
        # Then update it
        update_data = {
            'name': 'Updated Employee',
            'role': 'Senior Tailor'
        }
        response = self.client.put(f'/api/employees/{employee_id}', 
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['employee']['name'], 'Updated Employee')
        self.assertEqual(data['employee']['role'], 'Senior Tailor')
    
    def test_18_delete_employee(self):
        """Test deleting an employee"""
        # First create an employee
        employee_data = {
            'name': 'Test Delete Employee',
            'phone': '9876543218',
            'email': 'delete@employee.com',
            'role': 'Tailor'
        }
        create_response = self.client.post('/api/employees', 
                                         data=json.dumps(employee_data),
                                         content_type='application/json')
        employee_id = json.loads(create_response.data)['employee']['employee_id']
        
        # Then delete it
        response = self.client.delete(f'/api/employees/{employee_id}')
        self.assertEqual(response.status_code, 200)

class VATTests(TajirPOSRegressionTestCase):
    """Test VAT Management"""
    
    def test_19_get_vat_rates(self):
        """Test getting VAT rates"""
        response = self.client.get('/api/vat-rates')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('vat_rates', data)
    
    def test_20_create_vat_rate(self):
        """Test creating a new VAT rate"""
        vat_data = {
            'rate': 5.0,
            'description': 'Standard VAT'
        }
        response = self.client.post('/api/vat-rates', 
                                  data=json.dumps(vat_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('vat_rate', data)
        self.assertEqual(data['vat_rate']['rate'], 5.0)
    
    def test_21_delete_vat_rate(self):
        """Test deleting a VAT rate"""
        # First create a VAT rate
        vat_data = {
            'rate': 10.0,
            'description': 'VAT to be deleted'
        }
        create_response = self.client.post('/api/vat-rates', 
                                         data=json.dumps(vat_data),
                                         content_type='application/json')
        vat_id = json.loads(create_response.data)['vat_rate']['vat_id']
        
        # Then delete it
        response = self.client.delete(f'/api/vat-rates/{vat_id}')
        self.assertEqual(response.status_code, 200)

class BillingTests(TajirPOSRegressionTestCase):
    """Test Billing System"""
    
    def setUp(self):
        """Set up billing tests with required data"""
        super().setUp()
        self.setup_billing_data()
    
    def setup_billing_data(self):
        """Setup data required for billing tests"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if test data already exists
        cursor.execute('''
            SELECT type_id FROM product_types WHERE type_name = %s
        ''', ('Test Type',))
        existing_type = cursor.fetchone()
        
        if not existing_type:
            # Create product type
            cursor.execute('''
                INSERT INTO product_types (type_name, description)
                VALUES (%s, %s)
            ''', ('Test Type', 'Test product type'))
            
            # Create product
            cursor.execute('''
                INSERT INTO products (product_name, product_type_id, rate, description)
                VALUES (%s, %s, %s, %s)
            ''', ('Test Product', 1, 100.00, 'Test product'))
            
            # Create customer
            cursor.execute('''
                INSERT INTO customers (name, phone, email, city, area)
                VALUES (%s, %s, %s, %s, %s)
            ''', ('Test Customer', '9876543210', 'test@customer.com', 'Test City', 'Test Area'))
            
            # Create employee
            cursor.execute('''
                INSERT INTO employees (name, phone, email, role)
                VALUES (%s, %s, %s, %s)
            ''', ('Test Employee', '9876543211', 'test@employee.com', 'Tailor'))
            
            conn.commit()
        
        cursor.close()
        conn.close()
    
    def test_22_get_bills(self):
        """Test getting bills"""
        response = self.client.get('/api/bills')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('bills', data)
    
    def test_23_create_bill(self):
        """Test creating a new bill"""
        bill_data = {
            'customer_id': 1,
            'employee_id': 1,
            'bill_date': datetime.now().strftime('%Y-%m-%d'),
            'delivery_date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'trial_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'items': [
                {
                    'product_id': 1,
                    'quantity': 2,
                    'rate': 100.00,
                    'amount': 200.00
                }
            ],
            'subtotal': 200.00,
            'vat_amount': 10.00,
            'total_amount': 210.00,
            'advance_payment': 50.00,
            'remaining_amount': 160.00
        }
        response = self.client.post('/api/bills', 
                                  data=json.dumps(bill_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('bill', data)
        self.assertEqual(data['bill']['total_amount'], 210.00)
    
    def test_24_get_single_bill(self):
        """Test getting a single bill"""
        # First create a bill
        bill_data = {
            'customer_id': 1,
            'employee_id': 1,
            'bill_date': datetime.now().strftime('%Y-%m-%d'),
            'delivery_date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'trial_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'items': [
                {
                    'product_id': 1,
                    'quantity': 1,
                    'rate': 100.00,
                    'amount': 100.00
                }
            ],
            'subtotal': 100.00,
            'vat_amount': 5.00,
            'total_amount': 105.00,
            'advance_payment': 0.00,
            'remaining_amount': 105.00
        }
        create_response = self.client.post('/api/bills', 
                                         data=json.dumps(bill_data),
                                         content_type='application/json')
        bill_id = json.loads(create_response.data)['bill']['bill_id']
        
        # Then get it
        response = self.client.get(f'/api/bills/{bill_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('bill', data)
        self.assertEqual(data['bill']['total_amount'], 105.00)
    
    def test_25_delete_bill(self):
        """Test deleting a bill"""
        # First create a bill
        bill_data = {
            'customer_id': 1,
            'employee_id': 1,
            'bill_date': datetime.now().strftime('%Y-%m-%d'),
            'delivery_date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'trial_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'items': [
                {
                    'product_id': 1,
                    'quantity': 1,
                    'rate': 100.00,
                    'amount': 100.00
                }
            ],
            'subtotal': 100.00,
            'vat_amount': 5.00,
            'total_amount': 105.00,
            'advance_payment': 0.00,
            'remaining_amount': 105.00
        }
        create_response = self.client.post('/api/bills', 
                                         data=json.dumps(bill_data),
                                         content_type='application/json')
        bill_id = json.loads(create_response.data)['bill']['bill_id']
        
        # Then delete it
        response = self.client.delete(f'/api/bills/{bill_id}')
        self.assertEqual(response.status_code, 200)
    
    def test_26_update_bill_payment(self):
        """Test updating bill payment"""
        # First create a bill
        bill_data = {
            'customer_id': 1,
            'employee_id': 1,
            'bill_date': datetime.now().strftime('%Y-%m-%d'),
            'delivery_date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'trial_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'items': [
                {
                    'product_id': 1,
                    'quantity': 1,
                    'rate': 100.00,
                    'amount': 100.00
                }
            ],
            'subtotal': 100.00,
            'vat_amount': 5.00,
            'total_amount': 105.00,
            'advance_payment': 0.00,
            'remaining_amount': 105.00
        }
        create_response = self.client.post('/api/bills', 
                                         data=json.dumps(bill_data),
                                         content_type='application/json')
        bill_id = json.loads(create_response.data)['bill']['bill_id']
        
        # Then update payment
        payment_data = {
            'payment_amount': 50.00,
            'payment_date': datetime.now().strftime('%Y-%m-%d')
        }
        response = self.client.put(f'/api/bills/{bill_id}/payment', 
                                 data=json.dumps(payment_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['bill']['advance_payment'], 50.00)
        self.assertEqual(data['bill']['remaining_amount'], 55.00)

class DashboardTests(TajirPOSRegressionTestCase):
    """Test Dashboard Analytics"""
    
    def test_27_get_dashboard_data(self):
        """Test getting dashboard data"""
        response = self.client.get('/api/dashboard')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('dashboard', data)
        self.assertIn('total_bills', data['dashboard'])
        self.assertIn('total_customers', data['dashboard'])
        self.assertIn('total_products', data['dashboard'])
        self.assertIn('total_revenue', data['dashboard'])

class ReportsTests(TajirPOSRegressionTestCase):
    """Test Reports System"""
    
    def test_28_get_invoice_reports(self):
        """Test getting invoice reports"""
        response = self.client.get('/api/reports/invoices')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('reports', data)
    
    def test_29_get_employee_reports(self):
        """Test getting employee reports"""
        response = self.client.get('/api/reports/employees')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('reports', data)
    
    def test_30_get_product_reports(self):
        """Test getting product reports"""
        response = self.client.get('/api/reports/products')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('reports', data)

class ShopSettingsTests(TajirPOSRegressionTestCase):
    """Test Shop Settings"""
    
    def test_31_get_shop_settings(self):
        """Test getting shop settings"""
        response = self.client.get('/api/shop-settings')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('settings', data)
    
    def test_32_update_shop_settings(self):
        """Test updating shop settings"""
        settings_data = {
            'shop_name': 'Updated Test Shop',
            'address': 'Updated Test Address',
            'trn': '987654321'
        }
        response = self.client.put('/api/shop-settings', 
                                 data=json.dumps(settings_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['settings']['shop_name'], 'Updated Test Shop')

class LoyaltyTests(TajirPOSRegressionTestCase):
    """Test Loyalty Program"""
    
    def test_33_get_loyalty_config(self):
        """Test getting loyalty configuration"""
        response = self.client.get('/api/loyalty/config')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('config', data)
    
    def test_34_get_loyalty_tiers(self):
        """Test getting loyalty tiers"""
        response = self.client.get('/api/loyalty/tiers')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('tiers', data)
    
    def test_35_get_loyalty_customers(self):
        """Test getting loyalty customers"""
        response = self.client.get('/api/loyalty/customers')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('customers', data)
    
    def test_36_get_loyalty_rewards(self):
        """Test getting loyalty rewards"""
        response = self.client.get('/api/loyalty/rewards')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('rewards', data)
    
    def test_37_get_loyalty_analytics(self):
        """Test getting loyalty analytics"""
        response = self.client.get('/api/loyalty/analytics')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('analytics', data)

class ExpenseTests(TajirPOSRegressionTestCase):
    """Test Expense Management"""
    
    def setUp(self):
        """Set up expense tests with required data"""
        super().setUp()
        self.setup_expense_data()
    
    def setup_expense_data(self):
        """Setup data required for expense tests"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if test expense category already exists
        cursor.execute('''
            SELECT category_id FROM expense_categories WHERE category_name = %s AND user_id = %s
        ''', ('Test Expense Category', self.test_user_id))
        existing_category = cursor.fetchone()
        
        if not existing_category:
            # Create test expense category
            cursor.execute('''
                INSERT INTO expense_categories (category_name, description, user_id)
                VALUES (%s, %s, %s)
            ''', ('Test Expense Category', 'Test category for regression tests', self.test_user_id))
            conn.commit()
        
        cursor.close()
        conn.close()
    
    def test_38_get_expense_categories(self):
        """Test getting expense categories"""
        response = self.client.get('/api/expense-categories')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        # API returns list directly, not wrapped in 'categories' key
        self.assertIsInstance(data, list)
        if len(data) > 0:
            self.assertIn('category_id', data[0])
            self.assertIn('category_name', data[0])
    
    def test_39_create_expense_category(self):
        """Test creating expense category"""
        category_data = {
            'category_name': 'Test API Category',
            'description': 'Test expense category via API'
        }
        response = self.client.post('/api/expense-categories', 
                                  data=json.dumps(category_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('category', data)
        self.assertEqual(data['category']['category_name'], 'Test API Category')
        self.assertIn('category_id', data['category'])
    
    def test_40_update_expense_category(self):
        """Test updating expense category"""
        # First create a category
        category_data = {
            'category_name': 'Update Test Category',
            'description': 'Category to be updated'
        }
        create_response = self.client.post('/api/expense-categories', 
                                         data=json.dumps(category_data),
                                         content_type='application/json')
        category_id = json.loads(create_response.data)['category']['category_id']
        
        # Then update it
        update_data = {
            'category_name': 'Updated Category Name',
            'description': 'Updated description'
        }
        response = self.client.put(f'/api/expense-categories/{category_id}', 
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['category']['category_name'], 'Updated Category Name')
    
    def test_41_delete_expense_category(self):
        """Test deleting expense category"""
        # First create a category
        category_data = {
            'category_name': 'Delete Test Category',
            'description': 'Category to be deleted'
        }
        create_response = self.client.post('/api/expense-categories', 
                                         data=json.dumps(category_data),
                                         content_type='application/json')
        category_id = json.loads(create_response.data)['category']['category_id']
        
        # Then delete it
        response = self.client.delete(f'/api/expense-categories/{category_id}')
        self.assertEqual(response.status_code, 200)
    
    def test_42_get_expenses(self):
        """Test getting expenses"""
        response = self.client.get('/api/expenses')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('expenses', data)
        self.assertIsInstance(data['expenses'], list)
    
    def test_43_create_expense(self):
        """Test creating expense"""
        # Get a valid category_id first
        categories_response = self.client.get('/api/expense-categories')
        categories = json.loads(categories_response.data)['categories']
        self.assertGreater(len(categories), 0, "No expense categories available for testing")
        
        category_id = categories[0]['category_id']
        
        expense_data = {
            'category_id': category_id,
            'amount': 100.50,
            'description': 'Test expense for regression testing',
            'expense_date': datetime.now().strftime('%Y-%m-%d'),
            'payment_method': 'Cash'
        }
        response = self.client.post('/api/expenses', 
                                  data=json.dumps(expense_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('expense', data)
        self.assertEqual(data['expense']['amount'], 100.50)
        self.assertEqual(data['expense']['category_id'], category_id)
        self.assertEqual(data['expense']['payment_method'], 'Cash')
    
    def test_44_create_expense_validation(self):
        """Test expense creation validation"""
        # Test missing required fields
        invalid_expense_data = {
            'description': 'Test expense without required fields'
        }
        response = self.client.post('/api/expenses', 
                                  data=json.dumps(invalid_expense_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        # Test invalid amount
        invalid_amount_data = {
            'category_id': 1,
            'amount': -50.00,  # Negative amount
            'description': 'Test negative amount',
            'expense_date': datetime.now().strftime('%Y-%m-%d')
        }
        response = self.client.post('/api/expenses', 
                                  data=json.dumps(invalid_amount_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    def test_45_get_single_expense(self):
        """Test getting a single expense"""
        # First create an expense
        categories_response = self.client.get('/api/expense-categories')
        categories = json.loads(categories_response.data)['categories']
        category_id = categories[0]['category_id']
        
        expense_data = {
            'category_id': category_id,
            'amount': 75.25,
            'description': 'Test single expense',
            'expense_date': datetime.now().strftime('%Y-%m-%d'),
            'payment_method': 'Card'
        }
        create_response = self.client.post('/api/expenses', 
                                  data=json.dumps(expense_data),
                                  content_type='application/json')
        expense_id = json.loads(create_response.data)['expense']['expense_id']
        
        # Then get it
        response = self.client.get(f'/api/expenses/{expense_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('expense', data)
        self.assertEqual(data['expense']['amount'], 75.25)
        self.assertEqual(data['expense']['payment_method'], 'Card')
    
    def test_46_update_expense(self):
        """Test updating an expense"""
        # First create an expense
        categories_response = self.client.get('/api/expense-categories')
        categories = json.loads(categories_response.data)['categories']
        category_id = categories[0]['category_id']
        
        expense_data = {
            'category_id': category_id,
            'amount': 120.00,
            'description': 'Test update expense',
            'expense_date': datetime.now().strftime('%Y-%m-%d'),
            'payment_method': 'Cash'
        }
        create_response = self.client.post('/api/expenses', 
                                         data=json.dumps(expense_data),
                                         content_type='application/json')
        expense_id = json.loads(create_response.data)['expense']['expense_id']
        
        # Then update it
        update_data = {
            'amount': 150.75,
            'description': 'Updated expense description',
            'payment_method': 'Bank Transfer'
        }
        response = self.client.put(f'/api/expenses/{expense_id}', 
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['expense']['amount'], 150.75)
        self.assertEqual(data['expense']['description'], 'Updated expense description')
        self.assertEqual(data['expense']['payment_method'], 'Bank Transfer')
    
    def test_47_delete_expense(self):
        """Test deleting an expense"""
        # First create an expense
        categories_response = self.client.get('/api/expense-categories')
        categories = json.loads(categories_response.data)['categories']
        category_id = categories[0]['category_id']
        
        expense_data = {
            'category_id': category_id,
            'amount': 200.00,
            'description': 'Test delete expense',
            'expense_date': datetime.now().strftime('%Y-%m-%d'),
            'payment_method': 'Cash'
        }
        create_response = self.client.post('/api/expenses', 
                                         data=json.dumps(expense_data),
                                         content_type='application/json')
        expense_id = json.loads(create_response.data)['expense']['expense_id']
        
        # Then delete it
        response = self.client.delete(f'/api/expenses/{expense_id}')
        self.assertEqual(response.status_code, 200)
        
        # Verify it's deleted
        get_response = self.client.get(f'/api/expenses/{expense_id}')
        self.assertEqual(get_response.status_code, 404)
    
    def test_48_get_expenses_with_filters(self):
        """Test getting expenses with date and category filters"""
        # Test with date range filter
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        response = self.client.get(f'/api/expenses?start_date={start_date}&end_date={end_date}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('expenses', data)
        
        # Test with category filter
        categories_response = self.client.get('/api/expense-categories')
        categories = json.loads(categories_response.data)['categories']
        if len(categories) > 0:
            category_id = categories[0]['category_id']
            response = self.client.get(f'/api/expenses?category_id={category_id}')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('expenses', data)
    
    def test_49_get_expense_statistics(self):
        """Test getting expense statistics"""
        response = self.client.get('/api/expenses/statistics')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('total_expenses', data)
        self.assertIn('month_expenses', data)
        self.assertIn('categories_count', data)
        self.assertIn('avg_per_day', data)

class RecurringExpenseTests(TajirPOSRegressionTestCase):
    """Test Recurring Expense Management"""
    
    def setUp(self):
        """Set up recurring expense tests with required data"""
        super().setUp()
        self.setup_recurring_expense_data()
    
    def setup_recurring_expense_data(self):
        """Setup data required for recurring expense tests"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if test expense category already exists
        cursor.execute('''
            SELECT category_id FROM expense_categories WHERE category_name = %s AND user_id = %s
        ''', ('Recurring Test Category', self.test_user_id))
        existing_category = cursor.fetchone()
        
        if not existing_category:
            # Create test expense category for recurring expenses
            cursor.execute('''
                INSERT INTO expense_categories (category_name, description, user_id)
                VALUES (%s, %s, %s)
            ''', ('Recurring Test Category', 'Test category for recurring expense tests', self.test_user_id))
            conn.commit()
        
        cursor.close()
        conn.close()
    
    def test_50_get_recurring_expenses(self):
        """Test getting recurring expenses"""
        response = self.client.get('/api/recurring-expenses')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('recurring_expenses', data)
        self.assertIsInstance(data['recurring_expenses'], list)
    
    def test_51_create_recurring_expense(self):
        """Test creating recurring expense"""
        # Get a valid category_id first
        categories_response = self.client.get('/api/expense-categories')
        categories = json.loads(categories_response.data)['categories']
        self.assertGreater(len(categories), 0, "No expense categories available for testing")
        
        category_id = categories[0]['category_id']
        
        recurring_data = {
            'category_id': category_id,
            'title': 'Test Recurring Bill',
            'amount': 500.00,
            'description': 'Test recurring expense for regression testing',
            'frequency': 'monthly',
            'start_date': datetime.now().strftime('%Y-%m-%d'),
            'payment_method': 'Bank Transfer'
        }
        response = self.client.post('/api/recurring-expenses', 
                                  data=json.dumps(recurring_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('recurring_expense', data)
        self.assertEqual(data['recurring_expense']['amount'], 500.00)
        self.assertEqual(data['recurring_expense']['frequency'], 'monthly')
        self.assertEqual(data['recurring_expense']['title'], 'Test Recurring Bill')
    
    def test_52_create_recurring_expense_validation(self):
        """Test recurring expense creation validation"""
        # Test missing required fields
        invalid_data = {
            'description': 'Test recurring expense without required fields'
        }
        response = self.client.post('/api/recurring-expenses', 
                                  data=json.dumps(invalid_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        # Test invalid frequency
        categories_response = self.client.get('/api/expense-categories')
        categories = json.loads(categories_response.data)['categories']
        category_id = categories[0]['category_id']
        
        invalid_frequency_data = {
            'category_id': category_id,
            'title': 'Test Invalid Frequency',
            'amount': 100.00,
            'frequency': 'invalid_frequency',  # Invalid frequency
            'start_date': datetime.now().strftime('%Y-%m-%d')
        }
        response = self.client.post('/api/recurring-expenses', 
                                  data=json.dumps(invalid_frequency_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    def test_53_get_single_recurring_expense(self):
        """Test getting a single recurring expense"""
        # First create a recurring expense
        categories_response = self.client.get('/api/expense-categories')
        categories = json.loads(categories_response.data)['categories']
        category_id = categories[0]['category_id']
        
        recurring_data = {
            'category_id': category_id,
            'title': 'Test Single Recurring Bill',
            'amount': 300.00,
            'description': 'Test single recurring expense',
            'frequency': 'weekly',
            'start_date': datetime.now().strftime('%Y-%m-%d'),
            'payment_method': 'Cash'
        }
        create_response = self.client.post('/api/recurring-expenses', 
                                         data=json.dumps(recurring_data),
                                         content_type='application/json')
        recurring_id = json.loads(create_response.data)['recurring_expense']['recurring_id']
        
        # Then get it
        response = self.client.get(f'/api/recurring-expenses/{recurring_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('recurring_expense', data)
        self.assertEqual(data['recurring_expense']['amount'], 300.00)
        self.assertEqual(data['recurring_expense']['frequency'], 'weekly')
    
    def test_54_update_recurring_expense(self):
        """Test updating a recurring expense"""
        # First create a recurring expense
        categories_response = self.client.get('/api/expense-categories')
        categories = json.loads(categories_response.data)['categories']
        category_id = categories[0]['category_id']
        
        recurring_data = {
            'category_id': category_id,
            'title': 'Test Update Recurring Bill',
            'amount': 250.00,
            'description': 'Test update recurring expense',
            'frequency': 'monthly',
            'start_date': datetime.now().strftime('%Y-%m-%d'),
            'payment_method': 'Card'
        }
        create_response = self.client.post('/api/recurring-expenses', 
                                         data=json.dumps(recurring_data),
                                         content_type='application/json')
        recurring_id = json.loads(create_response.data)['recurring_expense']['recurring_id']
        
        # Then update it
        update_data = {
            'title': 'Updated Recurring Bill',
            'amount': 350.00,
            'description': 'Updated recurring expense description',
            'frequency': 'yearly'
        }
        response = self.client.put(f'/api/recurring-expenses/{recurring_id}', 
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['recurring_expense']['title'], 'Updated Recurring Bill')
        self.assertEqual(data['recurring_expense']['amount'], 350.00)
        self.assertEqual(data['recurring_expense']['frequency'], 'yearly')
    
    def test_55_delete_recurring_expense(self):
        """Test deleting a recurring expense"""
        # First create a recurring expense
        categories_response = self.client.get('/api/expense-categories')
        categories = json.loads(categories_response.data)['categories']
        category_id = categories[0]['category_id']
        
        recurring_data = {
            'category_id': category_id,
            'title': 'Test Delete Recurring Bill',
            'amount': 400.00,
            'description': 'Test delete recurring expense',
            'frequency': 'daily',
            'start_date': datetime.now().strftime('%Y-%m-%d'),
            'payment_method': 'Other'
        }
        create_response = self.client.post('/api/recurring-expenses', 
                                         data=json.dumps(recurring_data),
                                         content_type='application/json')
        recurring_id = json.loads(create_response.data)['recurring_expense']['recurring_id']
        
        # Then delete it
        response = self.client.delete(f'/api/recurring-expenses/{recurring_id}')
        self.assertEqual(response.status_code, 200)
        
        # Verify it's deleted
        get_response = self.client.get(f'/api/recurring-expenses/{recurring_id}')
        self.assertEqual(get_response.status_code, 404)
    
    def test_56_generate_recurring_expenses(self):
        """Test generating recurring expenses"""
        # First create a recurring expense that should generate bills
        categories_response = self.client.get('/api/expense-categories')
        categories = json.loads(categories_response.data)['categories']
        category_id = categories[0]['category_id']
        
        # Set start date to past to ensure it's due for generation
        past_date = (datetime.now() - timedelta(days=35)).strftime('%Y-%m-%d')
        
        recurring_data = {
            'category_id': category_id,
            'title': 'Test Generate Recurring Bill',
            'amount': 150.00,
            'description': 'Test generate recurring expense',
            'frequency': 'monthly',
            'start_date': past_date,
            'payment_method': 'Bank Transfer'
        }
        create_response = self.client.post('/api/recurring-expenses', 
                                         data=json.dumps(recurring_data),
                                         content_type='application/json')
        
        # Test the generation endpoint
        response = self.client.post('/api/recurring-expenses/generate')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('generated_count', data)
        self.assertIsInstance(data['generated_count'], int)

class UtilityTests(TajirPOSRegressionTestCase):
    """Test Utility Functions"""
    
    def test_57_get_cities(self):
        """Test getting cities"""
        response = self.client.get('/api/cities')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('cities', data)
    
    def test_58_get_areas(self):
        """Test getting areas"""
        response = self.client.get('/api/areas')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('areas', data)
    
    def test_59_get_next_bill_number(self):
        """Test getting next bill number"""
        response = self.client.get('/api/next-bill-number')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('next_bill_number', data)

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        ProductTypeTests,
        ProductTests,
        CustomerTests,
        EmployeeTests,
        VATTests,
        BillingTests,
        DashboardTests,
        ReportsTests,
        ShopSettingsTests,
        LoyaltyTests,
        ExpenseTests,
        RecurringExpenseTests,
        UtilityTests
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"REGRESSION TEST SUMMARY")
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
