from flask import Blueprint, request, jsonify
from db.connection import get_db_connection, get_placeholder, execute_query, execute_update
from api.utils import get_current_user_id

loyalty_api = Blueprint('loyalty_api', __name__)

@loyalty_api.route('/api/loyalty/config', methods=['GET'])
def get_loyalty_config():
    """Get loyalty program configuration for the current user."""
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        # Get loyalty config
        cursor = execute_query(conn, f'''
            SELECT * FROM loyalty_config WHERE user_id = {placeholder}
        ''', (user_id,))
        config = cursor.fetchone()
        
        # Get shop settings for loyalty program status
        cursor = execute_query(conn, f'''
            SELECT enable_loyalty_program, loyalty_program_name, loyalty_points_per_aed, loyalty_aed_per_point 
            FROM shop_settings WHERE user_id = {placeholder}
        ''', (user_id,))
        shop_settings = cursor.fetchone()
        
        conn.close()
        
        if config:
            config_dict = dict(config)
        else:
            # Default configuration
            config_dict = {
                'program_name': 'Loyalty Program',
                'is_active': True,
                'points_per_aed': 1.00,
                'aed_per_point': 0.01,
                'min_points_redemption': 100,
                'max_points_redemption_percent': 20,
                'birthday_bonus_points': 50,
                'anniversary_bonus_points': 100,
                'referral_bonus_points': 200
            }
        
        # Merge with shop settings
        if shop_settings:
            config_dict['enable_loyalty_program'] = bool(shop_settings['enable_loyalty_program'])
            config_dict['loyalty_program_name'] = shop_settings['loyalty_program_name']
            config_dict['loyalty_points_per_aed'] = float(shop_settings['loyalty_points_per_aed'])
            config_dict['loyalty_aed_per_point'] = float(shop_settings['loyalty_aed_per_point'])
        
        return jsonify({
            'success': True,
            'config': config_dict
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loyalty_api.route('/api/loyalty/config', methods=['PUT'])
def update_loyalty_config():
    """Update loyalty program configuration."""
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        conn = get_db_connection()
        
        # Update shop settings
        placeholder = get_placeholder()
        execute_update(conn, f'''
            UPDATE shop_settings SET 
                enable_loyalty_program = {placeholder},
                loyalty_program_name = {placeholder},
                loyalty_points_per_aed = {placeholder},
                loyalty_aed_per_point = {placeholder}
            WHERE user_id = {placeholder}
        ''', (
            data.get('enable_loyalty_program', False),
            data.get('loyalty_program_name', 'Loyalty Program'),
            data.get('loyalty_points_per_aed', 1.00),
            data.get('loyalty_aed_per_point', 0.01),
            user_id
        ))
        
        # Update or create loyalty config
        cursor = execute_query(conn, f'''
            SELECT config_id FROM loyalty_config WHERE user_id = {placeholder}
        ''', (user_id,))
        existing_config = cursor.fetchone()
        
        if existing_config:
            execute_update(conn, f'''
                UPDATE loyalty_config SET 
                    program_name = {placeholder},
                    is_active = {placeholder},
                    points_per_aed = {placeholder},
                    aed_per_point = {placeholder},
                    min_points_redemption = {placeholder},
                    max_points_redemption_percent = {placeholder},
                    birthday_bonus_points = {placeholder},
                    anniversary_bonus_points = {placeholder},
                    referral_bonus_points = {placeholder},
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = {placeholder}
            ''', (
                data.get('loyalty_program_name', 'Loyalty Program'),
                data.get('enable_loyalty_program', False),
                data.get('loyalty_points_per_aed', 1.00),
                data.get('loyalty_aed_per_point', 0.01),
                data.get('min_points_redemption', 100),
                data.get('max_points_redemption_percent', 20),
                data.get('birthday_bonus_points', 50),
                data.get('anniversary_bonus_points', 100),
                data.get('referral_bonus_points', 200),
                user_id
            ))
        else:
            execute_update(conn, f'''
                INSERT INTO loyalty_config (
                    user_id, program_name, is_active, points_per_aed, aed_per_point,
                    min_points_redemption, max_points_redemption_percent,
                    birthday_bonus_points, anniversary_bonus_points, referral_bonus_points
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder},
                         {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            ''', (
                user_id,
                data.get('loyalty_program_name', 'Loyalty Program'),
                data.get('enable_loyalty_program', False),
                data.get('loyalty_points_per_aed', 1.00),
                data.get('loyalty_aed_per_point', 0.01),
                data.get('min_points_redemption', 100),
                data.get('max_points_redemption_percent', 20),
                data.get('birthday_bonus_points', 50),
                data.get('anniversary_bonus_points', 100),
                data.get('referral_bonus_points', 200)
            ))
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Loyalty program configuration updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loyalty_api.route('/api/loyalty/tiers', methods=['GET'])
def get_loyalty_tiers():
    """Get loyalty tiers for the current user."""
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        cursor = execute_query(conn, f'''
            SELECT * FROM loyalty_tiers 
            WHERE user_id = {placeholder} AND is_active = TRUE
            ORDER BY points_threshold ASC
        ''', (user_id,))
        tiers = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'tiers': [dict(tier) for tier in tiers]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loyalty_api.route('/api/loyalty/tiers', methods=['POST'])
def create_loyalty_tier():
    """Create a new loyalty tier."""
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        execute_update(conn, f'''
            INSERT INTO loyalty_tiers (
                user_id, tier_name, tier_level, points_threshold, discount_percent, 
                bonus_points_multiplier, free_delivery, priority_service, exclusive_offers, color_code, is_active
            ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder},
                     {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        ''', (
            user_id,
            data['tier_name'],
            data.get('tier_level', data['tier_name']),
            data.get('points_threshold', 0),
            data.get('discount_percent', 0.0),
            data.get('bonus_points_multiplier', 1.0),
            data.get('free_delivery', False),
            data.get('priority_service', False),
            data.get('exclusive_offers', False),
            data.get('color_code', '#CD7F32'),
            True
        ))
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Loyalty tier created successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loyalty_api.route('/api/loyalty/customers', methods=['GET'])
def get_loyalty_customers():
    """Get all customers with their loyalty information."""
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        cursor = execute_query(conn, f'''
            SELECT 
                c.customer_id,
                c.name,
                c.phone,
                c.email,
                cl.loyalty_id,
                cl.total_points,
                cl.available_points,
                cl.tier_level,
                cl.join_date,
                cl.last_purchase_date,
                cl.total_purchases,
                cl.total_spent,
                cl.referral_code,
                cl.birthday,
                cl.anniversary_date
            FROM customers c
            LEFT JOIN customer_loyalty cl ON c.customer_id = cl.customer_id AND cl.user_id = {placeholder}
            WHERE c.user_id = {placeholder} AND c.is_active = TRUE
            ORDER BY cl.total_points DESC NULLS LAST, c.name ASC
        ''', (user_id, user_id))
        
        customers = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'customers': [dict(customer) for customer in customers]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loyalty_api.route('/api/loyalty/customers/<int:customer_id>', methods=['GET'])
def get_customer_loyalty(customer_id):
    """Get detailed loyalty information for a specific customer."""
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        # Get customer loyalty profile
        cursor = execute_query(conn, f'''
            SELECT 
                cl.*,
                c.name as customer_name,
                c.phone as customer_phone,
                c.email as customer_email
            FROM customer_loyalty cl
            JOIN customers c ON cl.customer_id = c.customer_id
            WHERE cl.user_id = {placeholder} AND cl.customer_id = {placeholder}
        ''', (user_id, customer_id))
        
        loyalty_profile = cursor.fetchone()
        
        if not loyalty_profile:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Customer loyalty profile not found'
            }), 404
        
        # Get recent transactions
        cursor = execute_query(conn, f'''
            SELECT * FROM loyalty_transactions
            WHERE user_id = {placeholder} AND customer_id = {placeholder}
            ORDER BY created_at DESC
            LIMIT 10
        ''', (user_id, customer_id))
        
        history = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'profile': dict(loyalty_profile),
            'history': [dict(h) for h in history]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loyalty_api.route('/api/loyalty/customers/<int:customer_id>/enroll', methods=['POST'])
