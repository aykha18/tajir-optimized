from flask import Blueprint, jsonify, request, render_template
from datetime import datetime
import logging
from db.connection import get_db_connection, get_placeholder, execute_query, execute_update, execute_with_returning
from api.utils import get_current_user_id
from api.i18n import get_user_language, get_translated_text
from plan_manager import plan_manager

plans_api = Blueprint('plans_api', __name__)
logger = logging.getLogger(__name__)

def get_user_plan_info():
    """Get current user plan information and shop settings for template rendering."""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return {
                'plan_type': 'trial',
                'plan_name': 'Tajir Trial',
                'plan_display_name': 'Tajir Trial',
                'shop_settings': None
            }
        
        conn = get_db_connection()
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT * FROM user_plans WHERE user_id = {placeholder} AND is_active = TRUE', (user_id,))
        user_plan = cursor.fetchone()
        cursor = execute_query(conn, f'SELECT * FROM shop_settings WHERE user_id = {placeholder}', (user_id,))
        shop_settings = cursor.fetchone()
        conn.close()
        
        if not user_plan:
            return {
                'plan_type': 'trial',
                'plan_name': 'Tajir Trial',
                'plan_display_name': 'Tajir Trial',
                'shop_settings': dict(shop_settings) if shop_settings else None
            }
        
        user_plan = dict(user_plan)
        plan_type = user_plan['plan_type']
        
        plan_names = {
            'trial': 'Tajir Trial',
            'basic': 'Tajir Basic', 
            'pro': 'Tajir Pro'
        }
        
        return {
            'plan_type': plan_type,
            'plan_name': plan_names.get(plan_type, 'Tajir Trial'),
            'plan_display_name': plan_names.get(plan_type, 'Tajir Trial'),
            'shop_settings': dict(shop_settings) if shop_settings else None
        }
    except Exception as e:
        logger.error(f"Error getting user plan: {e}")
        return {
            'plan_type': 'trial',
            'plan_name': 'Tajir Trial',
            'plan_display_name': 'Tajir Trial',
            'shop_settings': None
        }

@plans_api.route('/debug-plan')
def debug_plan():
    """Debug page for plan management."""
    user_plan_info = get_user_plan_info()
    return render_template('debug_plan.html', 
                        user_plan_info=user_plan_info,
                        get_user_language=get_user_language,
                        get_translated_text=get_translated_text)

@plans_api.route('/api/plan/status', methods=['GET'])
def get_plan_status():
    """Get current user plan status and enabled features."""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401

        conn = get_db_connection()
        # Get the most recent active plan for user_id
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT * FROM user_plans 
            WHERE user_id = {placeholder} AND is_active = TRUE 
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (user_id,))
        user_plan = cursor.fetchone()
        conn.close()
        
        if not user_plan:
            # Create default trial plan if none exists
            conn = get_db_connection()
            placeholder = get_placeholder()
            sql = f'INSERT INTO user_plans (user_id, plan_type, plan_start_date) VALUES ({placeholder}, {placeholder}, {placeholder})'
            execute_with_returning(conn, sql, (user_id, 'trial', datetime.now().strftime('%Y-%m-%d')))
            conn.close()
            
            user_plan = {
                'plan_type': 'trial',
                'plan_start_date': datetime.now().strftime('%Y-%m-%d')
            }
        else:
            user_plan = dict(user_plan)
        
        # Convert plan_start_date to string if it's a datetime.date object
        plan_start_date = user_plan['plan_start_date']
        if hasattr(plan_start_date, 'strftime'):
            plan_start_date = plan_start_date.strftime('%Y-%m-%d')
        
        plan_status = plan_manager.get_user_plan_status(
            user_plan['plan_type'], 
            plan_start_date
        )
        
        # Add upgrade options
        upgrade_options = plan_manager.get_upgrade_options(user_plan['plan_type'])
        plan_status['upgrade_options'] = upgrade_options
        
        # Add expiry warnings
        warnings = plan_manager.get_expiry_warnings(
            user_plan['plan_type'], 
            plan_start_date
        )
        plan_status['warnings'] = warnings
        
        return jsonify(plan_status)
        
    except Exception as e:
        logger.error(f"Error in get_plan_status: {e}")
        return jsonify({'error': str(e)}), 500

