from flask import Blueprint, jsonify, request, session
from datetime import datetime, timedelta
import logging
import bcrypt
import random
from db.connection import get_db_connection, get_placeholder, execute_query, execute_update
from api.utils import get_current_user_id, log_user_action

auth_api = Blueprint('auth_api', __name__)
logger = logging.getLogger(__name__)

@auth_api.route('/api/auth/login', methods=['POST'])
def auth_login():
    """Handle user login with multiple methods."""
    try:
        data = request.get_json()
        method = data.get('method')
        
        # Log login attempt
        log_user_action("LOGIN_ATTEMPT", None, {
            'method': method,
            'timestamp': datetime.now().isoformat()
        })
        
        conn = get_db_connection()
        
        if method == 'email':
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return jsonify({'success': False, 'message': 'Email and password required'})
            
            placeholder = get_placeholder()
            cursor = execute_query(conn, f'SELECT * FROM users WHERE email = {placeholder} AND is_active = TRUE', (email,))
            user = cursor.fetchone()
            
            if not user:
                return jsonify({'success': False, 'message': 'Invalid email or password'})
            
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return jsonify({'success': False, 'message': 'Invalid email or password'})
                
        elif method == 'mobile':
            mobile = data.get('mobile')
            otp = data.get('otp')
            
            if not mobile or not otp:
                return jsonify({'success': False, 'message': 'Mobile and OTP required'})
            
            # Verify OTP
            placeholder = get_placeholder()
            otp_record = execute_update(conn, f'''
                SELECT * FROM otp_codes 
                WHERE mobile = {placeholder} AND otp_code = {placeholder} AND is_used = 0 AND expires_at > CURRENT_TIMESTAMP
                ORDER BY created_at DESC LIMIT 1
            ''', (mobile, otp)).fetchone()
            
            if not otp_record:
                return jsonify({'success': False, 'message': 'Invalid or expired OTP'})
            
            # Mark OTP as used
            placeholder = get_placeholder()
            execute_update(conn, f'UPDATE otp_codes SET is_used = 1 WHERE id = {placeholder}', (otp_record['id'],))
            
            placeholder = get_placeholder()
            cursor = execute_query(conn, f'SELECT * FROM users WHERE mobile = {placeholder} AND is_active = TRUE', (mobile,))
            user = cursor.fetchone()
            
            if not user:
                return jsonify({'success': False, 'message': 'No account found with this mobile number'})
                
        elif method == 'shop_code':
            shop_code = data.get('shop_code')
            password = data.get('password')
            
            if not shop_code or not password:
                return jsonify({'success': False, 'message': 'Shop code and password required'})
            
            placeholder = get_placeholder()
            cursor = execute_query(conn, f'SELECT * FROM users WHERE shop_code = {placeholder} AND is_active = TRUE', (shop_code,))
            user = cursor.fetchone()
            
            if not user:
                return jsonify({'success': False, 'message': 'Invalid shop code or password'})
            
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return jsonify({'success': False, 'message': 'Invalid shop code or password'})
        else:
            return jsonify({'success': False, 'message': 'Invalid login method'})
        
        # Set session data
        session.permanent = True  # Make session persistent
        session['user_id'] = user['user_id']
        session['shop_name'] = user['shop_name']
        session['shop_code'] = user['shop_code']
        
        # Log successful login
        log_user_action("LOGIN_SUCCESS", user['user_id'], {
            'shop_name': user['shop_name'],
            'shop_code': user['shop_code'],
            'method': method,
            'timestamp': datetime.now().isoformat()
        })
        conn.close()
        
        # Check if there's a redirect destination stored in session
        next_url = session.get('next')
        if next_url:
            # Remove the stored destination
            session.pop('next', None)
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'redirect': next_url,
                'user': {
                    'user_id': user['user_id'],
                    'shop_name': user['shop_name'],
                    'shop_code': user['shop_code']
                }
            })
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'user_id': user['user_id'],
                'shop_name': user['shop_name'],
                'shop_code': user['shop_code']
            }
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'success': False, 'message': 'Login failed. Please try again.'})

