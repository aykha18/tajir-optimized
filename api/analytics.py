from flask import Blueprint, jsonify, session, request, render_template
from datetime import datetime, timedelta
from db.connection import (
    get_db_connection,
    get_placeholder,
    execute_query,
    execute_update,
    is_postgresql,
)
from api.utils import get_current_user_id, get_date_range, api_error_handler, fetch_payment_methods, fetch_repeated_customers, fetch_top_products_by_where
from api.plans import get_user_plan_info
from api.i18n import get_user_language, translate_text as get_translated_text

analytics_api = Blueprint('analytics_api', __name__, url_prefix='/api')
analytics_pages = Blueprint('analytics_pages', __name__)

def _fetch_top_products(conn, user_id, from_date, to_date, limit=10):
    placeholder = get_placeholder()
    where_clause = f"b.user_id = {placeholder} AND DATE(b.bill_date) BETWEEN {placeholder} AND {placeholder}"
    rows = fetch_top_products_by_where(conn, where_clause, (user_id, from_date, to_date), limit=limit)
    return [dict(r) for r in rows]

def _fetch_employee_performance(conn, user_id, from_date, to_date):
    placeholder = get_placeholder()
    rows = execute_query(conn, f'''
        SELECT 
            e.name as employee_name,
            COUNT(b.bill_id) as bills_handled,
            SUM(b.total_amount) as total_revenue,
            AVG(b.total_amount) as avg_bill_value
        FROM employees e
        LEFT JOIN bills b ON e.employee_id = b.master_id AND b.user_id = e.user_id
        WHERE e.user_id = {placeholder} 
        AND (b.bill_date IS NULL OR DATE(b.bill_date) BETWEEN {placeholder} AND {placeholder})
        GROUP BY e.employee_id, e.name
        ORDER BY total_revenue DESC
    ''', (user_id, from_date, to_date)).fetchall()
    return [dict(r) for r in rows]

def _fetch_payment_methods(conn, user_id, from_date, to_date):
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
    return [dict(r) for r in rows]

def _fetch_top_regions(conn, user_id, limit=10):
    placeholder = get_placeholder()
    rows = execute_query(conn, f'''
        SELECT COALESCE(customer_area, 'Unknown') as area, SUM(total_amount) as sales
        FROM bills
        WHERE customer_area IS NOT NULL AND customer_area != '' AND user_id = {placeholder}
        GROUP BY customer_area
        ORDER BY sales DESC
        LIMIT {limit}
    ''', (user_id,)).fetchall()
    return rows

def _fetch_expense_categories(conn, user_id, from_date, to_date, limit=5):
    placeholder = get_placeholder()
    rows = execute_query(conn, f'''
        SELECT 
            ec.category_name,
            SUM(e.amount) as total_amount,
            COUNT(*) as expense_count
        FROM expenses e
        JOIN expense_categories ec ON e.category_id = ec.category_id
        WHERE e.user_id = {placeholder} 
        AND DATE(e.expense_date) BETWEEN {placeholder} AND {placeholder}
        GROUP BY ec.category_id, ec.category_name
        ORDER BY total_amount DESC
        LIMIT {limit}
    ''', (user_id, from_date, to_date)).fetchall()
    return rows
def _fetch_today_revenue(conn, user_id):
    placeholder = get_placeholder()
    if is_postgresql():
        date_today = "CURRENT_DATE"
    else:
        date_today = "DATE('now')"
    cursor = execute_query(conn, f'''
        SELECT COALESCE(SUM(total_amount), 0) as total 
        FROM bills 
        WHERE DATE(bill_date) = {date_today} AND user_id = {placeholder}
    ''', (user_id,))
    result = cursor.fetchone()
    return result[0] if isinstance(result, tuple) else result['total']
def _fetch_today_bills_count(conn, user_id):
    placeholder = get_placeholder()
    if is_postgresql():
        date_today = "CURRENT_DATE"
    else:
        date_today = "DATE('now')"
    cursor = execute_query(conn, f'''
        SELECT COUNT(*) as count 
        FROM bills 
        WHERE DATE(bill_date) = {date_today} AND user_id = {placeholder}
    ''', (user_id,))
    result = cursor.fetchone()
    return result[0] if isinstance(result, tuple) else result['count']
