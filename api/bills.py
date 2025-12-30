from flask import Blueprint, request, jsonify, session
from db.connection import (
    get_db_connection,
    get_placeholder,
    execute_query,
    execute_update,
    execute_with_returning,
    get_db_integrity_error,
    is_postgresql,
)
from datetime import datetime
import time
import re
import uuid
import json

bills_api = Blueprint('bills_api', __name__, url_prefix='/api')

def get_current_user_id():
    user_id = session.get('user_id')
    if user_id is None:
        return 2
    return user_id

@bills_api.route('/bills', methods=['GET'])
def get_bills():
    user_id = get_current_user_id()
    bill_number = request.args.get('bill_number')
    conn = get_db_connection()
    placeholder = get_placeholder()
    if bill_number:
        cursor = execute_query(conn,
            f'SELECT * FROM bills WHERE bill_number = {placeholder} AND user_id = {placeholder}',
            (bill_number, user_id)
        )
        bills = cursor.fetchall()
    else:
        cursor = execute_query(conn, f'''
            SELECT b.*, c.name as customer_name 
            FROM bills b 
            LEFT JOIN customers c ON b.customer_id = c.customer_id AND c.user_id = b.user_id
            WHERE b.user_id = {placeholder}
            ORDER BY b.bill_date DESC, b.bill_id DESC
        ''', (user_id,))
        bills = cursor.fetchall()
    conn.close()
    return jsonify([dict(bill) for bill in bills])

@bills_api.route('/bills/<int:bill_id>', methods=['GET'])
def get_bill(bill_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'''
        SELECT b.*, c.name as customer_name, e.name as master_name
        FROM bills b 
        LEFT JOIN customers c ON b.customer_id = c.customer_id AND c.user_id = b.user_id
        LEFT JOIN employees e ON b.master_id = e.employee_id AND e.user_id = b.user_id
        WHERE b.bill_id = {placeholder} AND b.user_id = {placeholder}
    ''', (bill_id, user_id))
    bill = cursor.fetchone()
    if not bill:
        conn.close()
        return jsonify({'error': 'Bill not found'}), 404
    bill = dict(bill)
    cursor = execute_query(conn, f'''
        SELECT * FROM bill_items WHERE bill_id = {placeholder} AND user_id = {placeholder}
    ''', (bill_id, user_id))
    items = cursor.fetchall()
    conn.close()
    return jsonify({
        'bill': bill,
        'items': [dict(item) for item in items]
    })


@bills_api.route('/next-bill-number', methods=['GET'])
def get_next_bill_number():
    user_id = get_current_user_id()
    today = datetime.now().strftime('%Y%m%d')
    max_retries = 5
    for attempt in range(max_retries):
        try:
            conn = get_db_connection()
            placeholder = get_placeholder()
            cursor = execute_query(conn, f"""
                SELECT bill_number FROM bills WHERE bill_number LIKE {placeholder} AND user_id = {placeholder}
                ORDER BY bill_number DESC
            """, (f'BILL-{today}-%', user_id))
            bills = cursor.fetchall()
            max_seq = 0
            for b in bills:
                parts = b['bill_number'].split('-')
                if len(parts) == 3 and parts[1] == today and parts[2].isdigit():
                    seq = int(parts[2])
                    if seq > max_seq:
                        max_seq = seq
            next_seq = max_seq + 1
            bill_number = f'BILL-{today}-{next_seq:03d}'
            cursor = execute_query(conn, f"""
                SELECT COUNT(*) as count FROM bills WHERE bill_number = {placeholder} AND user_id = {placeholder}
            """, (bill_number, user_id))
            existing = cursor.fetchone()
            conn.close()
            if (existing['count'] if isinstance(existing, dict) else existing[0]) == 0:
                return jsonify({'next_number': bill_number})
            else:
                max_seq += 1
                next_seq = max_seq + 1
                bill_number = f'BILL-{today}-{next_seq:03d}'
                return jsonify({'next_number': bill_number})
        except Exception:
            if attempt == max_retries - 1:
                timestamp = int(time.time() * 1000) % 10000
                bill_number = f'BILL-{today}-{timestamp:04d}'
                return jsonify({'next_number': bill_number})
            time.sleep(0.1)

