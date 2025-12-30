from flask import Blueprint, request, jsonify, session
from db.connection import (
    get_db_connection,
    get_placeholder,
    execute_query,
    execute_update,
    execute_with_returning,
)
from api.utils import log_user_action

shop_settings_api = Blueprint('shop_settings_api', __name__, url_prefix='/api')

def get_current_user_id():
    user_id = session.get('user_id')
    if user_id is None:
        return 2
    return user_id

@shop_settings_api.route('/vat-rates', methods=['GET'])
def get_vat_rates():
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'SELECT * FROM vat_rates WHERE user_id = {placeholder} AND is_active = TRUE ORDER BY effective_from DESC', (user_id,))
    rates = cursor.fetchall()
    conn.close()
    return jsonify([dict(rate) for rate in rates])

@shop_settings_api.route('/vat-rates', methods=['POST'])
def add_vat_rate():
    data = request.get_json()
    rate_percentage = data.get('rate_percentage')
    effective_from = data.get('effective_from')
    effective_to = data.get('effective_to')
    user_id = get_current_user_id()
    if not all([rate_percentage, effective_from, effective_to]):
        return jsonify({'error': 'Rate percentage and dates are required'}), 400
    try:
        rate_percentage = float(rate_percentage)
        if rate_percentage < 0:
            return jsonify({'error': 'Rate percentage must be non-negative'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid rate percentage'}), 400
    conn = get_db_connection()
    placeholder = get_placeholder()
    cursor = execute_query(conn,
        f'SELECT 1 FROM vat_rates WHERE user_id = {placeholder} AND effective_from = {placeholder} AND effective_to = {placeholder} AND is_active = TRUE',
        (user_id, effective_from, effective_to)
    )
    exists = cursor.fetchone()
    if exists:
        conn.close()
        return jsonify({'error': 'A VAT rate with the same effective dates already exists.'}), 400
    cursor = execute_query(conn, f'SELECT vat_id, effective_to FROM vat_rates WHERE user_id = {placeholder} AND is_active = TRUE ORDER BY effective_from DESC LIMIT 1', (user_id,))
    prev = cursor.fetchone()
    if prev and prev['effective_to'] == '2099-12-31':
        from datetime import datetime, timedelta
        prev_to = (datetime.strptime(effective_from, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
        placeholder = get_placeholder()
        execute_update(conn, f'UPDATE vat_rates SET effective_to = {placeholder} WHERE vat_id = {placeholder} AND user_id = {placeholder}', (prev_to, prev['vat_id'], user_id))
    placeholder = get_placeholder()
    sql = f'''
        INSERT INTO vat_rates (user_id, rate_percentage, effective_from, effective_to) 
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
    '''
    vat_id = execute_with_returning(conn, sql, (user_id, rate_percentage, effective_from, effective_to))
    conn.close()
    return jsonify({'id': vat_id, 'message': 'VAT rate added successfully'})

@shop_settings_api.route('/vat-rates/<int:vat_id>', methods=['DELETE'])
def delete_vat_rate(vat_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    is_active_value = 'FALSE'
    execute_update(conn, f'UPDATE vat_rates SET is_active = {is_active_value} WHERE vat_id = {placeholder} AND user_id = {placeholder}', (vat_id, user_id))
    conn.close()
    return jsonify({'message': 'VAT rate deleted successfully'})

@shop_settings_api.route('/areas', methods=['GET'])
def get_areas():
    city = request.args.get('city', '').strip()
    conn = get_db_connection()
    if city:
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT ca.area_name 
            FROM city_area ca 
            JOIN cities c ON ca.city_id = c.city_id 
            WHERE c.city_name = {placeholder} 
            ORDER BY ca.area_name
        ''', (city,))
        areas = cursor.fetchall()
    else:
        cursor = execute_query(conn, 'SELECT area_name FROM city_area ORDER BY area_name')
        areas = cursor.fetchall()
    conn.close()
    return jsonify([row['area_name'] for row in areas])

@shop_settings_api.route('/cities', methods=['GET'])
def get_cities():
    area = request.args.get('area', '').strip()
    conn = get_db_connection()
    if area:
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT DISTINCT c.city_name 
            FROM cities c 
            JOIN city_area ca ON c.city_id = ca.city_id 
            WHERE ca.area_name = {placeholder} 
            ORDER BY c.city_name
        ''', (area,))
        cities = cursor.fetchall()
    else:
        cursor = execute_query(conn, 'SELECT city_name FROM cities ORDER BY city_name')
        cities = cursor.fetchall()
    conn.close()
    return jsonify([row['city_name'] for row in cities])

@shop_settings_api.route('/backups', methods=['GET'])
def list_backups():
    return jsonify([])

@shop_settings_api.route('/backup/download/<filename>', methods=['GET'])
def download_backup(filename):
    return jsonify({'error': 'Dropbox backup functionality has been removed.'}), 501

@shop_settings_api.route('/backup/upload', methods=['POST'])
def backup_upload():
    return jsonify({'error': 'Dropbox backup functionality has been removed.'}), 501

@shop_settings_api.route('/backup/restore/<filename>', methods=['POST'])
def restore_backup(filename):
    return jsonify({'error': 'Dropbox backup functionality has been removed.'}), 501

@shop_settings_api.route('/shop-settings', methods=['GET'])
def get_shop_settings():
    """Get current shop settings."""
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT * FROM shop_settings WHERE user_id = {placeholder}', (user_id,))
        settings = cursor.fetchone()
        conn.close()
        
        if settings:
            return jsonify({
                'success': True,
                'settings': dict(settings)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Shop settings not found'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@shop_settings_api.route('/shop-settings/payment-mode', methods=['GET'])
def get_payment_mode():
    """Get payment mode setting for the current user."""
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT payment_mode FROM shop_settings WHERE user_id = {placeholder}', (user_id,))
        settings = cursor.fetchone()
        conn.close()
        
        payment_mode = settings['payment_mode'] if settings else 'advance'
        return jsonify({
            'success': True,
            'payment_mode': payment_mode
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'payment_mode': 'advance'  # Default fallback
        }), 500

@shop_settings_api.route('/shop-settings/billing-config', methods=['GET'])
def get_billing_config():
    """Get billing field configuration for the current user."""
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT enable_trial_date, enable_delivery_date, enable_advance_payment, 
                   enable_customer_notes, enable_employee_assignment, default_delivery_days, default_trial_days, default_employee_id, include_vat_in_price, bill_template
            FROM shop_settings WHERE user_id = {placeholder}
        ''', (user_id,))
        settings = cursor.fetchone()
        conn.close()
        
        if settings:
            config = {
                'enable_trial_date': bool(settings['enable_trial_date']),
                'enable_delivery_date': bool(settings['enable_delivery_date']),
                'enable_advance_payment': bool(settings['enable_advance_payment']),
                'enable_customer_notes': bool(settings['enable_customer_notes']),
                'enable_employee_assignment': bool(settings['enable_employee_assignment']),
                'default_delivery_days': int(settings['default_delivery_days']),
                'default_trial_days': int(settings['default_trial_days']) if 'default_trial_days' in settings.keys() else 3,
                'default_employee_id': settings['default_employee_id'],
                'include_vat_in_price': bool(settings['include_vat_in_price']) if 'include_vat_in_price' in settings.keys() else True,
                'bill_template': settings['bill_template'] if 'bill_template' in settings.keys() else 'default'
            }
        else:
            # Default configuration
            config = {
                'enable_trial_date': True,
                'enable_delivery_date': True,
                'enable_advance_payment': True,
                'enable_customer_notes': True,
                'enable_employee_assignment': True,
                'default_delivery_days': 3,
                'default_trial_days': 3,
                'default_employee_id': None,
                'include_vat_in_price': True,
                'bill_template': 'default'
            }
        
        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'config': {
                'enable_trial_date': True,
                'enable_delivery_date': True,
                'enable_advance_payment': True,
                'enable_customer_notes': True,
                'enable_employee_assignment': True,
                'default_delivery_days': 3,
                'default_trial_days': 3,
                'default_employee_id': None,
                'include_vat_in_price': False
            }
        }), 500

@shop_settings_api.route('/shop-settings/vat-config', methods=['PUT'])
def update_vat_config():
    """Update only VAT-related settings without affecting other shop settings."""
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        include_vat_in_price = data.get('include_vat_in_price', False)
        bill_template = data.get('bill_template', 'default')
        
        conn = get_db_connection()
        
        # Check if shop settings exist for this user
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT setting_id FROM shop_settings WHERE user_id = {placeholder}', (user_id,))
        existing_settings = cursor.fetchone()
        
        if existing_settings:
            # Update only the include_vat_in_price field
            placeholder = get_placeholder()
            execute_update(conn, f'''
                UPDATE shop_settings 
                SET include_vat_in_price = {placeholder}, bill_template = {placeholder}, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = {placeholder}
            ''', (include_vat_in_price, bill_template, user_id))
        else:
            # Create new shop settings with only VAT config
            placeholder = get_placeholder()
            execute_update(conn, f'''
                INSERT INTO shop_settings (user_id, include_vat_in_price, bill_template)
                VALUES ({placeholder}, {placeholder}, {placeholder})
            ''', (user_id, include_vat_in_price, bill_template))
        
        conn.close()
        
        return jsonify({'success': True, 'message': 'VAT configuration updated successfully'})
        
    except Exception as e:
        print(f"Error updating VAT config: {e}")
        return jsonify({'error': 'Failed to update VAT configuration'}), 500

@shop_settings_api.route('/shop-settings', methods=['PUT'])
def update_shop_settings():
    """Update shop settings."""
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        shop_name = data.get('shop_name', '')
        address = data.get('address', '')
        trn = data.get('trn', '')
        city = data.get('city', '')
        area = data.get('area', '')
        logo_url = data.get('logo_url', '')
        shop_mobile = data.get('shop_mobile', '')
        working_hours = data.get('working_hours', '')
        invoice_static_info = data.get('invoice_static_info', '')
        use_dynamic_invoice_template = data.get('use_dynamic_invoice_template', False)
        payment_mode = data.get('payment_mode', 'advance')
        
        # Configurable input fields
        enable_trial_date = data.get('enable_trial_date', False)
        enable_delivery_date = data.get('enable_delivery_date', False)
        enable_advance_payment = data.get('enable_advance_payment', False)
        enable_customer_notes = data.get('enable_customer_notes', False)
        enable_employee_assignment = data.get('enable_employee_assignment', False)
        default_delivery_days = data.get('default_delivery_days', 3)
        default_trial_days = data.get('default_trial_days', 3)
        default_employee_id = data.get('default_employee_id')
        include_vat_in_price = data.get('include_vat_in_price', False)
        
        # Convert to proper types
        try:
            default_delivery_days = int(default_delivery_days) if default_delivery_days else 3
        except (ValueError, TypeError):
            default_delivery_days = 3
            
        try:
            default_trial_days = int(default_trial_days) if default_trial_days else 3
        except (ValueError, TypeError):
            default_trial_days = 3
            
        if default_employee_id == '' or default_employee_id is None:
            default_employee_id = None
        else:
            try:
                default_employee_id = int(default_employee_id)
            except (ValueError, TypeError):
                default_employee_id = None
        
        # Currency and timezone settings
        currency_code = data.get('currency_code', 'AED')
        currency_symbol = data.get('currency_symbol', 'د.إ')
        timezone = data.get('timezone', 'Asia/Dubai')
        date_format = data.get('date_format', 'DD/MM/YYYY')
        time_format = data.get('time_format', '24h')
        
        conn = get_db_connection()
        
        # Check if shop settings exist for this user
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT setting_id FROM shop_settings WHERE user_id = {placeholder}', (user_id,))
        existing_settings = cursor.fetchone()
        
        if existing_settings:
            # Update existing shop settings
            placeholder = get_placeholder()
            execute_update(conn, f'''
                UPDATE shop_settings 
                SET shop_name = {placeholder}, address = {placeholder}, trn = {placeholder}, city = {placeholder}, area = {placeholder}, logo_url = {placeholder}, 
                    shop_mobile = {placeholder}, working_hours = {placeholder}, invoice_static_info = {placeholder},
                    use_dynamic_invoice_template = {placeholder}, payment_mode = {placeholder}, 
                    enable_trial_date = {placeholder}, enable_delivery_date = {placeholder}, enable_advance_payment = {placeholder},
                    enable_customer_notes = {placeholder}, enable_employee_assignment = {placeholder}, default_delivery_days = {placeholder}, default_trial_days = {placeholder}, default_employee_id = {placeholder},
                    include_vat_in_price = {placeholder},
                    currency_code = {placeholder}, currency_symbol = {placeholder}, timezone = {placeholder}, date_format = {placeholder}, time_format = {placeholder},
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = {placeholder}
            ''', (shop_name, address, trn, city, area, logo_url, shop_mobile, working_hours, 
                  invoice_static_info, use_dynamic_invoice_template, payment_mode,
                  enable_trial_date, enable_delivery_date, enable_advance_payment,
                  enable_customer_notes, enable_employee_assignment, default_delivery_days, default_trial_days, default_employee_id,
                  include_vat_in_price,
                  currency_code, currency_symbol, timezone, date_format, time_format, user_id))
        else:
            # Create new shop settings for this user
            placeholder = get_placeholder()
            execute_update(conn, f'''
                INSERT INTO shop_settings (user_id, shop_name, address, trn, city, area, logo_url, 
                    shop_mobile, working_hours, invoice_static_info, use_dynamic_invoice_template, payment_mode,
                    enable_trial_date, enable_delivery_date, enable_advance_payment,
                    enable_customer_notes, enable_employee_assignment, default_delivery_days, default_trial_days, default_employee_id,
                    include_vat_in_price,
                    currency_code, currency_symbol, timezone, date_format, time_format)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, 
                    {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, 
                    {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder},
                    {placeholder},
                    {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            ''', (user_id, shop_name, address, trn, city, area, logo_url, shop_mobile, working_hours, 
                  invoice_static_info, use_dynamic_invoice_template, payment_mode,
                  enable_trial_date, enable_delivery_date, enable_advance_payment,
                  enable_customer_notes, enable_employee_assignment, default_delivery_days, default_trial_days, default_employee_id,
                  include_vat_in_price,
                  currency_code, currency_symbol, timezone, date_format, time_format))
        conn.close()
        
        # Log shop settings update
        log_user_action("UPDATE_SHOP_SETTINGS", user_id, {
            'shop_name': shop_name,
            'trn': trn,
            'address': address
        })
        
        return jsonify({'success': True, 'message': 'Shop settings updated successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@shop_settings_api.route('/currencies', methods=['GET'])
def get_currencies():
    """Get list of supported currencies."""
    currencies = {
        'AED': {'code': 'AED', 'symbol': 'د.إ', 'name': 'UAE Dirham', 'region': 'UAE'},
        'USD': {'code': 'USD', 'symbol': '$', 'name': 'US Dollar', 'region': 'USA'},
        'EUR': {'code': 'EUR', 'symbol': '€', 'name': 'Euro', 'region': 'Europe'},
        'GBP': {'code': 'GBP', 'symbol': '£', 'name': 'British Pound', 'region': 'UK'},
        'CAD': {'code': 'CAD', 'symbol': 'C$', 'name': 'Canadian Dollar', 'region': 'Canada'},
        'AUD': {'code': 'AUD', 'symbol': 'A$', 'name': 'Australian Dollar', 'region': 'Australia'},
        'INR': {'code': 'INR', 'symbol': '₹', 'name': 'Indian Rupee', 'region': 'India'},
        'SAR': {'code': 'SAR', 'symbol': '﷼', 'name': 'Saudi Riyal', 'region': 'Saudi Arabia'},
        'QAR': {'code': 'QAR', 'symbol': '﷼', 'name': 'Qatari Riyal', 'region': 'Qatar'},
        'KWD': {'code': 'KWD', 'symbol': 'د.ك', 'name': 'Kuwaiti Dinar', 'region': 'Kuwait'},
        'BHD': {'code': 'BHD', 'symbol': 'د.ب', 'name': 'Bahraini Dinar', 'region': 'Bahrain'},
        'OMR': {'code': 'OMR', 'symbol': '﷼', 'name': 'Omani Rial', 'region': 'Oman'},
        'JPY': {'code': 'JPY', 'symbol': '¥', 'name': 'Japanese Yen', 'region': 'Japan'},
        'CNY': {'code': 'CNY', 'symbol': '¥', 'name': 'Chinese Yuan', 'region': 'China'},
        'SGD': {'code': 'SGD', 'symbol': 'S$', 'name': 'Singapore Dollar', 'region': 'Singapore'},
        'MYR': {'code': 'MYR', 'symbol': 'RM', 'name': 'Malaysian Ringgit', 'region': 'Malaysia'},
        'THB': {'code': 'THB', 'symbol': '฿', 'name': 'Thai Baht', 'region': 'Thailand'},
        'PHP': {'code': 'PHP', 'symbol': '₱', 'name': 'Philippine Peso', 'region': 'Philippines'},
        'IDR': {'code': 'IDR', 'symbol': 'Rp', 'name': 'Indonesian Rupiah', 'region': 'Indonesia'},
        'VND': {'code': 'VND', 'symbol': '₫', 'name': 'Vietnamese Dong', 'region': 'Vietnam'},
        'KRW': {'code': 'KRW', 'symbol': '₩', 'name': 'South Korean Won', 'region': 'South Korea'},
        'TRY': {'code': 'TRY', 'symbol': '₺', 'name': 'Turkish Lira', 'region': 'Turkey'},
        'RUB': {'code': 'RUB', 'symbol': '₽', 'name': 'Russian Ruble', 'region': 'Russia'},
        'ZAR': {'code': 'ZAR', 'symbol': 'R', 'name': 'South African Rand', 'region': 'South Africa'},
        'BRL': {'code': 'BRL', 'symbol': 'R$', 'name': 'Brazilian Real', 'region': 'Brazil'},
        'MXN': {'code': 'MXN', 'symbol': '$', 'name': 'Mexican Peso', 'region': 'Mexico'},
        'ARS': {'code': 'ARS', 'symbol': '$', 'name': 'Argentine Peso', 'region': 'Argentina'},
        'CLP': {'code': 'CLP', 'symbol': '$', 'name': 'Chilean Peso', 'region': 'Chile'},
        'COP': {'code': 'COP', 'symbol': '$', 'name': 'Colombian Peso', 'region': 'Colombia'},
        'PEN': {'code': 'PEN', 'symbol': 'S/', 'name': 'Peruvian Sol', 'region': 'Peru'},
        'UYU': {'code': 'UYU', 'symbol': '$', 'name': 'Uruguayan Peso', 'region': 'Uruguay'},
        'EGP': {'code': 'EGP', 'symbol': '£', 'name': 'Egyptian Pound', 'region': 'Egypt'},
        'MAD': {'code': 'MAD', 'symbol': 'د.م.', 'name': 'Moroccan Dirham', 'region': 'Morocco'},
        'TND': {'code': 'TND', 'symbol': 'د.ت', 'name': 'Tunisian Dinar', 'region': 'Tunisia'},
        'DZD': {'code': 'DZD', 'symbol': 'د.ج', 'name': 'Algerian Dinar', 'region': 'Algeria'},
        'LYD': {'code': 'LYD', 'symbol': 'ل.د', 'name': 'Libyan Dinar', 'region': 'Libya'},
        'JOD': {'code': 'JOD', 'symbol': 'د.ا', 'name': 'Jordanian Dinar', 'region': 'Jordan'},
        'LBP': {'code': 'LBP', 'symbol': 'ل.ل', 'name': 'Lebanese Pound', 'region': 'Lebanon'},
        'ILS': {'code': 'ILS', 'symbol': '₪', 'name': 'Israeli Shekel', 'region': 'Israel'},
        'PKR': {'code': 'PKR', 'symbol': '₨', 'name': 'Pakistani Rupee', 'region': 'Pakistan'},
        'BDT': {'code': 'BDT', 'symbol': '৳', 'name': 'Bangladeshi Taka', 'region': 'Bangladesh'},
        'LKR': {'code': 'LKR', 'symbol': '₨', 'name': 'Sri Lankan Rupee', 'region': 'Sri Lanka'},
        'NPR': {'code': 'NPR', 'symbol': '₨', 'name': 'Nepalese Rupee', 'region': 'Nepal'},
        'AFN': {'code': 'AFN', 'symbol': '؋', 'name': 'Afghan Afghani', 'region': 'Afghanistan'},
        'IRR': {'code': 'IRR', 'symbol': '﷼', 'name': 'Iranian Rial', 'region': 'Iran'},
        'IQD': {'code': 'IQD', 'symbol': 'د.ع', 'name': 'Iraqi Dinar', 'region': 'Iraq'},
        'YER': {'code': 'YER', 'symbol': '﷼', 'name': 'Yemeni Rial', 'region': 'Yemen'},
        'SYP': {'code': 'SYP', 'symbol': '£', 'name': 'Syrian Pound', 'region': 'Syria'},
        'NGN': {'code': 'NGN', 'symbol': '₦', 'name': 'Nigerian Naira', 'region': 'Nigeria'},
        'KES': {'code': 'KES', 'symbol': 'KSh', 'name': 'Kenyan Shilling', 'region': 'Kenya'},
        'UGX': {'code': 'UGX', 'symbol': 'USh', 'name': 'Ugandan Shilling', 'region': 'Uganda'},
        'TZS': {'code': 'TZS', 'symbol': 'TSh', 'name': 'Tanzanian Shilling', 'region': 'Tanzania'},
        'ETB': {'code': 'ETB', 'symbol': 'Br', 'name': 'Ethiopian Birr', 'region': 'Ethiopia'},
        'GHS': {'code': 'GHS', 'symbol': '₵', 'name': 'Ghanaian Cedi', 'region': 'Ghana'},
        'XOF': {'code': 'XOF', 'symbol': 'CFA', 'name': 'West African CFA Franc', 'region': 'West Africa'},
        'XAF': {'code': 'XAF', 'symbol': 'FCFA', 'name': 'Central African CFA Franc', 'region': 'Central Africa'}
    }
    
    return jsonify({
        'success': True,
        'currencies': currencies
    })

@shop_settings_api.route('/timezones', methods=['GET'])
def get_timezones():
    """Get list of supported timezones."""
    timezones = {
        'Asia/Dubai': 'Dubai (UAE)',
        'Asia/Kuwait': 'Kuwait',
        'Asia/Riyadh': 'Riyadh (Saudi Arabia)',
        'Asia/Qatar': 'Doha (Qatar)',
        'Asia/Bahrain': 'Manama (Bahrain)',
        'Asia/Muscat': 'Muscat (Oman)',
        'Asia/Karachi': 'Karachi (Pakistan)',
        'Asia/Kolkata': 'Mumbai/Delhi (India)',
        'Asia/Dhaka': 'Dhaka (Bangladesh)',
        'Asia/Colombo': 'Colombo (Sri Lanka)',
        'Asia/Kathmandu': 'Kathmandu (Nepal)',
        'Asia/Kabul': 'Kabul (Afghanistan)',
        'Asia/Tehran': 'Tehran (Iran)',
        'Asia/Baghdad': 'Baghdad (Iraq)',
        'Asia/Amman': 'Amman (Jordan)',
        'Asia/Beirut': 'Beirut (Lebanon)',
        'Asia/Damascus': 'Damascus (Syria)',
        'Asia/Jerusalem': 'Jerusalem (Israel)',
        'Asia/Cairo': 'Cairo (Egypt)',
        'Africa/Casablanca': 'Casablanca (Morocco)',
        'Africa/Tunis': 'Tunis (Tunisia)',
        'Africa/Algiers': 'Algiers (Algeria)',
        'Africa/Tripoli': 'Tripoli (Libya)',
        'Africa/Khartoum': 'Khartoum (Sudan)',
        'Africa/Addis_Ababa': 'Addis Ababa (Ethiopia)',
        'Africa/Nairobi': 'Nairobi (Kenya)',
        'Africa/Kampala': 'Kampala (Uganda)',
        'Africa/Dar_es_Salaam': 'Dar es Salaam (Tanzania)',
        'Africa/Lagos': 'Lagos (Nigeria)',
        'Africa/Accra': 'Accra (Ghana)',
        'Africa/Dakar': 'Dakar (Senegal)',
        'Africa/Abidjan': 'Abidjan (Ivory Coast)',
        'America/New_York': 'New York (USA)',
        'America/Chicago': 'Chicago (USA)',
        'America/Denver': 'Denver (USA)',
        'America/Los_Angeles': 'Los Angeles (USA)',
        'America/Toronto': 'Toronto (Canada)',
        'America/Vancouver': 'Vancouver (Canada)',
        'America/Mexico_City': 'Mexico City (Mexico)',
        'America/Sao_Paulo': 'São Paulo (Brazil)',
        'America/Buenos_Aires': 'Buenos Aires (Argentina)',
        'America/Santiago': 'Santiago (Chile)',
        'America/Bogota': 'Bogotá (Colombia)',
        'America/Lima': 'Lima (Peru)',
        'America/Montevideo': 'Montevideo (Uruguay)',
        'Europe/London': 'London (UK)',
        'Europe/Paris': 'Paris (France)',
        'Europe/Berlin': 'Berlin (Germany)',
        'Europe/Rome': 'Rome (Italy)',
        'Europe/Madrid': 'Madrid (Spain)',
        'Europe/Amsterdam': 'Amsterdam (Netherlands)',
        'Europe/Brussels': 'Brussels (Belgium)',
        'Europe/Vienna': 'Vienna (Austria)',
        'Europe/Zurich': 'Zurich (Switzerland)',
        'Europe/Stockholm': 'Stockholm (Sweden)',
        'Europe/Oslo': 'Oslo (Norway)',
        'Europe/Copenhagen': 'Copenhagen (Denmark)',
        'Europe/Helsinki': 'Helsinki (Finland)',
        'Europe/Warsaw': 'Warsaw (Poland)',
        'Europe/Prague': 'Prague (Czech Republic)',
        'Europe/Budapest': 'Budapest (Hungary)',
        'Europe/Bucharest': 'Bucharest (Romania)',
        'Europe/Sofia': 'Sofia (Bulgaria)',
        'Europe/Athens': 'Athens (Greece)',
        'Europe/Istanbul': 'Istanbul (Turkey)',
        'Europe/Moscow': 'Moscow (Russia)',
        'Europe/Kiev': 'Kiev (Ukraine)',
        'Asia/Tokyo': 'Tokyo (Japan)',
        'Asia/Shanghai': 'Shanghai (China)',
        'Asia/Hong_Kong': 'Hong Kong',
        'Asia/Singapore': 'Singapore',
        'Asia/Kuala_Lumpur': 'Kuala Lumpur (Malaysia)',
        'Asia/Bangkok': 'Bangkok (Thailand)',
        'Asia/Manila': 'Manila (Philippines)',
        'Asia/Jakarta': 'Jakarta (Indonesia)',
        'Asia/Ho_Chi_Minh': 'Ho Chi Minh City (Vietnam)',
        'Asia/Seoul': 'Seoul (South Korea)',
        'Asia/Taipei': 'Taipei (Taiwan)',
        'Australia/Sydney': 'Sydney (Australia)',
        'Australia/Melbourne': 'Melbourne (Australia)',
        'Australia/Perth': 'Perth (Australia)',
        'Australia/Adelaide': 'Adelaide (Australia)',
        'Australia/Brisbane': 'Brisbane (Australia)',
        'Pacific/Auckland': 'Auckland (New Zealand)',
        'Pacific/Fiji': 'Suva (Fiji)',
        'Pacific/Honolulu': 'Honolulu (Hawaii)'
    }
    
    return jsonify({
        'success': True,
        'timezones': timezones
    })