def _fetch_pending_bills_count(conn, user_id):
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'''
        SELECT COUNT(*) as count 
        FROM bills 
        WHERE status = 'Pending' AND user_id = {placeholder}
    ''', (user_id,))
    result = cursor.fetchone()
    return result[0] if isinstance(result, tuple) else result['count']
def _fetch_total_customers(conn, user_id):
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'''
        SELECT COUNT(*) as count FROM customers WHERE user_id = {placeholder}
    ''', (user_id,))
    result = cursor.fetchone()
    return result[0] if isinstance(result, tuple) else result['count']
def _fetch_today_expenses(conn, user_id):
    placeholder = get_placeholder()
    if is_postgresql():
        date_today = "CURRENT_DATE"
    else:
        date_today = "DATE('now')"
    cursor = execute_query(conn, f'''
        SELECT COALESCE(SUM(amount), 0) as total 
        FROM expenses 
        WHERE DATE(expense_date) = {date_today} AND user_id = {placeholder}
    ''', (user_id,))
    result = cursor.fetchone()
    return result[0] if isinstance(result, tuple) else result['total']
def _fetch_month_expenses(conn, user_id):
    placeholder = get_placeholder()
    if is_postgresql():
        month_str = "TO_CHAR(expense_date, 'YYYY-MM')"
        month_str_now = "TO_CHAR(CURRENT_DATE, 'YYYY-MM')"
    else:
        month_str = "strftime('%Y-%m', expense_date)"
        month_str_now = "strftime('%Y-%m', 'now')"
    cursor = execute_query(conn, f'''
        SELECT COALESCE(SUM(amount), 0) as total 
        FROM expenses 
        WHERE {month_str} = {month_str_now} AND user_id = {placeholder}
    ''', (user_id,))
    result = cursor.fetchone()
    return result[0] if isinstance(result, tuple) else result['total']
def _fetch_monthly_expense_trends_by_category(conn, user_id, months=6):
    if is_postgresql():
        rows = execute_query(conn, f'''
            SELECT 
                ec.category_name,
                TO_CHAR(e.expense_date, 'YYYY-MM') as month,
                SUM(e.amount) as amount
            FROM expenses e
            JOIN expense_categories ec ON e.category_id = ec.category_id
            WHERE e.user_id = %s 
            AND e.expense_date >= CURRENT_DATE - INTERVAL '%s months'
            GROUP BY ec.category_id, ec.category_name, TO_CHAR(e.expense_date, 'YYYY-MM')
            ORDER BY month, amount DESC
        ''', (user_id, months)).fetchall()
    else:
        rows = execute_query(conn, f'''
            SELECT 
                ec.category_name,
                strftime('%Y-%m', e.expense_date) as month,
                SUM(e.amount) as amount
            FROM expenses e
            JOIN expense_categories ec ON e.category_id = ec.category_id
            WHERE e.user_id = ? 
            AND e.expense_date >= date('now', '-' || ? || ' months')
            GROUP BY ec.category_id, ec.category_name, strftime('%Y-%m', e.expense_date)
            ORDER BY month, amount DESC
        ''', (user_id, months)).fetchall()
    return rows

 

