from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import os
from datetime import datetime, date
import json
from decimal import Decimal
import dropbox
import zipfile
from io import BytesIO
from dotenv import load_dotenv
load_dotenv()
from num2words import num2words

app = Flask(__name__)
app.config['DATABASE'] = 'pos_tailor.db'

DROPBOX_ACCESS_TOKEN = os.getenv('DROPBOX_ACCESS_TOKEN')

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    need_init = False
    if not os.path.exists(app.config['DATABASE']):
        need_init = True
    else:
        # Check if main tables are empty
        conn = get_db_connection()
        try:
            cur = conn.execute("SELECT COUNT(*) FROM product_types")
            if cur.fetchone()[0] == 0:
                need_init = True
        except Exception:
            # Table doesn't exist, need to initialize
            need_init = True
        conn.close()
    if need_init:
        with open('database_schema.sql', 'r') as f:
            schema = f.read()
        conn = get_db_connection()
        conn.executescript(schema)
        conn.commit()
        conn.close()
        print("Database initialized successfully!")

@app.route('/')
def index():
    return render_template('index.html')

# Product Types API
@app.route('/api/product-types', methods=['GET'])
def get_product_types():
    conn = get_db_connection()
    types = conn.execute('SELECT * FROM product_types ORDER BY type_name').fetchall()
    conn.close()
    return jsonify([dict(type) for type in types])

