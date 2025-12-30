from flask import Blueprint, request, jsonify, render_template, Response, redirect
import csv
import math
import logging
from datetime import datetime, timedelta
from io import StringIO
from num2words import num2words
from db.connection import get_db_connection, get_placeholder, execute_query, is_postgresql
from api.utils import get_current_user_id, generate_zatca_qr_code, api_error_handler, fetch_top_customers, fetch_top_products_by_where
from api.i18n import number_to_arabic_words, get_translated_text, get_user_language

logger = logging.getLogger(__name__)

reports_api = Blueprint('reports_api', __name__)

def _build_common_bill_filters(user_id, filters, base_alias='b'):
    conn_placeholder = get_placeholder()
    where_conditions = [f'{base_alias}.user_id = {conn_placeholder}']
    params = [user_id]
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    city = filters.get('city')
    area = filters.get('area')
    status = filters.get('status')
    products = filters.get('products')
    if from_date:
        where_conditions.append(f'DATE({base_alias}.bill_date) >= {conn_placeholder}')
        params.append(from_date)
    if to_date:
        where_conditions.append(f'DATE({base_alias}.bill_date) <= {conn_placeholder}')
        params.append(to_date)
    if products and products != ['All Products']:
        placeholders = ','.join([conn_placeholder for _ in products])
        where_conditions.append(f'''EXISTS (
            SELECT 1 FROM bill_items bi2 
            WHERE bi2.bill_id = {base_alias}.bill_id 
            AND bi2.product_name IN ({placeholders})
        )''')
        params.extend(products)
    if city:
        where_conditions.append(f'c.city = {conn_placeholder}')
        params.append(city)
    if area:
        where_conditions.append(f'c.area = {conn_placeholder}')
        params.append(area)
    if status:
        where_conditions.append(f'{base_alias}.status = {conn_placeholder}')
        params.append(status)
    return ' AND '.join(where_conditions), params

def _get_bill_items_discount_and_products(conn, bill_id, user_id):
    placeholder = get_placeholder()
    items_cursor = execute_query(conn, f'''
        SELECT product_name, rate, quantity, discount 
        FROM bill_items 
        WHERE bill_id = {placeholder} AND user_id = {placeholder}
    ''', (bill_id, user_id))
    items = items_cursor.fetchall()
    discount_amounts = []
    product_names = []
    for it in items:
        it_d = dict(it)
        try:
            rate = float(it_d.get('rate') or 0)
            qty = float(it_d.get('quantity') or 0)
            disc = float(it_d.get('discount') or 0)
        except Exception:
            rate = qty = disc = 0.0
        discount_amounts.append(round(rate * qty * disc / 100.0, 2))
        pn = it_d.get('product_name')
        if pn:
            product_names.append(pn)
    return discount_amounts, (', '.join(product_names) if product_names else None)

def _build_employee_name_filter(base_alias, employee_names, user_id):
    if not employee_names or employee_names == ['All Employees']:
        return '', []
    placeholder = get_placeholder()
    name_placeholders = ','.join([placeholder for _ in employee_names])
    clause = f''' AND {base_alias}.master_id IN (
        SELECT employee_id FROM employees 
        WHERE name IN ({name_placeholders}) AND is_active = TRUE AND user_id = {placeholder}
    )'''
    params = list(employee_names) + [user_id]
    return clause, params