def _fetch_revenue_trends(conn, user_id, period, months):
    placeholder = get_placeholder()
    if period == 'daily':
        if is_postgresql():
            rows = execute_query(conn, '''
                SELECT 
                    DATE(bill_date) as date,
                    SUM(total_amount) as revenue,
                    COUNT(*) as invoices,
                    COUNT(DISTINCT customer_id) as customers
                FROM bills 
                WHERE user_id = %s 
                AND bill_date >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY DATE(bill_date)
                ORDER BY date
            ''', (user_id,)).fetchall()
        else:
            rows = execute_query(conn, '''
                SELECT 
                    DATE(bill_date) as date,
                    SUM(total_amount) as revenue,
                    COUNT(*) as invoices,
                    COUNT(DISTINCT customer_id) as customers
                FROM bills 
                WHERE user_id = ? 
                AND bill_date >= date('now', '-30 days')
                GROUP BY DATE(bill_date)
                ORDER BY date
            ''', (user_id,)).fetchall()
    elif period == 'weekly':
        if is_postgresql():
            rows = execute_query(conn, '''
                SELECT 
                    TO_CHAR(bill_date, 'IYYY-IW') as week,
                    SUM(total_amount) as revenue,
                    COUNT(*) as invoices,
                    COUNT(DISTINCT customer_id) as customers
                FROM bills 
                WHERE user_id = %s 
                AND bill_date >= CURRENT_DATE - INTERVAL '84 days'
                GROUP BY TO_CHAR(bill_date, 'IYYY-IW')
                ORDER BY week
            ''', (user_id,)).fetchall()
        else:
            rows = execute_query(conn, '''
                SELECT 
                    strftime('%Y-W%W', bill_date) as week,
                    SUM(total_amount) as revenue,
                    COUNT(*) as invoices,
                    COUNT(DISTINCT customer_id) as customers
                FROM bills 
                WHERE user_id = ? 
                AND bill_date >= date('now', '-84 days')
                GROUP BY strftime('%Y-W%W', bill_date)
                ORDER BY week
            ''', (user_id,)).fetchall()
    else:
        if is_postgresql():
            rows = execute_query(conn, '''
                SELECT 
                    TO_CHAR(bill_date, 'YYYY-MM') as month,
                    SUM(total_amount) as revenue,
                    COUNT(*) as invoices,
                    COUNT(DISTINCT customer_id) as customers
                FROM bills 
                WHERE user_id = %s 
                AND bill_date >= CURRENT_DATE - INTERVAL '%s months'
                GROUP BY TO_CHAR(bill_date, 'YYYY-MM')
                ORDER BY month
            ''', (user_id, months)).fetchall()
        else:
            rows = execute_query(conn, '''
                SELECT 
                    strftime('%Y-%m', bill_date) as month,
                    SUM(total_amount) as revenue,
                    COUNT(*) as invoices,
                    COUNT(DISTINCT customer_id) as customers
                FROM bills 
                WHERE user_id = ? 
                AND bill_date >= date('now', '-' || ? || ' months')
                GROUP BY strftime('%Y-%m', bill_date)
                ORDER BY month
            ''', (user_id, months)).fetchall()
    return [dict(r) for r in rows]

def _fetch_expense_trends(conn, user_id, period, months):
    placeholder = get_placeholder()
    if period == 'daily':
        if is_postgresql():
            rows = execute_query(conn, '''
                SELECT 
                    DATE(expense_date) as date,
                    SUM(amount) as expenses,
                    COUNT(*) as expense_count
                FROM expenses 
                WHERE user_id = %s 
                AND expense_date >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY DATE(expense_date)
                ORDER BY date
            ''', (user_id,)).fetchall()
        else:
            rows = execute_query(conn, '''
                SELECT 
                    DATE(expense_date) as date,
                    SUM(amount) as expenses,
                    COUNT(*) as expense_count
                FROM expenses 
                WHERE user_id = ? 
                AND expense_date >= date('now', '-30 days')
                GROUP BY DATE(expense_date)
                ORDER BY date
            ''', (user_id,)).fetchall()
    elif period == 'weekly':
        if is_postgresql():
            rows = execute_query(conn, '''
                SELECT 
                    TO_CHAR(expense_date, 'IYYY-IW') as week,
                    SUM(amount) as expenses,
                    COUNT(*) as expense_count
                FROM expenses 
                WHERE user_id = %s 
                AND expense_date >= CURRENT_DATE - INTERVAL '84 days'
                GROUP BY TO_CHAR(expense_date, 'IYYY-IW')
                ORDER BY week
            ''', (user_id,)).fetchall()
        else:
            rows = execute_query(conn, '''
                SELECT 
                    strftime('%Y-W%W', expense_date) as week,
                    SUM(amount) as expenses,
                    COUNT(*) as expense_count
                FROM expenses 
                WHERE user_id = ? 
                AND expense_date >= date('now', '-84 days')
                GROUP BY strftime('%Y-W%W', expense_date)
                ORDER BY week
            ''', (user_id,)).fetchall()
    else:
        if is_postgresql():
            rows = execute_query(conn, '''
                SELECT 
                    TO_CHAR(expense_date, 'YYYY-MM') as month,
                    SUM(amount) as expenses,
                    COUNT(*) as expense_count
                FROM expenses 
                WHERE user_id = %s 
                AND expense_date >= CURRENT_DATE - INTERVAL '%s months'
                GROUP BY TO_CHAR(expense_date, 'YYYY-MM')
                ORDER BY month
            ''', (user_id, months)).fetchall()
        else:
            rows = execute_query(conn, '''
                SELECT 
                    strftime('%Y-%m', expense_date) as month,
                    SUM(amount) as expenses,
                    COUNT(*) as expense_count
                FROM expenses 
                WHERE user_id = ? 
                AND expense_date >= date('now', '-' || ? || ' months')
                GROUP BY strftime('%Y-%m', expense_date)
                ORDER BY month
            ''', (user_id, months)).fetchall()
    return [dict(r) for r in rows]

