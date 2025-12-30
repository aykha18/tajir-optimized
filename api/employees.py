from flask import Blueprint, request, jsonify, session
from db.connection import (
    get_db_connection,
    get_placeholder,
    execute_query,
    execute_with_returning,
    execute_update,
)

employees_api = Blueprint('employees_api', __name__, url_prefix='/api')

def get_current_user_id():
    user_id = session.get('user_id')
    if user_id is None:
        return 2
    return user_id

@employees_api.route('/employees', methods=['GET'])
def get_employees():
    user_id = get_current_user_id()
    search = request.args.get('search', '').strip()
    conn = get_db_connection()
    placeholder = get_placeholder()
    if search:
        like_search = f"%{search}%"
        cursor = execute_query(conn, f'SELECT * FROM employees WHERE user_id = {placeholder} AND (name LIKE {placeholder} OR phone LIKE {placeholder} OR address LIKE {placeholder}) AND is_active = TRUE ORDER BY name', (user_id, like_search, like_search, like_search))
        employees = cursor.fetchall()
    else:
        cursor = execute_query(conn, f'SELECT * FROM employees WHERE user_id = {placeholder} AND is_active = TRUE ORDER BY name', (user_id,))
        employees = cursor.fetchall()
    conn.close()
    return jsonify([dict(emp) for emp in employees])

@employees_api.route('/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'SELECT * FROM employees WHERE employee_id = {placeholder} AND user_id = {placeholder} AND is_active = TRUE', (employee_id, user_id))
    employee = cursor.fetchone()
    conn.close()
    if employee:
        return jsonify(dict(employee))
    else:
        return jsonify({'error': 'Employee not found'}), 404

@employees_api.route('/employees', methods=['POST'])
def add_employee():
    from api.utils import log_dml_error
    data = request.get_json()
    name = data.get('name', '').strip()
    mobile = data.get('mobile', '').strip()
    address = data.get('address', '').strip()
    position = (data.get('position') or data.get('role') or '').strip()
    user_id = get_current_user_id()
    if not name:
        return jsonify({'error': 'Employee name is required'}), 400
    conn = get_db_connection()
    if mobile:
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT name FROM employees WHERE phone = {placeholder} AND user_id = {placeholder} AND is_active = TRUE', (mobile, user_id))
        existing_employee = cursor.fetchone()
        if existing_employee:
            conn.close()
            return jsonify({'error': f'Mobile number {mobile} is already assigned to employee "{existing_employee["name"]}"'}), 400
    placeholder = get_placeholder()
    try:
        sql = f'INSERT INTO employees (user_id, name, phone, address, position) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})'
        emp_id = execute_with_returning(conn, sql, (user_id, name, mobile, address, position))
    except Exception as e:
        if 'no such column' in str(e).lower() and 'position' in str(e).lower():
            sql = f'INSERT INTO employees (user_id, name, phone, address) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})'
            emp_id = execute_with_returning(conn, sql, (user_id, name, mobile, address))
        else:
            log_dml_error('INSERT', 'employees', e, user_id=user_id, data=data)
            conn.close()
            return jsonify({'error': 'Failed to add employee'}), 500
    conn.close()
    return jsonify({'id': emp_id, 'message': 'Employee added successfully'})

@employees_api.route('/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    from api.utils import log_dml_error
    data = request.get_json()
    name = data.get('name', '').strip()
    mobile = data.get('mobile', '').strip()
    address = data.get('address', '').strip()
    position = (data.get('position') or data.get('role') or '').strip()
    user_id = get_current_user_id()
    if not name:
        return jsonify({'error': 'Employee name is required'}), 400
    conn = get_db_connection()
    if mobile:
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT name FROM employees WHERE phone = {placeholder} AND user_id = {placeholder} AND employee_id != {placeholder} AND is_active = TRUE', (mobile, user_id, employee_id))
        existing_employee = cursor.fetchone()
        if existing_employee:
            conn.close()
            return jsonify({'error': f'Mobile number {mobile} is already assigned to employee "{existing_employee["name"]}"'}), 400
    try:
        placeholder = get_placeholder()
        sql = f'UPDATE employees SET name = {placeholder}, phone = {placeholder}, address = {placeholder}, position = {placeholder} WHERE employee_id = {placeholder} AND user_id = {placeholder}'
        execute_update(conn, sql, (name, mobile, address, position, employee_id, user_id))
    except Exception as e:
        if 'no such column' in str(e).lower() and 'position' in str(e).lower():
            conn.rollback()
            placeholder = get_placeholder()
            sql = f'UPDATE employees SET name = {placeholder}, phone = {placeholder}, address = {placeholder} WHERE employee_id = {placeholder} AND user_id = {placeholder}'
            execute_update(conn, sql, (name, mobile, address, employee_id, user_id))
        else:
            conn.rollback()
            log_dml_error('UPDATE', 'employees', e, user_id=user_id, data=data)
            conn.close()
            return jsonify({'error': 'Failed to update employee'}), 500
    conn.close()
    return jsonify({'message': 'Employee updated successfully'})

@employees_api.route('/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    is_active_value = 'FALSE'
    execute_update(conn, f'UPDATE employees SET is_active = {is_active_value} WHERE employee_id = {placeholder} AND user_id = {placeholder}', (employee_id, user_id))
    conn.close()
    return jsonify({'message': 'Employee deleted successfully'})
