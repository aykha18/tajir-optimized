from flask import Blueprint, request, jsonify, session, Response, render_template
from db.connection import (
    get_db_connection,
    get_placeholder,
    execute_query,
    execute_update,
    execute_with_returning,
    get_db_integrity_error,
    is_postgresql
)
from datetime import datetime, timedelta
import csv
from io import StringIO
from api.utils import log_user_action, log_dml_error
from api.plans import get_user_plan_info
from api.i18n import get_user_language, get_translated_text

expenses_api = Blueprint('expenses_api', __name__)

def get_current_user_id():
    """Get the current user's ID from session."""
    return session.get('user_id')

# Expense Categories API
@expenses_api.route('/api/expense-categories', methods=['GET'])
def get_expense_categories():
    """Get all expense categories for current user."""
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'''
        SELECT * FROM expense_categories 
        WHERE user_id = {placeholder} AND is_active = TRUE 
        ORDER BY category_name
    ''', (user_id,))
    categories = cursor.fetchall()
    conn.close()
    return jsonify([dict(category) for category in categories])

@expenses_api.route('/api/expense-categories', methods=['POST'])
def add_expense_category():
    """Add new expense category."""
    data = request.get_json()
    name = data.get('category_name', '').strip()
    description = data.get('description', '').strip()
    user_id = get_current_user_id()
    
    if not name:
        return jsonify({'error': 'Category name is required'}), 400
    
    conn = get_db_connection()
    try:
        placeholder = get_placeholder()
        sql = f'''
            INSERT INTO expense_categories (user_id, category_name, description) 
            VALUES ({placeholder}, {placeholder}, {placeholder})
        '''
        category_id = execute_with_returning(conn, sql, (user_id, name, description))
        conn.close()
        
        log_user_action('expense_category_added', user_id, {'category_name': name})
        return jsonify({'id': category_id, 'message': 'Category added successfully'})
    except get_db_integrity_error():
        conn.close()
        return jsonify({'error': 'Category already exists'}), 400
    except Exception as e:
        conn.close()
        log_dml_error('INSERT', 'expense_categories', e, user_id, data)
        return jsonify({'error': 'Failed to add category'}), 500

@expenses_api.route('/api/expense-categories/<int:category_id>', methods=['PUT'])
def update_expense_category(category_id):
    """Update expense category."""
    data = request.get_json()
    name = data.get('category_name', '').strip()
    description = data.get('description', '').strip()
    user_id = get_current_user_id()
    
    if not name:
        return jsonify({'error': 'Category name is required'}), 400
    
    conn = get_db_connection()
    try:
        # Check if category exists and belongs to user
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT category_id FROM expense_categories 
            WHERE category_id = {placeholder} AND user_id = {placeholder}
        ''', (category_id, user_id))
        category = cursor.fetchone()
        
        if not category:
            conn.close()
            return jsonify({'error': 'Category not found'}), 404
        
        placeholder = get_placeholder()
        sql = f'''
            UPDATE expense_categories 
            SET category_name = {placeholder}, description = {placeholder} 
            WHERE category_id = {placeholder} AND user_id = {placeholder}
        '''
        execute_update(conn, sql, (name, description, category_id, user_id))
        conn.close()
        
        log_user_action('expense_category_updated', user_id, {'category_id': category_id, 'category_name': name})
        return jsonify({'message': 'Category updated successfully'})
    except get_db_integrity_error():
        conn.close()
        return jsonify({'error': 'Category name already exists'}), 400
    except Exception as e:
        conn.close()
        log_dml_error('UPDATE', 'expense_categories', e, user_id, data)
        return jsonify({'error': 'Failed to update category'}), 500

@expenses_api.route('/api/expense-categories/<int:category_id>', methods=['DELETE'])
def delete_expense_category(category_id):
    """Delete expense category (soft delete)."""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    try:
        # Check if category has expenses
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT COUNT(*) FROM expenses 
            WHERE category_id = {placeholder} AND user_id = {placeholder}
        ''', (category_id, user_id))
        result = cursor.fetchone()
        # Handle both PostgreSQL (dict) and SQLite (tuple) results
        expense_count = result[0] if isinstance(result, tuple) else result['count']
        
        if expense_count > 0:
            conn.close()
            return jsonify({'error': 'Cannot delete category with existing expenses'}), 400
        
        # Soft delete by setting is_active = 0
        placeholder = get_placeholder()
        # Use TRUE/FALSE for PostgreSQL, 1/0 for SQLite
        is_active_value = 'FALSE' if is_postgresql() else '0'
        sql = f'''
            UPDATE expense_categories 
            SET is_active = {is_active_value} 
            WHERE category_id = {placeholder} AND user_id = {placeholder}
        '''
        execute_update(conn, sql, (category_id, user_id))
        conn.close()
        
        log_user_action('expense_category_deleted', user_id, {'category_id': category_id})
        return jsonify({'message': 'Category deleted successfully'})
    except Exception as e:
        conn.close()
        log_dml_error('DELETE', 'expense_categories', e, user_id, {'category_id': category_id})
        return jsonify({'error': 'Failed to delete category'}), 500

