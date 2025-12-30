import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import re
from flask import Blueprint, request, jsonify
from db.connection import get_db_connection, get_placeholder, execute_query, execute_update
from api.auth import get_current_user_id
from plan_manager import plan_manager

email_api = Blueprint('email_api', __name__)

# Email Configuration
def get_email_config():
    """Get email configuration from environment or shop settings"""
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'SELECT * FROM shop_settings WHERE user_id = {placeholder}', (user_id,))
    shop_settings_row = cursor.fetchone()
    conn.close()
    
    # Convert Row object to dictionary if it exists
    shop_settings = dict(shop_settings_row) if shop_settings_row else {}
    
    # Default email config for Outlook
    email_config = {
        'smtp_server': os.getenv('SMTP_SERVER', 'smtp-mail.outlook.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', '587')),
        'smtp_username': os.getenv('SMTP_USERNAME', 'khanayub25@outlook.com'),
        'smtp_password': os.getenv('SMTP_PASSWORD', ''),
        'from_email': os.getenv('FROM_EMAIL', 'khanayub25@outlook.com'),
        'from_name': os.getenv('FROM_NAME', 'Tajir POS')
    }
    
    # Override with shop settings if available
    if shop_settings:
        # Note: shop_settings table doesn't have an email column, so we skip that
        if shop_settings.get('shop_name'):
            email_config['from_name'] = shop_settings['shop_name']
    
    return email_config

