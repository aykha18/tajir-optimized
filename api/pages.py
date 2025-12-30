from flask import Blueprint, render_template, request, redirect, url_for, session, send_from_directory, send_file, abort, current_app
import os
import logging
from db.connection import get_db_connection, execute_query, get_placeholder
from api.plans import get_user_plan_info
from api.i18n import get_user_language, translate_text as get_translated_text
from api.utils import get_current_user_id

pages_api = Blueprint('pages_api', __name__)
logger = logging.getLogger(__name__)

@pages_api.route('/')
def index():
    try:
        # Check if user is logged in and user still exists in database
        if 'user_id' in session:
            user_id = session.get('user_id')
            # Verify user still exists in database
            try:
                conn = get_db_connection()
                placeholder = get_placeholder()
                cursor = execute_query(conn, f'SELECT user_id FROM users WHERE user_id = {placeholder}', (user_id,))
                user_exists = cursor.fetchone()
                conn.close()
                
                if user_exists:
                    # Redirect logged-in users to the app
                    return redirect(url_for('pages_api.app_page'))
                else:
                    # User was deleted, clear session
                    session.clear()
            except Exception as db_error:
                print(f"Database error checking user: {db_error}")
                # If database check fails, clear session to be safe
                session.clear()
        
        # Show landing page for non-logged-in users
        return render_template('modern_landing.html')
    except Exception as e:
        print(f"Error in root route: {e}")
        # Clear session and show fallback
        session.clear()
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tajir POS - UAE's Smart Point of Sale System</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <h1>Tajir POS</h1>
            <p>UAE's Smart Point of Sale System</p>
            <p><a href="/home">Go to Home</a></p>
        </body>
        </html>
        """

@pages_api.route('/landing')
def landing():
    user_plan_info = get_user_plan_info()
    return render_template('landing.html', 
                        user_plan_info=user_plan_info,
                        get_user_language=get_user_language,
                        get_translated_text=get_translated_text)

@pages_api.route('/home')
def home():
    return render_template('modern_landing.html')

@pages_api.route('/railway-redirect')
def railway_redirect():
    """Redirect Railway subdomain to custom domain"""
    return redirect('https://tajirtech.com', code=301)

# Serve demo videos
@pages_api.route('/<filename>.mp4')
def serve_video(filename):
    """Serve demo video files"""
    try:
        # Use current_app.root_path to find files
        return send_from_directory(current_app.root_path, f'{filename}.mp4', mimetype='video/mp4')
    except FileNotFoundError:
        abort(404)

# Serve QR code image
@pages_api.route('/URL QR Code.png')
def serve_qr_code():
    """Serve QR code image"""
    try:
        return send_from_directory(current_app.root_path, 'URL QR Code.png', mimetype='image/png')
    except FileNotFoundError:
        abort(404)

@pages_api.route('/favicon.ico')
def favicon():
    """Serve favicon."""
    return send_from_directory(os.path.join(current_app.root_path, 'static/icons'), 'icon-144.png', mimetype='image/png')

@pages_api.route('/app')
def app_page():
    """Main application page - requires authentication."""
    try:
        user_id = get_current_user_id()
        try:
            print(f"App page user_id: {user_id}")
        except Exception:
            pass
        if not user_id:
            # Store the intended destination in session for redirect after login
            session['next'] = request.url
            return redirect(url_for('pages_api.login'))
        
        user_plan_info = get_user_plan_info()
        return render_template('app.html', 
                            user_plan_info=user_plan_info,
                            get_user_language=get_user_language,
                            get_translated_text=get_translated_text)
        
    except Exception as e:
        try:
            logger.exception(f"App page error: {e}")
        except Exception:
            pass
        try:
            print(f"App page error: {e}")
        except Exception:
            pass
        # Store the intended destination in session for redirect after login
        session['next'] = request.url
        return redirect(url_for('pages_api.login'))

@pages_api.route('/pricing')
def pricing():
    user_plan_info = get_user_plan_info()
    return render_template('pricing.html', 
                        user_plan_info=user_plan_info,
                        get_user_language=get_user_language,
                        get_translated_text=get_translated_text)

@pages_api.route('/manifest.json')
def manifest():
    return send_from_directory(os.path.join(current_app.root_path, 'static'), 'manifest.json')

@pages_api.route('/sw.js')
def service_worker():
    response = send_from_directory(os.path.join(current_app.root_path, 'static/js'), 'sw.js')
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@pages_api.route('/app-template')
def app_template():
    return send_from_directory(os.path.join(current_app.root_path, 'templates'), 'app.html')

@pages_api.route('/debug')
def debug():
    return send_file(os.path.join(current_app.root_path, 'debug_css.html'))

@pages_api.route('/pwa-status')
def pwa_status():
    user_plan_info = get_user_plan_info()
    return render_template('pwa-status.html', 
                        user_plan_info=user_plan_info,
                        get_user_language=get_user_language,
                        get_translated_text=get_translated_text)

@pages_api.route('/expenses')
def expenses():
    user_plan_info = get_user_plan_info()
    return render_template('expenses.html', 
                        user_plan_info=user_plan_info,
                        get_user_language=get_user_language,
                        get_translated_text=get_translated_text)

@pages_api.route('/sw-debug')
def sw_debug():
    return send_file(os.path.join(current_app.root_path, 'sw_debug.html'))

@pages_api.route('/cache-clear-test')
def cache_clear_test():
    return send_file(os.path.join(current_app.root_path, 'cache-clear-test.html'))

@pages_api.route('/debug-plan')
def debug_plan():
    """Debug page for plan management."""
    user_plan_info = get_user_plan_info()
    return render_template('debug_plan.html', 
                        user_plan_info=user_plan_info,
                        get_user_language=get_user_language,
                        get_translated_text=get_translated_text)

@pages_api.route('/login')
def login():
    """Login page for multi-tenant system."""
    return render_template('login.html',
                        get_user_language=get_user_language,
                        get_translated_text=get_translated_text)

@pages_api.route('/static/<path:filename>')
def static_with_cache_busting(filename):
    """Serve static files with cache-busting headers."""
    response = send_from_directory(os.path.join(current_app.root_path, 'static'), filename)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    # Add timestamp to force cache refresh
    response.headers['Last-Modified'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
    return response