@bills_api.route('/bills', methods=['POST'])
def create_bill():
    user_id = get_current_user_id()
    conn = None
    if is_postgresql():
        try:
            temp_conn = get_db_connection()
            execute_query(temp_conn, "SELECT setval(pg_get_serial_sequence('bills','bill_id'), COALESCE((SELECT MAX(bill_id) FROM bills),0)+1, false)")
            execute_query(temp_conn, "SELECT setval(pg_get_serial_sequence('bill_items','item_id'), COALESCE((SELECT MAX(item_id) FROM bill_items),0)+1, false)")
            temp_conn.close()
        except Exception:
            pass
    try:
        if request.is_json:
            data = request.get_json()
            bill_data = data.get('bill', {})
            items_data = data.get('items', [])
            notes = bill_data.get('notes', '').strip()
            if not items_data:
                return jsonify({'error': 'At least one item is required'}), 400
            customer_phone = (bill_data.get('customer_phone') or '').strip()
            if not customer_phone:
                return jsonify({'error': 'Customer mobile is required'}), 400
            country_code = (bill_data.get('country_code') or '').strip()
            if country_code:
                country_code = re.sub(r'\D', '', country_code)
            if country_code and customer_phone:
                clean_phone = re.sub(r'\D', '', customer_phone)
                if clean_phone.startswith(country_code):
                    clean_phone = clean_phone[len(country_code):]
                full_phone = f"+{country_code}{clean_phone}"
            else:
                full_phone = re.sub(r'\D', '', customer_phone)
            master_id = bill_data.get('master_id')
            if not master_id:
                try:
                    conn = get_db_connection()
                    placeholder = get_placeholder()
                    cursor = execute_query(conn, f'SELECT employee_id FROM employees WHERE user_id = {placeholder} AND is_active = TRUE ORDER BY name LIMIT 1', (user_id,))
                    default_employee = cursor.fetchone()
                    conn.close()
                    if default_employee:
                        master_id = default_employee['employee_id']
                except Exception:
                    master_id = None
            conn = get_db_connection()
            placeholder = get_placeholder()
            cursor = execute_query(conn, f'SELECT include_vat_in_price FROM shop_settings WHERE user_id = {placeholder}', (user_id,))
            shop_settings = cursor.fetchone()
            include_vat_in_price = bool(shop_settings['include_vat_in_price']) if shop_settings and 'include_vat_in_price' in shop_settings else True
            subtotal = float(bill_data.get('subtotal', 0))
            vat_amount = float(bill_data.get('vat_amount', 0))
            total_amount = float(bill_data.get('total_amount', 0))
            advance_paid = float(bill_data.get('advance_paid', 0))
            balance_amount = float(bill_data.get('balance_amount', 0))
            vat_percent = 5.0
            if include_vat_in_price:
                total_including_vat = subtotal
                vat_rate = vat_percent / 100
                correct_subtotal = total_including_vat / (1 + vat_rate)
                correct_vat_amount = total_including_vat - correct_subtotal
                correct_total_amount = total_including_vat
                correct_balance_amount = correct_total_amount - advance_paid
                subtotal = round(correct_subtotal, 2)
            else:
                vat_rate = vat_percent / 100
                correct_vat_amount = subtotal * vat_rate
                correct_total_amount = subtotal + correct_vat_amount
                correct_balance_amount = correct_total_amount - advance_paid
            vat_amount = round(correct_vat_amount, 2)
            total_amount = round(correct_total_amount, 2)
            balance_amount = round(correct_balance_amount, 2)
            status = 'Paid' if abs(balance_amount) < 0.01 else ('Partial' if advance_paid > 0 else 'Pending')
            conn = get_db_connection()
            cursor = execute_query(conn,
                f'SELECT customer_id FROM customers WHERE phone = {placeholder} AND user_id = {placeholder}',
                (full_phone, user_id)
            )
            existing_customer = cursor.fetchone()
            if existing_customer:
                customer_id = existing_customer['customer_id']
            else:
                sql = f'''
                    INSERT INTO customers (user_id, name, phone, trn, city, area, customer_type, business_name, business_address)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                    ON CONFLICT (user_id, phone) DO UPDATE SET
                        name = EXCLUDED.name,
                        trn = EXCLUDED.trn,
                        city = EXCLUDED.city,
                        area = EXCLUDED.area,
                        customer_type = EXCLUDED.customer_type,
                        business_name = EXCLUDED.business_name,
                        business_address = EXCLUDED.business_address
                    RETURNING customer_id
                '''
                customer_id = execute_with_returning(conn, sql, (
                    user_id, bill_data.get('customer_name', ''),
                    full_phone,
                    bill_data.get('customer_trn', ''),
                    bill_data.get('customer_city', ''),
                    bill_data.get('customer_area', ''),
                    bill_data.get('customer_type', 'Individual'),
                    bill_data.get('business_name', ''),
                    bill_data.get('business_address', '')
                ))
                try:
                    import random
                    import string
                    referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    execute_update(conn, f'''
                        INSERT INTO customer_loyalty (
                            user_id, customer_id, tier_level, referral_code, 
                            total_points, available_points, lifetime_points, join_date, is_active
                        ) VALUES ({placeholder}, {placeholder}, 'Bronze', {placeholder}, 
                                 0, 0, 0, CURRENT_DATE, true)
                    ''', (user_id, customer_id, referral_code))
                except Exception:
                    pass
            bill_uuid = str(uuid.uuid4())
            max_retries = 3
            bill_created = False
            for attempt in range(max_retries):
                try:
                    bill_number = bill_data.get('bill_number', '').strip()
                    if not bill_number or attempt > 0:
                        today = datetime.now().strftime('%Y%m%d')
                        timestamp = int(time.time() * 1000) % 10000
                        bill_number = f'BILL-{today}-{timestamp:04d}'
                    if is_postgresql():
                        try:
                            execute_update(conn, "CREATE UNIQUE INDEX IF NOT EXISTS uniq_bills_user_billno ON bills(user_id, bill_number)")
                        except Exception:
                            pass
                        sql = f'''
                            INSERT INTO bills (
                                user_id, bill_number, customer_id, customer_name, customer_phone, 
                                customer_city, customer_area, customer_trn, customer_type, business_name, business_address,
                                uuid, bill_date, delivery_date, payment_method, subtotal, vat_amount, total_amount, 
                                advance_paid, balance_amount, status, master_id, trial_date, notes
                            ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                        '''
                        bill_date = bill_data.get('bill_date', '').strip() or datetime.now().strftime('%Y-%m-%d')
                        delivery_date = bill_data.get('delivery_date', '').strip() or datetime.now().strftime('%Y-%m-%d')
                        trial_date = bill_data.get('trial_date', '').strip() or datetime.now().strftime('%Y-%m-%d')
                        execute_update(conn, sql, (
                            user_id, bill_number, customer_id, bill_data.get('customer_name'),
                            full_phone,
                            bill_data.get('customer_city'),
                            bill_data.get('customer_area'), bill_data.get('customer_trn', ''),
                            bill_data.get('customer_type', 'Individual'), bill_data.get('business_name', ''),
                            bill_data.get('business_address', ''), bill_uuid, bill_date,
                            delivery_date, bill_data.get('payment_method', 'Cash'),
                            subtotal, vat_amount, total_amount, advance_paid, balance_amount,
                            status, master_id, trial_date, notes
                        ))
                        cur = execute_query(conn, f"SELECT bill_id FROM bills WHERE user_id = {placeholder} AND bill_number = {placeholder}", (user_id, bill_number))
                        exist = cur.fetchone()
                        bill_id = exist['bill_id'] if isinstance(exist, dict) else exist[0]
                        bill_created = True
                    else:
                        sql = f'''
                            INSERT OR IGNORE INTO bills (
                                user_id, bill_number, customer_id, customer_name, customer_phone, 
                                customer_city, customer_area, uuid, bill_date, delivery_date, 
                                payment_method, subtotal, vat_amount, total_amount, 
                                advance_paid, balance_amount, status, master_id, trial_date, notes
                            ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                        '''
                        execute_update(conn, sql, (
                            user_id, bill_number, customer_id, bill_data.get('customer_name'), full_phone,
                            bill_data.get('customer_city'), bill_data.get('customer_area'), bill_uuid, bill_data.get('bill_date', datetime.now().strftime('%Y-%m-%d')),
                            bill_data.get('delivery_date', datetime.now().strftime('%Y-%m-%d')), bill_data.get('payment_method', 'Cash'),
                            subtotal, vat_amount, total_amount, advance_paid, balance_amount, status, master_id, bill_data.get('trial_date', datetime.now().strftime('%Y-%m-%d')), notes
                        ))
                        cur = execute_query(conn, f"SELECT bill_id FROM bills WHERE user_id = {placeholder} AND bill_number = {placeholder}", (user_id, bill_number))
                        exist = cur.fetchone()
                        bill_id = exist['bill_id'] if isinstance(exist, dict) else exist[0]
                        bill_created = True
                    break
                except get_db_integrity_error() as e:
                    conn.rollback()
                    if "UNIQUE constraint failed: bills.user_id, bills.bill_number" in str(e):
                        if attempt == max_retries - 1:
                            conn.close()
                            return jsonify({'error': 'Failed to create bill due to duplicate bill number. Please try again.'}), 500
                        continue
                    elif "bills_pkey" in str(e) or "duplicate key value violates unique constraint \"bills_pkey\"" in str(e):
                        try:
                            execute_query(conn, "SELECT setval(pg_get_serial_sequence('bills','bill_id'), COALESCE((SELECT MAX(bill_id) FROM bills),0)+1, false)")
                            execute_query(conn, "SELECT setval(pg_get_serial_sequence('bill_items','item_id'), COALESCE((SELECT MAX(item_id) FROM bill_items),0)+1, false)")
                        except Exception:
                            pass
                        continue
                    else:
                        conn.close()
                        return jsonify({'error': f'Database error: {str(e)}'}), 500
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    conn.rollback()
                    conn.close()
                    return jsonify({'error': f'Error creating bill: {str(e)}'}), 500
            if not bill_created:
                conn.rollback()
                conn.close()
                return jsonify({'error': 'Failed to create bill after multiple attempts'}), 500
            try:
                execute_query(conn, "SELECT setval(pg_get_serial_sequence('bill_items','item_id'), COALESCE((SELECT MAX(item_id) FROM bill_items),0)+1, false)")
            except Exception:
                pass
            for item in items_data:
                item_rate = float(item.get('rate', 0))
                item_quantity = float(item.get('quantity', 1))
                item_discount_percent = float(item.get('discount', 0))
                item_subtotal_before_discount = item_rate * item_quantity
                item_discount_amount = item_subtotal_before_discount * (item_discount_percent / 100)
                item_subtotal = item_subtotal_before_discount - item_discount_amount
                if include_vat_in_price:
                    item_vat_amount = 0
                    item_total_amount = item_subtotal
                else:
                    item_vat_amount = item_subtotal * (vat_percent / 100)
                    item_total_amount = item_subtotal + item_vat_amount
                sql = f'''
                INSERT INTO bill_items (
                    user_id, bill_id, product_id, product_name, notes, quantity,
                    rate, discount, vat_amount, advance_paid, total_amount
                ) SELECT {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}
                WHERE NOT EXISTS (
                    SELECT 1 FROM bill_items
                    WHERE bill_id = {placeholder} AND product_id = {placeholder} AND product_name = {placeholder} AND rate = {placeholder} AND quantity = {placeholder}
                )
            '''
                execute_with_returning(conn, sql, (
                    user_id, bill_id,
                    item.get('product_id'),
                    item.get('product_name'),
                    item.get('notes', ''),
                    item.get('quantity', 1),
                    item.get('rate', 0),
                    item_discount_percent,
                    item_vat_amount,
                    item.get('advance_paid', 0),
                    item_total_amount,
                    bill_id, item.get('product_id'), item.get('product_name'), item.get('rate', 0), item.get('quantity', 1)
                ))
            loyalty_points_earned = 0
            if customer_id:
                try:
                    cursor = execute_query(conn, f'''
                        SELECT cl.customer_id, cl.tier_level, cl.available_points,
                               lc.points_per_aed
                        FROM customer_loyalty cl
                        LEFT JOIN loyalty_config lc ON cl.user_id = lc.user_id
                        WHERE cl.user_id = {placeholder} AND cl.customer_id = {placeholder}
                    ''', (user_id, customer_id))
                    loyalty_info = cursor.fetchone()
                    if loyalty_info and loyalty_info['customer_id']:
                        points_per_aed = float(loyalty_info['points_per_aed'] or 1.0)
                        loyalty_points_earned = int(total_amount * points_per_aed)
                        cursor = execute_query(conn, f'''
                            SELECT bonus_points_multiplier FROM loyalty_tiers 
                            WHERE user_id = {placeholder} AND tier_level = {placeholder}
                        ''', (user_id, loyalty_info['tier_level']))
                        tier_info = cursor.fetchone()
                        if tier_info:
                            multiplier = float(tier_info['bonus_points_multiplier'] or 1.0)
                            loyalty_points_earned = int(loyalty_points_earned * multiplier)
                        execute_update(conn, f'''
                            INSERT INTO loyalty_transactions (
                                user_id, customer_id, bill_id, points_earned, 
                                transaction_type, description
                            ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, 'earned', {placeholder})
                        ''', (
                            user_id, 
                            customer_id, 
                            bill_id, 
                            loyalty_points_earned,
                            f'Points earned from bill #{bill_number}'
                        ))
                        new_available_points = loyalty_info['available_points'] + loyalty_points_earned
                        execute_update(conn, f'''
                            UPDATE customer_loyalty SET 
                                available_points = {placeholder},
                                total_points = total_points + {placeholder},
                                last_purchase_date = CURRENT_DATE,
                                total_purchases = total_purchases + 1,
                                total_spent = total_spent + {placeholder}
                            WHERE customer_id = {placeholder}
                        ''', (
                            new_available_points,
                            loyalty_points_earned,
                            total_amount,
                            loyalty_info['customer_id']
                        ))
                except Exception:
                    pass
            return jsonify({
                'success': True, 
                'bill_id': bill_id,
                'bill_number': bill_number,
                'loyalty_points_earned': loyalty_points_earned
            })
        else:
            loyalty_points_earned = 0
            customer_name = request.form.get('customer_name', '').strip()
            customer_phone = request.form.get('customer_phone', '').strip()
            country_code = request.form.get('country_code', '').strip()
            if country_code and customer_phone:
                clean_phone = re.sub(r'\D', '', customer_phone)
                if clean_phone.startswith(country_code):
                    clean_phone = clean_phone[len(country_code):]
                full_phone = f"+{country_code}{clean_phone}"
            else:
                full_phone = re.sub(r'\D', '', customer_phone)
            customer_city = request.form.get('customer_city', '').strip()
            customer_area = request.form.get('customer_area', '').strip()
            bill_date = request.form.get('bill_date', '')
            delivery_date = request.form.get('delivery_date', '')
            trial_date = request.form.get('trial_date', '') or None
            payment_method = request.form.get('payment_method', 'Cash')
            master_id = request.form.get('master_id', '') or None
            notes = request.form.get('notes', '').strip()
            items_data = request.form.get('items', '[]')
            items = json.loads(items_data) if items_data else []
            if not items:
                return jsonify({'error': 'At least one item is required'}), 400
            if not customer_phone:
                return jsonify({'error': 'Customer mobile is required'}), 400
            subtotal_before_discount = sum(float(item.get('rate', 0)) * float(item.get('quantity', 1)) for item in items)
            total_discount_amount = 0
            for item in items:
                item_rate = float(item.get('rate', 0))
                item_quantity = float(item.get('quantity', 1))
                item_discount_percent = float(item.get('discount', 0))
                item_discount_amount = (item_rate * item_quantity) * (item_discount_percent / 100)
                total_discount_amount += item_discount_amount
            subtotal = subtotal_before_discount - total_discount_amount
            vat_percent = 5.0
            vat_amount = subtotal * (vat_percent / 100)
            total_amount = subtotal + vat_amount
            advance_paid = float(request.form.get('advance_paid', 0))
            balance_amount = total_amount - advance_paid
            status = 'Paid' if abs(balance_amount) < 0.01 else ('Partial' if advance_paid > 0 else 'Pending')
            conn = get_db_connection()
            placeholder = get_placeholder()
            cursor = execute_query(conn,
                f"""
                SELECT customer_id FROM customers 
                WHERE user_id = {placeholder} AND 
                      REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(phone, ' ', ''), '-', ''), '(', ''), ')', ''), '+', '') = {placeholder}
                """,
                (user_id, re.sub(r'\D', '', full_phone))
            )
            existing_customer = cursor.fetchone()
            if existing_customer:
                customer_id = existing_customer['customer_id']
            else:
                sql = f'''
                    INSERT INTO customers (user_id, name, phone, city, area) 
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                    ON CONFLICT (user_id, phone) DO UPDATE SET
                        name = EXCLUDED.name,
                        city = EXCLUDED.city,
                        area = EXCLUDED.area
                    RETURNING customer_id
                '''
                customer_id = execute_with_returning(conn, sql, (user_id, customer_name, full_phone, customer_city, customer_area))
            bill_uuid = str(uuid.uuid4())
            max_retries = 3
            bill_created = False
            for attempt in range(max_retries):
                try:
                    bill_number = request.form.get('bill_number', '').strip()
                    if not bill_number or attempt > 0:
                        today = datetime.now().strftime('%Y%m%d')
                        timestamp = int(time.time() * 1000) % 10000
                        bill_number = f'BILL-{today}-{timestamp:04d}'
                    if is_postgresql():
                        try:
                            execute_update(conn, "CREATE UNIQUE INDEX IF NOT EXISTS uniq_bills_user_billno ON bills(user_id, bill_number)")
                        except Exception:
                            pass
                        sql = f'''
                            INSERT INTO bills (
                                user_id, bill_number, customer_id, customer_name, customer_phone, 
                                customer_city, customer_area, uuid, bill_date, delivery_date, 
                                payment_method, subtotal, vat_amount, total_amount, 
                                advance_paid, balance_amount, status, master_id, trial_date, notes
                            ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                            ON CONFLICT (user_id, bill_number) DO NOTHING
                            RETURNING bill_id
                        '''
                        cur = execute_query(conn, sql, (
                            user_id, bill_number, customer_id, customer_name, full_phone,
                            customer_city, customer_area, bill_uuid, bill_date, delivery_date,
                            payment_method, subtotal, vat_amount, total_amount,
                            advance_paid, balance_amount, status, master_id, trial_date, notes
                        ))
                        row = cur.fetchone()
                        if row:
                            bill_id = row['bill_id'] if isinstance(row, dict) else row[0]
                            bill_created = True
                        else:
                            cur = execute_query(conn, f"SELECT bill_id FROM bills WHERE user_id = {placeholder} AND bill_number = {placeholder}", (user_id, bill_number))
                            exist = cur.fetchone()
                            bill_id = exist['bill_id'] if isinstance(exist, dict) else exist[0]
                            bill_created = False
                    else:
                        sql = f'''
                            INSERT OR IGNORE INTO bills (
                                user_id, bill_number, customer_id, customer_name, customer_phone, 
                                customer_city, customer_area, uuid, bill_date, delivery_date, 
                                payment_method, subtotal, vat_amount, total_amount, 
                                advance_paid, balance_amount, status, master_id, trial_date, notes
                            ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                        '''
                        execute_update(conn, sql, (
                            user_id, bill_number, customer_id, customer_name, full_phone,
                            customer_city, customer_area, bill_uuid, bill_date, delivery_date,
                            payment_method, subtotal, vat_amount, total_amount,
                            advance_paid, balance_amount, status, master_id, trial_date, notes
                        ))
                        cur = execute_query(conn, f"SELECT bill_id FROM bills WHERE user_id = {placeholder} AND bill_number = {placeholder}", (user_id, bill_number))
                        exist = cur.fetchone()
                        bill_id = exist['bill_id'] if isinstance(exist, dict) else exist[0]
                        bill_created = True
                    bill_created = True
                    break
                except get_db_integrity_error() as e:
                    conn.rollback()
                    if "UNIQUE constraint failed: bills.user_id, bills.bill_number" in str(e):
                        if attempt == max_retries - 1:
                            conn.close()
                            return jsonify({'error': 'Failed to create bill due to duplicate bill number. Please try again.'}), 500
                        continue
                    elif "bills_pkey" in str(e) or "duplicate key value violates unique constraint \"bills_pkey\"" in str(e):
                        try:
                            execute_query(conn, "SELECT setval(pg_get_serial_sequence('bills','bill_id'), COALESCE((SELECT MAX(bill_id) FROM bills),0)+1, false)")
                            execute_query(conn, "SELECT setval(pg_get_serial_sequence('bill_items','id'), COALESCE((SELECT MAX(id) FROM bill_items),0)+1, false)")
                        except Exception:
                            pass
                        continue
                    else:
                        conn.close()
                        return jsonify({'error': f'Database error: {str(e)}'}), 500
                except Exception as e:
                    conn.rollback()
                    conn.close()
                    return jsonify({'error': f'Error creating bill: {str(e)}'}), 500
            if not bill_created:
                conn.rollback()
                conn.close()
                return jsonify({'error': 'Failed to create bill after multiple attempts'}), 500
            vat_percent = 5.0
            for item in items:
                item_rate = float(item.get('rate', 0))
                item_quantity = float(item.get('quantity', 1))
                item_discount_percent = float(item.get('discount', 0))
                item_subtotal_before_discount = item_rate * item_quantity
                item_discount_amount = item_subtotal_before_discount * (item_discount_percent / 100)
                item_subtotal = item_subtotal_before_discount - item_discount_amount
                item_vat_amount = item_subtotal * (vat_percent / 100)
                item_total_amount = item_subtotal + item_vat_amount
                sql = f'''
                    INSERT INTO bill_items (bill_id, product_name, quantity, rate, discount, vat_amount, advance_paid, total_amount)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                '''
                execute_with_returning(conn, sql, (
                    bill_id, item.get('product_name', ''), 
                    item.get('quantity', 1), item.get('rate', 0),
                    item_discount_percent, item_vat_amount, item.get('advance_paid', 0), item_total_amount
                ))
            return jsonify({
                'success': True, 
                'bill_id': bill_id,
                'bill_number': bill_number,
                'loyalty_points_earned': loyalty_points_earned
            })
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

