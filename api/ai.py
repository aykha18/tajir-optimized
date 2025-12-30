from flask import Blueprint, jsonify, request, render_template, session, redirect, url_for, Response
from db.connection import get_db_connection, get_placeholder, execute_query
from api.utils import get_current_user_id
from api.plans import get_user_plan_info
from api.i18n import get_user_language, get_translated_text
import csv
from io import StringIO
from datetime import datetime

ai_api = Blueprint('ai_api', __name__)

# AI API Endpoints
@ai_api.route('/api/ai/customer-segmentation')
def get_customer_segmentation():
    """Get customer segmentation analysis using AI/ML."""
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        # Extract customer features for segmentation
        cursor = execute_query(conn, f'''
            SELECT 
                c.customer_id,
                c.name as customer_name,
                c.phone as customer_mobile,
                c.customer_type,
                c.city as customer_city,
                c.area as customer_area,
                COUNT(b.bill_id) as total_orders,
                COALESCE(SUM(b.total_amount), 0) as total_spent,
                COALESCE(AVG(b.total_amount), 0) as avg_order_value,
                MAX(b.bill_date) as last_order_date,
                                            CASE 
                                WHEN MAX(b.bill_date) IS NOT NULL 
                                THEN (NOW()::date - MAX(b.bill_date)::date)
                                ELSE 999 
                            END as days_since_last_order,
                            COUNT(DISTINCT b.bill_date::date) as unique_visit_days,
                            MIN(b.bill_date) as first_order_date,
                            CASE 
                                WHEN MAX(b.bill_date) IS NOT NULL AND MIN(b.bill_date) IS NOT NULL 
                                THEN (MAX(b.bill_date)::date - MIN(b.bill_date)::date)
                                ELSE 0 
                            END as customer_lifetime_days
            FROM customers c
            LEFT JOIN bills b ON c.customer_id = b.customer_id
            WHERE c.user_id = {placeholder}
            GROUP BY c.customer_id, c.name, c.phone, c.customer_type, c.city, c.area
            HAVING COUNT(b.bill_id) > 0
            ORDER BY total_spent DESC
        ''', (user_id,))
        
        customers = cursor.fetchall()
        
        if not customers:
            return jsonify({
                'success': False,
                'error': 'No customer data available for segmentation'
            })
        
        # Simple segmentation logic (can be enhanced with ML models later)
        segmented_customers = []
        for customer in customers:
            customer_dict = dict(customer)
            
            # Convert Decimal types to float for calculations
            total_spent = float(customer_dict['total_spent'] or 0)
            total_orders = int(customer_dict['total_orders'] or 0)
            days_since_last_order = int(customer_dict['days_since_last_order'] or 0)
            customer_lifetime_days = int(customer_dict['customer_lifetime_days'] or 0)
            avg_order_value = float(customer_dict['avg_order_value'] or 0)
            
            # Calculate customer value score (RFM analysis)
            recency_score = max(0, 100 - days_since_last_order)
            frequency_score = min(100, total_orders * 10)
            monetary_score = min(100, total_spent / 10)
            
            customer_value_score = (recency_score * 0.2 + frequency_score * 0.4 + monetary_score * 0.4)
            
            # Determine segment based on value score and behavior
            if customer_value_score >= 80 and total_orders >= 10:
                segment = 'Loyal VIPs'
            elif customer_value_score >= 60 and total_orders >= 5:
                segment = 'Regular Customers'
            elif days_since_last_order > 90:
                segment = 'At-Risk Customers'
            elif customer_lifetime_days < 30:
                segment = 'New Customers'
            else:
                segment = 'Occasional Buyers'
            
            customer_dict['segment'] = segment
            customer_dict['segment_label'] = segment
            customer_dict['customer_value_score'] = round(customer_value_score, 2)
            
            # Update the converted values in the dict
            customer_dict['total_spent'] = total_spent
            customer_dict['total_orders'] = total_orders
            customer_dict['days_since_last_order'] = days_since_last_order
            customer_dict['customer_lifetime_days'] = customer_lifetime_days
            customer_dict['avg_order_value'] = avg_order_value
            
            segmented_customers.append(customer_dict)
        
        # Group by segments for summary
        segments_summary = {}
        for customer in segmented_customers:
            segment = customer['segment_label']
            if segment not in segments_summary:
                segments_summary[segment] = {
                    'label': segment,
                    'count': 0,
                    'total_spent': 0.0,
                    'avg_order_value': 0.0
                }
            
            segments_summary[segment]['count'] += 1
            segments_summary[segment]['total_spent'] += float(customer['total_spent'])
            segments_summary[segment]['avg_order_value'] += float(customer['avg_order_value'])
        
        # Calculate averages
        for segment in segments_summary.values():
            if segment['count'] > 0:
                segment['avg_order_value'] = round(segment['avg_order_value'] / segment['count'], 2)
                segment['total_spent'] = round(segment['total_spent'], 2)
        
        segments_list = list(segments_summary.values())
        
        conn.close()
        
        return jsonify({
            'success': True,
            'segments': segments_list,
            'customers': segmented_customers
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_api.route('/api/ai/export-segmentation', methods=['POST'])
def export_segmentation_data():
    """Export customer segmentation data in various formats."""
    try:
        data = request.get_json()
        format_type = data.get('format', 'csv')
        customer_data = data.get('data', [])
        
        if not customer_data:
            return jsonify({
                'success': False,
                'error': 'No data provided for export'
            }), 400
        
        if format_type == 'csv':
            # Create CSV data
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            headers = ['Customer ID', 'Name', 'Mobile', 'Segment', 'Total Orders', 'Total Spent', 'Avg Order Value', 'Last Visit', 'Customer Value Score']
            writer.writerow(headers)
            
            # Write data
            for customer in customer_data:
                writer.writerow([
                    customer.get('customer_id', ''),
                    customer.get('customer_name', ''),
                    customer.get('customer_mobile', ''),
                    customer.get('segment_label', ''),
                    customer.get('total_orders', 0),
                    customer.get('total_spent', 0),
                    customer.get('avg_order_value', 0),
                    customer.get('last_order_date', ''),
                    customer.get('customer_value_score', 0)
                ])
            
            output.seek(0)
            
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=customer-segmentation-{datetime.now().strftime("%Y%m%d")}.csv'}
            )
        
        else:
            return jsonify({
                'success': False,
                'error': f'Unsupported export format: {format_type}'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_api.route('/ai-dashboard')
def ai_dashboard():
    """AI Dashboard page."""
    try:
        user_id = get_current_user_id()
        if not user_id:
            # Store the intended destination in session for redirect after login
            session['next'] = request.url
            return redirect(url_for('pages_api.login'))
        
        # Get user plan info for the template
        user_plan_info = get_user_plan_info()
        
        return render_template('ai-dashboard.html', 
                            user_plan_info=user_plan_info,
                            get_user_language=get_user_language,
                            get_translated_text=get_translated_text)
        
    except Exception as e:
        # Store the intended destination in session for redirect after login
        session['next'] = request.url
        return redirect(url_for('pages_api.login'))