@auth_api.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    """Handle user logout."""
    try:
        # Log logout action
        user_id = session.get('user_id')
        if user_id:
            log_user_action("LOGOUT", user_id, {
                'timestamp': datetime.now().isoformat()
            })
        
        # Clear session data
        session.clear()
        
        return jsonify({'success': True, 'message': 'Logout successful'})
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'success': False, 'message': 'Logout failed'}), 500

@auth_api.route('/api/account/password', methods=['PUT'])
def change_password():
    """Change current user's password (requires current password)."""
    try:
        data = request.get_json() or {}
        current_password = (data.get('current_password') or '').strip()
        new_password = (data.get('new_password') or '').strip()

        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401

        if not current_password or not new_password:
            return jsonify({'success': False, 'message': 'Current and new password are required'}), 400

        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'New password must be at least 6 characters'}), 400

        conn = get_db_connection()
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT user_id, password_hash FROM users WHERE user_id = {placeholder} AND is_active = TRUE', (user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return jsonify({'success': False, 'message': 'User not found'}), 404

        if not bcrypt.checkpw(current_password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            conn.close()
            return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400

        new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        placeholder = get_placeholder()
        execute_update(conn, f'UPDATE users SET password_hash = {placeholder}, updated_at = CURRENT_TIMESTAMP WHERE user_id = {placeholder}', (new_hash, user_id))
        conn.close()
        return jsonify({'success': True, 'message': 'Password updated successfully'})
    except Exception as e:
        logger.error(f"Change password error: {e}")
        return jsonify({'success': False, 'message': 'Failed to change password'}), 500

@auth_api.route('/api/change-password', methods=['POST'])
def change_password_post():
    """Change current user's password via POST method (for frontend compatibility)."""
    try:
        data = request.get_json() or {}
        
        current_password = (data.get('current_password') or '').strip()
        new_password = (data.get('new_password') or '').strip()
        
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401

        if not current_password or not new_password:
            return jsonify({'success': False, 'message': 'Current and new password are required'}), 400

        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'New password must be at least 6 characters'}), 400

        conn = get_db_connection()
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT user_id, password_hash FROM users WHERE user_id = {placeholder} AND is_active = TRUE', (user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return jsonify({'success': False, 'message': 'User not found'}), 404

        if not bcrypt.checkpw(current_password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            conn.close()
            return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400

        new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        placeholder = get_placeholder()
        execute_update(conn, f'UPDATE users SET password_hash = {placeholder}, updated_at = CURRENT_TIMESTAMP WHERE user_id = {placeholder}', (new_hash, user_id))
        conn.close()
        return jsonify({'success': True, 'message': 'Password updated successfully'})
    except Exception as e:
        logger.error(f"Change password error: {e}")
        return jsonify({'success': False, 'message': 'Failed to change password'}), 500

@auth_api.route('/api/auth/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to mobile number."""
    try:
        data = request.get_json()
        mobile = data.get('mobile')
        
        if not mobile:
            return jsonify({'success': False, 'message': 'Mobile number required'})
        
        # Generate 6-digit OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Store OTP in database (expires in 10 minutes)
        expires_at = datetime.now() + timedelta(minutes=10)
        
        conn = get_db_connection()
        placeholder = get_placeholder()
        execute_update(conn, f'''
            INSERT INTO otp_codes (mobile, otp_code, expires_at)
            VALUES ({placeholder}, {placeholder}, {placeholder})
        ''', (mobile, otp, expires_at))
        conn.close()
        
        # In production, you would integrate with SMS service here
        # For demo purposes, we'll just return the OTP
        # print(f"OTP for {mobile}: {otp}")
        logger.info(f"OTP for {mobile}: {otp}")
        
        return jsonify({
            'success': True,
            'message': 'OTP sent successfully',
            'otp': otp  # Remove this in production
        })
        
    except Exception as e:
        logger.error(f"Send OTP error: {e}")
        return jsonify({'success': False, 'message': 'Failed to send OTP'})