@bills_api.route('/bills/<int:bill_id>', methods=['DELETE'])
def delete_bill(bill_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    execute_update(conn, f'DELETE FROM bill_items WHERE bill_id = {placeholder} AND user_id = {placeholder}', (bill_id, user_id))
    execute_update(conn, f'DELETE FROM bills WHERE bill_id = {placeholder} AND user_id = {placeholder}', (bill_id, user_id))
    conn.close()
    return jsonify({'message': 'Bill deleted successfully'})

@bills_api.route('/bills/<int:bill_id>/payment', methods=['PUT'])
def update_bill_payment(bill_id):
    user_id = get_current_user_id()
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
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'SELECT advance_paid, balance_amount, total_amount FROM bills WHERE bill_id = {placeholder} AND user_id = {placeholder}', (bill_id, user_id))
    bill = cursor.fetchone()
    if not bill:
        conn.close()
        return jsonify({'error': 'Bill not found.'}), 404
    new_advance = float(bill['advance_paid']) + amount_paid
    new_balance = float(bill['total_amount']) - new_advance
    new_status = 'Paid' if abs(new_balance) < 0.01 else 'Partial'
    if new_balance < 0:
        conn.close()
        return jsonify({'error': 'Payment exceeds total amount.'}), 400
    sql = f'UPDATE bills SET advance_paid = {placeholder}, balance_amount = {placeholder}, status = {placeholder} WHERE bill_id = {placeholder} AND user_id = {placeholder}'
    execute_update(conn, sql, (new_advance, new_balance, new_status, bill_id, user_id))
    cursor = execute_query(conn, f'SELECT * FROM bills WHERE bill_id = {placeholder} AND user_id = {placeholder}', (bill_id, user_id))
    updated = cursor.fetchone()
    conn.close()
    return jsonify({'bill': dict(updated)})
