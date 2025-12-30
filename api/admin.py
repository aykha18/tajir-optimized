from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
import logging
import json
from datetime import datetime, timedelta, date
from db.connection import get_db_connection, get_placeholder, execute_query, execute_update, execute_with_returning, is_postgresql
from api.utils import log_user_action, admin_required
import bcrypt

admin_api = Blueprint('admin_api', __name__)
logger = logging.getLogger(__name__)

@admin_api.route('/admin/login')
def admin_login():
    """Admin login page."""
    if 'admin_logged_in' in session:
        return redirect('/admin')
    return render_template('admin_login.html')

@admin_api.route('/api/admin/login', methods=['POST'])
def admin_auth_login():
    """Handle admin login."""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        logger.info(f"Admin login attempt for email: {email}")
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password required'})
        
        conn = get_db_connection()
        
        # Check if user exists and is admin (look for admin user by email)
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT * FROM users WHERE email = {placeholder} AND is_active = TRUE', (email,))
        user = cursor.fetchone()
        
        if not user:
            logger.warning(f"Admin user not found for email: {email}")
            return jsonify({'success': False, 'message': 'Invalid credentials'})
        
        logger.info(f"Admin user found: {user['email']}, checking password...")
        
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            logger.warning(f"Password check failed for admin user: {email}")
            return jsonify({'success': False, 'message': 'Invalid credentials'})
        
        logger.info(f"Admin login successful for: {email}")
        
        # Set admin session
        session['admin_logged_in'] = True
        session['admin_user_id'] = user['user_id']
        session['admin_email'] = user['email']
        
        # Log admin login
        log_user_action("ADMIN_LOGIN", user['user_id'], {
            'email': user['email'],
            'timestamp': datetime.now().isoformat()
        })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Admin login successful'
        })
        
    except Exception as e:
        logger.error(f"Admin login error: {e}")
        return jsonify({'success': False, 'message': 'Login failed. Please try again.'}), 500

@admin_api.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    """Handle admin logout."""
    try:
        # Log admin logout
        if 'admin_user_id' in session:
            log_user_action("ADMIN_LOGOUT", session['admin_user_id'], {
                'email': session.get('admin_email'),
                'timestamp': datetime.now().isoformat()
            })
        
        # Clear admin session
        session.pop('admin_logged_in', None)
        session.pop('admin_user_id', None)
        session.pop('admin_email', None)
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
        
    except Exception as e:
        logger.error(f"Admin logout error: {e}")
        return jsonify({'success': False, 'message': 'Logout failed'}), 500

