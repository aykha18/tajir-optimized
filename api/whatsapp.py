from flask import Blueprint, request, jsonify
import re
import urllib.parse
from db.connection import get_db_connection, get_placeholder, execute_query
from api.utils import get_current_user_id
from plan_manager import plan_manager
from api.i18n import get_user_language

whatsapp_api = Blueprint('whatsapp_api', __name__)

def generate_whatsapp_message(bill_data, shop_settings, language='en'):
    """Generate WhatsApp message for invoice with modern design"""
    # Calculate VAT percentage (standard UAE VAT is 5%)
    vat_percent = 5.0
    discount_amount = bill_data.get('discount_amount', 0)
    
    # Get app name from config
    app_name = "Tajir-POS"  # Default app name
    
    if language == 'ar':
        # Arabic message with modern design
        message = f"""🧾 *{app_name}* - {shop_settings.get('shop_name', 'Tajir')}

📋 *تفاصيل الفاتورة:*
رقم الفاتورة: `{bill_data['bill_number']}`
التاريخ: {bill_data['bill_date']}

👤 *معلومات العميل:*
الاسم: {bill_data['customer_name']}
الهاتف: {bill_data['customer_phone']}
{f"المدينة: {bill_data['customer_city']}" if bill_data.get('customer_city') else ""}
{f"المنطقة: {bill_data['customer_area']}" if bill_data.get('customer_area') else ""}

🛍️ *المنتجات:*
"""
        
        # Add items
        for item in bill_data['items']:
            product_name = item.get('product_name', 'Unknown Product')
            qty = item.get('qty', 0)
            rate = float(item.get('rate', 0))
            total = float(item.get('total', 0))
            message += f"• {product_name} - {qty} × {rate:.2f} درهم = {total:.2f} درهم\n"
        
        message += f"""
💰 *الملخص المالي:*
المجموع الفرعي: {bill_data['subtotal']:.2f} درهم"""
        
        if discount_amount > 0:
            message += f"""
الخصم: -{discount_amount:.2f} درهم"""
        
        message += f"""
الضريبة (5%): {bill_data['vat_amount']:.2f} درهم
المدفوع مسبقاً: {bill_data.get('advance_paid', 0):.2f} درهم
*المجموع النهائي: {bill_data['total_amount']:.2f} درهم*

🙏 شكراً لتعاملكم معنا!
🏪 {shop_settings.get('shop_name', 'Tajir')}
{f"📍 العنوان: {shop_settings.get('address', '')}" if shop_settings.get('address') else ""}
{f"📞 الهاتف: {shop_settings.get('phone', '')}" if shop_settings.get('phone') else ""}"""
    else:
        # English message with modern design
        message = f"""🧾 *{app_name}* - {shop_settings.get('shop_name', 'Tajir')}

📋 *Invoice Details:*
Invoice #: `{bill_data['bill_number']}`
Date: {bill_data['bill_date']}

👤 *Customer Information:*
Name: {bill_data['customer_name']}
Phone: {bill_data['customer_phone']}
{f"City: {bill_data['customer_city']}" if bill_data.get('customer_city') else ""}
{f"Area: {bill_data['customer_area']}" if bill_data.get('customer_area') else ""}

🛍️ *Items:*
"""
        
        # Add items
        for item in bill_data['items']:
            product_name = item.get('product_name', 'Unknown Product')
            qty = item.get('qty', 0)
            rate = float(item.get('rate', 0))
            total = float(item.get('total', 0))
            message += f"• {product_name} - {qty} × AED {rate:.2f} = AED {total:.2f}\n"
        
        message += f"""
💰 *Financial Summary:*
Subtotal: AED {bill_data['subtotal']:.2f}"""
        
        if discount_amount > 0:
            message += f"""
Discount: -AED {discount_amount:.2f}"""
        
        message += f"""
VAT (5%): AED {bill_data['vat_amount']:.2f}
Advance Paid: AED {bill_data.get('advance_paid', 0):.2f}
*Total Amount: AED {bill_data['total_amount']:.2f}*

🙏 Thank you for your business!
🏪 {shop_settings.get('shop_name', 'Tajir')}
{f"📍 Address: {shop_settings.get('address', '')}" if shop_settings.get('address') else ""}
{f"📞 Phone: {shop_settings.get('phone', '')}" if shop_settings.get('phone') else ""}"""
    
    return message