# Expenses API
@expenses_api.route('/api/expenses', methods=['GET'])
def get_expenses():
    """Get expenses with optional filtering."""
    user_id = get_current_user_id()
    
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category_id = request.args.get('category_id')
    search = request.args.get('search', '').strip()
    
    conn = get_db_connection()
    
    # Build query with filters
    placeholder = get_placeholder()
    query = f'''
        SELECT e.*, ec.category_name 
        FROM expenses e 
        JOIN expense_categories ec ON e.category_id = ec.category_id 
        WHERE e.user_id = {placeholder} AND ec.user_id = {placeholder}
    '''
    params = [user_id, user_id]
    
    if start_date:
        query += f' AND e.expense_date >= {placeholder}'
        params.append(start_date)
    
    if end_date:
        query += f' AND e.expense_date <= {placeholder}'
        params.append(end_date)
    
    if category_id:
        query += f' AND e.category_id = {placeholder}'
        params.append(category_id)
    
    if search:
        query += f' AND (e.description LIKE {placeholder} OR ec.category_name LIKE {placeholder})'
        search_param = f'%{search}%'
        params.extend([search_param, search_param])
    
    query += ' ORDER BY e.expense_date DESC, e.created_at DESC'
    
    cursor = execute_query(conn, query, params)

    try:
        expenses = cursor.fetchall()
        conn.close()
        
        # Filter out any expenses with invalid dates
        valid_expenses = []
        for expense in expenses:
            try:
                # Convert to dict and validate date
                expense_dict = dict(expense)
                if 'expense_date' in expense_dict and expense_dict['expense_date']:
                    # Try to parse the date to ensure it's valid
                    datetime.strptime(str(expense_dict['expense_date']), '%Y-%m-%d')
                valid_expenses.append(expense_dict)
            except (ValueError, TypeError) as e:
                print(f"Skipping expense with invalid date: {e}")
                continue
        
        return jsonify(valid_expenses)
    except Exception as e:
        conn.close()
        print(f"Error fetching expenses: {e}")
        return jsonify([])

@expenses_api.route('/api/expenses', methods=['POST'])
def add_expense():
    """Add new expense."""
    data = request.get_json()
    category_id = data.get('category_id')
    expense_date = data.get('expense_date')
    amount = data.get('amount')
    description = data.get('description', '').strip()
    payment_method = data.get('payment_method', 'Cash')
    receipt_url = data.get('receipt_url', '').strip()
    user_id = get_current_user_id()
    
    # Validation
    if not all([category_id, expense_date, amount]):
        return jsonify({'error': 'Category, date, and amount are required'}), 400
    
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid amount value'}), 400
    
    conn = get_db_connection()
    try:
        # Verify category belongs to user
        placeholder = get_placeholder()
        category = execute_query(conn, f'''
            SELECT category_id FROM expense_categories 
            WHERE category_id = {placeholder} AND user_id = {placeholder} AND is_active = TRUE
        ''', (category_id, user_id)).fetchone()
        
        if not category:
            conn.close()
            return jsonify({'error': 'Invalid category'}), 400
        
        placeholder = get_placeholder()
        sql = f'''
            INSERT INTO expenses (user_id, category_id, expense_date, amount, description, payment_method, receipt_url) 
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        '''
        expense_id = execute_with_returning(conn, sql, (user_id, category_id, expense_date, amount, description, payment_method, receipt_url))
        conn.close()
        
        return jsonify({'id': expense_id, 'message': 'Expense added successfully'})
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Failed to add expense'}), 500

# Recurring Expenses API
@expenses_api.route('/api/recurring-expenses', methods=['GET'])
def get_recurring_expenses():
    """Get recurring expenses for the current user."""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    placeholder = get_placeholder()
    query = f'''
        SELECT re.*, ec.category_name 
        FROM recurring_expenses re 
        JOIN expense_categories ec ON re.category_id = ec.category_id 
        WHERE re.user_id = {placeholder} AND ec.user_id = {placeholder} AND re.is_active = TRUE
        ORDER BY re.created_at DESC
    '''
    
    cursor = execute_query(conn, query, (user_id, user_id))
    recurring_expenses = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(expense) for expense in recurring_expenses])