@admin_api.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard for plan management."""
    return render_template('admin.html')

@admin_api.route('/api/admin/stats')
@admin_required
def admin_stats():
    """Get admin dashboard statistics."""
    try:
        conn = get_db_connection()
        
        # Total shops
        cursor = execute_query(conn, 'SELECT COUNT(*) as count FROM users WHERE is_active = TRUE')
        result = cursor.fetchone()
        total_shops = result['count'] if result else 0
        
        # Active plans (not expired)
        cursor = execute_query(conn, '''
            SELECT COUNT(*) as count FROM user_plans up
            JOIN users u ON up.user_id = u.user_id
            WHERE up.is_active = TRUE AND u.is_active = TRUE
            AND (up.plan_type = 'pro' OR up.plan_end_date > CURRENT_DATE)
        ''')
        result = cursor.fetchone()
        active_plans = result['count'] if result else 0
        
        # Expiring soon (within 7 days)
        cursor = execute_query(conn, '''
            SELECT COUNT(*) as count FROM user_plans up
            JOIN users u ON up.user_id = u.user_id
            WHERE up.is_active = TRUE AND u.is_active = TRUE
            AND up.plan_type != 'pro'
            AND up.plan_end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
        ''')
        result = cursor.fetchone()
        expiring_soon = result['count'] if result else 0
        
        # Expired plans
        cursor = execute_query(conn, '''
            SELECT COUNT(*) as count FROM user_plans up
            JOIN users u ON up.user_id = u.user_id
            WHERE up.is_active = TRUE AND u.is_active = TRUE
            AND up.plan_type != 'pro'
            AND up.plan_end_date < CURRENT_DATE
        ''')
        result = cursor.fetchone()
        expired_plans = result['count'] if result else 0
        
        conn.close()
        
        return jsonify({
            'total_shops': total_shops,
            'active_plans': active_plans,
            'expiring_soon': expiring_soon,
            'expired_plans': expired_plans
        })
    except Exception as e:
        logger.error(f"Failed to load admin stats: {e}")
        return jsonify({'error': 'Failed to load stats'}), 500

@admin_api.route('/api/admin/shops')
@admin_required
def admin_shops():
    """Get all shops with their plan information."""
    try:
        conn = get_db_connection()
        
        cursor = execute_query(conn, '''
            SELECT u.user_id, u.shop_name, u.email, u.mobile, 
                   CAST(u.created_at AS VARCHAR) as created_at,
                   up.plan_type, 
                   CAST(up.plan_start_date AS VARCHAR) as plan_start_date, 
                   CAST(up.plan_end_date AS VARCHAR) as plan_end_date,
                   CASE 
                       WHEN up.plan_type = 'pro' AND up.plan_end_date IS NULL THEN 'Unlimited'
                       WHEN up.plan_end_date IS NULL THEN '0'
                       ELSE CAST(up.plan_end_date - CURRENT_DATE AS VARCHAR)
                   END as days_remaining,
                   CASE 
                       WHEN up.plan_type = 'pro' AND up.plan_end_date IS NULL THEN 0
                       WHEN up.plan_end_date IS NULL THEN 1
                       ELSE CASE WHEN up.plan_end_date < CURRENT_DATE THEN 1 ELSE 0 END
                   END as expired
            FROM users u
            LEFT JOIN user_plans up ON u.user_id = up.user_id AND up.is_active = TRUE
            WHERE u.is_active = TRUE
            ORDER BY u.created_at DESC
        ''')
        shops = cursor.fetchall()
        
        conn.close()
        
        return jsonify([dict(shop) for shop in shops])
    except Exception as e:
        logger.error(f"Failed to load shops: {e}")
        return jsonify({'error': 'Failed to load shops'}), 500

@admin_api.route('/api/admin/shops/<int:user_id>/plan')
@admin_required
def admin_shop_plan(user_id):
    """Get plan details for a specific shop."""
    try:
        conn = get_db_connection()
        
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT up.plan_type as plan, 
                   CAST(up.plan_start_date AS VARCHAR) as start_date, 
                   CAST(up.plan_end_date AS VARCHAR) as expiry_date,
                   CASE 
                       WHEN up.plan_type = 'pro' AND up.plan_end_date IS NULL THEN 'Unlimited'
                       WHEN up.plan_end_date IS NULL THEN '0'
                       ELSE CAST(up.plan_end_date - CURRENT_DATE AS VARCHAR)
                   END as days_remaining,
                   CASE 
                       WHEN up.plan_type = 'pro' AND up.plan_end_date IS NULL THEN 0
                       WHEN up.plan_end_date IS NULL THEN 1
                       ELSE CASE WHEN up.plan_end_date < CURRENT_DATE THEN 1 ELSE 0 END
                   END as expired
            FROM user_plans up
            WHERE up.user_id = {placeholder} AND up.is_active = TRUE
        ''', (user_id,))
        plan = cursor.fetchone()
        
        conn.close()
        
        if plan:
            return jsonify(dict(plan))
        else:
            return jsonify({'error': 'Plan not found'}), 404
    except Exception as e:
        logger.error(f"Failed to load shop plan: {e}")
        return jsonify({'error': 'Failed to load plan'}), 500

@admin_api.route('/api/admin/plans/upgrade', methods=['POST'])
@admin_required
def admin_upgrade_plan():
    """Upgrade or change plan for a shop."""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        plan_type = data.get('plan_type')
        duration_months = data.get('duration_months')
        
        if not all([user_id, plan_type]):
            return jsonify({'error': 'User ID and plan type are required'}), 400
        
        if plan_type not in ['trial', 'basic', 'pro']:
            return jsonify({'error': 'Invalid plan type'}), 400
        
        conn = get_db_connection()
        
        # Check if user exists
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT user_id, shop_name FROM users WHERE user_id = {placeholder} AND is_active = TRUE', (user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Deactivate current plan
        placeholder = get_placeholder()
        # Use TRUE/FALSE for PostgreSQL
        is_active_value = 'FALSE'
        execute_update(conn, f'UPDATE user_plans SET is_active = {is_active_value} WHERE user_id = {placeholder}', (user_id,))
        
        # Calculate new plan dates
        start_date = datetime.now().date()
        end_date = None
        
        if plan_type == 'trial':
            end_date = start_date + timedelta(days=15)
        elif plan_type == 'basic':
            if duration_months:
                end_date = start_date + timedelta(days=30 * duration_months)
            else:
                end_date = start_date + timedelta(days=365)  # Default 1 year
        elif plan_type == 'pro':
            if duration_months:
                end_date = start_date + timedelta(days=30 * duration_months)
            else:
                end_date = None  # Lifetime (default for PRO)
        
        # Insert new plan
        placeholder = get_placeholder()
        # Use TRUE/FALSE for PostgreSQL
        is_active_value = 'TRUE'
        sql = f'''
            INSERT INTO user_plans (user_id, plan_type, plan_start_date, plan_end_date, is_active)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {is_active_value})
        '''
        execute_with_returning(conn, sql, (user_id, plan_type, start_date, end_date))
        
        # Log the action
        log_user_action('plan_upgrade', user_id, {
            'plan_type': plan_type,
            'duration_months': duration_months,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat() if end_date else None
        })
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Plan upgraded to {plan_type.upper()} successfully',
            'shop_name': user['shop_name']
        })
    except Exception as e:
        logger.error(f"Failed to upgrade plan: {e}")
        return jsonify({'error': 'Failed to upgrade plan'}), 500

@admin_api.route('/api/admin/plans/expire', methods=['POST'])
@admin_required
def admin_expire_plan():
    """Expire a shop's plan immediately."""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400
        
        conn = get_db_connection()
        
        # Check if user exists
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT user_id, shop_name FROM users WHERE user_id = {placeholder} AND is_active = TRUE', (user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Get current plan
        cursor = execute_query(conn, f'SELECT plan_type FROM user_plans WHERE user_id = {placeholder} AND is_active = TRUE', (user_id,))
        current_plan = cursor.fetchone()
        if not current_plan:
            conn.close()
            return jsonify({'error': 'No active plan found'}), 404
        
        # Expire the plan by setting end date to yesterday
        expire_date = datetime.now().date() - timedelta(days=1)
        placeholder = get_placeholder()
        sql = f'''
            UPDATE user_plans 
            SET plan_end_date = {placeholder}, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = {placeholder} AND is_active = TRUE
        '''
        execute_update(conn, sql, (expire_date, user_id))
        
        # Log the action
        log_user_action('plan_expire', user_id, {
            'plan_type': current_plan['plan_type'],
            'expire_date': expire_date.isoformat()
        })
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Plan expired successfully',
            'shop_name': user['shop_name']
        })
    except Exception as e:
        logger.error(f"Failed to expire plan: {e}")
        return jsonify({'error': 'Failed to expire plan'}), 500

