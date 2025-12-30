from flask import Blueprint, jsonify, request, session, render_template
from db.connection import get_db_connection, get_placeholder, execute_update, execute_with_returning, get_db_integrity_error, execute_query
from api.utils import get_current_user_id
from api.plans import get_user_plan_info
from api.i18n import get_user_language, translate_text as get_translated_text
import logging
import os
import bcrypt
import random
import string
import re
from datetime import datetime, timedelta

setup_api = Blueprint('setup_api', __name__)
logger = logging.getLogger(__name__)

@setup_api.route('/setup-wizard')
def setup_wizard():
    """Serve the setup wizard page."""
    user_plan_info = get_user_plan_info()
    return render_template('setup_wizard.html', 
                        user_plan_info=user_plan_info,
                        get_user_language=get_user_language,
                        get_translated_text=get_translated_text)

@setup_api.route('/api/setup-wizard', methods=['POST'])
def handle_setup_wizard():
    """Handle setup wizard data submission."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['shopType', 'shopName', 'shopOwner', 'contactNumber', 'selectedPlan']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'})
        
        # Calculate expiry date based on plan
        if data['selectedPlan'] == 'trial':
            expiry_date = datetime.now() + timedelta(days=15)
            plan_type = 'trial'
        elif data['selectedPlan'] == 'basic':
            expiry_date = datetime.now() + timedelta(days=365)
            plan_type = 'basic'
        elif data['selectedPlan'] == 'pro':
            expiry_date = datetime.now() + timedelta(days=365)
            plan_type = 'pro'
        else:
            return jsonify({'success': False, 'message': 'Invalid plan selected'})
        
        conn = get_db_connection()
        
        # Generate unique shop code (retry to avoid rare collisions)
        def generate_shop_code():
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Prepare inputs
        contact_number_raw = (data.get('contactNumber') or '').strip()
        contact_number_digits = re.sub(r'\D', '', contact_number_raw)
        if not contact_number_digits:
            conn.close()
            return jsonify({'success': False, 'message': 'Contact number must contain digits'}), 400
        
        default_password = os.getenv('DEFAULT_PASSWORD', 'demo123')  # Default password from environment
        password_hash = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt())
        
        # Normalize email: if empty, use fallback
        provided_email = (data.get('emailAddress') or '').strip()
        # Shop code may be needed for fallback email; generate with collision check
        attempts = 0
        while True:
            attempts += 1
            shop_code = generate_shop_code()
            # Check uniqueness of shop_code
            placeholder = get_placeholder()
            cursor = execute_query(conn, f'SELECT 1 FROM users WHERE shop_code = {placeholder}', (shop_code,))
            existing = cursor.fetchone()
            if not existing:
                break
            if attempts > 5:
                conn.close()
                return jsonify({'success': False, 'message': 'Failed to generate unique shop code. Please try again.'}), 500
        
        user_email = provided_email if provided_email else f"shop_{shop_code}@tailorpos.com"
        
        # Insert new user
        try:
            placeholder = get_placeholder()
            new_user_id = execute_with_returning(conn, f'''
                INSERT INTO users (email, mobile, shop_code, password_hash, shop_name, shop_type, contact_number, email_address)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                RETURNING user_id
            ''', (
                user_email,
                contact_number_digits,
                shop_code,
                password_hash.decode('utf-8'),
                data['shopName'],
                data['shopType'],
                contact_number_digits,
                user_email
            ))
        except get_db_integrity_error() as ie:
            # Determine which unique constraint failed
            message = str(ie)
            friendly = 'Setup failed due to duplicate data.'
            if 'users.email' in message:
                friendly = 'This email is already registered. Please use a different email.'
            elif 'users.mobile' in message:
                friendly = 'This contact number is already registered. Please use a different number.'
            elif 'users.shop_code' in message:
                friendly = 'Generated shop code collided. Please try again.'
            conn.close()
            return jsonify({'success': False, 'message': friendly}), 400
        
        # Create shop settings for new user with TRN, address, dynamic template, currency, and timezone
        placeholder = get_placeholder()
        sql = f'''
            INSERT INTO shop_settings (user_id, shop_name, shop_mobile, trn, address, invoice_static_info, use_dynamic_invoice_template, currency_code, currency_symbol, timezone, date_format, time_format)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        '''
        execute_with_returning(conn, sql, (
            new_user_id, 
            data['shopName'], 
            contact_number_digits, 
            data.get('trn', ''),
            data.get('address', ''),
            f"Shop Type: {data['shopType']}",
            True,  # Enable dynamic invoice template by default
            'AED',  # Default currency
            'د.إ',  # Default currency symbol
            'Asia/Dubai',  # Default timezone
            'DD/MM/YYYY',  # Default date format
            '24h'  # Default time format
        ))
        
        # Create shop owner as employee with "Owner" position
        placeholder = get_placeholder()
        sql = f'''
            INSERT INTO employees (user_id, name, phone, address, position, is_active)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        '''
        execute_with_returning(conn, sql, (
            new_user_id,
            data['shopOwner'],
            contact_number_digits,
            data.get('address', ''),
            'Owner',
            True
        ))
        
        # Create user plan for new user
        placeholder = get_placeholder()
        sql = f'''
            INSERT INTO user_plans (user_id, plan_type, plan_start_date, plan_end_date)
            VALUES ({placeholder}, {placeholder}, CURRENT_DATE, {placeholder})
        '''
        execute_with_returning(conn, sql, (new_user_id, plan_type, expiry_date.strftime('%Y-%m-%d')))
        
        # Create default VAT rate (5% from 2018-01-01)
        placeholder = get_placeholder()
        sql = f'''
            INSERT INTO vat_rates (user_id, rate_percentage, effective_from, effective_to, is_active)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        '''
        execute_with_returning(conn, sql, (new_user_id, 5.00, '2018-01-01', '2099-12-31', True))
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': 'Setup completed successfully',
            'plan_type': plan_type,
            'expiry_date': expiry_date.strftime('%Y-%m-%d'),
            'shop_code': shop_code,
            'password': default_password,
            'emailAddress': user_email
        })
        
    except Exception as e:
        logger.error(f"Setup wizard error: {e}")
        try:
            conn.close()
        except:
            pass
        return jsonify({'success': False, 'message': f'Setup failed: {str(e)}'})

@setup_api.route('/api/setup/default-products', methods=['GET'])
def get_default_products():
    """Get default product types and products for laundry shop setup"""
    try:
        default_data = {
            'product_types': [
                {'type_name': 'Wash & Iron', 'description': 'Standard wash and iron service'},
                {'type_name': 'Dry Clean', 'description': 'Professional dry cleaning service'},
                {'type_name': 'Press Only', 'description': 'Ironing and pressing service'},
                {'type_name': 'Starch', 'description': 'Starch and iron service'},
                {'type_name': 'Express', 'description': 'Same day service'},
                {'type_name': 'Bulk', 'description': 'Large quantity orders'}
            ],
            'products': [
                # Wash & Iron Products
                {'product_name': 'Shirt Wash & Iron', 'product_type': 'Wash & Iron', 'rate': 8.00, 'description': 'Standard shirt wash and iron'},
                {'product_name': 'Pants Wash & Iron', 'product_type': 'Wash & Iron', 'rate': 10.00, 'description': 'Trousers wash and iron'},
                {'product_name': 'T-Shirt Wash & Iron', 'product_type': 'Wash & Iron', 'rate': 6.00, 'description': 'T-shirt wash and iron'},
                {'product_name': 'Dress Wash & Iron', 'product_type': 'Wash & Iron', 'rate': 12.00, 'description': 'Dress wash and iron'},
                {'product_name': 'Suit Wash & Iron', 'product_type': 'Wash & Iron', 'rate': 25.00, 'description': 'Complete suit wash and iron'},
                
                # Dry Clean Products
                {'product_name': 'Shirt Dry Clean', 'product_type': 'Dry Clean', 'rate': 15.00, 'description': 'Professional shirt dry cleaning'},
                {'product_name': 'Pants Dry Clean', 'product_type': 'Dry Clean', 'rate': 18.00, 'description': 'Trousers dry cleaning'},
                {'product_name': 'Suit Dry Clean', 'product_type': 'Dry Clean', 'rate': 35.00, 'description': 'Complete suit dry cleaning'},
                {'product_name': 'Coat Dry Clean', 'product_type': 'Dry Clean', 'rate': 30.00, 'description': 'Coat dry cleaning'},
                {'product_name': 'Dress Dry Clean', 'product_type': 'Dry Clean', 'rate': 20.00, 'description': 'Dress dry cleaning'},
                
                # Press Only Products
                {'product_name': 'Shirt Press Only', 'product_type': 'Press Only', 'rate': 5.00, 'description': 'Shirt ironing only'},
                {'product_name': 'Pants Press Only', 'product_type': 'Press Only', 'rate': 6.00, 'description': 'Trousers ironing only'},
                {'product_name': 'Dress Press Only', 'product_type': 'Press Only', 'rate': 8.00, 'description': 'Dress ironing only'},
                
                # Starch Products
                {'product_name': 'Shirt with Starch', 'product_type': 'Starch', 'rate': 10.00, 'description': 'Shirt with starch finish'},
                {'product_name': 'Pants with Starch', 'product_type': 'Starch', 'rate': 12.00, 'description': 'Trousers with starch finish'},
                
                # Express Products
                {'product_name': 'Express Shirt', 'product_type': 'Express', 'rate': 12.00, 'description': 'Same day shirt service'},
                {'product_name': 'Express Pants', 'product_type': 'Express', 'rate': 15.00, 'description': 'Same day pants service'},
                {'product_name': 'Express Suit', 'product_type': 'Express', 'rate': 40.00, 'description': 'Same day suit service'},
                
                # Bulk Products
                {'product_name': 'Bulk Shirts (10+)', 'product_type': 'Bulk', 'rate': 6.00, 'description': 'Bulk shirt discount'},
                {'product_name': 'Bulk Pants (10+)', 'product_type': 'Bulk', 'rate': 8.00, 'description': 'Bulk pants discount'},
                {'product_name': 'Bulk Mixed (20+)', 'product_type': 'Bulk', 'rate': 7.00, 'description': 'Mixed bulk discount'}
            ]
        }
        
        return jsonify({
            'success': True,
            'data': default_data
        })
    except Exception as e:
        logger.error(f"Error in get_default_products: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@setup_api.route('/api/setup/populate-products', methods=['POST'])
def populate_default_products():
    """Populate default products and product types for laundry shop"""
    conn = None
    try:
        user_id = get_current_user_id()
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        # Get default data
        resp = get_default_products()
        # Handle the response tuple if it exists
        if isinstance(resp, tuple):
            resp = resp[0]
            
        default_data = resp.get_json()['data']
        
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        # Insert product types first
        product_type_ids = {}
        for pt in default_data['product_types']:
            type_id = execute_with_returning(conn, f'''
                INSERT INTO product_types (type_name, description, user_id) 
                VALUES ({placeholder}, {placeholder}, {placeholder})
            ''', (pt['type_name'], pt['description'], user_id))
            
            product_type_ids[pt['type_name']] = type_id
        
        # Insert products
        for product in default_data['products']:
            execute_update(conn, f'''
                INSERT INTO products (product_name, product_type_id, rate, description, user_id) 
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            ''', (
                product['product_name'], 
                product_type_ids[product['product_type']], 
                product['rate'], 
                product['description'], 
                user_id
            ))
        
        return jsonify({
            'success': True,
            'message': f'Successfully populated {len(default_data["product_types"])} product types and {len(default_data["products"])} products'
        })
        
    except Exception as e:
        logger.error(f"Error in populate_default_products: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()