def validate_email(email):
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_email_template(bill_data, shop_settings, language='en'):
    """Generate professional email template for invoice"""
    if language == 'ar':
        # Arabic template
        template = f"""
        <div dir="rtl" style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f8f9fa; padding: 20px;">
            <div style="background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #6f42c1; margin: 0; font-size: 28px;">فاتورة - {shop_settings.get('shop_name', 'Tajir')}</h1>
                    <p style="color: #6c757d; margin: 10px 0;">رقم الفاتورة: {bill_data['bill_number']}</p>
                    <p style="color: #6c757d; margin: 5px 0;">التاريخ: {bill_data['bill_date']}</p>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #495057; border-bottom: 2px solid #6f42c1; padding-bottom: 10px;">تفاصيل العميل</h3>
                    <p><strong>الاسم:</strong> {bill_data['customer_name']}</p>
                    <p><strong>الهاتف:</strong> {bill_data['customer_phone']}</p>
                    {f"<p><strong>المدينة:</strong> {bill_data['customer_city']}</p>" if bill_data.get('customer_city') else ""}
                    {f"<p><strong>المنطقة:</strong> {bill_data['customer_area']}</p>" if bill_data.get('customer_area') else ""}
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #495057; border-bottom: 2px solid #6f42c1; padding-bottom: 10px;">تفاصيل الفاتورة</h3>
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                        <thead>
                            <tr style="background-color: #6f42c1; color: white;">
                                <th style="padding: 12px; text-align: right; border: 1px solid #dee2e6;">المنتج</th>
                                <th style="padding: 12px; text-align: center; border: 1px solid #dee2e6;">السعر</th>
                                <th style="padding: 12px; text-align: center; border: 1px solid #dee2e6;">الكمية</th>
                                <th style="padding: 12px; text-align: center; border: 1px solid #dee2e6;">المجموع</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        # Add bill items
        for item in bill_data['items']:
            template += f"""
                            <tr>
                                <td style="padding: 12px; border: 1px solid #dee2e6;">{item['product_name']}</td>
                                <td style="padding: 12px; text-align: center; border: 1px solid #dee2e6;">{item['rate']:.2f} درهم</td>
                                <td style="padding: 12px; text-align: center; border: 1px solid #dee2e6;">{item['qty']}</td>
                                <td style="padding: 12px; text-align: center; border: 1px solid #dee2e6;">{item['total']:.2f} درهم</td>
                            </tr>
            """
        
        template += f"""
                        </tbody>
                    </table>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span><strong>المجموع الفرعي:</strong></span>
                        <span>{bill_data['subtotal']:.2f} درهم</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span><strong>الضريبة ({bill_data.get('vat_percent', 5)}%):</strong></span>
                        <span>{bill_data['vat_amount']:.2f} درهم</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span><strong>المدفوع مسبقاً:</strong></span>
                        <span>{bill_data.get('advance_paid', 0):.2f} درهم</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; color: #6f42c1;">
                        <span><strong>المجموع النهائي:</strong></span>
                        <span>{bill_data['total_amount']:.2f} درهم</span>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                    <p style="color: #6c757d; margin: 5px 0;">شكراً لتعاملكم معنا</p>
                    <p style="color: #6c757d; margin: 5px 0;">{shop_settings.get('shop_name', 'Tajir')}</p>
                    {f"<p style='color: #6c757d; margin: 5px 0;'>{shop_settings.get('address', '')}</p>" if shop_settings.get('address') else ""}
                    {f"<p style='color: #6c757d; margin: 5px 0;'>{shop_settings.get('phone', '')}</p>" if shop_settings.get('phone') else ""}
                </div>
            </div>
        </div>
        """
    else:
        # English template
        template = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f8f9fa; padding: 20px;">
            <div style="background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #6f42c1; margin: 0; font-size: 28px;">Invoice - {shop_settings.get('shop_name', 'Tajir')}</h1>
                    <p style="color: #6c757d; margin: 10px 0;">Invoice #: {bill_data['bill_number']}</p>
                    <p style="color: #6c757d; margin: 5px 0;">Date: {bill_data['bill_date']}</p>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #495057; border-bottom: 2px solid #6f42c1; padding-bottom: 10px;">Customer Details</h3>
                    <p><strong>Name:</strong> {bill_data['customer_name']}</p>
                    <p><strong>Phone:</strong> {bill_data['customer_phone']}</p>
                    {f"<p><strong>City:</strong> {bill_data['customer_city']}</p>" if bill_data.get('customer_city') else ""}
                    {f"<p><strong>Area:</strong> {bill_data['customer_area']}</p>" if bill_data.get('customer_area') else ""}
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #495057; border-bottom: 2px solid #6f42c1; padding-bottom: 10px;">Invoice Details</h3>
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                        <thead>
                            <tr style="background-color: #6f42c1; color: white;">
                                <th style="padding: 12px; text-align: left; border: 1px solid #dee2e6;">Product</th>
                                <th style="padding: 12px; text-align: center; border: 1px solid #dee2e6;">Rate</th>
                                <th style="padding: 12px; text-align: center; border: 1px solid #dee2e6;">Qty</th>
                                <th style="padding: 12px; text-align: center; border: 1px solid #dee2e6;">Total</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        # Add bill items
        for item in bill_data['items']:
            template += f"""
                            <tr>
                                <td style="padding: 12px; border: 1px solid #dee2e6;">{item['product_name']}</td>
                                <td style="padding: 12px; text-align: center; border: 1px solid #dee2e6;">AED {item['rate']:.2f}</td>
                                <td style="padding: 12px; text-align: center; border: 1px solid #dee2e6;">{item['qty']}</td>
                                <td style="padding: 12px; text-align: center; border: 1px solid #dee2e6;">AED {item['total']:.2f}</td>
                            </tr>
            """
        
        template += f"""
                        </tbody>
                    </table>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span><strong>Subtotal:</strong></span>
                        <span>AED {bill_data['subtotal']:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span><strong>VAT ({bill_data.get('vat_percent', 5)}%):</strong></span>
                        <span>AED {bill_data['vat_amount']:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span><strong>Advance Paid:</strong></span>
                        <span>AED {bill_data.get('advance_paid', 0):.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; color: #6f42c1;">
                        <span><strong>Total Amount:</strong></span>
                        <span>AED {bill_data['total_amount']:.2f}</span>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                    <p style="color: #6c757d; margin: 5px 0;">Thank you for your business!</p>
                    <p style="color: #6c757d; margin: 5px 0;">{shop_settings.get('shop_name', 'Tajir')}</p>
                    {f"<p style='color: #6c757d; margin: 5px 0;'>{shop_settings.get('address', '')}</p>" if shop_settings.get('address') else ""}
                    {f"<p style='color: #6c757d; margin: 5px 0;'>{shop_settings.get('phone', '')}</p>" if shop_settings.get('phone') else ""}
                </div>
            </div>
        </div>
        """
    
    return template

def send_email_invoice(bill_id, recipient_email, language='en'):
    """Send invoice via email"""
    try:
        # Get bill data
        conn = get_db_connection()
        placeholder = get_placeholder()
        bill_row = execute_update(conn, f'''
            SELECT b.*, c.name as customer_name, c.phone as customer_phone, 
                   c.city as customer_city, c.area as customer_area,
                   s.shop_name, s.address, s.shop_mobile as phone, '' as email
            FROM bills b
            LEFT JOIN customers c ON b.customer_id = c.customer_id
            LEFT JOIN shop_settings s ON b.user_id = s.user_id
            WHERE b.bill_id = {placeholder} AND b.user_id = {placeholder}
        ''', (bill_id, get_current_user_id())).fetchone()
        
        if not bill_row:
            return {'success': False, 'error': 'Bill not found'}
        
        # Convert Row object to dictionary
        bill = dict(bill_row)
        
        # Get bill items
        items = execute_update(conn, f'''
            SELECT bi.*, p.product_name
            FROM bill_items bi
            JOIN products p ON bi.product_id = p.product_id
            WHERE bi.bill_id = {placeholder}
        ''', (bill_id,)).fetchall()
        
        conn.close()
        
        # Prepare bill data
        bill_data = {
            'bill_number': bill.get('bill_number', ''),
            'bill_date': bill.get('bill_date', ''),
            'customer_name': bill.get('customer_name', ''),
            'customer_phone': bill.get('customer_phone', ''),
            'customer_city': bill.get('customer_city', ''),
            'customer_area': bill.get('customer_area', ''),
            'subtotal': float(bill.get('subtotal', 0)),
            'vat_amount': float(bill.get('vat_amount', 0)),
            'vat_percent': (float(bill.get('vat_amount', 0)) / float(bill.get('subtotal', 1)) * 100) if float(bill.get('subtotal', 0)) > 0 else 0,
            'total_amount': float(bill.get('total_amount', 0)),
            'advance_paid': float(bill.get('advance_paid', 0)),
            'items': []
        }
        
        for item in items:
            item_dict = dict(item) if not isinstance(item, dict) else item
            bill_data['items'].append({
                'product_name': item_dict.get('product_name', ''),
                'rate': float(item_dict.get('rate', 0)),
                'qty': item_dict.get('quantity', 0),
                'total': float(item_dict.get('rate', 0)) * item_dict.get('quantity', 0)
            })
        
        # Get shop settings
        shop_settings = {
            'shop_name': bill.get('shop_name', ''),
            'address': bill.get('address', ''),
            'phone': bill.get('phone', ''),
            'email': bill.get('email', '')
        }
        
        # Generate email template
        email_html = generate_email_template(bill_data, shop_settings, language)
        
        # Get email configuration
        email_config = get_email_config()
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Invoice #{bill_data['bill_number']} - {shop_settings.get('shop_name', 'Tajir')}"
        msg['From'] = f"{email_config['from_name']} <{email_config['from_email']}>"
        msg['To'] = recipient_email
        
        # Add HTML content
        html_part = MIMEText(email_html, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
            server.starttls()
            server.login(email_config['smtp_username'], email_config['smtp_password'])
            server.send_message(msg)
        
        return {'success': True, 'message': 'Invoice sent successfully'}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Email API Routes
@email_api.route('/api/bills/<int:bill_id>/send-email', methods=['POST'])
def send_bill_email(bill_id):
    """Send bill via email"""
    try:
        data = request.get_json()
        recipient_email = data.get('email', '').strip()
        language = data.get('language', 'en')
        
        if not recipient_email:
            return jsonify({'success': False, 'error': 'Email address is required'}), 400
        
        if not validate_email(recipient_email):
            return jsonify({'success': False, 'error': 'Invalid email address format'}), 400
        
        # Check if user has email feature access
        if not plan_manager.check_feature_access(get_current_user_id(), 'email_integration'):
            return jsonify({'success': False, 'error': 'Email integration not available in your plan'}), 403
        
        result = send_email_invoice(bill_id, recipient_email, language)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@email_api.route('/api/email/test', methods=['POST'])
def test_email_config():
    """Test email configuration"""
    try:
        data = request.get_json()
        test_email = data.get('email', '').strip()
        
        if not test_email:
            return jsonify({'success': False, 'error': 'Email address is required'}), 400
        
        if not validate_email(test_email):
            return jsonify({'success': False, 'error': 'Invalid email address format'}), 400
        
        # Get email configuration
        email_config = get_email_config()
        
        # Create test message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Tajir POS - Email Configuration Test'
        msg['From'] = f"{email_config['from_name']} <{email_config['from_email']}>"
        msg['To'] = test_email
        
        test_html = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f8f9fa; padding: 20px;">
            <div style="background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #6f42c1; margin: 0; font-size: 28px;">Email Configuration Test</h1>
                    <p style="color: #6c757d; margin: 10px 0;">Tajir POS Email Integration</p>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #495057; border-bottom: 2px solid #6f42c1; padding-bottom: 10px;">Test Results</h3>
                    <p><strong>Status:</strong> ✅ Email configuration is working correctly!</p>
                    <p><strong>From:</strong> {email_config['from_name']} &lt;{email_config['from_email']}&gt;</p>
                    <p><strong>SMTP Server:</strong> {email_config['smtp_server']}:{email_config['smtp_port']}</p>
                    <p><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                    <p style="color: #6c757d; margin: 5px 0;">Your email integration is ready to use!</p>
                    <p style="color: #6c757d; margin: 5px 0;">You can now send invoices to your customers via email.</p>
                </div>
            </div>
        </div>
        """
        
        html_part = MIMEText(test_html, 'html')
        msg.attach(html_part)
        
        # Send test email
        with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
            server.starttls()
            server.login(email_config['smtp_username'], email_config['smtp_password'])
            server.send_message(msg)
        
        return jsonify({'success': True, 'message': 'Test email sent successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@email_api.route('/api/email/config', methods=['GET'])
def get_email_config_api():
    """Get current email configuration (without sensitive data)"""
    try:
        email_config = get_email_config()
        
        # Return only non-sensitive configuration
        safe_config = {
            'smtp_server': email_config['smtp_server'],
            'smtp_port': email_config['smtp_port'],
            'from_name': email_config['from_name'],
            'from_email': email_config['from_email'],
            'configured': bool(email_config['smtp_username'] and email_config['smtp_password'])
        }
        
        return jsonify({'success': True, 'config': safe_config})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@email_api.route('/api/email/config', methods=['PUT'])
def update_email_config():
    """Update email configuration"""
    try:
        data = request.get_json()
        password = data.get('password', '').strip()
        
        if not password:
            return jsonify({'success': False, 'error': 'Password is required'}), 400
        
        # Set environment variable for the password
        os.environ['SMTP_PASSWORD'] = password
        
        return jsonify({'success': True, 'message': 'Email configuration updated successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