@admin_api.route('/api/admin/activity')
@admin_required
def admin_activity():
    """Get recent admin activity."""
    try:
        conn = get_db_connection()
        
        cursor = execute_query(conn, '''
            SELECT ua.action, ua.details, ua.timestamp, u.shop_name
            FROM user_actions ua
            LEFT JOIN users u ON ua.user_id = u.user_id
            WHERE ua.action IN ('plan_upgrade', 'plan_expire', 'plan_renew')
            ORDER BY ua.timestamp DESC
            LIMIT 20
        ''')
        activities = cursor.fetchall()
        
        conn.close()
        
        # Format activities
        formatted_activities = []
        for activity in activities:
            details = json.loads(activity['details']) if activity['details'] else {}
            
            if activity['action'] == 'plan_upgrade':
                description = f"Upgraded to {details.get('plan_type', 'Unknown').upper()}"
                if details.get('duration_months'):
                    description += f" for {details['duration_months']} months"
            elif activity['action'] == 'plan_expire':
                description = f"Expired {details.get('plan_type', 'Unknown').upper()} plan"
            else:
                description = "Plan action performed"
            
            formatted_activities.append({
                'action': activity['action'],
                'description': description,
                'shop_name': activity['shop_name'] or 'Unknown Shop',
                'timestamp': activity['timestamp']
            })
        
        return jsonify(formatted_activities)
    except Exception as e:
        logger.error(f"Failed to load activity: {e}")
        return jsonify({'error': 'Failed to load activity'}), 500