@analytics_pages.route('/financial-insights')
def financial_insights():
    """Serve the financial insights page"""
    user_plan_info = get_user_plan_info()
    return render_template('financial_insights.html',
                         user_plan_info=user_plan_info,
                         get_user_language=get_user_language,
                         get_translated_text=get_translated_text)

@analytics_api.route('/dashboard', methods=['GET'])
@analytics_api.route('/analytics/dashboard', methods=['GET'])
@api_error_handler
def get_dashboard_data():
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    
    # Date query parts based on DB type
    if is_postgresql():
        date_today = "CURRENT_DATE"
        month_str = "TO_CHAR(expense_date, 'YYYY-MM')"
        month_str_now = "TO_CHAR(CURRENT_DATE, 'YYYY-MM')"
        date_6_months = "CURRENT_DATE - INTERVAL '6 months'"
        bill_month_str = "TO_CHAR(bill_date, 'YYYY-MM')"
        exp_month_str = "TO_CHAR(expense_date, 'YYYY-MM')"
    else:
        date_today = "DATE('now')"
        month_str = "strftime('%Y-%m', expense_date)"
        month_str_now = "strftime('%Y-%m', 'now')"
        date_6_months = "date('now', '-6 months')"
        bill_month_str = "strftime('%Y-%m', bill_date)"
        exp_month_str = "strftime('%Y-%m', expense_date)"

    total_revenue = _fetch_today_revenue(conn, user_id)
    total_bills_today = _fetch_today_bills_count(conn, user_id)
    pending_bills = _fetch_pending_bills_count(conn, user_id)
    total_customers = _fetch_total_customers(conn, user_id)
    total_expenses_today = _fetch_today_expenses(conn, user_id)
    total_expenses_month = _fetch_month_expenses(conn, user_id)
    
    monthly_revenue = _fetch_revenue_trends(conn, user_id, 'monthly', 6)
    monthly_expenses = _fetch_expense_trends(conn, user_id, 'monthly', 6)
    top_regions = _fetch_top_regions(conn, user_id, limit=10)
    from datetime import date
    today = date.today().strftime('%Y-%m-%d')
    rows = _fetch_top_products(conn, user_id, '1970-01-01', today, limit=100)
    rows_sorted = sorted(rows, key=lambda r: (r.get('total_quantity') or 0), reverse=True)[:10]
    trending_products = [{
        'product_name': r.get('product_name') or 'Unknown',
        'qty_sold': r.get('total_quantity') or 0,
        'total_revenue': r.get('total_revenue') or 0,
    } for r in rows_sorted]
    repeated_customers = fetch_repeated_customers(conn, user_id, limit=10)
    conn.close()
    return jsonify({
        'total_revenue': float(total_revenue),
        'total_bills_today': total_bills_today,
        'pending_bills': pending_bills,
        'total_customers': total_customers,
        'total_expenses_today': float(total_expenses_today),
        'total_expenses_month': float(total_expenses_month),
        'monthly_revenue': [dict(item) for item in monthly_revenue],
        'monthly_expenses': [dict(item) for item in monthly_expenses],
        'top_regions': [dict(item) for item in top_regions],
        'trending_products': [dict(item) for item in trending_products],
        'repeated_customers': [dict(item) for item in repeated_customers]
    })