@plans_api.route('/api/plan/upgrade', methods=['POST'])
def upgrade_plan():
    """Upgrade user plan."""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401

        data = request.get_json()
        new_plan = data.get('plan_type')
        
        if new_plan not in ['trial', 'basic', 'pro']:
            return jsonify({'error': 'Invalid plan type'}), 400
        
        conn = get_db_connection()
        
        # Instead of inserting a new plan, update the existing plan for user_id
        placeholder = get_placeholder()
        sql = f'''
            UPDATE user_plans
            SET plan_type = {placeholder}, plan_start_date = {placeholder}, is_active = TRUE, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = {placeholder}
        '''
        execute_update(conn, sql, (new_plan, datetime.now().strftime('%Y-%m-%d'), user_id))
        conn.close()
        
        return jsonify({
            'message': f'Successfully upgraded to {new_plan} plan',
            'plan_type': new_plan,
            'start_date': datetime.now().strftime('%Y-%m-%d')
        })
        
    except Exception as e:
        logger.error(f"Error in upgrade_plan: {e}")
        return jsonify({'error': str(e)}), 500

@plans_api.route('/api/plan/features', methods=['GET'])
def get_enabled_features():
    """Get list of enabled features for current user."""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401

        conn = get_db_connection()
        # Get the most recent active plan for user_id
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT * FROM user_plans 
            WHERE user_id = {placeholder} AND is_active = TRUE 
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (user_id,))
        user_plan = cursor.fetchone()
        conn.close()
        
        if not user_plan:
            return jsonify({'enabled_features': [], 'locked_features': []})
        
        user_plan = dict(user_plan)
        
        # Convert plan_start_date to string if it's a datetime.date object
        plan_start_date = user_plan['plan_start_date']
        if hasattr(plan_start_date, 'strftime'):
            plan_start_date = plan_start_date.strftime('%Y-%m-%d')
        
        plan_status = plan_manager.get_user_plan_status(
            user_plan['plan_type'], 
            plan_start_date
        )
        
        return jsonify({
            'enabled_features': plan_status.get('enabled_features', []),
            'locked_features': plan_status.get('locked_features', []),
            'plan_type': user_plan['plan_type'],
            'expired': plan_status.get('expired', False)
        })
        
    except Exception as e:
        logger.error(f"Error in get_enabled_features: {e}")
        return jsonify({'error': str(e)}), 500

@plans_api.route('/api/plan/check-feature/<feature>', methods=['GET'])
def check_feature_access(feature):
    """Check if a specific feature is enabled for current user."""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401

        conn = get_db_connection()
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT * FROM user_plans WHERE user_id = {placeholder} AND is_active = TRUE', (user_id,))

        user_plan = cursor.fetchone()
        conn.close()
        
        if not user_plan:
            return jsonify({'enabled': False, 'reason': 'No active plan'})
        
        user_plan = dict(user_plan)
        
        # Convert plan_start_date to string if it's a datetime.date object
        plan_start_date = user_plan['plan_start_date']
        if hasattr(plan_start_date, 'strftime'):
            plan_start_date = plan_start_date.strftime('%Y-%m-%d')
        
        is_enabled = plan_manager.is_feature_enabled(
            user_plan['plan_type'], 
            plan_start_date, 
            feature
        )
        
        return jsonify({'enabled': is_enabled})
    
    except Exception as e:
        logger.error(f"Error in check_feature_access: {e}")
        return jsonify({'error': str(e)}), 500
        
@plans_api.route('/api/plan/config', methods=['GET'])
def get_plan_config():
    """Get plan configuration for frontend."""
    try:
        return jsonify({
            'pricing_plans': plan_manager.config.get('pricing_plans', {}),
            'feature_definitions': plan_manager.config.get('feature_definitions', {}),
            'ui_settings': plan_manager.config.get('ui_settings', {}),
            'upgrade_options': plan_manager.config.get('upgrade_options', {})
        })
        
    except Exception as e:
        logger.error(f"Error in get_plan_config: {e}")
        return jsonify({'error': str(e)}), 500