@expenses_api.route('/api/recurring-expenses', methods=['POST'])
def add_recurring_expense():
    """Add new recurring expense."""
    data = request.get_json()
    title = data.get('title')
    amount = data.get('amount')
    description = data.get('description', '').strip()
    category_id = data.get('category_id')
    frequency = data.get('frequency')
    payment_method = data.get('payment_method', 'Cash')
    start_date = data.get('start_date')
    user_id = get_current_user_id()
    
    # Validation
    if not all([title, amount, category_id, frequency, start_date]):
        return jsonify({'error': 'Title, amount, category, frequency, and start date are required'}), 400
    
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid amount value'}), 400
    
    conn = get_db_connection()
    try:
        # Verify category belongs to user
        placeholder = get_placeholder()
        category = execute_query(conn, f'''
            SELECT category_id FROM expense_categories 
            WHERE category_id = {placeholder} AND user_id = {placeholder} AND is_active = TRUE
        ''', (category_id, user_id)).fetchone()
        
        if not category:
            conn.close()
            return jsonify({'error': 'Invalid category'}), 400
        
        # Calculate next_due_date based on start_date and frequency
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        if frequency == 'daily':
            next_due_date = start_date_obj + timedelta(days=1)
        elif frequency == 'weekly':
            next_due_date = start_date_obj + timedelta(weeks=1)
        elif frequency == 'monthly':
            # Add one month (approximate)
            if start_date_obj.month == 12:
                next_due_date = start_date_obj.replace(year=start_date_obj.year + 1, month=1)
            else:
                next_due_date = start_date_obj.replace(month=start_date_obj.month + 1)
        elif frequency == 'yearly':
            next_due_date = start_date_obj.replace(year=start_date_obj.year + 1)
        else:
            next_due_date = start_date_obj + timedelta(days=1)  # Default to daily
        
        placeholder = get_placeholder()
        sql = f'''
            INSERT INTO recurring_expenses (user_id, title, amount, description, category_id, frequency, payment_method, start_date, next_due_date) 
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        '''
        recurring_id = execute_with_returning(conn, sql, (user_id, title, amount, description, category_id, frequency, payment_method, start_date, next_due_date))
        conn.close()
        
        return jsonify({'id': recurring_id, 'message': 'Recurring expense added successfully'})
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Failed to add recurring expense'}), 500