def generate_whatsapp_share_link(phone_number, message):
    """Generate WhatsApp share link"""
    # Remove any non-digit characters from phone number
    clean_phone = ''.join(filter(str.isdigit, phone_number))
    
    # Handle international numbers (starting with +)
    if phone_number.strip().startswith('+'):
        # Trust the country code provided in the input
        pass
    else:
        # Handle UAE phone numbers properly (legacy behavior or local input)
        if clean_phone:
            if clean_phone.startswith('971'):
                # Already has country code
                pass
            elif clean_phone.startswith('0'):
                # Remove leading 0 and add 971
                clean_phone = '971' + clean_phone[1:]
            elif len(clean_phone) == 9:
                # 9-digit number, add 971
                clean_phone = '971' + clean_phone
            else:
                # Add 971 prefix as default fallback for UAE
                clean_phone = '971' + clean_phone
    
    # URL encode the message
    encoded_message = urllib.parse.quote(message)
    
    # Generate WhatsApp share link
    whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_message}"
    
    return whatsapp_url

@whatsapp_api.route('/api/bills/<int:bill_id>/whatsapp', methods=['POST'])
def send_bill_whatsapp(bill_id):
    """Generate WhatsApp share link for bill"""
    try:
        print(f"DEBUG: Starting WhatsApp function for bill_id: {bill_id}")
        data = request.get_json()
        print(f"DEBUG: Request data: {data}")
        phone_number = data.get('phone', '').strip()
        language = data.get('language', 'en')
        
        print(f"DEBUG: WhatsApp request - bill_id: {bill_id}, phone: {phone_number}, language: {language}")
        
        if not phone_number:
            return jsonify({'success': False, 'error': 'Phone number is required'}), 400
        
        # Validate phone number format
        phone_digits = re.sub(r'\D', '', phone_number)
        if len(phone_digits) < 9:
            return jsonify({'success': False, 'error': 'Invalid phone number format.'}), 400
        
        # Check if user has WhatsApp feature access
        try:
            user_id = get_current_user_id()
            print(f"DEBUG: User ID: {user_id}")
            
            if not plan_manager.check_feature_access(user_id, 'whatsapp_integration'):
                return jsonify({'success': False, 'error': 'WhatsApp integration not available in your plan'}), 403
        except Exception as e:
            print(f"DEBUG: Plan manager error: {e}")
            return jsonify({'success': False, 'error': f'Plan manager error: {str(e)}'}), 500
        
        # Get bill data (similar to email function)
        try:
            conn = get_db_connection()
            print(f"DEBUG: Querying bill with ID: {bill_id} for user: {get_current_user_id()}")
            
            placeholder = get_placeholder()
            bill_row = execute_query(conn, f'''
                SELECT b.*, c.name as customer_name, c.phone as customer_phone, 
                       c.city as customer_city, c.area as customer_area,
                       s.shop_name, s.address, s.shop_mobile as phone, '' as email
                FROM bills b
                LEFT JOIN customers c ON b.customer_id = c.customer_id
                LEFT JOIN shop_settings s ON b.user_id = s.user_id
                WHERE b.bill_id = {placeholder} AND b.user_id = {placeholder}
            ''', (bill_id, get_current_user_id())).fetchone()
            
            # Convert Row object to dictionary
            if bill_row:
                bill = dict(bill_row)
            else:
                bill = None
            
            print(f"DEBUG: Bill found: {bill is not None}")
            if bill:
                print(f"DEBUG: Bill type: {type(bill)}")
                print(f"DEBUG: Bill keys: {list(bill.keys()) if hasattr(bill, 'keys') else 'No keys method'}")
            
            if not bill:
                return jsonify({'success': False, 'error': 'Bill not found'}), 404
        except Exception as e:
            print(f"DEBUG: Database error: {e}")
            return jsonify({'success': False, 'error': f'Database error: {str(e)}'}), 500
        
        # Get bill items
        items = execute_query(conn, f'''
            SELECT bi.*, p.product_name
            FROM bill_items bi
            JOIN products p ON bi.product_id = p.product_id
            WHERE bi.bill_id = {placeholder}
        ''', (bill_id,)).fetchall()
        
        conn.close()
        
        # Calculate total discount from bill items (percentage-based)
        total_discount = 0
        for item in items:
            item_dict = dict(item) if not isinstance(item, dict) else item
            rate = float(item_dict.get('rate', 0) or 0)
            qty = int(item_dict.get('quantity', 0) or 0)
            discount_percent = float(item_dict.get('discount', 0) or 0)
            item_subtotal = rate * qty
            item_discount_amount = item_subtotal * (discount_percent / 100)
            total_discount += item_discount_amount
        
        # Prepare bill data
        print(f"DEBUG: Preparing bill data from bill keys: {list(bill.keys())}")
        bill_data = {
            'bill_number': bill.get('bill_number', ''),
            'bill_date': bill.get('bill_date', ''),
            'customer_name': bill.get('customer_name', ''),
            'customer_phone': bill.get('customer_phone', ''),
            'customer_city': bill.get('customer_city', ''),
            'customer_area': bill.get('customer_area', ''),
            'subtotal': float(bill.get('subtotal', 0) or 0),
            'vat_amount': float(bill.get('vat_amount', 0) or 0),
            'vat_percent': 5.0,  # Standard UAE VAT rate
            'total_amount': float(bill.get('total_amount', 0) or 0),
            'advance_paid': float(bill.get('advance_paid', 0) or 0),
            'discount_amount': total_discount,  # Calculate from bill items
            'items': []
        }
        
        for item in items:
            item_dict = dict(item) if not isinstance(item, dict) else item
            rate = float(item_dict.get('rate', 0) or 0)
            qty = int(item_dict.get('quantity', 0) or 0)
            discount_percent = float(item_dict.get('discount', 0) or 0)
            subtotal = rate * qty
            discount_amount = subtotal * (discount_percent / 100)
            total = subtotal - discount_amount
            bill_data['items'].append({
                'product_name': item_dict.get('product_name', 'Unknown Product'),
                'rate': rate,
                'qty': qty,
                'discount_percent': discount_percent,
                'discount_amount': discount_amount,
                'total': total
            })
        
        # Get shop settings
        shop_settings = {
            'shop_name': bill.get('shop_name', ''),
            'address': bill.get('address', ''),
            'phone': bill.get('phone', ''),
            'email': bill.get('email', '')
        }
        
        # Generate WhatsApp message
        whatsapp_message = generate_whatsapp_message(bill_data, shop_settings, language)

        # Append printable invoice link at the end of the message (environment-aware)
        try:
            base_url = request.host_url.rstrip('/')  # e.g., http://localhost:5000 or https://tajir.up.railway.app
            print_url = f"{base_url}/api/bills/{bill_id}/print"
            if language == 'ar':
                whatsapp_message += f"\n\n📄 رابط الفاتورة: {print_url}"
            else:
                whatsapp_message += f"\n\n📄 View/Print Invoice: {print_url}"
        except Exception as _ignore:
            # If anything goes wrong forming the URL, proceed without the link to avoid crashing
            pass

        # Generate WhatsApp share link
        whatsapp_url = generate_whatsapp_share_link(phone_number, whatsapp_message)
        
        return jsonify({
            'success': True,
            'whatsapp_url': whatsapp_url,
            'message': whatsapp_message,
            'phone_number': phone_number
        })
        
    except Exception as e:
        print(f"DEBUG: Exception in WhatsApp function: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@whatsapp_api.route('/api/whatsapp/test', methods=['POST'])
def test_whatsapp_config():
    """Test WhatsApp configuration"""
    try:
        data = request.get_json()
        test_phone = data.get('phone', '').strip()
        test_message = data.get('message', 'Test message from Tajir POS')
        
        if not test_phone:
            return jsonify({'success': False, 'error': 'Phone number is required'}), 400
        
        # Generate test WhatsApp link
        whatsapp_url = generate_whatsapp_share_link(test_phone, test_message)
        
        return jsonify({
            'success': True,
            'whatsapp_url': whatsapp_url,
            'message': 'WhatsApp link generated successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
