from flask import Blueprint, request, jsonify, session
import re
from datetime import datetime
from db.connection import (
    get_db_connection,
    get_placeholder,
    execute_query,
    execute_update,
    execute_with_returning,
    get_db_integrity_error,
)

customers_api = Blueprint('customers_api', __name__, url_prefix='/api')

def get_current_user_id():
    user_id = session.get('user_id')
    if user_id is None:
        return 2
    return user_id

@customers_api.route('/customers', methods=['GET'])
def get_customers():
    try:
        user_id = get_current_user_id()
        phone = request.args.get('phone')
        search = request.args.get('search', '').strip()
        conn = get_db_connection()
        if phone:
            phone_digits = re.sub(r'\D', '', phone)
            placeholder = get_placeholder()
            cursor = execute_query(conn, f'SELECT * FROM customers WHERE user_id = {placeholder} AND phone = {placeholder} AND is_active = TRUE', (user_id, phone_digits))
            customers = cursor.fetchall()
        elif search:
            like_search_lower = f"%{search.lower()}%"
            placeholder = get_placeholder()
            cursor = execute_query(conn, f'SELECT * FROM customers WHERE user_id = {placeholder} AND (LOWER(name) LIKE {placeholder} OR phone LIKE {placeholder} OR LOWER(COALESCE(business_name, \'\')) LIKE {placeholder}) AND is_active = TRUE ORDER BY name', (user_id, like_search_lower, search, like_search_lower))
            customers = cursor.fetchall()
        else:
            placeholder = get_placeholder()
            cursor = execute_query(conn, f'SELECT * FROM customers WHERE user_id = {placeholder} AND is_active = TRUE ORDER BY name', (user_id,))
            customers = cursor.fetchall()
        conn.close()

        customers_list = []
        for customer in customers:
            customer_dict = {}
            for key, value in dict(customer).items():
                if isinstance(value, datetime):
                    customer_dict[key] = value.isoformat()
                elif hasattr(value, '__float__') and not isinstance(value, bool):
                    customer_dict[key] = float(value)
                else:
                    customer_dict[key] = value
            customers_list.append(customer_dict)

        return jsonify(customers_list)
    except Exception as e:
        print(f"Error in get_customers: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Database connection failed. Please check your database configuration.'}), 500

@customers_api.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'SELECT * FROM customers WHERE customer_id = {placeholder} AND user_id = {placeholder} AND is_active = TRUE', (customer_id, user_id))
    customer = cursor.fetchone()
    conn.close()
    if customer:
        return jsonify(dict(customer))
    else:
        return jsonify({'error': 'Customer not found'}), 404

@customers_api.route('/customers/recent', methods=['GET'])
def get_recent_customers():
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        placeholder = get_placeholder()
        query = f"""
            SELECT c.customer_id, c.name, c.phone, c.city, c.area, c.trn, 
                   c.customer_type, c.business_name, c.business_address, 
                   MAX(b.bill_date) as latest_bill_date, MAX(b.bill_id) as latest_bill_id
            FROM customers c
            INNER JOIN bills b ON c.customer_id = b.customer_id
            WHERE c.user_id = {placeholder} AND b.user_id = {placeholder} AND c.is_active = TRUE
            GROUP BY c.customer_id, c.name, c.phone, c.city, c.area, c.trn, 
                     c.customer_type, c.business_name, c.business_address
            ORDER BY latest_bill_date DESC, latest_bill_id DESC
            LIMIT 3
        """
        cursor = execute_query(conn, query, (user_id, user_id))
        recent_customers = cursor.fetchall()
        conn.close()
        customers_list = []
        for customer in recent_customers:
            customers_list.append({
                'customer_id': customer['customer_id'],
                'name': customer['name'],
                'phone': customer['phone'],
                'city': customer['city'],
                'area': customer['area'],
                'trn': customer['trn'],
                'customer_type': customer['customer_type'],
                'business_name': customer['business_name'],
                'business_address': customer['business_address']
            })
        return jsonify(customers_list)
    except Exception as e:
        print(f"Error getting recent customers: {e}")
        return jsonify({'error': str(e)}), 500

