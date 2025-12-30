from flask import Blueprint, request, jsonify, session
from db.connection import (
    get_db_connection,
    get_placeholder,
    execute_query,
    execute_update,
    execute_with_returning,
    get_db_integrity_error,
)

products_api = Blueprint('products_api', __name__, url_prefix='/api')

def get_current_user_id():
    user_id = session.get('user_id')
    if user_id is None:
        return 2
    return user_id

@products_api.route('/product-types', methods=['GET'])
def get_product_types():
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'SELECT * FROM product_types WHERE user_id = {placeholder} ORDER BY type_name', (user_id,))
    types = cursor.fetchall()
    conn.close()
    return jsonify([dict(type) for type in types])

@products_api.route('/products', methods=['GET'])
def get_products():
    user_id = get_current_user_id()
    search = request.args.get('search', '').strip()
    barcode = request.args.get('barcode', '').strip()
    conn = get_db_connection()
    if barcode:
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT p.*, pt.type_name 
            FROM products p 
            JOIN product_types pt ON p.type_id = pt.type_id 
            WHERE p.user_id = {placeholder} AND pt.user_id = {placeholder} AND p.is_active = TRUE AND p.barcode = {placeholder}
            ORDER BY pt.type_name, p.product_name
        ''', (user_id, user_id, barcode))
        products = cursor.fetchall()
    elif search:
        like_search = f"%{search}%"
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT p.*, pt.type_name 
            FROM products p 
            JOIN product_types pt ON p.type_id = pt.type_id 
            WHERE p.user_id = {placeholder} AND pt.user_id = {placeholder} AND p.is_active = TRUE AND (p.product_name LIKE {placeholder} OR pt.type_name LIKE {placeholder})
            ORDER BY pt.type_name, p.product_name
        ''', (user_id, user_id, like_search, like_search))
        products = cursor.fetchall()
    else:
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT p.*, pt.type_name 
            FROM products p 
            JOIN product_types pt ON p.type_id = pt.type_id 
            WHERE p.user_id = {placeholder} AND pt.user_id = {placeholder} AND p.is_active = TRUE 
            ORDER BY pt.type_name, p.product_name
        ''', (user_id, user_id))
        products = cursor.fetchall()
    conn.close()
    return jsonify([dict(product) for product in products])

@products_api.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'''
        SELECT p.*, pt.type_name 
        FROM products p 
        JOIN product_types pt ON p.type_id = pt.type_id 
        WHERE p.product_id = {placeholder} AND p.user_id = {placeholder} AND pt.user_id = {placeholder} AND p.is_active = TRUE
    ''', (product_id, user_id, user_id))
    product = cursor.fetchone()
    conn.close()
    if product:
        return jsonify(dict(product))
    else:
        return jsonify({'error': 'Product not found'}), 404

@products_api.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    type_id = data.get('type_id')
    name = data.get('name', '').strip()
    rate = data.get('rate')
    description = data.get('description', '').strip()
    barcode = (data.get('barcode') or '').strip()
    user_id = get_current_user_id()
    if not all([type_id, name, rate]):
        return jsonify({'error': 'Type, name, and rate are required'}), 400
    try:
        rate = float(rate)
        if rate <= 0:
            return jsonify({'error': 'Rate must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid rate value'}), 400
    conn = get_db_connection()
    try:
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT type_id FROM product_types WHERE type_id = {placeholder} AND user_id = {placeholder}', (type_id, user_id))
        type_check = cursor.fetchone()
        if not type_check:
            conn.close()
            return jsonify({'error': 'Invalid product type'}), 400
        placeholder = get_placeholder()
        sql = f'''
            INSERT INTO products (user_id, type_id, product_name, rate, description, barcode) 
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        '''
        product_id = execute_with_returning(conn, sql, (user_id, type_id, name, rate, description, barcode or None))
        conn.close()
        return jsonify({'id': product_id, 'message': 'Product added successfully'})
    except get_db_integrity_error():
        conn.close()
        return jsonify({'error': 'Product already exists'}), 400

@products_api.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    name = data.get('product_name', '').strip()
    rate = data.get('rate')
    type_id = data.get('type_id')
    description = data.get('description', '').strip()
    barcode = (data.get('barcode') or '').strip()
    user_id = get_current_user_id()
    if not all([name, rate, type_id]):
        return jsonify({'error': 'Name, rate, and type are required'}), 400
    try:
        rate = float(rate)
        if rate <= 0:
            return jsonify({'error': 'Rate must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid rate value'}), 400
    conn = get_db_connection()
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'SELECT product_id FROM products WHERE product_id = {placeholder} AND user_id = {placeholder}', (product_id, user_id))
    product_check = cursor.fetchone()
    cursor = execute_query(conn, f'SELECT type_id FROM product_types WHERE type_id = {placeholder} AND user_id = {placeholder}', (type_id, user_id))
    type_check = cursor.fetchone()
    if not product_check:
        conn.close()
        return jsonify({'error': 'Product not found'}), 404
    if not type_check:
        conn.close()
        return jsonify({'error': 'Invalid product type'}), 400
    placeholder = get_placeholder()
    execute_update(conn, f'''
        UPDATE products 
        SET product_name = {placeholder}, rate = {placeholder}, type_id = {placeholder}, description = {placeholder}, barcode = {placeholder} 
        WHERE product_id = {placeholder} AND user_id = {placeholder}
    ''', (name, rate, type_id, description, barcode or None, product_id, user_id))
    conn.close()
    return jsonify({'message': 'Product updated successfully'})

@products_api.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    is_active_value = 'FALSE'
    execute_update(conn, f'UPDATE products SET is_active = {is_active_value} WHERE product_id = {placeholder} AND user_id = {placeholder}', (product_id, user_id))
    conn.close()
    return jsonify({'message': 'Product deleted successfully'})

@products_api.route('/product-types', methods=['POST'])
def add_product_type():
    data = request.get_json()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip() if data.get('description') else None
    user_id = get_current_user_id()
    
    if not name:
        return jsonify({'error': 'Type name is required'}), 400
    
    conn = get_db_connection()
    try:
        placeholder = get_placeholder()
        sql = f'INSERT INTO product_types (user_id, type_name, description) VALUES ({placeholder}, {placeholder}, {placeholder})'
        type_id = execute_with_returning(conn, sql, (user_id, name, description))
        conn.close()
        return jsonify({'id': type_id, 'name': name, 'description': description, 'message': 'Product type added successfully'})
    except get_db_integrity_error():
        conn.close()
        return jsonify({'error': 'Product type already exists'}), 400

@products_api.route('/product-types/<int:type_id>', methods=['DELETE'])
def delete_product_type(type_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    # Check if active products exist for this type
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'SELECT COUNT(*) FROM products WHERE type_id = {placeholder} AND user_id = {placeholder} AND is_active = TRUE', (type_id, user_id))
    result = cursor.fetchone()
    
    # Handle both PostgreSQL (dict) and SQLite (tuple) results
    active_products = result[0] if isinstance(result, tuple) else result['count']
    
    if active_products > 0:
        conn.close()
        return jsonify({'error': 'Cannot delete type with existing active products'}), 400
    
    # Delete any soft-deleted (inactive) products associated with this type
    # This ensures we can hard-delete the type without foreign key constraint violations
    placeholder = get_placeholder()
    execute_update(conn, f'DELETE FROM products WHERE type_id = {placeholder} AND user_id = {placeholder} AND is_active = FALSE', (type_id, user_id))
    
    # Delete the product type
    placeholder = get_placeholder()
    execute_update(conn, f'DELETE FROM product_types WHERE type_id = {placeholder} AND user_id = {placeholder}', (type_id, user_id))
    conn.close()
    return jsonify({'message': 'Product type deleted successfully'})
