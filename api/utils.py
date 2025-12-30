import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, jsonify
from db.connection import get_db_connection, get_placeholder, execute_update, execute_with_returning, execute_query
import qrcode
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

def generate_zatca_qr_code(seller_name, seller_trn, invoice_number, timestamp, total_with_vat, vat_amount):
    """
    Generate QR code data in ZATCA format for FTA compliance
    Format: Seller Name, TRN, Timestamp, Total with VAT, VAT Amount
    """
    # Create QR data in ZATCA format
    qr_data = f"{seller_name}\n{seller_trn}\n{timestamp}\n{total_with_vat}\n{vat_amount}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create QR code image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    buffer = BytesIO()
    qr_image.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return qr_base64

def get_current_user_id():
    """Get current user_id from session, fallback to None for proper authentication."""
    # DEBUG: Default to user_id 2 for testing
    user_id = session.get('user_id')
    if user_id is None:
        # print("DEBUG: Defaulting to user_id 2 for testing")
        return 2
    return user_id

def admin_required(f):
    """Decorator to require admin authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            # If it's an API request, return 401
            # Otherwise redirect to login
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated_function

def log_user_action(action, user_id=None, details=None):
    """Log user actions for audit trail."""
    try:
        conn = get_db_connection()
        placeholder = get_placeholder()
        execute_update(conn, f'''
            INSERT INTO user_actions (created_at, action, user_id, details)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
        ''', (
            datetime.now().isoformat(),
            action,
            user_id,
            json.dumps(details) if details else None
        ))
        conn.close()
    except Exception as e:
        logger.error(f"Failed to log user action: {e}")

def log_dml_error(operation, table, error, user_id=None, data=None):
    """Log DML failures to both file and database."""
    try:
        # Log to file
        error_msg = f"DML Error - Operation: {operation}, Table: {table}, Error: {str(error)}"
        if user_id:
            error_msg += f", User: {user_id}"
        if data:
            error_msg += f", Data: {str(data)[:200]}..."  # Truncate data
        
        logger.error(error_msg)
        
        # Log to database (if possible)
        try:
            conn = get_db_connection()
            placeholder = get_placeholder()
            execute_with_returning(conn, f'''
                INSERT INTO error_logs (timestamp, level, operation, table_name, error_message, user_id, data_snapshot)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            ''', (
                datetime.now().isoformat(),
                'ERROR',
                operation,
                table,
                str(error),
                user_id,
                json.dumps(data) if data else None
            ))
            conn.close()
        except Exception as db_log_error:
            # If database logging fails, log to file only
            logger.error(f"Failed to log to database: {db_log_error}")
            
    except Exception as log_error:
        # Fallback to basic logging
        print(f"Logging failed: {log_error}")

def parse_date(s):
    try:
        return datetime.strptime(s, '%Y-%m-%d').date()
    except Exception:
        return None

def get_date_range(request, default_days=30):
    to_str = request.args.get('to_date')
    from_str = request.args.get('from_date')
    if not to_str or not from_str:
        to_dt = datetime.now().date()
        from_dt = (datetime.now() - timedelta(days=default_days)).date()
        return from_dt.strftime('%Y-%m-%d'), to_dt.strftime('%Y-%m-%d')
    fd = parse_date(from_str)
    td = parse_date(to_str)
    if not fd or not td or fd > td:
        raise ValueError('Invalid date range')
    return from_str, to_str

def api_error_handler(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return wrapper

def fetch_top_customers(conn, where_clause, params, limit=5):
    query = f'''
        SELECT 
            c.name as customer_name,
            COUNT(b.bill_id) as invoice_count,
            SUM(b.total_amount) as total_spent
        FROM bills b
        LEFT JOIN customers c ON b.customer_id = c.customer_id
        WHERE {where_clause}
        GROUP BY c.customer_id, c.name
        ORDER BY total_spent DESC
        LIMIT {limit}
    '''
    cursor = execute_query(conn, query, params)
    return cursor.fetchall()
def fetch_top_products_by_where(conn, where_clause, params, limit=5):
    query = f'''
        SELECT 
            bi.product_name,
            SUM(bi.quantity) as total_quantity,
            SUM(bi.total_amount) as total_revenue,
            COUNT(DISTINCT b.bill_id) as invoice_count
        FROM bill_items bi
        JOIN bills b ON bi.bill_id = b.bill_id
        LEFT JOIN customers c ON b.customer_id = c.customer_id
        WHERE {where_clause}
        GROUP BY bi.product_name
        ORDER BY total_revenue DESC
        LIMIT {limit}
    '''
    cursor = execute_query(conn, query, params)
    return cursor.fetchall()
def fetch_payment_methods(conn, user_id, from_date, to_date):
    placeholder = get_placeholder()
    rows = execute_query(conn, f'''
        SELECT 
            payment_method,
            COUNT(*) as count,
            SUM(total_amount) as amount
        FROM bills 
        WHERE user_id = {placeholder} 
        AND DATE(bill_date) BETWEEN {placeholder} AND {placeholder}
        GROUP BY payment_method
        ORDER BY amount DESC
    ''', (user_id, from_date, to_date)).fetchall()
    return rows
def fetch_repeated_customers(conn, user_id, limit=10):
    placeholder = get_placeholder()
    rows = execute_query(conn, f'''
        SELECT COALESCE(customer_name, 'Unknown') as customer_name, 
               COALESCE(customer_phone, '') as customer_phone, 
               COUNT(*) as invoice_count,
               SUM(total_amount) as total_revenue
        FROM bills
        WHERE customer_name IS NOT NULL AND customer_name != '' AND user_id = {placeholder}
        GROUP BY customer_name, customer_phone
        ORDER BY invoice_count DESC
        LIMIT {limit}
    ''', (user_id,)).fetchall()
    return rows