@app.route('/api/product-types', methods=['POST'])
def add_product_type():
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': 'Type name is required'}), 400
    
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO product_types (type_name) VALUES (?)', (name,))
        conn.commit()
        type_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()
        return jsonify({'id': type_id, 'name': name, 'message': 'Product type added successfully'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Product type already exists'}), 400

@app.route('/api/product-types/<int:type_id>', methods=['DELETE'])
def delete_product_type(type_id):
    conn = get_db_connection()
    # Check if products exist for this type
    products = conn.execute('SELECT COUNT(*) FROM products WHERE type_id = ?', (type_id,)).fetchone()[0]
    if products > 0:
        conn.close()
        return jsonify({'error': 'Cannot delete type with existing products'}), 400
    
    conn.execute('DELETE FROM product_types WHERE type_id = ?', (type_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Product type deleted successfully'})

# Products API
@app.route('/api/products', methods=['GET'])
def get_products():
    search = request.args.get('search', '').strip()
    conn = get_db_connection()
    if search:
        like_search = f"%{search}%"
        products = conn.execute('''
            SELECT p.*, pt.type_name 
            FROM products p 
            JOIN product_types pt ON p.type_id = pt.type_id 
            WHERE p.is_active = 1 AND (p.product_name LIKE ? OR pt.type_name LIKE ?)
            ORDER BY pt.type_name, p.product_name
        ''', (like_search, like_search)).fetchall()
    else:
        products = conn.execute('''
            SELECT p.*, pt.type_name 
            FROM products p 
            JOIN product_types pt ON p.type_id = pt.type_id 
            WHERE p.is_active = 1 
            ORDER BY pt.type_name, p.product_name
        ''').fetchall()
    conn.close()
    return jsonify([dict(product) for product in products])

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.get_json()
    type_id = data.get('type_id')
    name = data.get('name', '').strip()
    rate = data.get('rate')
    description = data.get('description', '').strip()
    
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
        conn.execute('''
            INSERT INTO products (type_id, product_name, rate, description) 
            VALUES (?, ?, ?, ?)
        ''', (type_id, name, rate, description))
        conn.commit()
        product_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()
        return jsonify({'id': product_id, 'message': 'Product added successfully'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Product already exists'}), 400

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    name = data.get('name', '').strip()
    rate = data.get('rate')
    description = data.get('description', '').strip()
    
    if not all([name, rate]):
        return jsonify({'error': 'Name and rate are required'}), 400
    
    try:
        rate = float(rate)
        if rate <= 0:
            return jsonify({'error': 'Rate must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid rate value'}), 400
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE products 
        SET product_name = ?, rate = ?, description = ? 
        WHERE product_id = ?
    ''', (name, rate, description, product_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Product updated successfully'})

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = get_db_connection()
    conn.execute('UPDATE products SET is_active = 0 WHERE product_id = ?', (product_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Product deleted successfully'})

# Customers API
@app.route('/api/customers', methods=['GET'])
def get_customers():
    phone = request.args.get('phone')
    search = request.args.get('search', '').strip()
    conn = get_db_connection()
    if phone:
        customers = conn.execute('SELECT * FROM customers WHERE phone = ?', (phone,)).fetchall()
    elif search:
        like_search = f"%{search}%"
        customers = conn.execute('SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? ORDER BY name', (like_search, like_search)).fetchall()
    else:
        customers = conn.execute('SELECT * FROM customers ORDER BY name').fetchall()
    conn.close()
    return jsonify([dict(customer) for customer in customers])

@app.route('/api/customers', methods=['POST'])
def add_customer():
    data = request.get_json()
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    city = data.get('city', '').strip()
    area = data.get('area', '').strip()
    email = data.get('email', '').strip()
    address = data.get('address', '').strip()
    
    if not name:
        return jsonify({'error': 'Customer name is required'}), 400
    
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO customers (name, phone, city, area, email, address) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, phone, city, area, email, address))
        conn.commit()
        customer_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()
        return jsonify({'id': customer_id, 'message': 'Customer added successfully'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Phone number already exists'}), 400

@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.get_json()
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    city = data.get('city', '').strip()
    area = data.get('area', '').strip()
    email = data.get('email', '').strip()
    address = data.get('address', '').strip()
    
    if not name:
        return jsonify({'error': 'Customer name is required'}), 400
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE customers 
        SET name = ?, phone = ?, city = ?, area = ?, email = ?, address = ? 
        WHERE customer_id = ?
    ''', (name, phone, city, area, email, address, customer_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Customer updated successfully'})

@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM customers WHERE customer_id = ?', (customer_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Customer deleted successfully'})

# VAT Rates API
@app.route('/api/vat-rates', methods=['GET'])
def get_vat_rates():
    conn = get_db_connection()
    rates = conn.execute('SELECT * FROM vat_rates WHERE is_active = 1 ORDER BY effective_from DESC').fetchall()
    conn.close()
    return jsonify([dict(rate) for rate in rates])

@app.route('/api/vat-rates', methods=['POST'])
def add_vat_rate():
    data = request.get_json()
    rate_percentage = data.get('rate_percentage')
    effective_from = data.get('effective_from')
    effective_to = data.get('effective_to')
    
    if not all([rate_percentage, effective_from, effective_to]):
        return jsonify({'error': 'Rate percentage and dates are required'}), 400
    
    try:
        rate_percentage = float(rate_percentage)
        if rate_percentage < 0:
            return jsonify({'error': 'Rate percentage must be non-negative'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid rate percentage'}), 400
    
    conn = get_db_connection()
    # Check for duplicate effective_from and effective_to
    exists = conn.execute(
        'SELECT 1 FROM vat_rates WHERE effective_from = ? AND effective_to = ? AND is_active = 1',
        (effective_from, effective_to)
    ).fetchone()
    if exists:
        conn.close()
        return jsonify({'error': 'A VAT rate with the same effective dates already exists.'}), 400
    # Update previous active row's effective_to if needed
    prev = conn.execute('SELECT vat_id, effective_to FROM vat_rates WHERE is_active = 1 ORDER BY effective_from DESC LIMIT 1').fetchone()
    if prev and prev['effective_to'] == '2099-12-31':
        from datetime import datetime, timedelta
        prev_to = (datetime.strptime(effective_from, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
        conn.execute('UPDATE vat_rates SET effective_to = ? WHERE vat_id = ?', (prev_to, prev['vat_id']))
    conn.execute('''
        INSERT INTO vat_rates (rate_percentage, effective_from, effective_to) 
        VALUES (?, ?, ?)
    ''', (rate_percentage, effective_from, effective_to))
    conn.commit()
    vat_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.close()
    return jsonify({'id': vat_id, 'message': 'VAT rate added successfully'})

@app.route('/api/vat-rates/<int:vat_id>', methods=['DELETE'])
def delete_vat_rate(vat_id):
    conn = get_db_connection()
    conn.execute('UPDATE vat_rates SET is_active = 0 WHERE vat_id = ?', (vat_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'VAT rate deleted successfully'})

# Bills API
@app.route('/api/bills', methods=['GET'])
def get_bills():
    bill_number = request.args.get('bill_number')
    conn = get_db_connection()
    if bill_number:
        bills = conn.execute(
            'SELECT * FROM bills WHERE bill_number = ?',
            (bill_number,)
        ).fetchall()
    else:
        bills = conn.execute('''
            SELECT b.*, c.name as customer_name 
            FROM bills b 
            LEFT JOIN customers c ON b.customer_id = c.customer_id 
            ORDER BY b.bill_date DESC, b.bill_id DESC
        ''').fetchall()
    conn.close()
    return jsonify([dict(bill) for bill in bills])

@app.route('/api/bills', methods=['POST'])
def create_bill():
    data = request.get_json()
    
    # Extract bill data
    bill_data = data.get('bill', {})
    items_data = data.get('items', [])
    
    if not items_data:
        return jsonify({'error': 'At least one item is required'}), 400
    
    # Require master_id (Master Name)
    if not bill_data.get('master_id'):
        return jsonify({'error': 'Master Name is required.'}), 400
    
    conn = get_db_connection()
    try:
        # Insert bill
        conn.execute('''
            INSERT INTO bills (
                bill_number, customer_id, customer_name, customer_phone, 
                customer_city, customer_area, bill_date, delivery_date, 
                payment_method, subtotal, vat_amount, total_amount, 
                advance_paid, balance_amount, master_id, trial_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            bill_data.get('bill_number'),
            bill_data.get('customer_id'),
            bill_data.get('customer_name'),
            bill_data.get('customer_phone'),
            bill_data.get('customer_city'),
            bill_data.get('customer_area'),
            bill_data.get('bill_date'),
            bill_data.get('delivery_date'),
            bill_data.get('payment_method', 'Cash'),
            bill_data.get('subtotal', 0),
            bill_data.get('vat_amount', 0),
            bill_data.get('total_amount', 0),
            bill_data.get('advance_paid', 0),
            bill_data.get('balance_amount', 0),
            bill_data.get('master_id'),
            bill_data.get('trial_date')
        ))
        
        bill_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        
        # Insert bill items
        for item in items_data:
            conn.execute('''
                INSERT INTO bill_items (
                    bill_id, product_id, product_name, quantity, 
                    rate, discount, advance_paid, total_amount
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                bill_id,
                item.get('product_id'),
                item.get('product_name'),
                item.get('quantity', 1),
                item.get('rate', 0),
                item.get('discount', 0),
                item.get('advance_paid', 0),
                item.get('total_amount', 0)
            ))
        
        conn.commit()
        conn.close()
        return jsonify({'id': bill_id, 'message': 'Bill created successfully'})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/bills/<int:bill_id>', methods=['GET'])
def get_bill(bill_id):
    conn = get_db_connection()
    
    # Get bill details
    bill = conn.execute('''
        SELECT b.*, c.name as customer_name, e.name as master_name
        FROM bills b 
        LEFT JOIN customers c ON b.customer_id = c.customer_id 
        LEFT JOIN employees e ON b.master_id = e.employee_id
        WHERE b.bill_id = ?
    ''', (bill_id,)).fetchone()
    
    if not bill:
        conn.close()
        return jsonify({'error': 'Bill not found'}), 404
    
    # Get bill items
    items = conn.execute('''
        SELECT * FROM bill_items WHERE bill_id = ?
    ''', (bill_id,)).fetchall()
    
    conn.close()
    
    return jsonify({
        'bill': dict(bill),
        'items': [dict(item) for item in items]
    })

@app.route('/api/bills/<int:bill_id>', methods=['DELETE'])
def delete_bill(bill_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM bill_items WHERE bill_id = ?', (bill_id,))
    conn.execute('DELETE FROM bills WHERE bill_id = ?', (bill_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Bill deleted successfully'})

@app.route('/api/bills/<int:bill_id>/payment', methods=['PUT'])
def update_bill_payment(bill_id):
    data = request.get_json()
    amount_paid = data.get('amount_paid')
    if amount_paid is None:
        return jsonify({'error': 'Amount paid is required.'}), 400
    try:
        amount_paid = float(amount_paid)
        if amount_paid <= 0:
            return jsonify({'error': 'Amount must be positive.'}), 400
    except Exception:
        return jsonify({'error': 'Invalid amount.'}), 400
    conn = get_db_connection()
    bill = conn.execute('SELECT advance_paid, balance_amount, total_amount FROM bills WHERE bill_id = ?', (bill_id,)).fetchone()
    if not bill:
        conn.close()
        return jsonify({'error': 'Bill not found.'}), 404
    new_advance = float(bill['advance_paid']) + amount_paid
    new_balance = float(bill['total_amount']) - new_advance
    new_status = 'Paid' if abs(new_balance) < 0.01 else 'Partial'
    if new_balance < 0:
        conn.close()
        return jsonify({'error': 'Payment exceeds total amount.'}), 400
    conn.execute('UPDATE bills SET advance_paid = ?, balance_amount = ?, status = ? WHERE bill_id = ?', (new_advance, new_balance, new_status, bill_id))
    conn.commit()
    updated = conn.execute('SELECT * FROM bills WHERE bill_id = ?', (bill_id,)).fetchone()
    conn.close()
    return jsonify({'bill': dict(updated)})

# Dashboard API
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    conn = get_db_connection()
    
    # Get total revenue
    total_revenue = conn.execute('''
        SELECT COALESCE(SUM(total_amount), 0) as total 
        FROM bills 
        WHERE DATE(bill_date) = DATE('now')
    ''').fetchone()['total']
    
    # Get total bills today
    total_bills_today = conn.execute('''
        SELECT COUNT(*) as count 
        FROM bills 
        WHERE DATE(bill_date) = DATE('now')
    ''').fetchone()['count']
    
    # Get pending bills
    pending_bills = conn.execute('''
        SELECT COUNT(*) as count 
        FROM bills 
        WHERE status = 'Pending'
    ''').fetchone()['count']
    
    # Get total customers
    total_customers = conn.execute('SELECT COUNT(*) as count FROM customers').fetchone()['count']
    
    # Get monthly revenue data
    monthly_revenue = conn.execute('''
        SELECT strftime('%Y-%m', bill_date) as month, 
               SUM(total_amount) as revenue
        FROM bills 
        WHERE bill_date >= date('now', '-6 months')
        GROUP BY strftime('%Y-%m', bill_date)
        ORDER BY month
    ''').fetchall()

    # Top 10 regions by sales (for pie chart)
    top_regions = conn.execute('''
        SELECT COALESCE(customer_area, 'Unknown') as area, SUM(total_amount) as sales
        FROM bills
        WHERE customer_area IS NOT NULL AND customer_area != ''
        GROUP BY customer_area
        ORDER BY sales DESC
        LIMIT 10
    ''').fetchall()

    # Top 10 trending products (by quantity sold)
    trending_products = conn.execute('''
        SELECT COALESCE(product_name, 'Unknown') as product_name, 
               SUM(quantity) as qty_sold,
               SUM(total_amount) as total_revenue
        FROM bill_items
        WHERE product_name IS NOT NULL AND product_name != ''
        GROUP BY product_name
        ORDER BY qty_sold DESC
        LIMIT 10
    ''').fetchall()

    # Top 10 most repeated customers (by invoice count)
    repeated_customers = conn.execute('''
        SELECT COALESCE(customer_name, 'Unknown') as customer_name, 
               COALESCE(customer_phone, '') as customer_phone, 
               COUNT(*) as invoice_count,
               SUM(total_amount) as total_revenue
        FROM bills
        WHERE customer_name IS NOT NULL AND customer_name != ''
        GROUP BY customer_name, customer_phone
        ORDER BY invoice_count DESC
        LIMIT 10
    ''').fetchall()

    conn.close()
    
    return jsonify({
        'total_revenue': float(total_revenue),
        'total_bills_today': total_bills_today,
        'pending_bills': pending_bills,
        'total_customers': total_customers,
        'monthly_revenue': [dict(item) for item in monthly_revenue],
        'top_regions': [dict(item) for item in top_regions],
        'trending_products': [dict(item) for item in trending_products],
        'repeated_customers': [dict(item) for item in repeated_customers]
    })

# Print bill
@app.route('/api/bills/<int:bill_id>/print', methods=['GET'])
def print_bill(bill_id):
    conn = get_db_connection()
    # Get bill details, join with employees for master_name
    bill = conn.execute('''
        SELECT b.*, c.name as customer_name, c.phone as customer_phone, e.name as master_name
        FROM bills b 
        LEFT JOIN customers c ON b.customer_id = c.customer_id 
        LEFT JOIN employees e ON b.master_id = e.employee_id
        WHERE b.bill_id = ?
    ''', (bill_id,)).fetchone()
    if not bill:
        conn.close()
        return jsonify({'error': 'Bill not found'}), 404
    # Get bill items
    items = conn.execute('''
        SELECT * FROM bill_items WHERE bill_id = ?
    ''', (bill_id,)).fetchall()
    conn.close()
    bill = dict(bill)
    # Generate amount_in_words for the balance_amount
    try:
        amount = float(bill.get('balance_amount', 0))
        dirhams = int(amount)
        fils = int(round((amount - dirhams) * 100))
        if fils > 0:
            amount_in_words = f"{num2words(dirhams, lang='en').capitalize()} Dirhams and {num2words(fils, lang='en')} Fils Only"
        else:
            amount_in_words = f"{num2words(dirhams, lang='en').capitalize()} Dirhams Only"
    except Exception:
        amount_in_words = ''
    bill['amount_in_words'] = amount_in_words
    return render_template('print_bill.html', 
                         bill=bill, 
                         items=[dict(item) for item in items])

@app.route('/api/customer-invoice-heatmap', methods=['GET'])
def customer_invoice_heatmap():
    conn = get_db_connection()
    # Get last 6 months (including current)
    months = [row['month'] for row in conn.execute("""
        SELECT DISTINCT strftime('%Y-%m', bill_date) as month
        FROM bills
        WHERE bill_date >= date('now', '-5 months', 'start of month')
        ORDER BY month ASC
    """).fetchall()]

    # Get customers with at least one invoice in the last 6 months
    customers = conn.execute("""
        SELECT c.customer_id, c.name, COUNT(b.bill_id) as total_invoices
        FROM customers c
        JOIN bills b ON c.customer_id = b.customer_id
        WHERE b.bill_date >= date('now', '-5 months', 'start of month')
        GROUP BY c.customer_id, c.name
        ORDER BY total_invoices DESC
    """).fetchall()
    customer_ids = [row['customer_id'] for row in customers]
    customer_names = [row['name'] for row in customers]

    # Build matrix: rows=customers, cols=months
    matrix = []
    for cid in customer_ids:
        row = []
        for m in months:
            count = conn.execute("""
                SELECT COUNT(*) FROM bills
                WHERE customer_id = ? AND strftime('%Y-%m', bill_date) = ?
            """, (cid, m)).fetchone()[0]
            row.append(count)
        matrix.append(row)
    conn.close()
    return jsonify({
        'customers': customer_names,
        'months': months,
        'matrix': matrix
    })

@app.route('/api/areas', methods=['GET'])
def get_areas():
    conn = get_db_connection()
    areas = conn.execute('SELECT area_name FROM city_area ORDER BY area_name').fetchall()
    conn.close()
    return jsonify([row['area_name'] for row in areas])

@app.route('/api/cities', methods=['GET'])
def get_cities():
    conn = get_db_connection()
    cities = conn.execute('SELECT city_name FROM cities ORDER BY city_name').fetchall()
    conn.close()
    return jsonify([row['city_name'] for row in cities])

# Employees API
@app.route('/api/employees', methods=['GET'])
def get_employees():
    conn = get_db_connection()
    employees = conn.execute('SELECT * FROM employees ORDER BY name').fetchall()
    conn.close()
    return jsonify([dict(emp) for emp in employees])

@app.route('/api/employees', methods=['POST'])
def add_employee():
    data = request.get_json()
    name = data.get('name', '').strip()
    mobile = data.get('mobile', '').strip()
    address = data.get('address', '').strip()
    if not name:
        return jsonify({'error': 'Employee name is required'}), 400
    conn = get_db_connection()
    conn.execute('INSERT INTO employees (name, mobile, address) VALUES (?, ?, ?)', (name, mobile, address))
    conn.commit()
    emp_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.close()
    return jsonify({'id': emp_id, 'message': 'Employee added successfully'})

@app.route('/api/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    data = request.get_json()
    name = data.get('name', '').strip()
    mobile = data.get('mobile', '').strip()
    address = data.get('address', '').strip()
    if not name:
        return jsonify({'error': 'Employee name is required'}), 400
    conn = get_db_connection()
    conn.execute('UPDATE employees SET name = ?, mobile = ?, address = ? WHERE employee_id = ?', (name, mobile, address, employee_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Employee updated successfully'})

@app.route('/api/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM employees WHERE employee_id = ?', (employee_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Employee deleted successfully'})

@app.route('/api/next-bill-number', methods=['GET'])
def get_next_bill_number():
    today = datetime.now().strftime('%Y%m%d')
    conn = get_db_connection()
    # Find all bills for today with the new format
    bills = conn.execute("""
        SELECT bill_number FROM bills WHERE bill_number LIKE ?
    """, (f'BILL-{today}-%',)).fetchall()
    conn.close()
    max_seq = 0
    for b in bills:
        parts = b['bill_number'].split('-')
        if len(parts) == 3 and parts[1] == today and parts[2].isdigit():
            seq = int(parts[2])
            if seq > max_seq:
                max_seq = seq
    next_seq = max_seq + 1
    bill_number = f'BILL-{today}-{next_seq:03d}'
    return jsonify({'bill_number': bill_number})

@app.route('/api/employee-analytics', methods=['GET'])
def employee_analytics():
    conn = get_db_connection()
    # Top 5 employees by revenue
    top5 = conn.execute('''
        SELECT e.name, COALESCE(SUM(b.total_amount), 0) as total_revenue
        FROM employees e
        LEFT JOIN bills b ON e.employee_id = b.master_id
        GROUP BY e.employee_id
        ORDER BY total_revenue DESC
        LIMIT 5
    ''').fetchall()
    # Revenue share for all employees
    shares = conn.execute('''
        SELECT e.name, COALESCE(SUM(b.total_amount), 0) as total_revenue
        FROM employees e
        LEFT JOIN bills b ON e.employee_id = b.master_id
        GROUP BY e.employee_id
        ORDER BY total_revenue DESC
    ''').fetchall()
    conn.close()
    return jsonify({
        'top5': [dict(row) for row in top5],
        'shares': [dict(row) for row in shares]
    })

# Helper: zip the database file in memory
def zip_db():
    mem_zip = BytesIO()
    with zipfile.ZipFile(mem_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write('pos_tailor.db', arcname='pos_tailor.db')
    mem_zip.seek(0)
    return mem_zip

# Helper: get Dropbox client
def get_dbx():
    return dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

# Helper: prune to last 7 backups
def prune_dropbox_backups(dbx, folder='/'):
    files = dbx.files_list_folder(folder).entries
    backups = sorted([f for f in files if f.name.startswith('pos_tailor_') and f.name.endswith('.db.zip')], key=lambda f: f.client_modified, reverse=True)
    for f in backups[7:]:
        dbx.files_delete_v2(f.path_lower)

@app.route('/api/backup/upload', methods=['POST'])
def backup_upload():
    dbx = get_dbx()
    today = datetime.now().strftime('%Y%m%d')
    filename = f'/pos_tailor_{today}.db.zip'
    mem_zip = zip_db()
    try:
        dbx.files_upload(mem_zip.read(), filename, mode=dropbox.files.WriteMode.overwrite)
        prune_dropbox_backups(dbx)
        return jsonify({'message': 'Backup uploaded to Dropbox.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backups', methods=['GET'])
def list_backups():
    dbx = get_dbx()
    try:
        files = dbx.files_list_folder('').entries
        backups = sorted([f for f in files if f.name.startswith('pos_tailor_') and f.name.endswith('.db.zip')], key=lambda f: f.client_modified, reverse=True)
        result = [
            {
                'name': f.name,
                'date': f.client_modified.strftime('%Y-%m-%d'),
                'path': f.path_lower
            } for f in backups[:7]
        ]
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backup/download/<filename>', methods=['GET'])
def download_backup(filename):
    dbx = get_dbx()
    path = f'/{filename}'
    try:
        md, res = dbx.files_download(path)
        return send_file(BytesIO(res.content), download_name=filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backup/restore/<filename>', methods=['POST'])
def restore_backup(filename):
    dbx = get_dbx()
    path = f'/{filename}'
    try:
        md, res = dbx.files_download(path)
        # Unzip and replace local db
        with zipfile.ZipFile(BytesIO(res.content)) as zf:
            zf.extract('pos_tailor.db', path='.')
        return jsonify({'message': f'Restored {filename} from Dropbox.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000) 