@expenses_api.route('/api/expenses/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    """Get specific expense."""
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    expense = execute_query(conn, f'''
        SELECT e.*, ec.category_name 
        FROM expenses e 
        JOIN expense_categories ec ON e.category_id = ec.category_id 
        WHERE e.expense_id = {placeholder} AND e.user_id = {placeholder} AND ec.user_id = {placeholder}
    ''', (expense_id, user_id, user_id)).fetchone()
    conn.close()
    
    if expense:
        return jsonify(dict(expense))
    else:
        return jsonify({'error': 'Expense not found'}), 404

@expenses_api.route('/api/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """Update expense."""
    data = request.get_json()
    category_id = data.get('category_id')
    expense_date = data.get('expense_date')
    amount = data.get('amount')
    description = data.get('description', '').strip()
    payment_method = data.get('payment_method', 'Cash')
    receipt_url = data.get('receipt_url', '').strip()
    user_id = get_current_user_id()
    
    # Validation
    if not all([category_id, expense_date, amount]):
        return jsonify({'error': 'Category, date, and amount are required'}), 400
    
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid amount value'}), 400
    
    conn = get_db_connection()
    try:
        # Verify expense and category belong to user
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT expense_id FROM expenses 
            WHERE expense_id = {placeholder} AND user_id = {placeholder}
        ''', (expense_id, user_id))
        expense = cursor.fetchone()
        
        cursor = execute_query(conn, f'''
            SELECT category_id FROM expense_categories 
            WHERE category_id = {placeholder} AND user_id = {placeholder} AND is_active = TRUE
        ''', (category_id, user_id))
        category = cursor.fetchone()
        
        if not expense:
            conn.close()
            return jsonify({'error': 'Expense not found'}), 404
        
        if not category:
            conn.close()
            return jsonify({'error': 'Invalid category'}), 400
        
        placeholder = get_placeholder()
        sql = f'''
            UPDATE expenses 
            SET category_id = {placeholder}, expense_date = {placeholder}, amount = {placeholder}, description = {placeholder}, payment_method = {placeholder}, receipt_url = {placeholder} 
            WHERE expense_id = {placeholder} AND user_id = {placeholder}
        '''
        execute_update(conn, sql, (category_id, expense_date, amount, description, payment_method, receipt_url, expense_id, user_id))
        conn.close()
        
        log_user_action('expense_updated', user_id, {'expense_id': expense_id, 'amount': amount, 'category_id': category_id})
        return jsonify({'message': 'Expense updated successfully'})
    except Exception as e:
        conn.close()
        log_dml_error('UPDATE', 'expenses', e, user_id, data)
        return jsonify({'error': 'Failed to update expense'}), 500

@expenses_api.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """Delete expense."""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    try:
        # Get expense details for logging
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT amount, category_id FROM expenses 
            WHERE expense_id = {placeholder} AND user_id = {placeholder}
        ''', (expense_id, user_id))
        expense = cursor.fetchone()
        
        if not expense:
            conn.close()
            return jsonify({'error': 'Expense not found'}), 404
        
        placeholder = get_placeholder()
        execute_update(conn, f'DELETE FROM expenses WHERE expense_id = {placeholder} AND user_id = {placeholder}', (expense_id, user_id))
        conn.close()
        
        log_user_action('expense_deleted', user_id, {
            'expense_id': expense_id, 
            'amount': expense['amount'], 
            'category_id': expense['category_id']
        })
        return jsonify({'message': 'Expense deleted successfully'})
    except Exception as e:
        conn.close()
        log_dml_error('DELETE', 'expenses', e, user_id, {'expense_id': expense_id})
        return jsonify({'error': 'Failed to delete expense'}), 500

@expenses_api.route('/api/expenses/report', methods=['GET'])
def expense_report():
    """Get expense report with summary data."""
    user_id = get_current_user_id()
    
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category_id = request.args.get('category_id')
    
    conn = get_db_connection()
    
    # Build base query
    base_where = 'WHERE e.user_id = ? AND ec.user_id = ?'
    params = [user_id, user_id]
    
    if start_date:
        base_where += ' AND e.expense_date >= ?'
        params.append(start_date)
    
    if end_date:
        base_where += ' AND e.expense_date <= ?'
        params.append(end_date)
    
    if category_id:
        base_where += ' AND e.category_id = ?'
        params.append(category_id)
    
    # Get total expenses
    total_query = f'''
        SELECT SUM(e.amount) as total_amount, COUNT(*) as total_count
        FROM expenses e 
        JOIN expense_categories ec ON e.category_id = ec.category_id 
        {base_where}
    '''
    cursor = execute_query(conn, total_query, params)

    total_result = cursor.fetchone()
    
    # Get expenses by category
    category_query = f'''
        SELECT ec.category_name, SUM(e.amount) as total_amount, COUNT(*) as count
        FROM expenses e 
        JOIN expense_categories ec ON e.category_id = ec.category_id 
        {base_where}
        GROUP BY ec.category_id, ec.category_name
        ORDER BY total_amount DESC
    '''
    cursor = execute_query(conn, category_query, params)

    category_results = cursor.fetchall()
    
    # Get monthly breakdown
    monthly_query = f'''
        SELECT strftime('%Y-%m', e.expense_date) as month, 
               SUM(e.amount) as total_amount, COUNT(*) as count
        FROM expenses e 
        JOIN expense_categories ec ON e.category_id = ec.category_id 
        {base_where}
        GROUP BY strftime('%Y-%m', e.expense_date)
        ORDER BY month DESC
        LIMIT 12
    '''
    cursor = execute_query(conn, monthly_query, params)

    monthly_results = cursor.fetchall()
    
    conn.close()
    
    return jsonify({
        'summary': {
            'total_amount': float(total_result['total_amount'] or 0),
            'total_count': total_result['total_count'] or 0
        },
        'by_category': [dict(result) for result in category_results],
        'by_month': [dict(result) for result in monthly_results]
    })

@expenses_api.route('/api/expenses/download', methods=['GET'])
def download_expenses():
    """Download expenses as CSV."""
    user_id = get_current_user_id()
    
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category_id = request.args.get('category_id')
    
    conn = get_db_connection()
    
    # Build query
    query = '''
        SELECT e.expense_date, ec.category_name, e.amount, e.description, e.payment_method, e.receipt_url
        FROM expenses e 
        JOIN expense_categories ec ON e.category_id = ec.category_id 
        WHERE e.user_id = ? AND ec.user_id = ?
    '''
    params = [user_id, user_id]
    
    if start_date:
        query += ' AND e.expense_date >= ?'
        params.append(start_date)
    
    if end_date:
        query += ' AND e.expense_date <= ?'
        params.append(end_date)
    
    if category_id:
        query += ' AND e.category_id = ?'
        params.append(category_id)
    
    query += ' ORDER BY e.expense_date DESC'
    
    cursor = execute_query(conn, query, params)

    
    expenses = cursor.fetchall()
    conn.close()
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Category', 'Amount', 'Description', 'Payment Method', 'Receipt URL'])
    
    for expense in expenses:
        writer.writerow([
            expense['expense_date'],
            expense['category_name'],
            expense['amount'],
            expense['description'] or '',
            expense['payment_method'],
            expense['receipt_url'] or ''
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=expenses.csv'}
    )

@expenses_api.route('/expenses')
def expenses_page():
    """Render expenses page."""
    user_plan_info = get_user_plan_info()
    return render_template('expenses.html', 
                        user_plan_info=user_plan_info,
                        get_user_language=get_user_language,
                        get_translated_text=get_translated_text)