@admin_api.route('/admin/logs')
@admin_required
def admin_logs():
    """Admin interface to view error logs."""
    try:
        conn = get_db_connection()
        
        # Get recent error logs
        cursor = execute_query(conn, '''
            SELECT el.*, u.shop_name 
            FROM error_logs el 
            LEFT JOIN users u ON el.user_id = u.user_id 
            ORDER BY el.timestamp DESC 
            LIMIT 100
        ''')

        error_logs = cursor.fetchall()
        
        # Get recent user actions
        cursor = execute_query(conn, '''
            SELECT ua.*, u.shop_name 
            FROM user_actions ua 
            LEFT JOIN users u ON ua.user_id = u.user_id 
            ORDER BY ua.timestamp DESC 
            LIMIT 50
        ''')

        user_actions = cursor.fetchall()
        
        conn.close()
        
        return render_template('admin_logs.html', 
                            error_logs=error_logs, 
                            user_actions=user_actions)
    except Exception as e:
        logger.error(f"Failed to load admin logs: {e}")
        return jsonify({'error': 'Failed to load logs'}), 500

@admin_api.route('/api/admin/check-schema')
@admin_required
def check_schema():
    """Check database schema and return detailed information."""
    try:
        # Get database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if we're using PostgreSQL or SQLite
        is_pg = is_postgresql()
        
        schema_info = {
            'tables': [],
            'primary_keys': [],
            'foreign_keys': [],
            'unique_constraints': [],
            'check_constraints': [],
            'indexes': [],
            'sequences': [],
            'row_counts': {},
            'important_data': {}
        }
        
        if is_pg:
            # PostgreSQL Schema Checks
            # 1. Check all tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            schema_info['tables'] = [table[0] if isinstance(table, tuple) else table['table_name'] for table in tables]
            
            # 2. Check primary keys
            cursor.execute("""
                SELECT 
                    tc.table_name,
                    kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name
                WHERE tc.constraint_type = 'PRIMARY KEY'
                    AND tc.table_schema = 'public'
                ORDER BY tc.table_name, kcu.ordinal_position
            """)
            primary_keys = cursor.fetchall()
            schema_info['primary_keys'] = [
                f"{pk[0]}.{pk[1]}" if isinstance(pk, tuple) else f"{pk['table_name']}.{pk['column_name']}" 
                for pk in primary_keys
            ]
        else:
            # SQLite Schema Checks
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            schema_info['tables'] = [table[0] if isinstance(table, tuple) else table['name'] for table in tables]
            
            # Simple PK check for SQLite
            for table in schema_info['tables']:
                try:
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    for col in columns:
                        # col structure: (cid, name, type, notnull, dflt_value, pk)
                        # If accessing by index: col[5] is pk
                        is_pk = col[5] if isinstance(col, tuple) else col['pk']
                        name = col[1] if isinstance(col, tuple) else col['name']
                        if is_pk:
                            schema_info['primary_keys'].append(f"{table}.{name}")
                except:
                    pass
        
        conn.close()
        return jsonify(schema_info)
        
    except Exception as e:
        logger.error(f"Failed to check schema: {e}")
        return jsonify({'error': str(e)}), 500
        
        # 3. Check foreign keys
        cursor.execute("""
            SELECT 
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                rc.delete_rule,
                rc.update_rule
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu 
                ON ccu.constraint_name = tc.constraint_name
            JOIN information_schema.referential_constraints rc 
                ON tc.constraint_name = rc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = 'public'
            ORDER BY tc.table_name, kcu.column_name
        """)
        foreign_keys = cursor.fetchall()
        # Handle both tuple and dict cursor results
        schema_info['foreign_keys'] = [
            f"{fk[0]}.{fk[1]} → {fk[2]}.{fk[3]} ({fk[4]}/{fk[5]})" if isinstance(fk, tuple) 
            else f"{fk['table_name']}.{fk['column_name']} → {fk['foreign_table_name']}.{fk['foreign_column_name']} ({fk['delete_rule']}/{fk['update_rule']})" 
            for fk in foreign_keys
        ]
        
        # 4. Check unique constraints
        cursor.execute("""
            SELECT 
                tc.table_name,
                kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'UNIQUE'
                AND tc.table_schema = 'public'
            ORDER BY tc.table_name, kcu.column_name
        """)
        unique_constraints = cursor.fetchall()
        # Handle both tuple and dict cursor results
        schema_info['unique_constraints'] = [
            f"{uc[0]}.{uc[1]}" if isinstance(uc, tuple) else f"{uc['table_name']}.{uc['column_name']}" 
            for uc in unique_constraints
        ]
        
        # 5. Check check constraints
        cursor.execute("""
            SELECT 
                tc.table_name,
                tc.constraint_name,
                cc.check_clause
            FROM information_schema.table_constraints tc
            JOIN information_schema.check_constraints cc 
                ON tc.constraint_name = cc.constraint_name
            WHERE tc.constraint_type = 'CHECK'
                AND tc.table_schema = 'public'
            ORDER BY tc.table_name, tc.constraint_name
        """)
        check_constraints = cursor.fetchall()
        # Handle both tuple and dict cursor results
        schema_info['check_constraints'] = [
            f"{cc[0]}.{cc[1]}: {cc[2]}" if isinstance(cc, tuple) else f"{cc['table_name']}.{cc['constraint_name']}: {cc['check_clause']}" 
            for cc in check_constraints
        ]
        
        # 6. Check indexes
        cursor.execute("""
            SELECT 
                tablename,
                indexname,
                indexdef
            FROM pg_indexes 
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """)
        indexes = cursor.fetchall()
        # Handle both tuple and dict cursor results
        schema_info['indexes'] = [
            f"{idx[0]}.{idx[1]}: {idx[2]}" if isinstance(idx, tuple) else f"{idx['tablename']}.{idx['indexname']}: {idx['indexdef']}" 
            for idx in indexes
        ]
        
        # 7. Check sequences
        cursor.execute("""
            SELECT sequence_name 
            FROM information_schema.sequences 
            WHERE sequence_schema = 'public'
            ORDER BY sequence_name
        """)
        sequences = cursor.fetchall()
        # Handle both tuple and dict cursor results
        schema_info['sequences'] = [seq[0] if isinstance(seq, tuple) else seq['sequence_name'] for seq in sequences]
        
        # 8. Check table row counts
        for table in tables:
            try:
                table_name = table[0] if isinstance(table, tuple) else table['table_name']
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                result = cursor.fetchone()
                count = result[0] if isinstance(result, tuple) else result['count']
                schema_info['row_counts'][table_name] = count
            except Exception as e:
                table_name = table[0] if isinstance(table, tuple) else table['table_name']
                schema_info['row_counts'][table_name] = f"Error: {e}"
        
        # 9. Check specific important data
        try:
            cursor.execute("SELECT COUNT(*) FROM users WHERE user_id = 1")
            result = cursor.fetchone()
            admin_count = result[0] if isinstance(result, tuple) else result['count']
            schema_info['important_data']['admin_user'] = 'Exists' if admin_count > 0 else 'Missing'
        except Exception as e:
            schema_info['important_data']['admin_user'] = f"Error: {e}"
        
        try:
            cursor.execute("SELECT COUNT(*) FROM cities")
            result = cursor.fetchone()
            cities_count = result[0] if isinstance(result, tuple) else result['count']
            schema_info['important_data']['cities'] = cities_count
        except Exception as e:
            schema_info['important_data']['cities'] = f"Error: {e}"
        
        try:
            cursor.execute("SELECT COUNT(*) FROM vat_rates")
            result = cursor.fetchone()
            vat_count = result[0] if isinstance(result, tuple) else result['count']
            schema_info['important_data']['vat_rates'] = vat_count
        except Exception as e:
            schema_info['important_data']['vat_rates'] = f"Error: {e}"
        
        cursor.close()
        conn.close()
        
        return jsonify(schema_info)
        
    except Exception as e:
        import traceback
        error_details = {
            'error': str(e),
            'traceback': traceback.format_exc(),
            'postgresql_detected': is_postgresql()
        }
        return jsonify(error_details), 500

@admin_api.route('/api/admin/db-check')
@admin_required
def db_check():
    """Check database contents"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check users table
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT user_id, email, is_active FROM users ORDER BY user_id")
        users = cursor.fetchall()
        
        # Check user_plans table
        cursor.execute("SELECT COUNT(*) FROM user_plans")
        plan_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT user_id, plan_type, is_active FROM user_plans ORDER BY user_id")
        plans = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'users_count': user_count,
            'users': [{'id': u[0], 'email': u[1], 'active': u[2]} for u in users],
            'plans_count': plan_count,
            'plans': [{'user_id': p[0], 'type': p[1], 'active': p[2]} for p in plans]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