def enroll_customer_loyalty(customer_id):
    """Enroll a customer in the loyalty program."""
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        # Check if customer exists
        cursor = execute_query(conn, f'''
            SELECT customer_id FROM customers 
            WHERE user_id = {placeholder} AND customer_id = {placeholder}
        ''', (user_id, customer_id))
        
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Customer not found'
            }), 404
        
        # Check if already enrolled
        cursor = execute_query(conn, f'''
            SELECT loyalty_id FROM customer_loyalty 
            WHERE user_id = {placeholder} AND customer_id = {placeholder}
        ''', (user_id, customer_id))
        
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Customer is already enrolled in loyalty program'
            }), 400
        
        # Generate unique referral code
        import random
        import string
        referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Enroll customer
        execute_update(conn, f'''
            INSERT INTO customer_loyalty (
                user_id, customer_id, tier_level, birthday, anniversary_date, referral_code, 
                total_points, available_points, lifetime_points, join_date, is_active
            ) VALUES ({placeholder}, {placeholder}, 'Bronze', {placeholder}, {placeholder}, {placeholder}, 
                     0, 0, 0, CURRENT_DATE, true)
        ''', (
            user_id, 
            customer_id, 
            data.get('birthday'),
            data.get('anniversary_date'),
            referral_code
        ))
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Customer enrolled in loyalty program successfully',
            'referral_code': referral_code
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loyalty_api.route('/api/loyalty/transactions', methods=['GET'])
def get_loyalty_transactions():
    """Get loyalty transactions for the current user."""
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        cursor = execute_query(conn, f'''
            SELECT 
                lt.*,
                c.name as customer_name,
                c.phone as customer_phone
            FROM loyalty_transactions lt
            JOIN customer_loyalty cl ON lt.loyalty_id = cl.loyalty_id
            JOIN customers c ON cl.customer_id = c.customer_id
            WHERE lt.user_id = {placeholder}
            ORDER BY lt.created_at DESC
            LIMIT 100
        ''', (user_id,))
        
        transactions = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'transactions': [dict(txn) for txn in transactions]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loyalty_api.route('/api/loyalty/rewards', methods=['GET'])