def get_invoice_summary_data(user_id, current_date=None):
    """Get comprehensive summary data for invoices."""
    if current_date is None:
        current_date = datetime.now().date()
    
    conn = get_db_connection()
    
    # Get current month data
    current_month_start = current_date.replace(day=1)
    # Handle December case for next month calculation
    if current_date.month == 12:
        next_month = current_date.replace(year=current_date.year + 1, month=1, day=1)
    else:
        next_month = current_date.replace(month=current_date.month + 1, day=1)
    current_month_end = next_month - timedelta(days=1)
    
    # Get current year data
    current_year_start = current_date.replace(month=1, day=1)
    current_year_end = current_date.replace(month=12, day=31)
    
    # Current month summary
    placeholder = get_placeholder()
    month_data = execute_query(conn, f'''
        SELECT 
            COUNT(*) as total_invoices,
            SUM(total_amount) as total_revenue,
            SUM(vat_amount) as total_vat_collected,
            SUM(subtotal) as total_subtotal,
            SUM(0) as total_discounts,
            AVG(total_amount) as avg_invoice_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM bills 
        WHERE user_id = {placeholder} 
        AND DATE(bill_date) BETWEEN {placeholder} AND {placeholder}
    ''', (user_id, current_month_start, current_month_end)).fetchone()
    
    # Current year summary
    year_data = execute_query(conn, f'''
        SELECT 
            COUNT(*) as total_invoices,
            SUM(total_amount) as total_revenue,
            SUM(vat_amount) as total_vat_collected,
            SUM(subtotal) as total_subtotal,
            SUM(0) as total_discounts,
            AVG(total_amount) as avg_invoice_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM bills 
        WHERE user_id = {placeholder} 
        AND DATE(bill_date) BETWEEN {placeholder} AND {placeholder}
    ''', (user_id, current_year_start, current_year_end)).fetchone()
    
    # All time summary
    all_time_data = execute_query(conn, f'''
        SELECT 
            COUNT(*) as total_invoices,
            SUM(total_amount) as total_revenue,
            SUM(vat_amount) as total_vat_collected,
            SUM(subtotal) as total_subtotal,
            SUM(0) as total_discounts,
            AVG(total_amount) as avg_invoice_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM bills 
        WHERE user_id = {placeholder}
    ''', (user_id,)).fetchone()
    
    # Get top selling products (current month)
    top_products = execute_query(conn, f'''
        SELECT 
            bi.product_name,
            SUM(bi.quantity) as total_quantity,
            SUM(bi.total_amount) as total_revenue
        FROM bill_items bi
        JOIN bills b ON bi.bill_id = b.bill_id
        WHERE b.user_id = {placeholder} 
        AND DATE(b.bill_date) BETWEEN {placeholder} AND {placeholder}
        GROUP BY bi.product_name
        ORDER BY total_revenue DESC
        LIMIT 5
    ''', (user_id, current_month_start, current_month_end)).fetchall()
    
    # Get top customers (current month)
    where_clause = f"b.user_id = {placeholder} AND DATE(b.bill_date) BETWEEN {placeholder} AND {placeholder}"
    top_customers = fetch_top_customers(conn, where_clause, (user_id, current_month_start, current_month_end), limit=5)
    
    conn.close()
    
    return {
        'current_month': dict(month_data) if month_data else {},
        'current_year': dict(year_data) if year_data else {},
        'all_time': dict(all_time_data) if all_time_data else {},
        'top_products': [dict(product) for product in top_products],
        'top_customers': [dict(customer) for customer in top_customers],
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def get_filtered_invoice_summary(user_id, filters=None):
    """Get summary data for invoices based on filters."""
    if filters is None:
        filters = {}
    
    conn = get_db_connection()
    placeholder = get_placeholder()
    normalized_filters = {
        'from_date': filters.get('from_date'),
        'to_date': filters.get('to_date'),
        'city': filters.get('city') if filters.get('city') and filters.get('city') != 'All Cities' else None,
        'area': filters.get('area') if filters.get('area') and filters.get('area') != 'All Areas' else None,
        'status': filters.get('status') if filters.get('status') and filters.get('status') != 'All' else None,
        'products': filters.get('products') if filters.get('products') and filters.get('products') != ['All Products'] else None
    }
    where_clause, params = _build_common_bill_filters(user_id, normalized_filters, base_alias='b')
    if filters.get('employees') and filters['employees'] != ['All Employees']:
        emp_clause, emp_params = _build_employee_name_filter('b', filters['employees'], user_id)
        where_clause = f"{where_clause}{emp_clause}"
        params.extend(emp_params)
    
    # Main summary query
    summary_query = f'''
        SELECT 
            COUNT(*) as total_invoices,
            COALESCE(SUM(b.total_amount), 0) as total_revenue,
            COALESCE(SUM(b.vat_amount), 0) as total_vat_collected,
            COALESCE(SUM(b.subtotal), 0) as total_subtotal,
            COALESCE(SUM(
                (SELECT SUM(bi.rate * bi.quantity * bi.discount / 100) 
                 FROM bill_items bi 
                 WHERE bi.bill_id = b.bill_id)
            ), 0) as total_discounts,
            COALESCE(AVG(b.total_amount), 0) as avg_invoice_value,
            COUNT(DISTINCT b.customer_id) as unique_customers,
            SUM(CASE WHEN b.status = 'Paid' THEN 1 ELSE 0 END) as paid_invoices,
            SUM(CASE WHEN b.status = 'Paid' THEN b.total_amount ELSE 0 END) as paid_amount,
            SUM(CASE WHEN b.status = 'Pending' THEN 1 ELSE 0 END) as pending_invoices,
            SUM(CASE WHEN b.status = 'Pending' THEN b.total_amount ELSE 0 END) as pending_amount
        FROM bills b
        LEFT JOIN customers c ON b.customer_id = c.customer_id
        WHERE {where_clause}
    '''
    
    cursor = execute_query(conn, summary_query, params)
    
    summary_data = cursor.fetchone()
    
    top_products = fetch_top_products_by_where(conn, where_clause, params, limit=5)
    
    # Top customers query
    top_customers = fetch_top_customers(conn, where_clause, params, limit=5)
    
    conn.close()
    
    return {
        'summary': dict(summary_data) if summary_data else {},
        'top_products': [dict(p) for p in top_products],
        'top_customers': [dict(c) for c in top_customers]
    }

@reports_api.route('/api/reports/invoices', methods=['GET'])
@api_error_handler
def get_invoices_report():
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    filters = {
        'from_date': request.args.get('from_date'),
        'to_date': request.args.get('to_date'),
        'city': request.args.get('city') if request.args.get('city') and request.args.get('city') != 'All' else None,
        'area': request.args.get('area') if request.args.get('area') and request.args.get('area') != 'All' else None,
        'status': request.args.get('status') if request.args.get('status') and request.args.get('status') != 'All' else None,
        'products': request.args.getlist('products[]') if request.args.getlist('products[]') and request.args.getlist('products[]') != ['All Products'] else None
    }
    where_clause, params = _build_common_bill_filters(user_id, filters, base_alias='b')
    employees = request.args.getlist('employees[]')
    if employees and employees != ['All Employees']:
        emp_clause, emp_params = _build_employee_name_filter('b', employees, user_id)
        where_clause = f"{where_clause}{emp_clause}"
        params.extend(emp_params)
    query = f'''
        SELECT 
            b.bill_id,
            b.bill_number,
            b.bill_date,
            b.delivery_date,
            b.subtotal,
            b.vat_amount,
            b.total_amount,
            b.status,
            COALESCE(c.name, '') as customer_name
        FROM bills b
        LEFT JOIN customers c ON b.customer_id = c.customer_id
        WHERE {where_clause}
        ORDER BY b.bill_date DESC
        LIMIT 100
    '''
    cursor = execute_query(conn, query, params)
    rows = cursor.fetchall()
    invoices = []
    for r in rows:
        d = dict(r)
        bill_id = d.get('bill_id')
        discount_amounts, products_str = _get_bill_items_discount_and_products(conn, bill_id, user_id)
        d['discount_amounts'] = discount_amounts
        d['products'] = products_str
        invoices.append(d)
    conn.close()
    return jsonify({'success': True, 'invoices': invoices})

@reports_api.route('/api/invoice-summary', methods=['POST'])
@api_error_handler
def invoice_summary():
    user_id = get_current_user_id()
    data = request.get_json(silent=True) or {}
    filters = data.get('filters') or {}
    result = get_filtered_invoice_summary(user_id, filters)
    return jsonify(result)
@reports_api.route('/api/bills/<int:bill_id>/print', methods=['GET'])
def print_bill(bill_id):
    user_id = get_current_user_id()
    logger.info(f"DEBUG: print_bill called for bill_id: {bill_id}")
    
    conn = get_db_connection()
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'''
        SELECT b.*, c.name as customer_name, c.phone as customer_phone, 
               c.city as customer_city, c.area as customer_area,
               c.customer_type, c.business_name, c.business_address,
               e.name as master_name
        FROM bills b
        LEFT JOIN customers c ON b.customer_id = c.customer_id AND c.user_id = b.user_id
        LEFT JOIN employees e ON b.master_id = e.employee_id AND e.user_id = b.user_id
        WHERE b.bill_id = {placeholder} AND b.user_id = {placeholder}
    ''', (bill_id, user_id))
    bill = cursor.fetchone()
    
    if not bill:
        conn.close()
        return jsonify({'error': 'Bill not found'}), 404
    
    # Get shop settings first
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'SELECT * FROM shop_settings WHERE user_id = {placeholder}', (user_id,))
    shop_settings = cursor.fetchone()

    # Check if VAT should be recalculated for display
    # Default to True since user says prices include VAT
    shop_settings_dict = dict(shop_settings) if shop_settings else {}
    include_vat_in_price = bool(shop_settings_dict.get('include_vat_in_price', True))

    # Get bill items
    cursor = execute_query(conn, f'''
        SELECT * FROM bill_items WHERE bill_id = {placeholder} AND user_id = {placeholder}
    ''', (bill_id, user_id))
    items = cursor.fetchall()
    conn.close()

    # Calculate discount amount for each item and recalculate totals if needed
    items_with_discount = []
    for item in items:
        item_dict = dict(item)
        # Calculate discount amount: (rate * quantity * discount_percentage) / 100
        discount_amount = (float(item_dict['rate']) * float(item_dict['quantity']) * float(item_dict['discount'])) / 100
        item_dict['discount_amount'] = round(discount_amount, 2)

        # Recalculate item total based on include_vat_in_price setting
        if include_vat_in_price:
            # If VAT is included in price, item total is just discounted amount
            item_total = (float(item_dict['rate']) * float(item_dict['quantity'])) - discount_amount
            item_dict['total_amount'] = round(item_total, 2)
            item_dict['vat_amount'] = 0  # VAT already included

        items_with_discount.append(item_dict)
    
    bill = dict(bill)
    shop_settings = shop_settings_dict

    # Handle VAT calculation based on include_vat_in_price setting
    if include_vat_in_price:
        # For include_vat_in_price, ensure correct VAT calculation from total
        total_amount = float(bill.get('total_amount', 0))
        vat_rate = 0.05  # 5%
        bill['vat_amount'] = round(total_amount * vat_rate, 2)
        bill['subtotal'] = round(total_amount - bill['vat_amount'], 2)
    else:
        # Recalculate VAT for display
        actual_subtotal = sum(item['total_amount'] for item in items)
        vat_percent = 5.0
        # Recalculate VAT
        correct_vat_amount = actual_subtotal * (vat_percent / 100)
        correct_total_amount = actual_subtotal + correct_vat_amount
        advance_paid = float(bill.get('advance_paid') or bill.get('advance_payment') or 0)
        correct_balance_amount = correct_total_amount - advance_paid

        # Use corrected values
        bill['vat_amount'] = round(correct_vat_amount, 2)
        bill['total_amount'] = round(correct_total_amount, 2)
        bill['balance_amount'] = round(correct_balance_amount, 2)

    logger.info(f"DEBUG: Retrieved bill data: {bill}")
    logger.info(f"DEBUG: Bill notes from database: '{bill.get('notes')}'")
    logger.info(f"DEBUG: Notes type: {type(bill.get('notes'))}")
    logger.info(f"DEBUG: include_vat_in_price: {include_vat_in_price}")
    
    # Generate amount_in_words for the balance_amount
    try:
        amount = float(bill.get('balance_amount', 0))
        dirhams = int(amount)
        fils = int(round((amount - dirhams) * 100))
        if fils > 0:
            amount_in_words = f"{num2words(dirhams, lang='en').capitalize()} Dirhams and {num2words(fils, lang='en')} Fils Only"
        else:
            amount_in_words = f"{num2words(dirhams, lang='en').capitalize()} Dirhams Only"
        
        # Generate Arabic amount in words
        arabic_amount_in_words = number_to_arabic_words(amount)
    except Exception as e:
        # logger.info(f"DEBUG: Error calculating amount in words: {e}")
        amount_in_words = ''
        arabic_amount_in_words = ''

    # Generate QR code for FTA compliance
    try:
        seller_name = shop_settings.get('shop_name', 'Tajir')
        seller_trn = shop_settings.get('trn', 'N/A')
        invoice_number = bill.get('bill_number', 'N/A')
        timestamp = bill.get('bill_date', datetime.now().strftime('%Y-%m-%d'))
        total_with_vat = float(bill.get('total_amount', 0))
        vat_amount = float(bill.get('vat_amount', 0))
        
        qr_code_base64 = generate_zatca_qr_code(
            seller_name, seller_trn, invoice_number, timestamp, 
            total_with_vat, vat_amount
        )
    except Exception as e:
        logger.info(f"DEBUG: Error generating QR code: {e}")
        qr_code_base64 = None
    
    # Get summary data
    bill_date = bill.get('bill_date', datetime.now().date())
    if isinstance(bill_date, str):
        bill_date = datetime.strptime(bill_date, '%Y-%m-%d').date()
    summary_data = get_invoice_summary_data(user_id, bill_date)
    
    # Check if VAT should be displayed based on VAT amount
    # If VAT amount is 0, don't show VAT sections
    should_show_vat = bill.get('should_show_vat', bill.get('vat_amount', 0) > 0)
    
    # Get bill template setting from shop settings
    bill_template = shop_settings.get('bill_template', 'default')
    
    # Get currency information from shop settings
    currency_code = shop_settings.get('currency_code', 'AED')
    currency_symbol = shop_settings.get('currency_symbol', 'د.إ')
    
    # Choose template based on setting
    if bill_template == 'receipt':
        # For receipt template, redirect to the receipt route
        return redirect(f'/bills/{bill_id}/receipt')
    else:
        # Use default template
        return render_template('print_bill.html', 
                             bill=bill, 
                             items=items_with_discount,
                             amount_in_words=amount_in_words,
                             arabic_amount_in_words=arabic_amount_in_words,
                             qr_code_base64=qr_code_base64,
                             shop_settings=shop_settings,
                             summary_data=summary_data,
                             should_show_vat=should_show_vat,
                             include_vat_in_price=include_vat_in_price,
                             currency_code=currency_code,
                             currency_symbol=currency_symbol,
                             get_user_language=get_user_language,
                             get_translated_text=get_translated_text)