@customers_api.route('/customers', methods=['POST'])
def add_customer():
    data = request.get_json()
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    trn = data.get('trn', '').strip()
    city = data.get('city', '').strip()
    area = data.get('area', '').strip()
    email = data.get('email', '').strip()
    address = data.get('address', '').strip()
    customer_type = data.get('customer_type', 'Individual').strip()
    business_name = data.get('business_name', '').strip()
    business_address = data.get('business_address', '').strip()
    user_id = get_current_user_id()
    if not name:
        return jsonify({'error': 'Customer name is required'}), 400
    if not phone:
        return jsonify({'error': 'Customer mobile is required'}), 400
    phone_digits = re.sub(r'\D', '', phone)
    if len(phone_digits) < 9 or len(phone_digits) > 15:
        return jsonify({'error': 'Customer mobile must be 9-15 digits'}), 400
    if customer_type not in ['Individual', 'Business']:
        return jsonify({'error': 'Customer type must be Individual or Business'}), 400
    if customer_type == 'Business' and not business_name:
        return jsonify({'error': 'Business name is required for Business customers'}), 400
    conn = get_db_connection()
    if phone_digits:
        placeholder = get_placeholder()
        cursor = execute_query(conn,
            f"""
            SELECT name FROM customers 
            WHERE user_id = {placeholder} AND 
                  REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(phone, ' ', ''), '-', ''), '(', ''), ')', ''), '+', '') = {placeholder}
                  AND is_active = TRUE
            """,
            (user_id, phone_digits)
        )
        existing_customer = cursor.fetchone()
        if existing_customer:
            conn.close()
            return jsonify({'error': f'Phone number {phone} is already assigned to customer "{existing_customer["name"]}"'}), 400
    try:
        placeholder = get_placeholder()
        sql = f'''
            INSERT INTO customers (user_id, name, phone, trn, city, area, email, address, customer_type, business_name, business_address, is_active)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, TRUE)
            ON CONFLICT (user_id, phone) DO UPDATE SET
                name = EXCLUDED.name,
                trn = EXCLUDED.trn,
                city = EXCLUDED.city,
                area = EXCLUDED.area,
                email = EXCLUDED.email,
                address = EXCLUDED.address,
                customer_type = EXCLUDED.customer_type,
                business_name = EXCLUDED.business_name,
                business_address = EXCLUDED.business_address,
                is_active = TRUE
            RETURNING customer_id
        '''
        customer_id = execute_with_returning(conn, sql, (user_id, name, phone_digits, trn, city, area, email, address, customer_type, business_name, business_address))
        conn.close()
        return jsonify({'id': customer_id, 'message': 'Customer added successfully'})
    except get_db_integrity_error():
        conn.close()
        return jsonify({'error': 'Customer already exists'}), 400

@customers_api.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.get_json()
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    trn = data.get('trn', '').strip()
    city = data.get('city', '').strip()
    area = data.get('area', '').strip()
    email = data.get('email', '').strip()
    address = data.get('address', '').strip()
    customer_type = data.get('customer_type', 'Individual').strip()
    business_name = data.get('business_name', '').strip()
    business_address = data.get('business_address', '').strip()
    user_id = get_current_user_id()
    if not name:
        return jsonify({'error': 'Customer name is required'}), 400
    if customer_type not in ['Individual', 'Business']:
        return jsonify({'error': 'Customer type must be Individual or Business'}), 400
    if customer_type == 'Business' and not business_name:
        return jsonify({'error': 'Business name is required for Business customers'}), 400
    conn = get_db_connection()
    phone_digits = re.sub(r'\D', '', phone)
    if phone and (len(phone_digits) < 9 or len(phone_digits) > 15):
        conn.close()
        return jsonify({'error': 'Customer mobile must be 9-15 digits'}), 400
    if phone_digits:
        placeholder = get_placeholder()
        cursor = execute_query(conn,
            f"""
            SELECT name FROM customers 
            WHERE user_id = {placeholder} AND customer_id != {placeholder} AND 
                  REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(phone, ' ', ''), '-', ''), '(', ''), ')', ''), '+', '') = {placeholder}
            """,
            (user_id, customer_id, phone_digits)
        )
        existing_customer = cursor.fetchone()
        if existing_customer:
            conn.close()
            return jsonify({'error': f'Phone number {phone} is already assigned to customer "{existing_customer["name"]}"'}), 400
    placeholder = get_placeholder()
    sql = f'''
        UPDATE customers 
        SET name = {placeholder}, phone = {placeholder}, trn = {placeholder}, city = {placeholder}, area = {placeholder}, email = {placeholder}, address = {placeholder}, 
            customer_type = {placeholder}, business_name = {placeholder}, business_address = {placeholder}
        WHERE customer_id = {placeholder} AND user_id = {placeholder}
    '''
    execute_update(conn, sql, (name, phone_digits, trn, city, area, email, address, customer_type, business_name, business_address, customer_id, user_id))
    conn.close()
    return jsonify({'message': 'Customer updated successfully'})

@customers_api.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    is_active_value = 'FALSE'
    execute_update(conn, f'UPDATE customers SET is_active = {is_active_value} WHERE customer_id = {placeholder} AND user_id = {placeholder}', (customer_id, user_id))
    conn.close()
    return jsonify({'message': 'Customer deleted successfully'})