def get_loyalty_rewards():
    """Get available loyalty rewards."""
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        cursor = execute_query(conn, f'''
            SELECT * FROM loyalty_rewards 
            WHERE user_id = {placeholder} AND is_active = TRUE
            ORDER BY points_cost ASC
        ''', (user_id,))
        
        rewards = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'rewards': [dict(reward) for reward in rewards]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loyalty_api.route('/api/loyalty/rewards', methods=['POST'])
def create_loyalty_reward():
    """Create a new loyalty reward."""
    try:
        user_id = get_current_user_id()
        data = request.get_json()
        
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        execute_update(conn, f'''
            INSERT INTO loyalty_rewards (
                user_id, reward_name, reward_type, points_cost, discount_percent, 
                discount_amount, description
            ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        ''', (
            user_id,
            data['reward_name'],
            data['reward_type'],
            data.get('points_cost', 0),
            data.get('discount_percent', 0.0),
            data.get('discount_amount', 0.0),
            data.get('description', '')
        ))
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Loyalty reward created successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loyalty_api.route('/api/loyalty/offers', methods=['GET'])
def get_personalized_offers():
    """Get personalized offers for customers."""
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        cursor = execute_query(conn, f'''
            SELECT 
                po.*,
                c.name as customer_name,
                c.phone as customer_phone
            FROM personalized_offers po
            JOIN customer_loyalty cl ON po.loyalty_id = cl.loyalty_id
            JOIN customers c ON cl.customer_id = c.customer_id
            WHERE po.user_id = {placeholder} AND po.is_active = TRUE
            AND po.valid_from <= CURRENT_DATE AND po.valid_until >= CURRENT_DATE
            ORDER BY po.created_at DESC
        ''', (user_id,))
        
        offers = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'offers': [dict(offer) for offer in offers]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@loyalty_api.route('/api/loyalty/analytics', methods=['GET'])
def get_loyalty_analytics():
    """Get loyalty program analytics."""
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        # Total enrolled customers
        cursor = execute_query(conn, f'''
            SELECT COUNT(*) as total_customers FROM customer_loyalty 
            WHERE user_id = {placeholder} AND is_active = TRUE
        ''', (user_id,))
        total_customers = cursor.fetchone()['total_customers']
        
        # Total points issued
        cursor = execute_query(conn, f'''
            SELECT SUM(points_amount) as total_points FROM loyalty_transactions 
            WHERE user_id = {placeholder} AND transaction_type = 'earned'
        ''', (user_id,))
        total_points = cursor.fetchone()['total_points'] or 0
        
        # Total points redeemed
        cursor = execute_query(conn, f'''
            SELECT SUM(points_amount) as redeemed_points FROM loyalty_transactions 
            WHERE user_id = {placeholder} AND transaction_type = 'redeemed'
        ''', (user_id,))
        redeemed_points = cursor.fetchone()['redeemed_points'] or 0
        
        # Tier distribution
        cursor = execute_query(conn, f'''
            SELECT tier_level, COUNT(*) as count FROM customer_loyalty 
            WHERE user_id = {placeholder} AND is_active = TRUE
            GROUP BY tier_level
        ''', (user_id,))
        tier_distribution = {row['tier_level']: row['count'] for row in cursor.fetchall()}
        
        # Recent activity
        cursor = execute_query(conn, f'''
            SELECT COUNT(*) as recent_activity FROM loyalty_transactions 
            WHERE user_id = {placeholder} AND created_at >= CURRENT_DATE - INTERVAL '7 days'
        ''', (user_id,))
        recent_activity = cursor.fetchone()['recent_activity']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'analytics': {
                'total_customers': total_customers,
                'total_points_issued': total_points,
                'total_points_redeemed': redeemed_points,
                'active_points': total_points - redeemed_points,
                'tier_distribution': tier_distribution,
                'recent_activity': recent_activity
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