@reports_api.route('/bills/<int:bill_id>/receipt', methods=['GET'])
def print_receipt(bill_id):
    """Print bill using the receipt template."""
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        
        # Get bill details
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT b.*, c.name as customer_name, c.phone as customer_phone, c.city as customer_city, c.area as customer_area
            FROM bills b
            LEFT JOIN customers c ON b.customer_id = c.customer_id
            WHERE b.bill_id = {placeholder} AND b.user_id = {placeholder}
        ''', (bill_id, user_id))
        bill = cursor.fetchone()
        
        if not bill:
            conn.close()
            return "Bill not found", 404
        
        # Get bill items
        cursor = execute_query(conn, f'''
            SELECT * FROM bill_items WHERE bill_id = {placeholder} ORDER BY item_id
        ''', (bill_id,))
        items = cursor.fetchall()
        
        # Get shop settings
        cursor = execute_query(conn, f'''
            SELECT * FROM shop_settings WHERE user_id = {placeholder}
        ''', (user_id,))
        shop_settings = cursor.fetchone()
        
        conn.close()
        
        # Convert rows to dicts for safe access and pre-compute line totals
        bill = dict(bill)
        shop_settings = dict(shop_settings) if shop_settings else {}
        items_dicts = []
        for i in items:
            item = dict(i)
            try:
                rate = float(item.get('rate') or 0)
                qty = float(item.get('quantity') or 0)
                discount = float(item.get('discount') or 0)
            except Exception:
                rate = qty = discount = 0.0
            gross = rate * qty
            discount_amount = gross * discount / 100.0
            net_amount = gross - discount_amount
            item['rate_float'] = rate
            item['quantity_float'] = qty
            item['discount_float'] = discount
            item['gross_amount'] = round(gross, 2)
            item['discount_amount'] = round(discount_amount, 2)
            item['net_amount'] = round(net_amount, 2)
            items_dicts.append(item)
        items = items_dicts
        
        # Determine if VAT should be shown
        show_vat = bool(bill.get('should_show_vat', bill.get('vat_amount', 0) > 0))
        
        # Get currency symbol
        currency_symbol = "AED"
        # Include VAT in price flag from shop settings
        include_vat_in_price = bool(shop_settings.get('include_vat_in_price', False))
        
        # Calculate VAT percentage dynamically
        vat_percent = 0
        if bill.get('subtotal') and float(bill.get('subtotal')) > 0:
            vat_amount_val = float(bill.get('vat_amount', 0))
            subtotal_val = float(bill.get('subtotal', 0))
            vat_percent = (vat_amount_val / subtotal_val) * 100
        
        # Precompute monetary totals as floats to avoid Decimal/float mix
        try:
            gross_amount = round(float(bill.get('subtotal') or 0), 2)
        except Exception:
            gross_amount = 0.0
        try:
            discount_amount = round(float(bill.get('discount') or 0), 2)
        except Exception:
            discount_amount = 0.0
        total_before_tax = round(gross_amount - discount_amount, 2)
        try:
            tax_amount = round(float(bill.get('vat_amount') or 0), 2)
        except Exception:
            tax_amount = 0.0
        try:
            net_amount = round(float(bill.get('total_amount') or (total_before_tax + tax_amount)), 2)
        except Exception:
            net_amount = round(total_before_tax + tax_amount, 2)
        try:
            advance_paid = round(float(bill.get('advance_paid') or bill.get('advance_payment') or 0), 2)
        except Exception:
            advance_paid = 0.0
        change_amount = round(max(0.0, advance_paid - net_amount), 2)

        # Current date/time for template
        now = datetime.now()
        current_date = now.date()
        current_time = now
        # Bill date display
        bill_date = bill.get('bill_date', current_date)
        try:
            bill_date_display = bill_date.strftime('%d %b %Y')
        except Exception:
            bill_date_display = str(bill_date)

        # For receipt display, show net amount as integer (floor)
        net_amount_integer = int(math.floor(net_amount))

        # Distribute VAT across items when VAT is included in price
        total_net_no_vat = sum(i.get('net_amount', 0) for i in items)
        if bool(shop_settings.get('include_vat_in_price', False)) and total_net_no_vat > 0 and tax_amount > 0:
            for i in items:
                share = (i.get('net_amount', 0) / total_net_no_vat)
                i['display_amount'] = round(i.get('net_amount', 0) + tax_amount * share, 2)
        else:
            for i in items:
                i['display_amount'] = round(i.get('net_amount', 0), 2)

        # Generate QR code image (base64)
        qr_code_base64 = None
        try:
            import qrcode
            import base64
            from io import BytesIO
            payload = f"INV:{bill.get('bill_number','')}|DATE:{bill_date_display}|TOTAL:{net_amount:.2f}|VAT:{tax_amount:.2f}"
            img = qrcode.make(payload)
            buf = BytesIO()
            img.save(buf, format='PNG')
            qr_code_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        except Exception:
            pass

        return render_template('receipt_template.html',
                             bill=bill,
                             items=items,
                             shop_settings=shop_settings,
                             show_vat=show_vat,
                             currency_symbol=currency_symbol,
                             vat_percent=vat_percent,
                             current_date=current_date,
                             current_time=current_time,
                             bill_date_display=bill_date_display,
                             gross_amount=gross_amount,
                             discount_amount=discount_amount,
                             total_before_tax=total_before_tax,
                             tax_amount=tax_amount,
                             net_amount=net_amount,
                             net_amount_integer=net_amount_integer,
                             advance_paid=advance_paid,
                             change_amount=change_amount,
                             qr_code_base64=qr_code_base64,
                             include_vat_in_price=include_vat_in_price)
        
    except Exception as e:
        print(f"Error generating receipt: {e}")
        return "Error generating receipt", 500