@analytics_api.route('/customer-invoice-heatmap', methods=['GET'])
@analytics_api.route('/analytics/customer-invoice-heatmap', methods=['GET'])
def customer_invoice_heatmap():
    user_id = get_current_user_id()
    conn = None
    try:
        conn = get_db_connection()
        placeholder = get_placeholder()
        if is_postgresql():
            months_rows = execute_query(conn, f"""
                SELECT DISTINCT TO_CHAR(bill_date, 'YYYY-MM') as month
                FROM bills
                WHERE bill_date >= CURRENT_DATE - INTERVAL '5 months' AND user_id = {placeholder}
                ORDER BY month ASC
            """, (user_id,)).fetchall()
            customers = execute_query(conn, f"""
                SELECT c.customer_id, c.name, COUNT(b.bill_id) as total_invoices
                FROM customers c
                JOIN bills b ON c.customer_id = b.customer_id AND c.user_id = b.user_id
                WHERE b.bill_date >= CURRENT_DATE - INTERVAL '5 months' AND b.user_id = {placeholder}
                GROUP BY c.customer_id, c.name
                ORDER BY total_invoices DESC
            """, (user_id,)).fetchall()
            counts_rows = execute_query(conn, f"""
                SELECT customer_id,
                       TO_CHAR(bill_date, 'YYYY-MM') as month,
                       COUNT(*) as count
                FROM bills
                WHERE bill_date >= CURRENT_DATE - INTERVAL '5 months' AND user_id = {placeholder}
                GROUP BY customer_id, TO_CHAR(bill_date, 'YYYY-MM')
            """, (user_id,)).fetchall()
        else:
            months_rows = execute_query(conn, f"""
                SELECT DISTINCT strftime('%Y-%m', bill_date) as month
                FROM bills
                WHERE bill_date >= date('now', '-5 months', 'start of month') AND user_id = {placeholder}
                ORDER BY month ASC
            """, (user_id,)).fetchall()
            customers = execute_query(conn, f"""
                SELECT c.customer_id, c.name, COUNT(b.bill_id) as total_invoices
                FROM customers c
                JOIN bills b ON c.customer_id = b.customer_id AND c.user_id = b.user_id
                WHERE b.bill_date >= date('now', '-5 months', 'start of month') AND b.user_id = {placeholder}
                GROUP BY c.customer_id, c.name
                ORDER BY total_invoices DESC
            """, (user_id,)).fetchall()
            counts_rows = execute_query(conn, f"""
                SELECT customer_id,
                       strftime('%Y-%m', bill_date) as month,
                       COUNT(*) as count
                FROM bills
                WHERE bill_date >= date('now', '-5 months', 'start of month') AND user_id = {placeholder}
                GROUP BY customer_id, strftime('%Y-%m', bill_date)
            """, (user_id,)).fetchall()
        months = []
        for row in months_rows:
            if isinstance(row, tuple):
                if len(row) > 0:
                    months.append(row[0])
            else:
                m = row.get('month')
                if m is not None:
                    months.append(m)
        customer_ids = []
        customer_names = []
        for row in customers:
            if isinstance(row, tuple):
                if len(row) >= 2:
                    customer_ids.append(row[0])
                    customer_names.append(row[1])
            else:
                cid = row.get('customer_id')
                name = row.get('name')
                if cid is not None and name is not None:
                    customer_ids.append(cid)
                    customer_names.append(name)
        count_map = {}
        for r in counts_rows:
            if isinstance(r, tuple):
                if len(r) >= 3:
                    cid, m, cnt = r[0], r[1], r[2]
                    count_map[(cid, m)] = cnt
            else:
                cid = r.get('customer_id')
                m = r.get('month')
                cnt = r.get('count')
                if cid is not None and m is not None and cnt is not None:
                    count_map[(cid, m)] = cnt
        matrix = []
        for cid in customer_ids:
            row = []
            for m in months:
                row.append(count_map.get((cid, m), 0))
            matrix.append(row)
        return jsonify({
            'customers': customer_names,
            'months': months,
            'matrix': matrix
        })
    except Exception:
        return jsonify({
            'customers': [],
            'months': [],
            'matrix': []
        })
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass

@analytics_api.route('/employee-analytics', methods=['GET'])
@analytics_api.route('/analytics/employee-analytics', methods=['GET'])
@api_error_handler
def employee_analytics():
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'''
        SELECT e.name, COALESCE(SUM(b.total_amount), 0) as total_revenue
        FROM employees e
        LEFT JOIN bills b ON e.employee_id = b.master_id AND b.user_id = e.user_id
        WHERE e.user_id = {placeholder} AND e.is_active = TRUE
        GROUP BY e.employee_id
        ORDER BY total_revenue DESC
        LIMIT 5
    ''', (user_id,))
    top5 = cursor.fetchall()
    cursor = execute_query(conn, f'''
        SELECT e.name, COALESCE(SUM(b.total_amount), 0) as total_revenue
        FROM employees e
        LEFT JOIN bills b ON e.employee_id = b.master_id AND b.user_id = e.user_id
        WHERE e.user_id = {placeholder} AND e.is_active = TRUE
        GROUP BY e.employee_id
        ORDER BY total_revenue DESC
    ''', (user_id,))
    shares = cursor.fetchall()
    conn.close()
    return jsonify({
        'top5': [dict(row) for row in top5],
        'shares': [dict(row) for row in shares]
    })

@analytics_api.route('/analytics/financial-overview', methods=['GET'])
@api_error_handler
def get_financial_overview():
    """Get comprehensive financial overview with key metrics"""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    from_date, to_date = get_date_range(request, default_days=30)
    
    try:
        # Revenue calculations
        placeholder = get_placeholder()
        revenue_data = execute_query(conn, f'''
            SELECT 
                COUNT(*) as total_invoices,
                SUM(total_amount) as total_revenue,
                SUM(subtotal) as gross_revenue,
                SUM(vat_amount) as total_vat,
                AVG(total_amount) as avg_invoice_value,
                COUNT(DISTINCT customer_id) as unique_customers
            FROM bills 
            WHERE user_id = {placeholder} 
            AND DATE(bill_date) BETWEEN {placeholder} AND {placeholder}
        ''', (user_id, from_date, to_date)).fetchone()
        
        # Expense calculations
        expense_data = execute_query(conn, f'''
            SELECT 
                COUNT(*) as total_expenses,
                SUM(amount) as total_expenses_amount,
                AVG(amount) as avg_expense_amount
            FROM expenses 
            WHERE user_id = {placeholder} 
            AND DATE(expense_date) BETWEEN {placeholder} AND {placeholder}
        ''', (user_id, from_date, to_date)).fetchone()
        
        # Calculate profit metrics
        total_revenue = float(revenue_data['total_revenue'] or 0)
        total_expenses = float(expense_data['total_expenses_amount'] or 0)
        net_profit = total_revenue - total_expenses
        gross_profit = float(revenue_data['gross_revenue'] or 0) - total_expenses
        
        # Calculate margins
        gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        net_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Get top revenue sources
        top_products_raw = _fetch_top_products(conn, user_id, from_date, to_date, limit=5)
        top_products = [{
            'product_name': p.get('product_name'),
            'revenue': p.get('total_revenue'),
            'quantity_sold': p.get('total_quantity')
        } for p in top_products_raw]
        
        top_expense_categories = _fetch_expense_categories(conn, user_id, from_date, to_date, limit=5)
        
        conn.close()
        
        return jsonify({
            'period': {
                'from_date': from_date,
                'to_date': to_date
            },
            'revenue': {
                'total_revenue': total_revenue,
                'gross_revenue': float(revenue_data['gross_revenue'] or 0),
                'total_vat': float(revenue_data['total_vat'] or 0),
                'total_invoices': revenue_data['total_invoices'],
                'avg_invoice_value': float(revenue_data['avg_invoice_value'] or 0),
                'unique_customers': revenue_data['unique_customers']
            },
            'expenses': {
                'total_expenses': total_expenses,
                'total_expense_count': expense_data['total_expenses'],
                'avg_expense_amount': float(expense_data['avg_expense_amount'] or 0)
            },
            'profitability': {
                'gross_profit': gross_profit,
                'net_profit': net_profit,
                'gross_margin': round(gross_margin, 2),
                'net_margin': round(net_margin, 2)
            },
            'top_products': [dict(product) for product in top_products],
            'top_expense_categories': [dict(category) for category in top_expense_categories]
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@analytics_api.route('/analytics/revenue-trends', methods=['GET'])
@api_error_handler
def get_revenue_trends():
    """Get revenue trends over time"""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    # Get period from query params (daily, weekly, monthly)
    period = request.args.get('period', 'monthly')
    months = int(request.args.get('months', 6))
    
    trends = _fetch_revenue_trends(conn, user_id, period, months)
    conn.close()
    return jsonify({
        'period': period,
        'trends': trends
    })

@analytics_api.route('/expense-trends', methods=['GET'])
@analytics_api.route('/analytics/expense-trends', methods=['GET'])
@api_error_handler
def get_expense_trends():
    """Get expense trends over time"""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    # Get period from query params (daily, weekly, monthly)
    period = request.args.get('period', 'monthly')
    months = int(request.args.get('months', 6))
    
    trends = _fetch_expense_trends(conn, user_id, period, months)
    conn.close()
    return jsonify({
        'period': period,
        'trends': trends
    })

@analytics_api.route('/analytics/cash-flow', methods=['GET'])
@api_error_handler
def get_cash_flow():
    """Get cash flow analysis"""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    from_date, to_date = get_date_range(request, default_days=30)
    
    try:
        # Cash inflows (revenue)
        placeholder = get_placeholder()
        cash_inflows = execute_query(conn, f'''
            SELECT 
                SUM(total_amount) as total_inflow,
                SUM(advance_paid) as advance_payments,
                SUM(balance_amount) as pending_payments
            FROM bills 
            WHERE user_id = {placeholder} 
            AND DATE(bill_date) BETWEEN {placeholder} AND {placeholder}
        ''', (user_id, from_date, to_date)).fetchone()
        
        # Cash outflows (expenses)
        cash_outflows = execute_query(conn, f'''
            SELECT 
                SUM(amount) as total_outflow,
                COUNT(*) as expense_count
            FROM expenses 
            WHERE user_id = {placeholder} 
            AND DATE(expense_date) BETWEEN {placeholder} AND {placeholder}
        ''', (user_id, from_date, to_date)).fetchone()
        
        payment_methods = fetch_payment_methods(conn, user_id, from_date, to_date)
        
        conn.close()
        
        total_inflow = float(cash_inflows['total_inflow'] or 0)
        total_outflow = float(cash_outflows['total_outflow'] or 0)
        net_cash_flow = total_inflow - total_outflow
        
        return jsonify({
            'period': {
                'from_date': from_date,
                'to_date': to_date
            },
            'cash_flow': {
                'total_inflow': total_inflow,
                'total_outflow': total_outflow,
                'net_cash_flow': net_cash_flow,
                'advance_payments': float(cash_inflows['advance_payments'] or 0),
                'pending_payments': float(cash_inflows['pending_payments'] or 0)
            },
            'payment_methods': [dict(method) for method in payment_methods]
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@analytics_api.route('/business-metrics', methods=['GET'])
@analytics_api.route('/analytics/business-metrics', methods=['GET'])
@api_error_handler
def get_business_metrics():
    """Get key business performance metrics"""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    from_date, to_date = get_date_range(request, default_days=30)
    
    try:
        placeholder = get_placeholder()
        
        # Customer metrics
        if is_postgresql():
            customer_metrics = execute_query(conn, f'''
                SELECT 
                    COUNT(DISTINCT customer_id) as total_customers,
                    COUNT(DISTINCT CASE WHEN bill_date >= CURRENT_DATE - INTERVAL '7 days' THEN customer_id END) as new_customers_7d,
                    COUNT(DISTINCT CASE WHEN bill_date >= CURRENT_DATE - INTERVAL '30 days' THEN customer_id END) as new_customers_30d,
                    AVG(total_amount) as avg_order_value,
                    SUM(total_amount) / COUNT(DISTINCT customer_id) as revenue_per_customer
                FROM bills 
                WHERE user_id = {placeholder} 
                AND DATE(bill_date) BETWEEN {placeholder} AND {placeholder}
            ''', (user_id, from_date, to_date)).fetchone()
        else:
            customer_metrics = execute_query(conn, f'''
            SELECT 
                COUNT(DISTINCT customer_id) as total_customers,
                COUNT(DISTINCT CASE WHEN bill_date >= date('now', '-7 days') THEN customer_id END) as new_customers_7d,
                COUNT(DISTINCT CASE WHEN bill_date >= date('now', '-30 days') THEN customer_id END) as new_customers_30d,
                AVG(total_amount) as avg_order_value,
                SUM(total_amount) / COUNT(DISTINCT customer_id) as revenue_per_customer
            FROM bills 
                WHERE user_id = {placeholder} 
                AND DATE(bill_date) BETWEEN {placeholder} AND {placeholder}
        ''', (user_id, from_date, to_date)).fetchone()
        
        # Employee performance
        employee_performance = _fetch_employee_performance(conn, user_id, from_date, to_date)
        
        # Product performance
        product_performance = _fetch_top_products(conn, user_id, from_date, to_date, limit=10)
        
        conn.close()
        
        return jsonify({
            'period': {
                'from_date': from_date,
                'to_date': to_date
            },
            'customer_metrics': {
                'total_customers': customer_metrics['total_customers'],
                'new_customers_7d': customer_metrics['new_customers_7d'],
                'new_customers_30d': customer_metrics['new_customers_30d'],
                'avg_order_value': float(customer_metrics['avg_order_value'] or 0),
                'revenue_per_customer': float(customer_metrics['revenue_per_customer'] or 0)
            },
            'employee_performance': [dict(emp) for emp in employee_performance],
            'product_performance': [dict(prod) for prod in product_performance]
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@analytics_api.route('/analytics/expense-breakdown', methods=['GET'])
@api_error_handler
def get_expense_breakdown():
    """Get detailed expense breakdown by category"""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    from_date, to_date = get_date_range(request, default_days=30)
    
    try:
        placeholder = get_placeholder()
        
        # Expense breakdown by category
        category_breakdown = execute_query(conn, f'''
            SELECT 
                ec.category_name,
                ec.description,
                SUM(e.amount) as total_amount,
                COUNT(*) as expense_count,
                AVG(e.amount) as avg_amount,
                MIN(e.amount) as min_amount,
                MAX(e.amount) as max_amount
            FROM expenses e
            JOIN expense_categories ec ON e.category_id = ec.category_id
            WHERE e.user_id = {placeholder} 
            AND DATE(e.expense_date) BETWEEN {placeholder} AND {placeholder}
            GROUP BY ec.category_id, ec.category_name, ec.description
            ORDER BY total_amount DESC
        ''', (user_id, from_date, to_date)).fetchall()
        
        monthly_trends = _fetch_monthly_expense_trends_by_category(conn, user_id, months=6)
        
        conn.close()
        
        return jsonify({
            'period': {
                'from_date': from_date,
                'to_date': to_date
            },
            'category_breakdown': [dict(cat) for cat in category_breakdown],
            'monthly_trends': [dict(trend) for trend in monthly_trends]
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@analytics_api.route('/analytics/top-products', methods=['GET'])
@api_error_handler
def get_top_products():
    """Get top performing products by revenue"""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    from_date, to_date = get_date_range(request, default_days=30)
    
    try:
        rows = _fetch_top_products(conn, user_id, from_date, to_date, limit=10)
        top_products = [{
            'product_name': r.get('product_name'),
            'quantity_sold': r.get('total_quantity'),
            'total_revenue': r.get('total_revenue'),
            'bill_count': r.get('invoices_count'),
            'avg_unit_price': r.get('avg_price'),
        } for r in rows]
        
        conn.close()
        
        return jsonify({
            'period': {
                'from_date': from_date,
                'to_date': to_date
            },
            'top_products': top_products
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500
