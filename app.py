from flask import Flask, render_template, request, jsonify, send_file, session, send_from_directory, redirect, url_for
import sqlite3
import os
import secrets
from datetime import datetime, date, timedelta
import json
from decimal import Decimal
import zipfile
from io import BytesIO
from dotenv import load_dotenv
load_dotenv()
from num2words import num2words
from plan_manager import plan_manager
import csv
from io import StringIO
from flask import Response
import bcrypt
import random
import string
import base64
import qrcode
from io import BytesIO
from PIL import Image
import hashlib
import hmac
import struct
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import re
import logging
import logging.handlers
import traceback
import sys
from pathlib import Path
import pytesseract
from werkzeug.utils import secure_filename

# Try to import PostgreSQL dependencies
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False
    psycopg2 = None
    RealDictCursor = None

# Try to import OpenCV and NumPy, with fallback for Railway deployment
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError as e:
    print(f"OpenCV/NumPy not available: {e}")
    print("OCR will use basic image processing without OpenCV")
    OPENCV_AVAILABLE = False
    cv2 = None
    np = None

# Configure comprehensive logging system
def setup_logging():
    """Setup comprehensive logging for production."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure file logging
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/tajir_pos.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    
    # Configure error file logging
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/errors.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    
    # Configure console logging for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    error_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    file_handler.setFormatter(file_formatter)
    error_handler.setFormatter(error_formatter)
    console_handler.setFormatter(file_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

# Initialize logging
logger = setup_logging()

def log_dml_error(operation, table, error, user_id=None, data=None):
    """Log DML failures to both file and database."""
    try:
        # Log to file
        error_msg = f"DML Error - Operation: {operation}, Table: {table}, Error: {str(error)}"
        if user_id:
            error_msg += f", User: {user_id}"
        if data:
            error_msg += f", Data: {str(data)[:200]}..."  # Truncate data
        
        logger.error(error_msg)
        
        # Log to database (if possible)
        try:
            conn = get_db_connection()
            placeholder = get_placeholder()
            execute_with_returning(conn, f'''
                INSERT INTO error_logs (timestamp, level, operation, table_name, error_message, user_id, data_snapshot)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            ''', (
                datetime.now().isoformat(),
                'ERROR',
                operation,
                table,
                str(error),
                user_id,
                json.dumps(data) if data else None
            ))
            conn.close()
        except Exception as db_log_error:
            # If database logging fails, log to file only
            logger.error(f"Failed to log to database: {db_log_error}")
            
    except Exception as log_error:
        # Fallback to basic logging
        print(f"Logging failed: {log_error}")

def log_user_action(action, user_id=None, details=None):
    """Log user actions for audit trail."""
    try:
        conn = get_db_connection()
        placeholder = get_placeholder()
        execute_update(conn, f'''
            INSERT INTO user_actions (timestamp, action, user_id, details)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
        ''', (
            datetime.now().isoformat(),
            action,
            user_id,
            json.dumps(details) if details else None
        ))
        conn.close()
    except Exception as e:
        logger.error(f"Failed to log user action: {e}")

app = Flask(__name__)
app.config['DATABASE'] = os.getenv('DATABASE_PATH', 'pos_tailor.db')
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))  # Add secret key for sessions



def get_db_connection():
    """Get database connection - supports both SQLite (development) and PostgreSQL (production)"""
    # Check if we should use PostgreSQL (Railway deployment)
    # Prioritize DATABASE_URL (Railway standard), then PG_ variables, then custom POSTGRES_ variables
    database_url = os.getenv('DATABASE_URL')
    pg_host = os.getenv('PGHOST') or os.getenv('POSTGRES_HOST')
    
    if POSTGRESQL_AVAILABLE and (database_url or pg_host):
        try:
            if database_url:
                # Use DATABASE_URL (Railway standard approach)
                # print(f"Connecting using DATABASE_URL")
                conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
            else:
                # Fallback to individual variables
                pg_port = os.getenv('PGPORT') or os.getenv('POSTGRES_PORT', '5432')
                pg_database = os.getenv('PGDATABASE') or os.getenv('POSTGRES_DB', 'tajir_pos')
                pg_user = os.getenv('PGUSER') or os.getenv('POSTGRES_USER', 'postgres')
                pg_password = os.getenv('PGPASSWORD') or os.getenv('POSTGRES_PASSWORD', 'password')
                
                pg_config = {
                    'host': pg_host,
                    'port': pg_port,
                    'database': pg_database,
                    'user': pg_user,
                    'password': pg_password,
                    'cursor_factory': RealDictCursor
                }
                # print(f"Connecting using individual variables")
                conn = psycopg2.connect(**pg_config)
            return conn
        except Exception as e:
            # print(f"PostgreSQL connection failed: {e}")
            # Try to create the database if it doesn't exist
            if "database" in str(e).lower() and "does not exist" in str(e).lower():
                # print("Database doesn't exist, attempting to create it...")
                try:
                    # Connect to default 'postgres' database to create our database
                    if database_url:
                        # Parse DATABASE_URL to get connection details
                        from urllib.parse import urlparse
                        parsed = urlparse(database_url)
                        create_db_config = {
                            'host': parsed.hostname,
                            'port': parsed.port,
                            'database': 'postgres',  # Connect to default database
                            'user': parsed.username,
                            'password': parsed.password
                        }
                    else:
                        create_db_config = {
                            'host': pg_host,
                            'port': pg_port,
                            'database': 'postgres',  # Connect to default database
                            'user': pg_user,
                            'password': pg_password
                        }
                    
                    # Connect to default database and create our database
                    temp_conn = psycopg2.connect(**create_db_config)
                    temp_conn.autocommit = True
                    cursor = temp_conn.cursor()
                    
                    # Get database name
                    db_name = parsed.path[1:] if database_url else pg_database
                    cursor.execute(f"CREATE DATABASE {db_name}")
                    cursor.close()
                    temp_conn.close()
                    
                    # print(f"Database '{db_name}' created successfully!")
                    
                    # Now try to connect to the newly created database
                    if database_url:
                        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
                    else:
                        conn = psycopg2.connect(**pg_config)
                    return conn
                    
                except Exception as create_error:
                    # print(f"Failed to create database: {create_error}")
                    # print("Falling back to SQLite...")
                    pass
            else:
                # print("Falling back to SQLite...")
                pass
    
    # Fallback to SQLite (development)
    conn = sqlite3.connect(app.config['DATABASE'], timeout=20.0)
    conn.row_factory = sqlite3.Row
    return conn

def get_db_integrity_error():
    """Get the appropriate IntegrityError class for the current database"""
    if POSTGRESQL_AVAILABLE and os.getenv('POSTGRES_HOST'):
        return psycopg2.IntegrityError
    else:
        return sqlite3.IntegrityError

def is_postgresql():
    """Check if we're using PostgreSQL"""
    # Check for DATABASE_URL (Railway standard) or Railway's PG_ variables or our custom POSTGRES_ variables
    database_url = os.getenv('DATABASE_URL')
    pg_host = os.getenv('PGHOST') or os.getenv('POSTGRES_HOST')
    is_pg = POSTGRESQL_AVAILABLE and bool(database_url or pg_host)
    # print(f"is_postgresql() check: POSTGRESQL_AVAILABLE={POSTGRESQL_AVAILABLE}, database_url={'set' if database_url else 'not set'}, pg_host={'set' if pg_host else 'not set'}, result={is_pg}")
    return is_pg

def get_placeholder():
    """Get the appropriate placeholder for the current database"""
    return '%s' if is_postgresql() else '?'

def execute_with_returning(conn, sql, params=None):
    """Execute SQL and return the inserted ID for both SQLite and PostgreSQL"""
    if is_postgresql():
        # For PostgreSQL, determine the correct ID column name based on the table
        if sql.strip().upper().startswith('INSERT'):
            # Extract table name from INSERT statement
            table_match = re.search(r'INSERT INTO (\w+)', sql, re.IGNORECASE)
            if table_match:
                table_name = table_match.group(1)
                # Map table names to their ID column names
                id_columns = {
                    'employees': 'employee_id',
                    'customers': 'customer_id',
                    'products': 'product_id',
                    'product_types': 'type_id',
                    'bills': 'bill_id',
                    'bill_items': 'item_id',
                    'expenses': 'expense_id',
                    'expense_categories': 'category_id',
                    'vat_rates': 'vat_id',
                    'user_plans': 'plan_id',
                    'shop_settings': 'setting_id',
                    'users': 'user_id',
                    'otp_codes': 'id',
                    'error_logs': 'id',
                    'user_actions': 'action_id',
                    'recurring_expenses': 'recurring_id'
                }
                id_column = id_columns.get(table_name, 'id')
                
                # Add RETURNING clause if not already present
                if 'RETURNING' not in sql.upper():
                    sql += f' RETURNING {id_column}'
                
                cursor = conn.cursor()
                cursor.execute(sql, params)
                result = cursor.fetchone()
                conn.commit()  # Commit the transaction
                # Handle both dict and tuple results
                if result:
                    if isinstance(result, dict):
                        return result[id_column]
                    else:
                        # For tuple results, return the first element
                        return result[0]
                return None
            else:
                # Fallback to generic 'id' if table name can't be determined
                # For PostgreSQL, we need to determine the correct ID column
                if 'RETURNING' not in sql.upper():
                    # Try to extract table name from INSERT statement
                    if sql.strip().upper().startswith('INSERT INTO'):
                        # Extract table name from INSERT INTO table_name
                        parts = sql.split()
                        if len(parts) >= 3:
                            table_name = parts[2].strip()
                            # Map common table names to their ID columns
                            id_columns = {
                                'employees': 'employee_id',
                                'products': 'product_id', 
                                'customers': 'customer_id',
                                'bills': 'bill_id',
                                'bill_items': 'item_id',
                                'product_types': 'type_id',
                                'vat_rates': 'vat_id',
                                'expense_categories': 'category_id',
                                'expenses': 'expense_id',
                                'user_plans': 'plan_id',
                                'shop_settings': 'setting_id',
                                'users': 'user_id',
                                'otp_codes': 'otp_id',
                                'recurring_expenses': 'recurring_id'
                            }
                            id_column = id_columns.get(table_name.lower(), 'id')
                            sql += f' RETURNING {id_column}'
                        else:
                            sql += ' RETURNING id'
                    else:
                        sql += ' RETURNING id'
                cursor = conn.cursor()
                cursor.execute(sql, params)
                result = cursor.fetchone()
                conn.commit()  # Commit the transaction
                # Determine the correct key to use
                if result:
                    if isinstance(result, dict):
                        keys = list(result.keys())
                        return result[keys[0]] if keys else None
                    else:
                        # For tuple results, return the first element
                        return result[0]
                return None
        else:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()  # Commit the transaction
            return None
    else:
        # For SQLite, use the original approach
        cursor = conn.cursor()
        cursor.execute(sql, params)
        if sql.strip().upper().startswith('INSERT'):
            return cursor.lastrowid
        return None

def execute_query(conn, sql, params=None):
    """Execute a query and return results - works for both SQLite and PostgreSQL"""
    cursor = conn.cursor()
    cursor.execute(sql, params)
    return cursor

def execute_update(conn, sql, params=None):
    """Execute an UPDATE/DELETE statement - works for both SQLite and PostgreSQL"""
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    return cursor.rowcount

def get_current_user_id():
    """Get current user_id from session, fallback to 1 for backward compatibility."""
    # For testing purposes, return user_id 2 since that's where the bills are
    return session.get('user_id', 2)

def get_user_plan_info():
    """Get current user plan information and shop settings for template rendering."""
    try:
        user_id = get_current_user_id()
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
        
        # Map plan types to display names
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
        print(f"Error getting user plan: {e}")
        return {
            'plan_type': 'trial',
            'plan_name': 'Tajir Trial',
            'plan_display_name': 'Tajir Trial',
            'shop_settings': None
        }

def init_db():
    need_init = False
    if is_postgresql():
        # For PostgreSQL, check if tables exist
        try:
            conn = get_db_connection()
            cursor = execute_query(conn, "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'product_types'")
            result = cursor.fetchone()
            # Handle both PostgreSQL (dict) and SQLite (tuple) results
            count = result[0] if isinstance(result, tuple) else result['count']
            if count == 0:
                need_init = True
                # print("PostgreSQL detected - tables don't exist, initializing database...")
            else:
                # print("PostgreSQL detected - tables already exist, skipping initialization")
                pass
            conn.close()
        except Exception as e:
            # Table doesn't exist, need to initialize
            need_init = True
            # print(f"PostgreSQL detected - error checking tables: {e}, initializing database...")
    else:
        # For SQLite, check if database file exists
        if not os.path.exists(app.config['DATABASE']):
            need_init = True
        else:
            # Check if main tables are empty
            conn = get_db_connection()
            try:
                cursor = execute_query(conn, "SELECT COUNT(*) FROM product_types")
                result = cursor.fetchone()
                # Handle both PostgreSQL (dict) and SQLite (tuple) results
                count = result[0] if isinstance(result, tuple) else result['count']
                if count == 0:
                    need_init = True
            except Exception:
                # Table doesn't exist, need to initialize
                need_init = True
            conn.close()
    
    if need_init:
        # Choose the appropriate schema file based on database type
        pg_check = is_postgresql()
        print(f"Database type check: is_postgresql() = {pg_check}")
        print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")
        print(f"PGHOST: {os.getenv('PGHOST', 'Not set')}")
        print(f"POSTGRESQL_AVAILABLE: {POSTGRESQL_AVAILABLE}")
        
        if is_postgresql():
            schema_file = 'database_schema_postgresql.sql'
            print(f"Using PostgreSQL schema: {schema_file}")
        else:
            schema_file = 'database_schema.sql'
            print(f"Using SQLite schema: {schema_file}")
        
        try:
            with open(schema_file, 'r') as f:
                schema = f.read()
        except FileNotFoundError:
            print(f"Schema file {schema_file} not found, using default schema")
            schema_file = 'database_schema.sql'
            with open(schema_file, 'r') as f:
                schema = f.read()
        
        conn = get_db_connection()
        try:
            if is_postgresql():
                # For PostgreSQL, execute statements one by one
                statements = schema.split(';')
                cursor = conn.cursor()
                print(f"Executing {len(statements)} statements from schema file...")
                executed_count = 0
                for i, statement in enumerate(statements):
                    statement = statement.strip()
                    print(f"Statement {i+1} (length: {len(statement)}): {statement[:50]}...")
                    
                    # Skip empty statements
                    if not statement:
                        print(f"Skipping statement {i+1} (empty)")
                        continue
                    
                    # Skip pure comment statements (lines that are only comments)
                    if statement.startswith('--') and not any(keyword in statement.upper() for keyword in ['CREATE', 'INSERT', 'ALTER', 'DROP', 'SELECT', 'UPDATE', 'DELETE']):
                        print(f"Skipping statement {i+1} (pure comment)")
                        continue
                    
                    # Execute the statement
                    try:
                        print(f"Executing statement {i+1}: {statement[:100]}...")
                        cursor.execute(statement)
                        executed_count += 1
                        print(f"✅ Statement {i+1} executed successfully")
                    except Exception as stmt_error:
                        print(f"❌ Warning: Failed to execute statement {i+1}: {stmt_error}")
                        print(f"Statement: {statement}")
                        # Continue with other statements
                
                print(f"Successfully executed {executed_count} statements")
                conn.commit()  # Commit the transaction
                cursor.close()
                
                # Verify tables were created
                try:
                    verify_cursor = conn.cursor()
                    verify_cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                    tables = verify_cursor.fetchall()
                    print(f"Tables created: {[table[0] for table in tables]}")
                    verify_cursor.close()
                except Exception as verify_error:
                    print(f"Error verifying tables: {verify_error}")
                
                print(f"PostgreSQL database initialized successfully using {schema_file}")
            else:
                # For SQLite, use executescript
                conn.executescript(schema)
                print("SQLite database initialized successfully")
            logger.info("Database initialized successfully with logging tables")
        except Exception as e:
            log_dml_error("INIT", "database", e)
            print(f"Database initialization error: {e}")
            # Don't raise the error, just log it and continue
        finally:
            conn.close()
        print("Database initialization completed!")
        
        # Setup admin user after tables are created
        try:
            from setup_production_admin import setup_production_admin
            setup_production_admin()
            logger.info("Admin user setup completed")
        except Exception as e:
            logger.error(f"Failed to setup admin user: {e}")
    
    # Always clean up corrupted data, regardless of whether initialization was needed
    try:
        conn = get_db_connection()
        cleanup_corrupted_data(conn)
        conn.close()
    except Exception as e:
        print(f"Warning: Failed to clean up corrupted data: {e}")
    
    # If no initialization was needed, still ensure admin user exists
    # But only if this is the first time init_db() is called
    if not need_init and not hasattr(init_db, '_admin_setup_done'):
        try:
            from setup_production_admin import setup_production_admin
            setup_production_admin()
            logger.info("Admin user setup completed")
            init_db._admin_setup_done = True
        except Exception as e:
            logger.error(f"Failed to setup admin user: {e}")


def cleanup_corrupted_data(conn):
    """Clean up corrupted data in the database."""
    try:
        cursor = conn.cursor()
        
        # Fix corrupted dates in expenses table
        if is_postgresql():
            # For PostgreSQL, update invalid dates to current date
            cursor.execute("""
                UPDATE expenses 
                SET expense_date = CURRENT_DATE 
                WHERE expense_date IS NULL 
                   OR expense_date < '1900-01-01' 
                   OR expense_date > '2100-12-31'
            """)
            
            # Reset sequence if needed
            cursor.execute("SELECT setval('expenses_expense_id_seq', (SELECT COALESCE(MAX(expense_id), 1) FROM expenses))")
            
        else:
            # For SQLite, update invalid dates
            cursor.execute("""
                UPDATE expenses 
                SET expense_date = date('now') 
                WHERE expense_date IS NULL 
                   OR expense_date < '1900-01-01' 
                   OR expense_date > '2100-12-31'
            """)
        
        conn.commit()
        print("✓ Corrupted data cleaned up successfully")
        
    except Exception as e:
        print(f"⚠ Warning: Failed to clean up corrupted data: {e}")
        conn.rollback()


@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Add HSTS header for HTTPS
    if request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Add comprehensive CSP header
    csp_policy = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://unpkg.com https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https://images.unsplash.com https://*.unsplash.com; "
        "connect-src 'self' https://cdn.tailwindcss.com https://fonts.googleapis.com https://fonts.gstatic.com https://unpkg.com https://cdn.jsdelivr.net https://images.unsplash.com https://*.unsplash.com; "
        "worker-src 'self' blob:; "
        "child-src 'self' blob:;"
    )
    response.headers['Content-Security-Policy'] = csp_policy
    
    return response

@app.route('/')
def index():
    user_plan_info = get_user_plan_info()
    return render_template('index.html', 
                        user_plan_info=user_plan_info,
                        get_user_language=get_user_language,
                        get_translated_text=get_translated_text)

@app.route('/landing')
def landing():
    user_plan_info = get_user_plan_info()
    return render_template('landing.html', 
                        user_plan_info=user_plan_info,
                        get_user_language=get_user_language,
                        get_translated_text=get_translated_text)

@app.route('/')
def modern_landing():
    return render_template('modern_landing.html')

@app.route('/home')
def home():
    return render_template('modern_landing.html')

@app.route('/setup-wizard')
def setup_wizard():
    user_plan_info = get_user_plan_info()
    return render_template('setup_wizard.html', 
                        user_plan_info=user_plan_info,
                        get_user_language=get_user_language,
                        get_translated_text=get_translated_text)

# Serve demo videos
@app.route('/<filename>.mp4')
def serve_video(filename):
    """Serve demo video files"""
    try:
        return send_from_directory('.', f'{filename}.mp4', mimetype='video/mp4')
    except FileNotFoundError:
        abort(404)

# Serve QR code image
@app.route('/URL QR Code.png')
def serve_qr_code():
    """Serve QR code image"""
    try:
        return send_from_directory('.', 'URL QR Code.png', mimetype='image/png')
    except FileNotFoundError:
        abort(404)

@app.route('/favicon.ico')
def favicon():
    """Serve favicon."""
    return send_from_directory('static/icons', 'icon-144.png', mimetype='image/png')

@app.route('/app')
def app_page():
    user_plan_info = get_user_plan_info()
    return render_template('app.html', 
                        user_plan_info=user_plan_info,
                        get_user_language=get_user_language,
                        get_translated_text=get_translated_text)









@app.route('/pricing')
def pricing():
    user_plan_info = get_user_plan_info()
    return render_template('pricing.html', 
                        user_plan_info=user_plan_info,
                        get_user_language=get_user_language,
                        get_translated_text=get_translated_text)

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    response = send_from_directory('static/js', 'sw.js')
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/app-template')
def app_template():
    return send_from_directory('templates', 'app.html')

@app.route('/debug')
def debug():
    return send_file('debug_css.html')



@app.route('/pwa-status')
def pwa_status():
    user_plan_info = get_user_plan_info()
    return render_template('pwa-status.html', 
                        user_plan_info=user_plan_info,
                        get_user_language=get_user_language,
                        get_translated_text=get_translated_text)

@app.route('/expenses')
def expenses():
    user_plan_info = get_user_plan_info()
    return render_template('expenses.html', 
                        user_plan_info=user_plan_info,
                        get_user_language=get_user_language,
                        get_translated_text=get_translated_text)

@app.route('/sw-debug')
def sw_debug():
    return send_file('sw_debug.html')

@app.route('/cache-clear-test')
def cache_clear_test():
    return send_file('cache-clear-test.html')





# Product Types API
@app.route('/api/product-types', methods=['GET'])
def get_product_types():
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'SELECT * FROM product_types WHERE user_id = {placeholder} ORDER BY type_name', (user_id,))
    types = cursor.fetchall()
    conn.close()
    return jsonify([dict(type) for type in types])

@app.route('/api/product-types', methods=['POST'])
def add_product_type():
    data = request.get_json()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip() if data.get('description') else None
    user_id = get_current_user_id()
    
    if not name:
        return jsonify({'error': 'Type name is required'}), 400
    
    conn = get_db_connection()
    try:
        placeholder = get_placeholder()
        sql = f'INSERT INTO product_types (user_id, type_name, description) VALUES ({placeholder}, {placeholder}, {placeholder})'
        type_id = execute_with_returning(conn, sql, (user_id, name, description))
        conn.close()
        return jsonify({'id': type_id, 'name': name, 'description': description, 'message': 'Product type added successfully'})
    except get_db_integrity_error():
        conn.close()
        return jsonify({'error': 'Product type already exists'}), 400

@app.route('/api/product-types/<int:type_id>', methods=['DELETE'])
def delete_product_type(type_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    # Check if products exist for this type
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'SELECT COUNT(*) FROM products WHERE type_id = {placeholder} AND user_id = {placeholder}', (type_id, user_id))
    result = cursor.fetchone()
    # Handle both PostgreSQL (dict) and SQLite (tuple) results
    products = result[0] if isinstance(result, tuple) else result['count']
    if products > 0:
        conn.close()
        return jsonify({'error': 'Cannot delete type with existing products'}), 400
    
    placeholder = get_placeholder()
    execute_update(conn, f'DELETE FROM product_types WHERE type_id = {placeholder} AND user_id = {placeholder}', (type_id, user_id))
    conn.close()
    return jsonify({'message': 'Product type deleted successfully'})

# Products API
@app.route('/api/products', methods=['GET'])
def get_products():
    user_id = get_current_user_id()
    search = request.args.get('search', '').strip()
    barcode = request.args.get('barcode', '').strip()
    conn = get_db_connection()
    if barcode:
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT p.*, pt.type_name 
            FROM products p 
            JOIN product_types pt ON p.type_id = pt.type_id 
            WHERE p.user_id = {placeholder} AND pt.user_id = {placeholder} AND p.is_active = TRUE AND p.barcode = {placeholder}
            ORDER BY pt.type_name, p.product_name
        ''', (user_id, user_id, barcode))
        products = cursor.fetchall()
    elif search:
        like_search = f"%{search}%"
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT p.*, pt.type_name 
            FROM products p 
            JOIN product_types pt ON p.type_id = pt.type_id 
            WHERE p.user_id = {placeholder} AND pt.user_id = {placeholder} AND p.is_active = TRUE AND (p.product_name LIKE {placeholder} OR pt.type_name LIKE {placeholder})
            ORDER BY pt.type_name, p.product_name
        ''', (user_id, user_id, like_search, like_search))
        products = cursor.fetchall()
    else:
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT p.*, pt.type_name 
            FROM products p 
            JOIN product_types pt ON p.type_id = pt.type_id 
            WHERE p.user_id = {placeholder} AND pt.user_id = {placeholder} AND p.is_active = TRUE 
            ORDER BY pt.type_name, p.product_name
        ''', (user_id, user_id))
        products = cursor.fetchall()
    conn.close()
    return jsonify([dict(product) for product in products])

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.get_json()
    type_id = data.get('type_id')
    name = data.get('name', '').strip()
    rate = data.get('rate')
    description = data.get('description', '').strip()
    barcode = (data.get('barcode') or '').strip()
    user_id = get_current_user_id()
    
    if not all([type_id, name, rate]):
        return jsonify({'error': 'Type, name, and rate are required'}), 400
    
    try:
        rate = float(rate)
        if rate <= 0:
            return jsonify({'error': 'Rate must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid rate value'}), 400
    
    conn = get_db_connection()
    try:
        # Verify the product type belongs to current user
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT type_id FROM product_types WHERE type_id = {placeholder} AND user_id = {placeholder}', (type_id, user_id))
        type_check = cursor.fetchone()
        if not type_check:
            conn.close()
            return jsonify({'error': 'Invalid product type'}), 400
            
        placeholder = get_placeholder()
        sql = f'''
            INSERT INTO products (user_id, type_id, product_name, rate, description, barcode) 
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        '''
        product_id = execute_with_returning(conn, sql, (user_id, type_id, name, rate, description, barcode or None))
        conn.close()
        return jsonify({'id': product_id, 'message': 'Product added successfully'})
    except get_db_integrity_error():
        conn.close()
        return jsonify({'error': 'Product already exists'}), 400

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'''
        SELECT p.*, pt.type_name 
        FROM products p 
        JOIN product_types pt ON p.type_id = pt.type_id 
        WHERE p.product_id = {placeholder} AND p.user_id = {placeholder} AND pt.user_id = {placeholder} AND p.is_active = TRUE
    ''', (product_id, user_id, user_id))
    product = cursor.fetchone()
    conn.close()
    
    if product:
        return jsonify(dict(product))
    else:
        return jsonify({'error': 'Product not found'}), 404

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    name = data.get('product_name', '').strip()
    rate = data.get('rate')
    type_id = data.get('type_id')
    description = data.get('description', '').strip()
    barcode = (data.get('barcode') or '').strip()
    user_id = get_current_user_id()
    
    if not all([name, rate, type_id]):
        return jsonify({'error': 'Name, rate, and type are required'}), 400
    
    try:
        rate = float(rate)
        if rate <= 0:
            return jsonify({'error': 'Rate must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid rate value'}), 400
    
    conn = get_db_connection()
    # Verify the product and type belong to current user
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'SELECT product_id FROM products WHERE product_id = {placeholder} AND user_id = {placeholder}', (product_id, user_id))
    product_check = cursor.fetchone()
    cursor = execute_query(conn, f'SELECT type_id FROM product_types WHERE type_id = {placeholder} AND user_id = {placeholder}', (type_id, user_id))
    type_check = cursor.fetchone()
    
    if not product_check:
        conn.close()
        return jsonify({'error': 'Product not found'}), 404
    if not type_check:
        conn.close()
        return jsonify({'error': 'Invalid product type'}), 400
        
    placeholder = get_placeholder()
    execute_update(conn, f'''
        UPDATE products 
        SET product_name = {placeholder}, rate = {placeholder}, type_id = {placeholder}, description = {placeholder}, barcode = {placeholder} 
        WHERE product_id = {placeholder} AND user_id = {placeholder}
    ''', (name, rate, type_id, description, barcode or None, product_id, user_id))
    conn.close()
    return jsonify({'message': 'Product updated successfully'})

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    # Use TRUE/FALSE for PostgreSQL, 1/0 for SQLite
    is_active_value = 'FALSE' if is_postgresql() else '0'
    execute_update(conn, f'UPDATE products SET is_active = {is_active_value} WHERE product_id = {placeholder} AND user_id = {placeholder}', (product_id, user_id))
    conn.close()
    return jsonify({'message': 'Product deleted successfully'})

# Customers API
@app.route('/api/customers', methods=['GET'])
def get_customers():
    user_id = get_current_user_id()
    phone = request.args.get('phone')
    search = request.args.get('search', '').strip()
    conn = get_db_connection()
    if phone:
        # Normalize phone by removing common non-digit characters for comparison
        import re as _re
        phone_digits = _re.sub(r'\D', '', phone)
        placeholder = get_placeholder()
        cursor = execute_query(conn, f"""
            SELECT * FROM customers 
            WHERE user_id = {placeholder} AND 
                  REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(phone, ' ', ''), '-', ''), '(', ''), ')', ''), '+', '') = {placeholder} AND
                  is_active = TRUE
            """,
            (user_id, phone_digits)
        )
        customers = cursor.fetchall()
    elif search:
        like_search = f"%{search}%"
        placeholder = get_placeholder()
        # Use ILIKE for case-insensitive search in PostgreSQL, fallback to LOWER() for SQLite
        if POSTGRESQL_AVAILABLE and (os.getenv('DATABASE_URL') or os.getenv('POSTGRES_HOST')):
            # PostgreSQL - use ILIKE for case-insensitive search
            cursor = execute_query(conn, f'SELECT * FROM customers WHERE user_id = {placeholder} AND (name ILIKE {placeholder} OR phone ILIKE {placeholder} OR business_name ILIKE {placeholder}) AND is_active = TRUE ORDER BY name', (user_id, like_search, like_search, like_search))
        else:
            # SQLite - use LOWER() for case-insensitive search
            cursor = execute_query(conn, f'SELECT * FROM customers WHERE user_id = {placeholder} AND (LOWER(name) LIKE LOWER({placeholder}) OR LOWER(phone) LIKE LOWER({placeholder}) OR LOWER(business_name) LIKE LOWER({placeholder})) AND is_active = TRUE ORDER BY name', (user_id, like_search, like_search, like_search))
        customers = cursor.fetchall()
    else:
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT * FROM customers WHERE user_id = {placeholder} AND is_active = TRUE ORDER BY name', (user_id,))
        customers = cursor.fetchall()
    conn.close()
    return jsonify([dict(customer) for customer in customers])

@app.route('/api/customers', methods=['POST'])
def add_customer():
    data = request.get_json()
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    trn = data.get('trn', '').strip()
    city = data.get('city', '').strip()
    area = data.get('area', '').strip()
    email = data.get('email', '').strip()
    address = data.get('address', '').strip()
    customer_type = data.get('customer_type', 'Individual').strip()
    business_name = data.get('business_name', '').strip()
    business_address = data.get('business_address', '').strip()
    user_id = get_current_user_id()
    
    if not name:
        return jsonify({'error': 'Customer name is required'}), 400
    if not phone:
        return jsonify({'error': 'Customer mobile is required'}), 400
    # Enforce 9-10 digits for mobile
    phone_digits = re.sub(r'\D', '', phone)
    if len(phone_digits) < 9 or len(phone_digits) > 10:
        return jsonify({'error': 'Customer mobile must be 9-10 digits'}), 400
    
    # Validate customer type
    if customer_type not in ['Individual', 'Business']:
        return jsonify({'error': 'Customer type must be Individual or Business'}), 400
    
    # For Business customers, require business name
    if customer_type == 'Business' and not business_name:
        return jsonify({'error': 'Business name is required for Business customers'}), 400
    
    conn = get_db_connection()
    
    # Check for duplicate phone number (normalize stored values)
    if phone_digits:
        placeholder = get_placeholder()
        cursor = execute_query(conn,
            f"""
            SELECT name FROM customers 
            WHERE user_id = {placeholder} AND 
                  REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(phone, ' ', ''), '-', ''), '(', ''), ')', ''), '+', '') = {placeholder}
            """,
            (user_id, phone_digits)
        )
        existing_customer = cursor.fetchone()
        if existing_customer:
            conn.close()
            return jsonify({'error': f'Phone number {phone} is already assigned to customer "{existing_customer["name"]}"'}), 400
    
    try:
        placeholder = get_placeholder()
        sql = f'''
            INSERT INTO customers (user_id, name, phone, trn, city, area, email, address, customer_type, business_name, business_address) 
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        '''
        customer_id = execute_with_returning(conn, sql, (user_id, name, phone_digits, trn, city, area, email, address, customer_type, business_name, business_address))
        conn.close()
        return jsonify({'id': customer_id, 'message': 'Customer added successfully'})
    except get_db_integrity_error():
        conn.close()
        return jsonify({'error': 'Customer already exists'}), 400

@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'SELECT * FROM customers WHERE customer_id = {placeholder} AND user_id = {placeholder}', (customer_id, user_id))
    customer = cursor.fetchone()
    conn.close()
    
    if customer:
        return jsonify(dict(customer))
    else:
        return jsonify({'error': 'Customer not found'}), 404

@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.get_json()
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    trn = data.get('trn', '').strip()
    city = data.get('city', '').strip()
    area = data.get('area', '').strip()
    email = data.get('email', '').strip()
    address = data.get('address', '').strip()
    customer_type = data.get('customer_type', 'Individual').strip()
    business_name = data.get('business_name', '').strip()
    business_address = data.get('business_address', '').strip()
    user_id = get_current_user_id()
    
    if not name:
        return jsonify({'error': 'Customer name is required'}), 400
    
    # Validate customer type
    if customer_type not in ['Individual', 'Business']:
        return jsonify({'error': 'Customer type must be Individual or Business'}), 400
    
    # For Business customers, require business name
    if customer_type == 'Business' and not business_name:
        return jsonify({'error': 'Business name is required for Business customers'}), 400
    
    conn = get_db_connection()
    
    # Enforce 9-10 digits for mobile
    phone_digits = re.sub(r'\D', '', phone)
    if phone and (len(phone_digits) < 9 or len(phone_digits) > 10):
        conn.close()
        return jsonify({'error': 'Customer mobile must be 9-10 digits'}), 400

    # Check for duplicate phone number (excluding current customer, normalized)
    if phone_digits:
        placeholder = get_placeholder()
        cursor = execute_query(conn,
            f"""
            SELECT name FROM customers 
            WHERE user_id = {placeholder} AND customer_id != {placeholder} AND 
                  REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(phone, ' ', ''), '-', ''), '(', ''), ')', ''), '+', '') = {placeholder}
            """,
            (user_id, customer_id, phone_digits)
        )
        existing_customer = cursor.fetchone()
        if existing_customer:
            conn.close()
            return jsonify({'error': f'Phone number {phone} is already assigned to customer "{existing_customer["name"]}"'}), 400
    
    placeholder = get_placeholder()
    sql = f'''
        UPDATE customers 
        SET name = {placeholder}, phone = {placeholder}, trn = {placeholder}, city = {placeholder}, area = {placeholder}, email = {placeholder}, address = {placeholder}, 
            customer_type = {placeholder}, business_name = {placeholder}, business_address = {placeholder}
        WHERE customer_id = {placeholder} AND user_id = {placeholder}
    '''
    execute_update(conn, sql, (name, phone_digits, trn, city, area, email, address, customer_type, business_name, business_address, customer_id, user_id))
    conn.close()
    return jsonify({'message': 'Customer updated successfully'})

@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    # Use TRUE/FALSE for PostgreSQL, 1/0 for SQLite
    is_active_value = 'FALSE' if is_postgresql() else '0'
    execute_update(conn, f'UPDATE customers SET is_active = {is_active_value} WHERE customer_id = {placeholder} AND user_id = {placeholder}', (customer_id, user_id))
    conn.close()
    return jsonify({'message': 'Customer deleted successfully'})

@app.route('/api/customers/recent', methods=['GET'])
def get_recent_customers():
    """Get the last 3 customers used in bills for quick selection."""
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        
        # Get the last 3 unique customers from bills, ordered by most recent
        placeholder = get_placeholder()
        query = f"""
            SELECT c.customer_id, c.name, c.phone, c.city, c.area, c.trn, 
                   c.customer_type, c.business_name, c.business_address, 
                   MAX(b.bill_date) as latest_bill_date, MAX(b.bill_id) as latest_bill_id
            FROM customers c
            INNER JOIN bills b ON c.customer_id = b.customer_id
            WHERE c.user_id = {placeholder} AND b.user_id = {placeholder}
            GROUP BY c.customer_id, c.name, c.phone, c.city, c.area, c.trn, 
                     c.customer_type, c.business_name, c.business_address
            ORDER BY latest_bill_date DESC, latest_bill_id DESC
            LIMIT 3
        """
        
        cursor = execute_query(conn, query, (user_id, user_id))
        recent_customers = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        customers_list = []
        for customer in recent_customers:
            customers_list.append({
                'customer_id': customer['customer_id'],
                'name': customer['name'],
                'phone': customer['phone'],
                'city': customer['city'],
                'area': customer['area'],
                'trn': customer['trn'],
                'customer_type': customer['customer_type'],
                'business_name': customer['business_name'],
                'business_address': customer['business_address']
            })
        
        return jsonify(customers_list)
    except Exception as e:
        print(f"Error getting recent customers: {e}")
        return jsonify({'error': str(e)}), 500

# VAT Rates API
@app.route('/api/vat-rates', methods=['GET'])
def get_vat_rates():
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'SELECT * FROM vat_rates WHERE user_id = {placeholder} AND is_active = TRUE ORDER BY effective_from DESC', (user_id,))
    rates = cursor.fetchall()
    conn.close()
    return jsonify([dict(rate) for rate in rates])

@app.route('/api/vat-rates', methods=['POST'])
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
    # Check for duplicate effective_from and effective_to
    placeholder = get_placeholder()
    cursor = execute_query(conn,
        f'SELECT 1 FROM vat_rates WHERE user_id = {placeholder} AND effective_from = {placeholder} AND effective_to = {placeholder} AND is_active = TRUE',
        (user_id, effective_from, effective_to)
    )
    exists = cursor.fetchone()
    if exists:
        conn.close()
        return jsonify({'error': 'A VAT rate with the same effective dates already exists.'}), 400
    # Update previous active row's effective_to if needed
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

@app.route('/api/vat-rates/<int:vat_id>', methods=['DELETE'])
def delete_vat_rate(vat_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    # Use TRUE/FALSE for PostgreSQL, 1/0 for SQLite
    is_active_value = 'FALSE' if is_postgresql() else '0'
    execute_update(conn, f'UPDATE vat_rates SET is_active = {is_active_value} WHERE vat_id = {placeholder} AND user_id = {placeholder}', (vat_id, user_id))
    conn.close()
    return jsonify({'message': 'VAT rate deleted successfully'})

# Bills API
@app.route('/api/bills', methods=['GET'])
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

@app.route('/api/bills', methods=['POST'])
def create_bill():
    print("DEBUG: create_bill endpoint called")
    user_id = get_current_user_id()
    
    # Log user action for bill creation
    try:
        log_user_action("CREATE_BILL_ATTEMPT", user_id, {
            'timestamp': datetime.now().isoformat(),
            'endpoint': '/api/bills'
        })
    except Exception as log_error:
        print(f"Failed to log user action: {log_error}")
    
    conn = None
    
    # Pre-fix sequences to prevent 500 errors
    if is_postgresql():
        try:
            temp_conn = get_db_connection()
            # Fix bills sequence
            execute_query(temp_conn, "SELECT setval(pg_get_serial_sequence('bills','bill_id'), COALESCE((SELECT MAX(bill_id) FROM bills),0)+1, false)")
            # Fix bill_items sequence
            execute_query(temp_conn, "SELECT setval(pg_get_serial_sequence('bill_items','item_id'), COALESCE((SELECT MAX(item_id) FROM bill_items),0)+1, false)")
            temp_conn.close()
            print("DEBUG: Pre-fixed sequences for bills and bill_items")
        except Exception as seq_error:
            print(f"DEBUG: Failed to pre-fix sequences: {seq_error}")
    
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
            print(f"DEBUG: JSON data received: {data}")
            
            # Extract bill data from JSON
            bill_data = data.get('bill', {})
            items_data = data.get('items', [])
            notes = bill_data.get('notes', '').strip()
            
            if not items_data:
                return jsonify({'error': 'At least one item is required'}), 400
            
            # Validate required customer mobile
            customer_phone = (bill_data.get('customer_phone') or '').strip()
            if not customer_phone:
                return jsonify({'error': 'Customer mobile is required'}), 400

            # Check for master_id (Master Name) - make it optional for now
            print(f"DEBUG: master_id received: {bill_data.get('master_id')} (type: {type(bill_data.get('master_id'))})")
            master_id = bill_data.get('master_id')
            
            # If no master is selected, try to get the first available employee as default
            if not master_id:
                try:
                    conn = get_db_connection()
                    placeholder = get_placeholder()
                    cursor = execute_query(conn, f'SELECT employee_id FROM employees WHERE user_id = {placeholder} AND is_active = TRUE ORDER BY name LIMIT 1', (user_id,))
                    default_employee = cursor.fetchone()
                    conn.close()
                    
                    if default_employee:
                        master_id = default_employee['employee_id']
                        print(f"DEBUG: Using default master_id: {master_id}")
                    else:
                        print("DEBUG: No employees found, master_id will be None")
                except Exception as e:
                    print(f"DEBUG: Error getting default master: {e}")
                    master_id = None
            
            # Use totals calculated by frontend instead of recalculating
            subtotal = float(bill_data.get('subtotal', 0))
            vat_amount = float(bill_data.get('vat_amount', 0))
            total_amount = float(bill_data.get('total_amount', 0))
            advance_paid = float(bill_data.get('advance_paid', 0))
            balance_amount = float(bill_data.get('balance_amount', 0))
            vat_percent = 5.0  # Keep this for bill item calculations
            
            # Get or create customer
            conn = get_db_connection()
            
            # Check if customer exists
            placeholder = get_placeholder()
            cursor = execute_query(conn,
                f'SELECT customer_id FROM customers WHERE phone = {placeholder} AND user_id = {placeholder}', 
                (re.sub(r'\D', '', customer_phone), user_id)
            )
            existing_customer = cursor.fetchone()
            
            if existing_customer:
                customer_id = existing_customer['customer_id']
            else:
                # Create new customer
                placeholder = get_placeholder()
                sql = f'''
                    INSERT INTO customers (user_id, name, phone, trn, city, area, customer_type, business_name, business_address) 
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                '''
                customer_id = execute_with_returning(conn, sql, (
                    user_id, bill_data.get('customer_name', ''),
                    re.sub(r'\D', '', customer_phone),
                    bill_data.get('customer_trn', ''),
                    bill_data.get('customer_city', ''),
                    bill_data.get('customer_area', ''),
                    bill_data.get('customer_type', 'Individual'),
                    bill_data.get('business_name', ''),
                    bill_data.get('business_address', '')
                ))
                
                # Automatically enroll new customer in loyalty program
                try:
                    import random
                    import string
                    referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                    
                    placeholder = get_placeholder()
                    execute_update(conn, f'''
                        INSERT INTO customer_loyalty (
                            user_id, customer_id, tier_level, referral_code, 
                            total_points, available_points, lifetime_points, join_date, is_active
                        ) VALUES ({placeholder}, {placeholder}, 'Bronze', {placeholder}, 
                                 0, 0, 0, CURRENT_DATE, true)
                    ''', (user_id, customer_id, referral_code))
                    print(f"DEBUG: Auto-enrolled new customer {customer_id} in loyalty program")
                except Exception as enroll_error:
                    print(f"DEBUG: Failed to auto-enroll customer: {enroll_error}")
                    # Continue with bill creation even if enrollment fails
            
            # Create bill with retry logic for duplicate bill numbers
            bill_uuid = str(uuid.uuid4())
            max_retries = 3
            bill_created = False
            
            for attempt in range(max_retries):
                try:
                    # Generate a unique bill number if needed
                    bill_number = bill_data.get('bill_number', '').strip()
                    if not bill_number or attempt > 0:
                        # If no bill number provided or retrying, generate a new bill number
                        today = datetime.now().strftime('%Y%m%d')
                        import time
                        timestamp = int(time.time() * 1000) % 10000
                        bill_number = f'BILL-{today}-{timestamp:04d}'
                    
                    placeholder = get_placeholder()
                    sql = f'''
                        INSERT INTO bills (
                            user_id, bill_number, customer_id, customer_name, customer_phone, 
                            customer_city, customer_area, customer_trn, customer_type, business_name, business_address,
                            uuid, bill_date, delivery_date, payment_method, subtotal, vat_amount, total_amount, 
                            advance_paid, balance_amount, status, master_id, trial_date, notes
                        ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                    '''
                    # Handle date fields with validation and defaults
                    bill_date = bill_data.get('bill_date', '').strip()
                    delivery_date = bill_data.get('delivery_date', '').strip()
                    trial_date = bill_data.get('trial_date', '').strip()
                    
                    # Set default dates if empty
                    if not bill_date:
                        bill_date = datetime.now().strftime('%Y-%m-%d')
                    if not delivery_date:
                        delivery_date = datetime.now().strftime('%Y-%m-%d')
                    if not trial_date:
                        trial_date = datetime.now().strftime('%Y-%m-%d')
                    
                    bill_id = execute_with_returning(conn, sql, (
                        user_id, bill_number, customer_id, bill_data.get('customer_name'),
                        re.sub(r'\D', '', customer_phone), bill_data.get('customer_city'),
                        bill_data.get('customer_area'), bill_data.get('customer_trn', ''),
                        bill_data.get('customer_type', 'Individual'), bill_data.get('business_name', ''),
                        bill_data.get('business_address', ''), bill_uuid, bill_date, 
                        delivery_date, bill_data.get('payment_method', 'Cash'),
                        subtotal, vat_amount, total_amount, advance_paid, balance_amount,
                        'Pending', master_id, trial_date, notes
                    ))
                    bill_created = True
                    break
                    
                except get_db_integrity_error() as e:
                    # Always rollback on integrity error to reset transaction state
                    conn.rollback()
                    
                    if "UNIQUE constraint failed: bills.user_id, bills.bill_number" in str(e):
                        if attempt == max_retries - 1:
                            # Last attempt failed
                            conn.close()
                            return jsonify({'error': 'Failed to create bill due to duplicate bill number. Please try again.'}), 500
                        # Continue to next attempt
                        continue
                    elif "bills_pkey" in str(e) or "duplicate key value violates unique constraint \"bills_pkey\"" in str(e):
                        # Sequence mismatch: auto-heal by syncing sequence to MAX(bill_id)+1 and retry
                        try:
                            # Fix sequence outside of transaction
                            execute_query(conn, "SELECT setval(pg_get_serial_sequence('bills','bill_id'), COALESCE((SELECT MAX(bill_id) FROM bills),0)+1, false)")
                            # bill_items primary key is item_id in Postgres
                            execute_query(conn, "SELECT setval(pg_get_serial_sequence('bill_items','item_id'), COALESCE((SELECT MAX(item_id) FROM bill_items),0)+1, false)")
                            print(f"DEBUG: Fixed sequence, retrying attempt {attempt + 1}")
                        except Exception as seq_err:
                            print(f"DEBUG: Failed to auto-fix sequence: {seq_err}")
                        # retry next loop attempt
                        continue
                    else:
                        # Other integrity error
                        conn.close()
                        return jsonify({'error': f'Database error: {str(e)}'}), 500
                except Exception as e:
                    conn.rollback()
                    conn.close()
                    # Log detailed error for production debugging
                    error_msg = f'Error creating bill: {str(e)}'
                    print(f"DEBUG: {error_msg}")
                    try:
                        log_user_action("CREATE_BILL_ERROR", user_id, {
                            'error': str(e),
                            'timestamp': datetime.now().isoformat(),
                            'bill_data': str(bill_data)[:500]  # Truncate for logging
                        })
                    except Exception as log_error:
                        print(f"DEBUG: Failed to log error: {log_error}")
                    return jsonify({'error': error_msg}), 500
            
            if not bill_created:
                conn.rollback()
                conn.close()
                return jsonify({'error': 'Failed to create bill after multiple attempts'}), 500
            
            # print(f"DEBUG: Created bill_id: {bill_id}")
            # print(f"DEBUG: Notes saved to database: '{notes}'")
            
            # Best-effort: sync bill_items sequence before inserting items (Postgres only)
            try:
                execute_query(conn, "SELECT setval(pg_get_serial_sequence('bill_items','item_id'), COALESCE((SELECT MAX(item_id) FROM bill_items),0)+1, false)")
            except Exception:
                pass

            # Insert bill items
            for item in items_data:
                # Calculate VAT for each item
                item_rate = float(item.get('rate', 0))
                item_quantity = float(item.get('quantity', 1))
                item_discount_percent = float(item.get('discount', 0))
                item_subtotal_before_discount = item_rate * item_quantity
                item_discount_amount = item_subtotal_before_discount * (item_discount_percent / 100)
                item_subtotal = item_subtotal_before_discount - item_discount_amount
                item_vat_amount = item_subtotal * (vat_percent / 100)
                item_total_amount = item_subtotal + item_vat_amount
                
                placeholder = get_placeholder()
                sql = f'''
                INSERT INTO bill_items (
                    user_id, bill_id, product_id, product_name, quantity, 
                    rate, discount, vat_amount, advance_paid, total_amount
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            '''
                try:
                    execute_with_returning(conn, sql, (
                user_id, bill_id,
                item.get('product_id'),
                item.get('product_name'),
                item.get('quantity', 1),
                item.get('rate', 0),
                item_discount_percent,  # Store discount percentage
                item_vat_amount,
                item.get('advance_paid', 0),
                item_total_amount
            ))
                except get_db_integrity_error() as e:
                    # Heal bill_items sequence and retry once if PK collision
                    conn.rollback()
                    try:
                        execute_query(conn, "SELECT setval(pg_get_serial_sequence('bill_items','item_id'), COALESCE((SELECT MAX(item_id) FROM bill_items),0)+1, false)")
                    except Exception:
                        pass
                    execute_with_returning(conn, sql, (
                        user_id, bill_id,
                        item.get('product_id'),
                        item.get('product_name'),
                        item.get('quantity', 1),
                        item.get('rate', 0),
                        item_discount_percent,
                        item_vat_amount,
                        item.get('advance_paid', 0),
                        item_total_amount
                    ))
            
            # Process loyalty points if customer is enrolled
            loyalty_points_earned = 0
            if customer_id:
                try:
                    # Check if customer is enrolled in loyalty program
                    cursor = execute_query(conn, f'''
                        SELECT cl.customer_id, cl.tier_level, cl.available_points,
                               lc.points_per_currency
                        FROM customer_loyalty cl
                        LEFT JOIN loyalty_config lc ON cl.user_id = lc.user_id
                        WHERE cl.user_id = {placeholder} AND cl.customer_id = {placeholder}
                    ''', (user_id, customer_id))
                    
                    loyalty_info = cursor.fetchone()
                    
                    if loyalty_info and loyalty_info['customer_id']:
                        # Calculate points earned
                        points_per_currency = float(loyalty_info['points_per_currency'] or 1.0)
                        loyalty_points_earned = int(total_amount * points_per_currency)
                        
                        # Get tier multiplier
                        cursor = execute_query(conn, f'''
                            SELECT bonus_points_multiplier FROM loyalty_tiers 
                            WHERE user_id = {placeholder} AND tier_level = {placeholder}
                        ''', (user_id, loyalty_info['tier_level']))
                        
                        tier_info = cursor.fetchone()
                        if tier_info:
                            multiplier = float(tier_info['bonus_points_multiplier'] or 1.0)
                            loyalty_points_earned = int(loyalty_points_earned * multiplier)
                        
                        # Add points transaction
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
                        
                        # Update customer loyalty profile
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
                        
                        # Check for tier upgrade
                        cursor = execute_query(conn, f'''
                            SELECT tier_level, points_threshold FROM loyalty_tiers 
                            WHERE user_id = {placeholder} AND points_threshold <= {placeholder}
                            ORDER BY points_threshold DESC LIMIT 1
                        ''', (user_id, new_available_points))
                        
                        new_tier = cursor.fetchone()
                        if new_tier and new_tier['tier_level'] != loyalty_info['tier_level']:
                            execute_update(conn, f'''
                                UPDATE customer_loyalty SET tier_level = {placeholder} 
                                WHERE customer_id = {placeholder}
                            ''', (new_tier['tier_level'], loyalty_info['customer_id']))
                            
                            # Add tier upgrade bonus
                            execute_update(conn, f'''
                                INSERT INTO loyalty_transactions (
                                    user_id, customer_id, transaction_type, 
                                    points_earned, description
                                ) VALUES ({placeholder}, {placeholder}, 'bonus', 100, {placeholder})
                            ''', (
                                user_id, 
                                customer_id,
                                f'Tier upgrade bonus to tier {new_tier["tier_id"]}'
                            ))
                            
                            # Update current points with bonus
                            execute_update(conn, f'''
                                UPDATE customer_loyalty SET 
                                    current_points = current_points + 100
                                WHERE loyalty_id = {placeholder}
                            ''', (loyalty_info['loyalty_id']))
                            
                            loyalty_points_earned += 100
                            
                except Exception as loyalty_error:
                    print(f"Loyalty processing error: {loyalty_error}")
                    # Continue with bill creation even if loyalty processing fails
            
            print(f"DEBUG: Bill creation completed successfully")
            return jsonify({
                'success': True, 
                'bill_id': bill_id,
                'bill_number': bill_number,
                'loyalty_points_earned': loyalty_points_earned
            })
            
        else:
            # Handle form data
            print(f"DEBUG: Form data received: {dict(request.form)}")
            
            # Extract form data
            customer_name = request.form.get('customer_name', '').strip()
            customer_phone = request.form.get('customer_phone', '').strip()
            customer_city = request.form.get('customer_city', '').strip()
            customer_area = request.form.get('customer_area', '').strip()
            bill_date = request.form.get('bill_date', '')
            delivery_date = request.form.get('delivery_date', '')
            trial_date = request.form.get('trial_date', '')
            payment_method = request.form.get('payment_method', 'Cash')
            master_id = request.form.get('master_id', '')
            notes = request.form.get('notes', '').strip()
            
            print(f"DEBUG: Extracted notes: '{notes}'")
            print(f"DEBUG: Notes type: {type(notes)}")
            print(f"DEBUG: Notes length: {len(notes) if notes else 0}")
            
            # Get items from request
            items_data = request.form.get('items', '[]')
            items = json.loads(items_data) if items_data else []
            
            print(f"DEBUG: Items count: {len(items)}")
            
            if not items:
                return jsonify({'error': 'At least one item is required'}), 400

            # Validate required customer mobile for form submission
            if not customer_phone:
                return jsonify({'error': 'Customer mobile is required'}), 400
            
            # Calculate totals with discount
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
            
            print(f"DEBUG: Calculated totals - subtotal: {subtotal}, total: {total_amount}, balance: {balance_amount}")
            
            # Get or create customer
            conn = get_db_connection()
            
            # Check if customer exists
            placeholder = get_placeholder()
            cursor = execute_query(conn,
                f"""
                SELECT customer_id FROM customers 
                WHERE user_id = {placeholder} AND 
                      REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(phone, ' ', ''), '-', ''), '(', ''), ')', ''), '+', '') = {placeholder}
                """,
                (user_id, re.sub(r'\D', '', customer_phone))
            )
            existing_customer = cursor.fetchone()
            
            if existing_customer:
                customer_id = existing_customer['customer_id']
                print(f"DEBUG: Using existing customer_id: {customer_id}")
            else:
                # Create new customer
                placeholder = get_placeholder()
                sql = f'''
                    INSERT INTO customers (user_id, name, phone, city, area) 
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                '''
                customer_id = execute_with_returning(conn, sql, (user_id, customer_name, customer_phone, customer_city, customer_area))
                print(f"DEBUG: Created new customer_id: {customer_id}")
            
            # Create bill with retry logic for duplicate bill numbers
            bill_uuid = str(uuid.uuid4())
            max_retries = 3
            bill_created = False
            
            for attempt in range(max_retries):
                try:
                    # Generate a unique bill number if needed
                    bill_number = request.form.get('bill_number', '').strip()
                    if not bill_number or attempt > 0:
                        # If no bill number provided or retrying, generate a new bill number
                        today = datetime.now().strftime('%Y%m%d')
                        import time
                        timestamp = int(time.time() * 1000) % 10000
                        bill_number = f'BILL-{today}-{timestamp:04d}'
                    
                    placeholder = get_placeholder()
                    sql = f'''
                        INSERT INTO bills (
                            user_id, bill_number, customer_id, customer_name, customer_phone, 
                            customer_city, customer_area, uuid, bill_date, delivery_date, 
                            payment_method, subtotal, vat_amount, total_amount, 
                            advance_paid, balance_amount, status, master_id, trial_date, notes
                        ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                    '''
                    bill_id = execute_with_returning(conn, sql, (
                        user_id, bill_number, customer_id, customer_name, customer_phone,
                        customer_city, customer_area, bill_uuid, bill_date, delivery_date,
                        payment_method, subtotal, vat_amount, total_amount,
                        advance_paid, balance_amount, 'Pending', master_id, trial_date, notes
                    ))
                    bill_created = True
                    break
                    
                except get_db_integrity_error() as e:
                    # Always rollback on integrity error to reset transaction state
                    conn.rollback()
                    
                    if "UNIQUE constraint failed: bills.user_id, bills.bill_number" in str(e):
                        if attempt == max_retries - 1:
                            # Last attempt failed
                            conn.close()
                            return jsonify({'error': 'Failed to create bill due to duplicate bill number. Please try again.'}), 500
                        # Continue to next attempt
                        continue
                    elif "bills_pkey" in str(e) or "duplicate key value violates unique constraint \"bills_pkey\"" in str(e):
                        # Sequence mismatch: auto-heal by syncing sequence to MAX(bill_id)+1 and retry
                        try:
                            # Fix sequence outside of transaction
                            execute_query(conn, "SELECT setval(pg_get_serial_sequence('bills','bill_id'), COALESCE((SELECT MAX(bill_id) FROM bills),0)+1, false)")
                            execute_query(conn, "SELECT setval(pg_get_serial_sequence('bill_items','id'), COALESCE((SELECT MAX(id) FROM bill_items),0)+1, false)")
                            print(f"DEBUG: Fixed sequence, retrying attempt {attempt + 1}")
                        except Exception as seq_err:
                            print(f"DEBUG: Failed to auto-fix sequence: {seq_err}")
                        # retry next loop attempt
                        continue
                    else:
                        # Other integrity error
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
            
            print(f"DEBUG: Created bill_id: {bill_id}")
            print(f"DEBUG: Notes saved to database: '{notes}'")
            
            # Insert bill items
            for item in items:
                # Calculate discount amount from percentage
                item_rate = float(item.get('rate', 0))
                item_quantity = float(item.get('quantity', 1))
                item_discount_percent = float(item.get('discount', 0))
                item_subtotal_before_discount = item_rate * item_quantity
                item_discount_amount = item_subtotal_before_discount * (item_discount_percent / 100)
                item_subtotal = item_subtotal_before_discount - item_discount_amount
                item_vat_amount = item_subtotal * (vat_percent / 100)
                item_total_amount = item_subtotal + item_vat_amount
                
                placeholder = get_placeholder()
                sql = f'''
                    INSERT INTO bill_items (bill_id, product_name, quantity, rate, discount, vat_amount, advance_paid, total_amount)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                '''
                execute_with_returning(conn, sql, (
                    bill_id, item.get('product_name', ''), 
                    item.get('quantity', 1), item.get('rate', 0),
                    item_discount_percent, item_vat_amount, item.get('advance_paid', 0), item_total_amount
                ))
            

            
            print(f"DEBUG: Bill creation completed successfully")
            return jsonify({
                'success': True, 
                'bill_id': bill_id,
                'bill_number': bill_number,
                'loyalty_points_earned': loyalty_points_earned
            })
        
    except Exception as e:
        print(f"DEBUG: Error in create_bill: {e}")
        import traceback
        traceback.print_exc()
        
        # Log DML error
        log_dml_error("CREATE", "bills", e, user_id, {
            'customer_name': customer_name if 'customer_name' in locals() else None,
            'total_amount': total_amount if 'total_amount' in locals() else None,
            'item_count': len(items) if 'items' in locals() else 0
        })
        
        # Rollback transaction if connection exists
        if conn:
            try:
                conn.rollback()
            except:
                pass
        return jsonify({'error': str(e)}), 500
    finally:
        # Always close the connection
        if conn:
            try:
                conn.close()
            except:
                pass

@app.route('/api/bills/<int:bill_id>', methods=['GET'])
def get_bill(bill_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    # Get bill details
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
    
    # Get bill items
    cursor = execute_query(conn, f'''
        SELECT * FROM bill_items WHERE bill_id = {placeholder} AND user_id = {placeholder}
    ''', (bill_id, user_id))
    items = cursor.fetchall()
    
    conn.close()
    
    return jsonify({
        'bill': bill,
        'items': [dict(item) for item in items]
    })

@app.route('/api/bills/<int:bill_id>', methods=['DELETE'])
def delete_bill(bill_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    execute_update(conn, f'DELETE FROM bill_items WHERE bill_id = {placeholder} AND user_id = {placeholder}', (bill_id, user_id))
    execute_update(conn, f'DELETE FROM bills WHERE bill_id = {placeholder} AND user_id = {placeholder}', (bill_id, user_id))
    conn.close()
    return jsonify({'message': 'Bill deleted successfully'})

@app.route('/api/bills/<int:bill_id>/payment', methods=['PUT'])
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
    placeholder = get_placeholder()
    sql = f'UPDATE bills SET advance_paid = {placeholder}, balance_amount = {placeholder}, status = {placeholder} WHERE bill_id = {placeholder} AND user_id = {placeholder}'
    execute_update(conn, sql, (new_advance, new_balance, new_status, bill_id, user_id))
    cursor = execute_query(conn, f'SELECT * FROM bills WHERE bill_id = {placeholder} AND user_id = {placeholder}', (bill_id, user_id))
    updated = cursor.fetchone()
    conn.close()
    return jsonify({'bill': dict(updated)})

# Dashboard API
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    # Get total revenue
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'''
        SELECT COALESCE(SUM(total_amount), 0) as total 
        FROM bills 
        WHERE DATE(bill_date) = DATE('now') AND user_id = {placeholder}
    ''', (user_id,))
    result = cursor.fetchone()
    total_revenue = result[0] if isinstance(result, tuple) else result['total']
    
    # Get total bills today
    cursor = execute_query(conn, f'''
        SELECT COUNT(*) as count 
        FROM bills 
        WHERE DATE(bill_date) = DATE('now') AND user_id = {placeholder}
    ''', (user_id,))
    result = cursor.fetchone()
    total_bills_today = result[0] if isinstance(result, tuple) else result['count']
    
    # Get pending bills
    cursor = execute_query(conn, f'''
        SELECT COUNT(*) as count 
        FROM bills 
        WHERE status = 'Pending' AND user_id = {placeholder}
    ''', (user_id,))
    result = cursor.fetchone()
    pending_bills = result[0] if isinstance(result, tuple) else result['count']
    
    # Get total customers
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'SELECT COUNT(*) as count FROM customers WHERE user_id = {placeholder}', (user_id,))
    result = cursor.fetchone()
    total_customers = result[0] if isinstance(result, tuple) else result['count']
    
    # Get total expenses today
    cursor = execute_query(conn, f'''
        SELECT COALESCE(SUM(amount), 0) as total 
        FROM expenses 
        WHERE DATE(expense_date) = DATE('now') AND user_id = {placeholder}
    ''', (user_id,))
    result = cursor.fetchone()
    total_expenses_today = result[0] if isinstance(result, tuple) else result['total']
    
    # Get total expenses this month
    if is_postgresql():
        cursor = execute_query(conn, f'''
        SELECT COALESCE(SUM(amount), 0) as total 
        FROM expenses 
            WHERE TO_CHAR(expense_date, 'YYYY-MM') = TO_CHAR(CURRENT_DATE, 'YYYY-MM') AND user_id = {placeholder}
        ''', (user_id,))
    else:
        cursor = execute_query(conn, f'''
            SELECT COALESCE(SUM(amount), 0) as total 
            FROM expenses 
            WHERE strftime('%Y-%m', expense_date) = strftime('%Y-%m', 'now') AND user_id = {placeholder}
        ''', (user_id,))
    result = cursor.fetchone()
    total_expenses_month = result[0] if isinstance(result, tuple) else result['total']
    
    # Get monthly revenue data
    if is_postgresql():
        cursor = execute_query(conn, f'''
            SELECT TO_CHAR(bill_date, 'YYYY-MM') as month, 
                   SUM(total_amount) as revenue
            FROM bills 
            WHERE bill_date >= CURRENT_DATE - INTERVAL '6 months' AND user_id = {placeholder}
            GROUP BY TO_CHAR(bill_date, 'YYYY-MM')
            ORDER BY month
        ''', (user_id,))
    else:
        cursor = execute_query(conn, f'''
        SELECT strftime('%Y-%m', bill_date) as month, 
               SUM(total_amount) as revenue
        FROM bills 
            WHERE bill_date >= date('now', '-6 months') AND user_id = {placeholder}
        GROUP BY strftime('%Y-%m', bill_date)
        ORDER BY month
        ''', (user_id,))
    monthly_revenue = cursor.fetchall()
    
    # Get monthly expenses data
    if is_postgresql():
        cursor = execute_query(conn, f'''
            SELECT TO_CHAR(expense_date, 'YYYY-MM') as month, 
                   SUM(amount) as expenses
            FROM expenses 
            WHERE expense_date >= CURRENT_DATE - INTERVAL '6 months' AND user_id = {placeholder}
            GROUP BY TO_CHAR(expense_date, 'YYYY-MM')
            ORDER BY month
        ''', (user_id,))
    else:
        cursor = execute_query(conn, f'''
        SELECT strftime('%Y-%m', expense_date) as month, 
               SUM(amount) as expenses
        FROM expenses 
            WHERE expense_date >= date('now', '-6 months') AND user_id = {placeholder}
        GROUP BY strftime('%Y-%m', expense_date)
        ORDER BY month
        ''', (user_id,))
    monthly_expenses = cursor.fetchall()

    # Top 10 regions by sales (for pie chart)
    cursor = execute_query(conn, f'''
        SELECT COALESCE(customer_area, 'Unknown') as area, SUM(total_amount) as sales
        FROM bills
        WHERE customer_area IS NOT NULL AND customer_area != '' AND user_id = {placeholder}
        GROUP BY customer_area
        ORDER BY sales DESC
        LIMIT 10
    ''', (user_id,))
    top_regions = cursor.fetchall()

    # Top 10 trending products (by quantity sold)
    cursor = execute_query(conn, f'''
        SELECT COALESCE(product_name, 'Unknown') as product_name, 
               SUM(quantity) as qty_sold,
               SUM(total_amount) as total_revenue
        FROM bill_items
        WHERE product_name IS NOT NULL AND product_name != '' AND user_id = {placeholder}
        GROUP BY product_name
        ORDER BY qty_sold DESC
        LIMIT 10
    ''', (user_id,))
    trending_products = cursor.fetchall()

    # Top 10 most repeated customers (by invoice count)
    cursor = execute_query(conn, f'''
        SELECT COALESCE(customer_name, 'Unknown') as customer_name, 
               COALESCE(customer_phone, '') as customer_phone, 
               COUNT(*) as invoice_count,
               SUM(total_amount) as total_revenue
        FROM bills
        WHERE customer_name IS NOT NULL AND customer_name != '' AND user_id = {placeholder}
        GROUP BY customer_name, customer_phone
        ORDER BY invoice_count DESC
        LIMIT 10
    ''', (user_id,))
    repeated_customers = cursor.fetchall()

    conn.close()
    
    return jsonify({
        'total_revenue': float(total_revenue),
        'total_bills_today': total_bills_today,
        'pending_bills': pending_bills,
        'total_customers': total_customers,
        'total_expenses_today': float(total_expenses_today),
        'total_expenses_month': float(total_expenses_month),
        'monthly_revenue': [dict(item) for item in monthly_revenue],
        'monthly_expenses': [dict(item) for item in monthly_expenses],
        'top_regions': [dict(item) for item in top_regions],
        'trending_products': [dict(item) for item in trending_products],
        'repeated_customers': [dict(item) for item in repeated_customers]
    })

# Print bill
@app.route('/api/bills/<int:bill_id>/print', methods=['GET'])
def print_bill(bill_id):
    user_id = get_current_user_id()
    print(f"DEBUG: print_bill called for bill_id: {bill_id}")
    
    conn = get_db_connection()
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'''
        SELECT b.*, c.name as customer_name, c.phone as customer_phone, 
               c.city as customer_city, c.area as customer_area,
               c.customer_type, c.business_name, c.business_address,
               e.name as master_name
        FROM bills b
        LEFT JOIN customers c ON b.customer_id = c.customer_id AND c.user_id = b.user_id
        LEFT JOIN employees e ON b.master_id = e.employee_id AND e.user_id = b.user_id
        WHERE b.bill_id = {placeholder} AND b.user_id = {placeholder}
    ''', (bill_id, user_id))
    bill = cursor.fetchone()
    
    if not bill:
        conn.close()
        return jsonify({'error': 'Bill not found'}), 404
    
    # Get bill items
    cursor = execute_query(conn, f'''
        SELECT * FROM bill_items WHERE bill_id = {placeholder} AND user_id = {placeholder}
    ''', (bill_id, user_id))
    items = cursor.fetchall()
    
    # Calculate discount amount for each item
    items_with_discount = []
    for item in items:
        item_dict = dict(item)
        # Calculate discount amount: (rate * quantity * discount_percentage) / 100
        discount_amount = (float(item_dict['rate']) * float(item_dict['quantity']) * float(item_dict['discount'])) / 100
        item_dict['discount_amount'] = round(discount_amount, 2)
        items_with_discount.append(item_dict)
    
    # Get shop settings
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'SELECT * FROM shop_settings WHERE user_id = {placeholder}', (user_id,))
    shop_settings = cursor.fetchone()
    conn.close()
    
    bill = dict(bill)
    shop_settings = dict(shop_settings) if shop_settings else {}
    print(f"DEBUG: Retrieved bill data: {bill}")
    print(f"DEBUG: Bill notes from database: '{bill.get('notes')}'")
    print(f"DEBUG: Notes type: {type(bill.get('notes'))}")
    
    # Generate amount_in_words for the balance_amount
    try:
        amount = float(bill.get('balance_amount', 0))
        dirhams = int(amount)
        fils = int(round((amount - dirhams) * 100))
        if fils > 0:
            amount_in_words = f"{num2words(dirhams, lang='en').capitalize()} Dirhams and {num2words(fils, lang='en')} Fils Only"
        else:
            amount_in_words = f"{num2words(dirhams, lang='en').capitalize()} Dirhams Only"
        
        # Generate Arabic amount in words
        arabic_amount_in_words = number_to_arabic_words(amount)
    except Exception as e:
        print(f"DEBUG: Error calculating amount in words: {e}")
        amount_in_words = ''
        arabic_amount_in_words = ''
    
    print(f"DEBUG: Final amount_in_words: {amount_in_words}")
    print(f"DEBUG: Final arabic_amount_in_words: {arabic_amount_in_words}")
    print(f"DEBUG: Template variables - bill.notes: '{bill.get('notes')}', amount_in_words: '{amount_in_words}'")
    
    # Generate QR code for FTA compliance
    try:
        seller_name = shop_settings.get('shop_name', 'Tajir')
        seller_trn = shop_settings.get('trn', 'N/A')
        invoice_number = bill.get('bill_number', 'N/A')
        timestamp = bill.get('bill_date', datetime.now().strftime('%Y-%m-%d'))
        total_with_vat = float(bill.get('total_amount', 0))
        vat_amount = float(bill.get('vat_amount', 0))
        
        qr_code_base64 = generate_zatca_qr_code(
            seller_name, seller_trn, invoice_number, timestamp, 
            total_with_vat, vat_amount
        )
    except Exception as e:
        print(f"DEBUG: Error generating QR code: {e}")
        qr_code_base64 = None
    
    # Get summary data
    bill_date = bill.get('bill_date', datetime.now().date())
    if isinstance(bill_date, str):
        bill_date = datetime.strptime(bill_date, '%Y-%m-%d').date()
    summary_data = get_invoice_summary_data(user_id, bill_date)
    
    return render_template('print_bill.html', 
                         bill=bill, 
                         items=items_with_discount,
                         amount_in_words=amount_in_words,
                         arabic_amount_in_words=arabic_amount_in_words,
                         qr_code_base64=qr_code_base64,
                         shop_settings=shop_settings,
                         summary_data=summary_data,
                         get_user_language=get_user_language,
                         get_translated_text=get_translated_text)

@app.route('/api/customer-invoice-heatmap', methods=['GET'])
def customer_invoice_heatmap():
    user_id = get_current_user_id()
    conn = get_db_connection()
    # Get last 6 months (including current)
    placeholder = get_placeholder()
    months = [row['month'] for row in execute_update(conn, f"""
        SELECT DISTINCT strftime('%Y-%m', bill_date) as month
        FROM bills
        WHERE bill_date >= date('now', '-5 months', 'start of month') AND user_id = {placeholder}
        ORDER BY month ASC
    """, (user_id,)).fetchall()]

    # Get customers with at least one invoice in the last 6 months
    customers = execute_update(conn, f"""
        SELECT c.customer_id, c.name, COUNT(b.bill_id) as total_invoices
        FROM customers c
        JOIN bills b ON c.customer_id = b.customer_id AND c.user_id = b.user_id
        WHERE b.bill_date >= date('now', '-5 months', 'start of month') AND b.user_id = {placeholder}
        GROUP BY c.customer_id, c.name
        ORDER BY total_invoices DESC
    """, (user_id,)).fetchall()
    customer_ids = [row['customer_id'] for row in customers]
    customer_names = [row['name'] for row in customers]

    # Build matrix: rows=customers, cols=months
    matrix = []
    for cid in customer_ids:
        row = []
        for m in months:
            cursor = execute_query(conn, f"""
                SELECT COUNT(*) FROM bills
                WHERE customer_id = {placeholder} AND strftime('%Y-%m', bill_date) = {placeholder} AND user_id = {placeholder}
            """, (cid, m, user_id))
            result = cursor.fetchone()
            # Handle both PostgreSQL (dict) and SQLite (tuple) results
            count = result[0] if isinstance(result, tuple) else result['count']
            row.append(count)
        matrix.append(row)
    conn.close()
    return jsonify({
        'customers': customer_names,
        'months': months,
        'matrix': matrix
    })

@app.route('/api/areas', methods=['GET'])
def get_areas():
    city = request.args.get('city', '').strip()
    conn = get_db_connection()
    
    if city:
        # Get areas for specific city
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
        # Get all areas
        cursor = execute_query(conn, 'SELECT area_name FROM city_area ORDER BY area_name')
        areas = cursor.fetchall()
    
    conn.close()
    return jsonify([row['area_name'] for row in areas])

@app.route('/api/cities', methods=['GET'])
def get_cities():
    area = request.args.get('area', '').strip()
    conn = get_db_connection()
    
    if area:
        # Get cities for specific area
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
        # Get all cities
        cursor = execute_query(conn, 'SELECT city_name FROM cities ORDER BY city_name')
        cities = cursor.fetchall()
    
    conn.close()
    return jsonify([row['city_name'] for row in cities])

# Employees API
@app.route('/api/employees', methods=['GET'])
def get_employees():
    user_id = get_current_user_id()
    search = request.args.get('search', '').strip()
    conn = get_db_connection()
    
    placeholder = get_placeholder()
    if search:
        like_search = f"%{search}%"
        cursor = execute_query(conn, f'SELECT * FROM employees WHERE user_id = {placeholder} AND (name LIKE {placeholder} OR phone LIKE {placeholder} OR address LIKE {placeholder}) AND is_active = TRUE ORDER BY name', (user_id, like_search, like_search, like_search))
        employees = cursor.fetchall()
    else:
        cursor = execute_query(conn, f'SELECT * FROM employees WHERE user_id = {placeholder} AND is_active = TRUE ORDER BY name', (user_id,))
        employees = cursor.fetchall()
    
    conn.close()
    return jsonify([dict(emp) for emp in employees])

@app.route('/api/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'SELECT * FROM employees WHERE employee_id = {placeholder} AND user_id = {placeholder} AND is_active = TRUE', (employee_id, user_id))
    employee = cursor.fetchone()
    conn.close()
    
    if employee:
        return jsonify(dict(employee))
    else:
        return jsonify({'error': 'Employee not found'}), 404

@app.route('/api/employees', methods=['POST'])
def add_employee():
    data = request.get_json()
    name = data.get('name', '').strip()
    mobile = data.get('mobile', '').strip()
    address = data.get('address', '').strip()
    # Accept optional role/position
    position = (data.get('position') or data.get('role') or '').strip()
    user_id = get_current_user_id()
    
    if not name:
        return jsonify({'error': 'Employee name is required'}), 400
    
    conn = get_db_connection()
    
    # Check for duplicate mobile number
    if mobile:
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT name FROM employees WHERE phone = {placeholder} AND user_id = {placeholder} AND is_active = TRUE', (mobile, user_id))
        existing_employee = cursor.fetchone()
        if existing_employee:
            conn.close()
            return jsonify({'error': f'Mobile number {mobile} is already assigned to employee "{existing_employee["name"]}"'}), 400
    
    # Insert with optional position; fallback if legacy DB lacks column
    placeholder = get_placeholder()
    try:
        sql = f'INSERT INTO employees (user_id, name, phone, address, position) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})'
        emp_id = execute_with_returning(conn, sql, (user_id, name, mobile, address, position))
    except Exception as e:
        if 'no such column' in str(e).lower() and 'position' in str(e).lower():
            # Legacy DB without position column
            sql = f'INSERT INTO employees (user_id, name, phone, address) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})'
            emp_id = execute_with_returning(conn, sql, (user_id, name, mobile, address))
        else:
            log_dml_error('INSERT', 'employees', e, user_id=user_id, data=data)
            conn.close()
            return jsonify({'error': 'Failed to add employee'}), 500
    conn.close()
    return jsonify({'id': emp_id, 'message': 'Employee added successfully'})

@app.route('/api/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    data = request.get_json()
    name = data.get('name', '').strip()
    mobile = data.get('mobile', '').strip()
    address = data.get('address', '').strip()
    # Accept optional role/position
    position = (data.get('position') or data.get('role') or '').strip()
    user_id = get_current_user_id()
    
    if not name:
        return jsonify({'error': 'Employee name is required'}), 400
    
    conn = get_db_connection()
    
    # Check for duplicate mobile number (excluding current employee)
    if mobile:
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'SELECT name FROM employees WHERE phone = {placeholder} AND user_id = {placeholder} AND employee_id != {placeholder} AND is_active = TRUE', (mobile, user_id, employee_id))
        existing_employee = cursor.fetchone()
        if existing_employee:
            conn.close()
            return jsonify({'error': f'Mobile number {mobile} is already assigned to employee "{existing_employee["name"]}"'}), 400
    
    try:
        placeholder = get_placeholder()
        sql = f'UPDATE employees SET name = {placeholder}, phone = {placeholder}, address = {placeholder}, position = {placeholder} WHERE employee_id = {placeholder} AND user_id = {placeholder}'
        execute_update(conn, sql, (name, mobile, address, position, employee_id, user_id))
    except Exception as e:
        if 'no such column' in str(e).lower() and 'position' in str(e).lower():
            # Legacy DB without position column
            conn.rollback()
            placeholder = get_placeholder()
            sql = f'UPDATE employees SET name = {placeholder}, phone = {placeholder}, address = {placeholder} WHERE employee_id = {placeholder} AND user_id = {placeholder}'
            execute_update(conn, sql, (name, mobile, address, employee_id, user_id))
        else:
            conn.rollback()
            log_dml_error('UPDATE', 'employees', e, user_id=user_id, data=data)
            conn.close()
            return jsonify({'error': 'Failed to update employee'}), 500
    conn.close()
    return jsonify({'message': 'Employee updated successfully'})

@app.route('/api/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    # Use TRUE/FALSE for PostgreSQL, 1/0 for SQLite
    is_active_value = 'FALSE' if is_postgresql() else '0'
    execute_update(conn, f'UPDATE employees SET is_active = {is_active_value} WHERE employee_id = {placeholder} AND user_id = {placeholder}', (employee_id, user_id))
    conn.close()
    return jsonify({'message': 'Employee deleted successfully'})

@app.route('/api/next-bill-number', methods=['GET'])
def get_next_bill_number():
    user_id = get_current_user_id()
    today = datetime.now().strftime('%Y%m%d')
    
    # Use a more robust approach with retry logic
    max_retries = 5
    for attempt in range(max_retries):
        try:
            conn = get_db_connection()
            # Use a transaction to prevent race conditions
            # Note: PostgreSQL doesn't need explicit BEGIN TRANSACTION
            # The transaction is automatically started
            
            # Find all bills for today with the new format
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
            
            # Verify this bill number doesn't exist (double-check)
            cursor = execute_query(conn, f"""
                SELECT COUNT(*) as count FROM bills WHERE bill_number = {placeholder} AND user_id = {placeholder}
            """, (bill_number, user_id))
            existing = cursor.fetchone()
            
            if existing['count'] == 0:
                conn.close()
                return jsonify({'next_number': bill_number})
            else:
                # If bill number exists, increment and try again
                max_seq += 1
                next_seq = max_seq + 1
                bill_number = f'BILL-{today}-{next_seq:03d}'
                conn.close()
                return jsonify({'next_number': bill_number})
                
        except Exception as e:
            conn.rollback()
            conn.close()
            if attempt == max_retries - 1:
                # Last attempt failed, generate a unique bill number with timestamp
                import time
                timestamp = int(time.time() * 1000) % 10000  # Last 4 digits of timestamp
                bill_number = f'BILL-{today}-{timestamp:04d}'
                return jsonify({'next_number': bill_number})
            time.sleep(0.1)  # Small delay before retry

@app.route('/api/employee-analytics', methods=['GET'])
def employee_analytics():
    user_id = get_current_user_id()
    conn = get_db_connection()
    # Top 5 employees by revenue
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'''
        SELECT e.name, COALESCE(SUM(b.total_amount), 0) as total_revenue
        FROM employees e
        LEFT JOIN bills b ON e.employee_id = b.master_id AND b.user_id = e.user_id
        WHERE e.user_id = {placeholder} AND e.is_active = TRUE
        GROUP BY e.employee_id
        ORDER BY total_revenue DESC
        LIMIT 5
    ''', (user_id,))
    top5 = cursor.fetchall()
    # Revenue share for all employees
    cursor = execute_query(conn, f'''
        SELECT e.name, COALESCE(SUM(b.total_amount), 0) as total_revenue
        FROM employees e
        LEFT JOIN bills b ON e.employee_id = b.master_id AND b.user_id = e.user_id
        WHERE e.user_id = {placeholder} AND e.is_active = TRUE
        GROUP BY e.employee_id
        ORDER BY total_revenue DESC
    ''', (user_id,))
    shares = cursor.fetchall()
    conn.close()
    return jsonify({
        'top5': [dict(row) for row in top5],
        'shares': [dict(row) for row in shares]
    })

# Helper: zip the database file in memory
def zip_db():
    mem_zip = BytesIO()
    with zipfile.ZipFile(mem_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write('pos_tailor.db', arcname='pos_tailor.db')
    mem_zip.seek(0)
    return mem_zip



@app.route('/api/backup/upload', methods=['POST'])
def backup_upload():
    return jsonify({'error': 'Dropbox backup functionality has been removed.'}), 501

@app.route('/api/backups', methods=['GET'])
def list_backups():
    return jsonify([])

@app.route('/api/backup/download/<filename>', methods=['GET'])
def download_backup(filename):
    return jsonify({'error': 'Dropbox backup functionality has been removed.'}), 501

@app.route('/api/backup/restore/<filename>', methods=['POST'])
def restore_backup(filename):
    return jsonify({'error': 'Dropbox backup functionality has been removed.'}), 501

# Plan Management API
@app.route('/api/plan/status', methods=['GET'])
def get_plan_status():
    """Get current user plan status and enabled features."""
    try:
        conn = get_db_connection()
        # Get the most recent active plan for user_id = 1
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT * FROM user_plans 
            WHERE user_id = 1 AND is_active = TRUE 
            ORDER BY created_at DESC 
            LIMIT 1
        ''')
        user_plan = cursor.fetchone()
        conn.close()
        
        if not user_plan:
            # Create default trial plan if none exists
            conn = get_db_connection()
            placeholder = get_placeholder()
            sql = f'INSERT INTO user_plans (user_id, plan_type, plan_start_date) VALUES (1, {placeholder}, {placeholder})'
            execute_with_returning(conn, sql, ('trial', datetime.now().strftime('%Y-%m-%d')))
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
        print(f"Error in get_plan_status: {e}")  # Add logging
        return jsonify({'error': str(e)}), 500

@app.route('/api/plan/upgrade', methods=['POST'])
def upgrade_plan():
    """Upgrade user plan."""
    try:
        data = request.get_json()
        new_plan = data.get('plan_type')
        
        if new_plan not in ['trial', 'basic', 'pro']:
            return jsonify({'error': 'Invalid plan type'}), 400
        
        conn = get_db_connection()
        
        # Instead of inserting a new plan, update the existing plan for user_id=1
        placeholder = get_placeholder()
        sql = f'''
            UPDATE user_plans
            SET plan_type = {placeholder}, plan_start_date = {placeholder}, is_active = TRUE, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = 1
        '''
        execute_update(conn, sql, (new_plan, datetime.now().strftime('%Y-%m-%d')))
        conn.close()
        
        return jsonify({
            'message': f'Successfully upgraded to {new_plan} plan',
            'plan_type': new_plan,
            'start_date': datetime.now().strftime('%Y-%m-%d')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/plan/features', methods=['GET'])
def get_enabled_features():
    """Get list of enabled features for current user."""
    try:
        conn = get_db_connection()
        # Get the most recent active plan for user_id = 1
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT * FROM user_plans 
            WHERE user_id = 1 AND is_active = TRUE 
            ORDER BY created_at DESC 
            LIMIT 1
        ''')
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
        print(f"Error in get_enabled_features: {e}")  # Add logging
        return jsonify({'error': str(e)}), 500

@app.route('/api/plan/check-feature/<feature>', methods=['GET'])
def check_feature_access(feature):
    """Check if a specific feature is enabled for current user."""
    try:
        conn = get_db_connection()
        cursor = execute_query(conn, 'SELECT * FROM user_plans WHERE user_id = 1 AND is_active = TRUE')

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
        
        return jsonify({
            'enabled': is_enabled,
            'feature': feature,
            'plan_type': user_plan['plan_type']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/plan/config', methods=['GET'])
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/plan/expire-trial', methods=['POST'])
def expire_trial():
    """Expire trial for testing purposes."""
    try:
        data = request.get_json()
        days_ago = data.get('days_ago', 16)
        
        conn = get_db_connection()
        execute_update(conn, '''
            UPDATE user_plans 
            SET plan_start_date = date('now', '-{} days')
            WHERE user_id = 1 AND plan_type = 'trial' AND is_active = TRUE
        '''.format(days_ago))
        conn.close()
        
        return jsonify({
            'message': f'Trial expired (set to {days_ago} days ago)',
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/plan/reset-trial', methods=['POST'])
def reset_trial():
    """Reset trial to today for testing purposes."""
    try:
        conn = get_db_connection()
        execute_update(conn, '''
            UPDATE user_plans 
            SET plan_start_date = date('now')
            WHERE user_id = 1 AND plan_type = 'trial' AND is_active = TRUE
        ''')
        conn.close()
        
        return jsonify({
            'message': 'Trial reset to today',
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug-plan')
def debug_plan():
    """Debug page for plan management."""
    user_plan_info = get_user_plan_info()
    return render_template('debug_plan.html', 
                        user_plan_info=user_plan_info,
                        get_user_language=get_user_language,
                        get_translated_text=get_translated_text)

@app.route('/login')
def login():
    """Login page for multi-tenant system."""
    return render_template('login.html',
                        get_user_language=get_user_language,
                        get_translated_text=get_translated_text)



@app.route('/setup')
def setup():
    """Alternative setup route."""
    user_plan_info = get_user_plan_info()
    return render_template('setup_wizard.html', 
                        user_plan_info=user_plan_info,
                        get_user_language=get_user_language,
                        get_translated_text=get_translated_text)

@app.route('/api/setup-wizard', methods=['POST'])
def handle_setup_wizard():
    """Handle setup wizard data submission."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['shopType', 'shopName', 'shopOwner', 'contactNumber', 'selectedPlan']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Missing required field: {field}'})
        
        # Calculate expiry date based on plan
        from datetime import datetime, timedelta
        
        if data['selectedPlan'] == 'trial':
            expiry_date = datetime.now() + timedelta(days=15)
            plan_type = 'trial'
        elif data['selectedPlan'] == 'basic':
            expiry_date = datetime.now() + timedelta(days=365)
            plan_type = 'basic'
        elif data['selectedPlan'] == 'pro':
            expiry_date = datetime.now() + timedelta(days=365)
            plan_type = 'pro'
        else:
            return jsonify({'success': False, 'message': 'Invalid plan selected'})
        
        conn = get_db_connection()
        
        # Generate unique shop code (retry to avoid rare collisions)
        import random
        import string
        def generate_shop_code():
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Prepare inputs
        contact_number_raw = (data.get('contactNumber') or '').strip()
        contact_number_digits = re.sub(r'\D', '', contact_number_raw)
        if not contact_number_digits:
            conn.close()
            return jsonify({'success': False, 'message': 'Contact number must contain digits'}), 400
        
        default_password = os.getenv('DEFAULT_PASSWORD', 'demo123')  # Default password from environment
        password_hash = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt())
        
        # Normalize email: if empty, use fallback
        provided_email = (data.get('emailAddress') or '').strip()
        # Shop code may be needed for fallback email; generate with collision check
        attempts = 0
        while True:
            attempts += 1
            shop_code = generate_shop_code()
            # Check uniqueness of shop_code
            placeholder = get_placeholder()
            cursor = execute_query(conn, f'SELECT 1 FROM users WHERE shop_code = {placeholder}', (shop_code,))
            existing = cursor.fetchone()
            if not existing:
                break
            if attempts > 5:
                conn.close()
                return jsonify({'success': False, 'message': 'Failed to generate unique shop code. Please try again.'}), 500
        
        user_email = provided_email if provided_email else f"shop_{shop_code}@tailorpos.com"
        
        # Insert new user
        try:
            placeholder = get_placeholder()
            cursor = execute_update(conn, f'''
                INSERT INTO users (email, mobile, shop_code, password_hash, shop_name, shop_type, contact_number, email_address)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            ''', (
                user_email,
                contact_number_digits,
                shop_code,
                password_hash.decode('utf-8'),
                data['shopName'],
                data['shopType'],
                contact_number_digits,
                user_email
            ))
        except get_db_integrity_error() as ie:
            # Determine which unique constraint failed
            message = str(ie)
            friendly = 'Setup failed due to duplicate data.'
            if 'users.email' in message:
                friendly = 'This email is already registered. Please use a different email.'
            elif 'users.mobile' in message:
                friendly = 'This contact number is already registered. Please use a different number.'
            elif 'users.shop_code' in message:
                friendly = 'Generated shop code collided. Please try again.'
            conn.close()
            return jsonify({'success': False, 'message': friendly}), 400
        
        new_user_id = cursor.lastrowid
        
        # Create shop settings for new user with TRN, address, and dynamic template enabled
        placeholder = get_placeholder()
        sql = f'''
            INSERT INTO shop_settings (user_id, shop_name, shop_mobile, trn, address, invoice_static_info, use_dynamic_invoice_template)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        '''
        execute_with_returning(conn, sql, (
            new_user_id, 
            data['shopName'], 
            contact_number_digits, 
            data.get('trn', ''),
            data.get('address', ''),
            f"Shop Type: {data['shopType']}",
            1  # Enable dynamic invoice template by default
        ))
        
        # Create shop owner as employee with "Owner" position
        placeholder = get_placeholder()
        sql = f'''
            INSERT INTO employees (user_id, name, phone, address, position, is_active)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        '''
        execute_with_returning(conn, sql, (
            new_user_id,
            data['shopOwner'],
            contact_number_digits,
            data.get('address', ''),
            'Owner',
            1
        ))
        
        # Create user plan for new user
        placeholder = get_placeholder()
        sql = f'''
            INSERT INTO user_plans (user_id, plan_type, plan_start_date, plan_end_date)
            VALUES ({placeholder}, {placeholder}, CURRENT_DATE, {placeholder})
        '''
        execute_with_returning(conn, sql, (new_user_id, plan_type, expiry_date.strftime('%Y-%m-%d')))
        
        # Create default VAT rate (5% from 2018-01-01)
        placeholder = get_placeholder()
        sql = f'''
            INSERT INTO vat_rates (user_id, rate_percentage, effective_from, effective_to, is_active)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        '''
        execute_with_returning(conn, sql, (new_user_id, 5.00, '2018-01-01', '2099-12-31', 1))
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': 'Setup completed successfully',
            'plan_type': plan_type,
            'expiry_date': expiry_date.strftime('%Y-%m-%d'),
            'shop_code': shop_code,
            'password': default_password,
            'emailAddress': user_email
        })
        
    except Exception as e:
        print(f"Setup wizard error: {e}")
        try:
            conn.close()
        except:
            pass
        return jsonify({'success': False, 'message': 'Setup failed. Please try again.'})

@app.route('/api/auth/login', methods=['POST'])
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
            
            import bcrypt
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
            
            import bcrypt
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return jsonify({'success': False, 'message': 'Invalid shop code or password'})
        else:
            return jsonify({'success': False, 'message': 'Invalid login method'})
        
        # Set session data (you might want to use Flask-Session or JWT tokens)
        # For now, we'll store user info in session
        from flask import session
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
        print(f"Login error: {e}")
        return jsonify({'success': False, 'message': 'Login failed. Please try again.'})

@app.route('/api/auth/logout', methods=['POST'])
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
        print(f"Logout error: {e}")
        return jsonify({'success': False, 'message': 'Logout failed'}), 500

@app.route('/api/account/password', methods=['PUT'])
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
        print(f"Change password error: {e}")
        return jsonify({'success': False, 'message': 'Failed to change password'}), 500

@app.route('/api/change-password', methods=['POST'])
def change_password_post():
    """Change current user's password via POST method (for frontend compatibility)."""
    try:
        # print(f"Change password request received")
        data = request.get_json() or {}
        # print(f"Request data: {data}")
        
        current_password = (data.get('current_password') or '').strip()
        new_password = (data.get('new_password') or '').strip()
        
        # print(f"Current password length: {len(current_password)}")
        # print(f"New password length: {len(new_password)}")

        user_id = get_current_user_id()
        # print(f"User ID: {user_id}")
        if not user_id:
            # print("No user ID found - not authenticated")
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401

        if not current_password or not new_password:
            # print(f"Missing passwords - current: {bool(current_password)}, new: {bool(new_password)}")
            return jsonify({'success': False, 'message': 'Current and new password are required'}), 400

        if len(new_password) < 6:
            # print(f"New password too short: {len(new_password)}")
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
        print(f"Change password error: {e}")
        return jsonify({'success': False, 'message': 'Failed to change password'}), 500

@app.route('/api/auth/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to mobile number."""
    try:
        data = request.get_json()
        mobile = data.get('mobile')
        
        if not mobile:
            return jsonify({'success': False, 'message': 'Mobile number required'})
        
        # Generate 6-digit OTP
        import random
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Store OTP in database (expires in 10 minutes)
        from datetime import datetime, timedelta
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
        print(f"OTP for {mobile}: {otp}")
        
        return jsonify({
            'success': True,
            'message': 'OTP sent successfully',
            'otp': otp  # Remove this in production
        })
        
    except Exception as e:
        print(f"Send OTP error: {e}")
        return jsonify({'success': False, 'message': 'Failed to send OTP'})

@app.route('/api/language/switch', methods=['POST'])
def switch_language():
    """Switch user language preference"""
    try:
        data = request.get_json()
        language = data.get('language', 'en')
        
        if language not in ['en', 'ar']:
            return jsonify({'error': 'Invalid language'}), 400
        
        set_user_language(language)
        
        return jsonify({
            'success': True, 
            'language': language,
            'message': get_translated_text('language_switched', language)
        })
        
    except Exception as e:
        print(f"DEBUG: Error in switch_language: {e}")
        return jsonify({'error': 'Failed to switch language'}), 500

@app.route('/api/language/current', methods=['GET'])
def get_current_language():
    """Get current user language preference"""
    try:
        language = get_user_language()
        return jsonify({
            'success': True,
            'language': language,
            'is_rtl': language == 'ar'
        })
        
    except Exception as e:
        print(f"DEBUG: Error in get_current_language: {e}")
        return jsonify({'error': 'Failed to get language preference'}), 500

@app.route('/api/reports/invoices', methods=['GET'])
def report_invoices():
    """
    Returns filtered invoice data for the Advanced Reports section.
    Accepts query parameters: from_date, to_date, products, employees, city, area, status, client_id
    """
    try:
        # Parse query parameters with defaults
        from_date = request.args.get('from_date', '')
        to_date = request.args.get('to_date', '')
        products = request.args.getlist('products[]')  # Multiple products
        employees = request.args.getlist('employees[]')  # Multiple employees
        city = request.args.get('city', '')
        area = request.args.get('area', '')
        status = request.args.get('status', '')
        client_id = request.args.get('client_id', '')
        
        # Build SQL query with filters
        if is_postgresql():
            base_query = """
                SELECT 
                    b.bill_number,
                    b.bill_date,
                    b.customer_name,
                    b.customer_phone,
                    b.customer_city,
                    b.customer_area,
                    b.delivery_date,
                    round(b.subtotal,0) as subtotal,
                    round(b.vat_amount, 2) as vat_amount,
                    round(b.total_amount, 2) as total_amount,
                    b.status,
                    b.master_id,
                    e.name as employee_name,
                    STRING_AGG(bi.product_name, ',') as products,
                    STRING_AGG(bi.quantity::text, ',') as quantities,
                    STRING_AGG(bi.rate::text, ',') as prices,
                    STRING_AGG(bi.discount::text, ',') as discount_percentages,
                    STRING_AGG(round((bi.rate * bi.quantity * bi.discount / 100), 2)::text, ',') as discount_amounts
                FROM bills b
                LEFT JOIN bill_items bi ON b.bill_id = bi.bill_id
                LEFT JOIN employees e ON b.master_id = e.employee_id
            """
        else:
            base_query = """
                SELECT 
                    b.bill_number,
                    b.bill_date,
                    b.customer_name,
                    b.customer_phone,
                    b.customer_city,
                    b.customer_area,
                    b.delivery_date,
                    round(b.subtotal,0) as subtotal,
                    round(b.vat_amount, 2) as vat_amount,
                    round(b.total_amount, 2) as total_amount,
                    b.status,
                    b.master_id,
                    e.name as employee_name,
                    GROUP_CONCAT(bi.product_name) as products,
                    GROUP_CONCAT(bi.quantity) as quantities,
                    GROUP_CONCAT(bi.rate) as prices,
                    GROUP_CONCAT(bi.discount) as discount_percentages,
                    GROUP_CONCAT(round((bi.rate * bi.quantity * bi.discount / 100), 2)) as discount_amounts
                FROM bills b
                LEFT JOIN bill_items bi ON b.bill_id = bi.bill_id
                LEFT JOIN employees e ON b.master_id = e.employee_id
            """
        
        conditions = []
        params = []
        
        # Get placeholder for database type
        placeholder = get_placeholder()
        
        # Client ID filter (most important)
        if client_id:
            conditions.append(f"b.user_id = {placeholder}")
            params.append(client_id)
        
        # Date range filter
        if from_date:
            conditions.append(f"b.bill_date >= {placeholder}")
            params.append(from_date)
        if to_date:
            conditions.append(f"b.bill_date <= {placeholder}")
            params.append(to_date)
        
        # Products filter
        if products and "All" not in products:
            placeholders = ','.join([placeholder for _ in products])
            conditions.append(f"bi.product_name IN ({placeholders})")
            params.extend(products)
        
        # Employees filter
        if employees and "All" not in employees:
            placeholders = ','.join([placeholder for _ in employees])
            conditions.append(f"e.name IN ({placeholders})")
            params.extend(employees)
        
        # City filter
        if city and city != "All":
            conditions.append(f"b.customer_city = {placeholder}")
            params.append(city)
        
        # Area filter
        if area and area != "All":
            conditions.append(f"b.customer_area = {placeholder}")
            params.append(area)
        
        # Status filter
        if status and status != "All":
            conditions.append(f"b.status = {placeholder}")
            params.append(status)
            
        # Build final query
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
            
        if is_postgresql():
            base_query += " GROUP BY b.bill_id, b.bill_number, b.bill_date, b.customer_name, b.customer_phone, b.customer_city, b.customer_area, b.delivery_date, b.subtotal, b.vat_amount, b.total_amount, b.status, b.master_id, e.name ORDER BY b.bill_date DESC LIMIT 50"
        else:
            base_query += " GROUP BY b.bill_id ORDER BY b.bill_date DESC LIMIT 50"
        
        # Execute query and fetch results
        conn = get_db_connection()
        cursor = execute_query(conn, base_query, params)
        rows = cursor.fetchall()
        
        # Format results for JSON response
        invoices_data = []
        
        # Format results for JSON response
        for row in rows:
            invoice = {
                'bill_number': row['bill_number'],
                'bill_date': row['bill_date'],
                'customer_name': row['customer_name'],
                'customer_phone': row['customer_phone'],
                'customer_city': row['customer_city'],
                'customer_area': row['customer_area'],
                'delivery_date': row['delivery_date'],
                'subtotal': round(float(row['subtotal']), 2) if row['subtotal'] is not None else 0.0,
                'vat_amount': round(float(row['vat_amount']), 2) if row['vat_amount'] is not None else 0.0,
                'total_amount': round(float(row['total_amount']), 2) if row['total_amount'] is not None else 0.0,
                'status': row['status'],
                'master_id': row['master_id'],
                'employee_name': row['employee_name'],
                'products': row['products'].split(',') if row['products'] else [],
                'quantities': [int(q) for q in row['quantities'].split(',')] if row['quantities'] else [],
                'prices': [float(p) for p in row['prices'].split(',')] if row['prices'] else [],
                'discount_percentages': [float(d) for d in row['discount_percentages'].split(',')] if row['discount_percentages'] else [],
                'discount_amounts': [float(d) for d in row['discount_amounts'].split(',')] if row['discount_amounts'] else []
            }
            invoices_data.append(invoice)
        

        
        # Calculate summary statistics
        total_invoices = len(invoices_data)
        total_amount = sum(inv['total_amount'] for inv in invoices_data)
        paid_invoices = len([inv for inv in invoices_data if inv['status'] == 'Paid'])
        
        return jsonify({
            'success': True,
            'invoices': invoices_data,  # Changed from 'data' to 'invoices'
            'summary': {
                'total_invoices': total_invoices,
                'total_amount': total_amount,
                'paid_invoices': paid_invoices,
                'pending_invoices': total_invoices - paid_invoices
            },
            'filters_applied': {
                'from_date': from_date,
                'to_date': to_date,
                'products': products,
                'employees': employees,
                'city': city,
                'area': area,
                'status': status,
                'client_id': client_id
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/invoices/download', methods=['GET'])
def download_invoices():
    """
    Returns all filtered invoice data as a CSV file for download.
    Accepts the same query parameters as /api/reports/invoices.
    """
    try:
        from_date = request.args.get('from_date', '')
        to_date = request.args.get('to_date', '')
        products = request.args.getlist('products[]')
        employees = request.args.getlist('employees[]')
        city = request.args.get('city', '')
        area = request.args.get('area', '')
        status = request.args.get('status', '')
        client_id = request.args.get('client_id', '2')  # Default to client_id 2 for testing
        base_query = """
            SELECT 
                b.bill_number as bill_id,
                b.bill_date,
                b.customer_name,
                b.customer_phone,
                b.customer_city,
                b.customer_area,
                b.delivery_date,
                b.subtotal,
                b.vat_amount,
                b.total_amount,
                b.status,
                b.master_id,
                e.name as employee_name,
                GROUP_CONCAT(bi.product_name) as products,
                GROUP_CONCAT(bi.quantity) as quantities,
                GROUP_CONCAT(bi.rate) as prices
            FROM bills b
            LEFT JOIN bill_items bi ON b.bill_id = bi.bill_id
            LEFT JOIN employees e ON b.master_id = e.employee_id
            WHERE b.user_id = ?
        """
        conditions = []
        params = [client_id]
        if from_date:
            conditions.append("b.bill_date >= ?")
            params.append(from_date)
        if to_date:
            conditions.append("b.bill_date <= ?")
            params.append(to_date)
        if products and "All" not in products:
            placeholders = ','.join(['?' for _ in products])
            conditions.append(f"bi.product_name IN ({placeholders})")
            params.extend(products)
        if employees and "All" not in employees:
            placeholders = ','.join(['?' for _ in employees])
            conditions.append(f"e.name IN ({placeholders})")
            params.extend(employees)
        if city and city != "All":
            conditions.append("b.customer_city = ?")
            params.append(city)
        if area and area != "All":
            conditions.append("b.customer_area = ?")
            params.append(area)
        if status and status != "All":
            conditions.append("b.status = ?")
            params.append(status)
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        base_query += " GROUP BY b.bill_id ORDER BY b.bill_date DESC"
        cursor = get_db_connection().cursor()
        cursor.execute(base_query, params)
        rows = cursor.fetchall()
        si = StringIO()
        writer = csv.writer(si)
        writer.writerow([
            'Bill#', 'Bill Date', 'Customer Name', 'Delivery Date',
            'Total Before VAT', 'VAT', 'Total After VAT', 'Status', 'Products'
        ])
        for row in rows:
            products = row[13].split(',') if row[13] else []
            writer.writerow([
                row[0], row[1], row[2], row[6],
                round(float(row[7]), 2) if row[7] is not None else 0.0,
                round(float(row[8]), 2) if row[8] is not None else 0.0,
                round(float(row[9]), 2) if row[9] is not None else 0.0,
                row[10],
                ', '.join(products)
            ])
        output = si.getvalue()
        si.close()
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=invoices_report.csv"}
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/invoices/print')
def print_invoices():
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    products = request.args.getlist('products[]')
    employees = request.args.getlist('employees[]')
    city = request.args.get('city', '')
    area = request.args.get('area', '')
    status = request.args.get('status', '')

    base_query = """
        SELECT 
            b.bill_number as bill_id,
            b.bill_date,
            b.customer_name,
            b.customer_phone,
            b.customer_city,
            b.customer_area,
            b.delivery_date,
            b.subtotal,
            b.vat_amount,
            b.total_amount,
            b.status,
            b.master_id,
            e.name as employee_name,
            GROUP_CONCAT(bi.product_name) as products,
            GROUP_CONCAT(bi.quantity) as quantities,
            GROUP_CONCAT(bi.rate) as prices
        FROM bills b
        LEFT JOIN bill_items bi ON b.bill_id = bi.bill_id
        LEFT JOIN employees e ON b.master_id = e.employee_id
    """
    conditions = []
    params = []
    if from_date:
        conditions.append("b.bill_date >= ?")
        params.append(from_date)
    if to_date:
        conditions.append("b.bill_date <= ?")
        params.append(to_date)
    if products and "All" not in products:
        placeholders = ','.join(['?' for _ in products])
        conditions.append(f"bi.product_name IN ({placeholders})")
        params.extend(products)
    if employees and "All" not in employees:
        placeholders = ','.join(['?' for _ in employees])
        conditions.append(f"e.name IN ({placeholders})")
        params.extend(employees)
    if city and city != "All":
        conditions.append("b.customer_city = ?")
        params.append(city)
    if area and area != "All":
        conditions.append("b.customer_area = ?")
        params.append(area)
    if status and status != "All":
        conditions.append("b.status = ?")
        params.append(status)
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    base_query += " GROUP BY b.bill_id ORDER BY b.bill_date DESC"
    cursor = get_db_connection().cursor()
    cursor.execute(base_query, params)
    rows = cursor.fetchall()
    invoices_data = []
    for row in rows:
        invoices_data.append({
            'bill_id': row[0],
            'bill_date': row[1],
            'customer_name': row[2],
            'customer_phone': row[3],
            'customer_city': row[4],
            'customer_area': row[5],
            'delivery_date': row[6],
            'total_before_vat': round(float(row[7]), 2) if row[7] is not None else 0.0,
            'vat': round(float(row[8]), 2) if row[8] is not None else 0.0,
            'total_after_vat': round(float(row[9]), 2) if row[9] is not None else 0.0,
            'status': row[10],
            'products': row[13].split(',') if row[13] else []
        })
    return render_template('print_invoices.html', invoices=invoices_data)

@app.route('/api/reports/employees', methods=['GET'])
def report_employees():
    """
    Returns filtered employee report data for the Advanced Reports section.
    Accepts query parameters: from_date, to_date, products, city, area, status, client_id
    """
    try:
        from_date = request.args.get('from_date', '')
        to_date = request.args.get('to_date', '')
        products = request.args.getlist('products[]')
        city = request.args.get('city', '')
        area = request.args.get('area', '')
        status = request.args.get('status', '')
        client_id = request.args.get('client_id', '')

        conn = get_db_connection()
        placeholder = get_placeholder()
        
        # Use conditional SQL for GROUP_CONCAT vs STRING_AGG
        if is_postgresql():
            group_concat_sql = "STRING_AGG(DISTINCT bi.product_name, ',')"
        else:
            group_concat_sql = "GROUP_CONCAT(DISTINCT bi.product_name)"
        
        base_query = f"""
            SELECT 
                e.employee_id,
                e.name as employee_name,
                COUNT(DISTINCT b.bill_id) as bills_handled,
                SUM(b.total_amount) as total_billed,
                {group_concat_sql} as products
            FROM employees e
            LEFT JOIN bills b ON e.employee_id = b.master_id
            LEFT JOIN bill_items bi ON b.bill_id = bi.bill_id
        """

        conditions = []
        params = []

        # Client ID filter (most important)
        if client_id:
            conditions.append(f"e.user_id = {placeholder}")
            params.append(client_id)

        if from_date:
            conditions.append(f"b.bill_date >= {placeholder}")
            params.append(from_date)
        if to_date:
            conditions.append(f"b.bill_date <= {placeholder}")
            params.append(to_date)
        if products and "All" not in products:
            placeholders = ','.join([placeholder for _ in products])
            conditions.append(f"bi.product_name IN ({placeholders})")
            params.extend(products)
        if city and city != "All":
            conditions.append(f"b.customer_city = {placeholder}")
            params.append(city)
        if area and area != "All":
            conditions.append(f"b.customer_area = {placeholder}")
            params.append(area)
        if status and status != "All":
            conditions.append(f"b.status = {placeholder}")
            params.append(status)

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        base_query += " GROUP BY e.employee_id, e.name ORDER BY total_billed DESC"

        cursor = execute_query(conn, base_query, params)
        rows = cursor.fetchall()

        employees_data = []
        for row in rows:
            try:
                products_str = row[4] if row[4] else ''
                products_list = products_str.split(',') if products_str else []
                # Filter out empty strings
                products_list = [p.strip() for p in products_list if p.strip()]
                
                employees_data.append({
                    'employee_id': row[0],
                    'name': row[1],  # Changed to match frontend expectation
                    'bills_handled': row[2] or 0,
                    'total_billed': round(float(row[3]), 2) if row[3] is not None else 0.0,
                    'products_handled': products_list  # Changed to match frontend
                })
            except Exception as e:
                print(f"Error processing employee row {row}: {e}")
                continue

        return jsonify({
            'success': True,
            'employees': employees_data,  # Changed from 'data' to 'employees'
            'filters_applied': {
                'from_date': from_date,
                'to_date': to_date,
                'products': products,
                'city': city,
                'area': area,
                'status': status,
                'client_id': client_id
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/products', methods=['GET'])
def report_products():
    try:
        # Get filter parameters
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        product_type = request.args.get('product_type')
        city = request.args.get('city')
        area = request.args.get('area')
        status = request.args.get('status')
        client_id = request.args.get('client_id', '')
        
        conn = get_db_connection()
        placeholder = get_placeholder()
        
        # Build base query
        base_query = f"""
            SELECT 
                p.product_name,
                pt.type_name as product_type,
                SUM(bi.quantity) as total_quantity,
                SUM(bi.total_amount) as total_revenue
            FROM bill_items bi
            JOIN products p ON bi.product_id = p.product_id
            JOIN product_types pt ON p.type_id = pt.type_id
            JOIN bills b ON bi.bill_id = b.bill_id
            WHERE 1=1
        """
        
        params = []
        
        # Client ID filter (most important)
        if client_id:
            base_query += f" AND b.user_id = {placeholder}"
            params.append(client_id)
        
        # Add filters
        if from_date:
            base_query += f" AND b.bill_date >= {placeholder}"
            params.append(from_date)
        
        if to_date:
            base_query += f" AND b.bill_date <= {placeholder}"
            params.append(to_date)
        
        if product_type and product_type != "All":
            base_query += f" AND pt.type_name = {placeholder}"
            params.append(product_type)
        
        if city and city != "All":
            base_query += f" AND b.customer_city = {placeholder}"
            params.append(city)
        
        if area and area != "All":
            base_query += f" AND b.customer_area = {placeholder}"
            params.append(area)
        
        if status and status != "All":
            base_query += f" AND b.status = {placeholder}"
            params.append(status)
        
        base_query += " GROUP BY p.product_id, p.product_name, pt.type_name ORDER BY total_revenue DESC"
        
        cursor = execute_query(conn, base_query, params)
        rows = cursor.fetchall()
        
        products = []
        for row in rows:
            try:
                products.append({
                    'product_name': row[0],
                    'type_name': row[1],  # Changed to match frontend expectation
                    'total_quantity': row[2] or 0,
                    'total_revenue': round(float(row[3]), 2) if row[3] is not None else 0.0
                })
            except Exception as e:
                print(f"Error processing product row {row}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'products': products
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/shop-settings', methods=['GET'])
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

@app.route('/api/shop-settings/payment-mode', methods=['GET'])
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

@app.route('/api/shop-settings/billing-config', methods=['GET'])
def get_billing_config():
    """Get billing field configuration for the current user."""
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT enable_trial_date, enable_delivery_date, enable_advance_payment, 
                   enable_customer_notes, enable_employee_assignment, default_delivery_days, default_trial_days, default_employee_id
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
                'default_employee_id': settings['default_employee_id']
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
                'default_employee_id': None
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
                'default_employee_id': None
            }
        }), 500

@app.route('/api/shop-settings', methods=['PUT'])
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
        enable_trial_date = data.get('enable_trial_date', True)
        enable_delivery_date = data.get('enable_delivery_date', True)
        enable_advance_payment = data.get('enable_advance_payment', True)
        enable_customer_notes = data.get('enable_customer_notes', True)
        enable_employee_assignment = data.get('enable_employee_assignment', True)
        default_delivery_days = data.get('default_delivery_days', 3)
        default_trial_days = data.get('default_trial_days', 3)
        default_employee_id = data.get('default_employee_id')
        
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
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = {placeholder}
            ''', (shop_name, address, trn, city, area, logo_url, shop_mobile, working_hours, 
                  invoice_static_info, use_dynamic_invoice_template, payment_mode,
                  enable_trial_date, enable_delivery_date, enable_advance_payment,
                  enable_customer_notes, enable_employee_assignment, default_delivery_days, default_trial_days, default_employee_id, user_id))
        else:
            # Create new shop settings for this user
            execute_update(conn, '''
                INSERT INTO shop_settings (user_id, shop_name, address, trn, city, area, logo_url, 
                    shop_mobile, working_hours, invoice_static_info, use_dynamic_invoice_template, payment_mode,
                    enable_trial_date, enable_delivery_date, enable_advance_payment,
                    enable_customer_notes, enable_employee_assignment, default_delivery_days, default_trial_days, default_employee_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, shop_name, address, trn, city, area, logo_url, shop_mobile, working_hours, 
                  invoice_static_info, use_dynamic_invoice_template, payment_mode,
                  enable_trial_date, enable_delivery_date, enable_advance_payment,
                  enable_customer_notes, enable_employee_assignment, default_delivery_days, default_trial_days, default_employee_id))
        conn.close()
        
        # Log shop settings update
        log_user_action("UPDATE_SHOP_SETTINGS", user_id, {
            'shop_name': shop_name,
            'trn': trn,
            'city': city,
            'area': area,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True,
            'message': 'Shop settings updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Arabic Language Support
def number_to_arabic_words(number):
    """Convert number to Arabic words"""
    if number == 0:
        return "صفر"
    
    # Arabic number words
    ones = {
        0: "", 1: "واحد", 2: "اثنان", 3: "ثلاثة", 4: "أربعة", 5: "خمسة",
        6: "ستة", 7: "سبعة", 8: "ثمانية", 9: "تسعة", 10: "عشرة",
        11: "أحد عشر", 12: "اثنا عشر", 13: "ثلاثة عشر", 14: "أربعة عشر", 15: "خمسة عشر",
        16: "ستة عشر", 17: "سبعة عشر", 18: "ثمانية عشر", 19: "تسعة عشر"
    }
    
    tens = {
        2: "عشرون", 3: "ثلاثون", 4: "أربعون", 5: "خمسون",
        6: "ستون", 7: "سبعون", 8: "ثمانون", 9: "تسعون"
    }
    
    hundreds = {
        1: "مائة", 2: "مئتان", 3: "ثلاثمائة", 4: "أربعمائة", 5: "خمسمائة",
        6: "ستمائة", 7: "سبعمائة", 8: "ثمانمائة", 9: "تسعمائة"
    }
    
    def convert_less_than_one_thousand(n):
        if n == 0:
            return ""
        
        if n < 20:
            return ones[n]
        
        if n < 100:
            if n % 10 == 0:
                return tens[n // 10]
            else:
                return ones[n % 10] + " و " + tens[n // 10]
        
        if n < 1000:
            if n % 100 == 0:
                return hundreds[n // 100]
            else:
                return hundreds[n // 100] + " و " + convert_less_than_one_thousand(n % 100)
    
    # Split into integer and decimal parts
    integer_part = int(number)
    decimal_part = round((number - integer_part) * 100)
    
    # Convert integer part
    if integer_part == 0:
        result = "صفر"
    elif integer_part < 1000:
        result = convert_less_than_one_thousand(integer_part)
    else:
        # Handle thousands
        thousands_count = integer_part // 1000
        remainder = integer_part % 1000
        
        if thousands_count == 1:
            result = "ألف"
        elif thousands_count == 2:
            result = "ألفان"
        elif thousands_count < 11:
            result = ones[thousands_count] + " آلاف"
        else:
            result = convert_less_than_one_thousand(thousands_count) + " ألف"
        
        if remainder > 0:
            result += " و " + convert_less_than_one_thousand(remainder)
    
    # Add currency
    result += " درهم"
    
    # Add decimal part if exists
    if decimal_part > 0:
        if decimal_part == 1:
            result += " و فلس واحد"
        else:
            result += " و " + convert_less_than_one_thousand(decimal_part) + " فلس"
    
    result += " فقط"
    return result

def get_user_language():
    """Get user's preferred language from session or default to English"""
    return session.get('language', 'en')

def set_user_language(language):
    """Set user's preferred language in session"""
    session['language'] = language

def translate_text(text, language='en'):
    """Translate text based on language"""
    translations = {
        'en': {
            # Navigation
            'app': 'App',
            'pricing': 'Pricing',
            'professional_business_management': 'Professional Business Management',
            'sign_in': 'Sign In',
            'sign_up': 'Sign Up',
            'logout': 'Logout',
            
            # Dashboard
            'dashboard': 'Dashboard',
            'total_revenue': 'Total Revenue',
            'total_bills': 'Total Bills',
            'total_customers': 'Total Customers',
            'total_products': 'Total Products',
            'recent_bills': 'Recent Bills',
            'top_products': 'Top Products',
            'employee_performance': 'Employee Performance',
            
            # Operations
            'operations': 'Operations',
            'billing': 'Billing',
            'products': 'Products',
            'customers': 'Customers',
            'employees': 'Employees',
            'vat_rates': 'VAT Rates',
            'advanced_reports': 'Advanced Reports',
            'shop_settings': 'Shop Settings',
            
            # Common Actions
            'add': 'Add',
            'edit': 'Edit',
            'delete': 'Delete',
            'save': 'Save',
            'cancel': 'Cancel',
            'close': 'Close',
            'search': 'Search',
            'filter': 'Filter',
            'download': 'Download',
            'print': 'Print',
            'preview': 'Preview',
            
            # Status
            'pending': 'Pending',
            'completed': 'Completed',
            'cancelled': 'Cancelled',
            'paid': 'Paid',
            'unpaid': 'Unpaid',
            
            # Messages
            'success': 'Success',
            'error': 'Error',
            'warning': 'Warning',
            'info': 'Information',
            'loading': 'Loading...',
            'no_data_found': 'No data found',
            'are_you_sure': 'Are you sure?',
            'this_action_cannot_be_undone': 'This action cannot be undone',
            
            # Forms
            'name': 'Name',
            'phone': 'Phone',
            'email': 'Email',
            'address': 'Address',
            'city': 'City',
            'area': 'Area',
            'position': 'Position',
            'rate': 'Rate',
            'quantity': 'Quantity',
            'total': 'Total',
            'subtotal': 'Subtotal',
            'vat': 'VAT',
            'discount': 'Discount',
            'advance_paid': 'Advance Paid',
            'balance': 'Balance',
            'payment_method': 'Payment Method',
            'cash': 'Cash',
            'card': 'Card',
            'bank_transfer': 'Bank Transfer',
            
            # Reports
            'invoices': 'Invoices',
            'employees': 'Employees',
            'products': 'Products',
            'from_date': 'From Date',
            'to_date': 'To Date',
            'bill_number': 'Bill #',
            'bill_date': 'Bill Date',
            'delivery_date': 'Delivery Date',
            'customer_name': 'Customer Name',
            'status': 'Status',
            'amount': 'Amount',
            'revenue': 'Revenue',
            'performance': 'Performance',
            
            # Setup Wizard
            'shop_type': 'Shop Type',
            'shop_name': 'Shop Name',
            'contact_number': 'Contact Number',
            'choose_plan': 'Choose Plan',
            'trial': 'Trial',
            'basic': 'Basic',
            'pro': 'Pro',
            'days': 'Days',
            'year': 'Year',
            'next': 'Next',
            'previous': 'Previous',
            'finish': 'Finish',
            
            # Plans
            'trial_plan': 'Trial Plan',
            'basic_plan': 'Basic Plan',
            'pro_plan': 'Pro Plan',
            'enterprise_plan': 'Enterprise Plan',
            'features': 'Features',
            'upgrade': 'Upgrade',
            'current_plan': 'Current Plan',
            'plan_expires': 'Plan Expires',
            'unlimited': 'Unlimited',
            'limited': 'Limited',
            
            # Settings
            'settings': 'Settings',
            'logo_url': 'Logo URL',
            'working_hours': 'Working Hours',
            'static_info': 'Static Information',
            'invoice_template': 'Invoice Template',
            'dynamic_template': 'Dynamic Template',
            'static_template': 'Static Template',
            
            # Authentication
            'login': 'Login',
            'password': 'Password',
            'confirm_password': 'Confirm Password',
            'forgot_password': 'Forgot Password?',
            'remember_me': 'Remember Me',
            'dont_have_account': "Don't have an account?",
            'already_have_account': 'Already have an account?',
            'sign_up_here': 'Sign up here',
            'sign_in_here': 'Sign in here',
            'mobile_login': 'Mobile Login',
            'otp': 'OTP',
            'send_otp': 'Send OTP',
            'verify_otp': 'Verify OTP',
            'shop_code': 'Shop Code',
            'enter_shop_code': 'Enter Shop Code',
            
            # Currency
            'aed': 'AED',
            'dirhams': 'Dirhams',
            'fils': 'Fils',
            'only': 'Only',
            
            # Time
            'today': 'Today',
            'yesterday': 'Yesterday',
            'this_week': 'This Week',
            'this_month': 'This Month',
            'this_year': 'This Year',
            'last_week': 'Last Week',
            'last_month': 'Last Month',
            'last_year': 'Last Year',
            
            # Charts
            'sales': 'Sales',
            'revenue_chart': 'Revenue Chart',
            'sales_chart': 'Sales Chart',
            'performance_chart': 'Performance Chart',
            'heatmap': 'Heatmap',
            
            # Notifications
            'notification': 'Notification',
            'notifications': 'Notifications',
            'new_bill': 'New Bill',
            'payment_received': 'Payment Received',
            'low_stock': 'Low Stock',
            'expiring_plan': 'Expiring Plan',
            
            # Help
            'help': 'Help',
            'support': 'Support',
            'documentation': 'Documentation',
            'contact_us': 'Contact Us',
            'feedback': 'Feedback',
            'bug_report': 'Bug Report',
            'feature_request': 'Feature Request',
            
            # Language
            'language': 'Language',
            'english': 'English',
            'arabic': 'Arabic',
            'switch_language': 'Switch Language',
            
            # Default text
            'default': text
        },
        'ar': {
            # Navigation
            'app': 'التطبيق',
            'pricing': 'الأسعار',
            'professional_business_management': 'إدارة الأعمال الاحترافية',
            'sign_in': 'تسجيل الدخول',
            'sign_up': 'إنشاء حساب',
            'logout': 'تسجيل الخروج',
            
            # Dashboard
            'dashboard': 'لوحة التحكم',
            'total_revenue': 'إجمالي الإيرادات',
            'total_bills': 'إجمالي الفواتير',
            'total_customers': 'إجمالي العملاء',
            'total_products': 'إجمالي المنتجات',
            'recent_bills': 'الفواتير الحديثة',
            'top_products': 'أفضل المنتجات',
            'employee_performance': 'أداء الموظفين',
            
            # Operations
            'operations': 'العمليات',
            'billing': 'الفواتير',
            'products': 'المنتجات',
            'customers': 'العملاء',
            'employees': 'الموظفون',
            'vat_rates': 'معدلات الضريبة',
            'advanced_reports': 'التقارير المتقدمة',
            'shop_settings': 'إعدادات المتجر',
            
            # Common Actions
            'add': 'إضافة',
            'edit': 'تعديل',
            'delete': 'حذف',
            'save': 'حفظ',
            'cancel': 'إلغاء',
            'close': 'إغلاق',
            'search': 'بحث',
            'filter': 'تصفية',
            'download': 'تحميل',
            'print': 'طباعة',
            'preview': 'معاينة',
            
            # Status
            'pending': 'قيد الانتظار',
            'completed': 'مكتمل',
            'cancelled': 'ملغي',
            'paid': 'مدفوع',
            'unpaid': 'غير مدفوع',
            
            # Messages
            'success': 'نجح',
            'error': 'خطأ',
            'warning': 'تحذير',
            'info': 'معلومات',
            'loading': 'جاري التحميل...',
            'no_data_found': 'لم يتم العثور على بيانات',
            'are_you_sure': 'هل أنت متأكد؟',
            'this_action_cannot_be_undone': 'لا يمكن التراجع عن هذا الإجراء',
            
            # Forms
            'name': 'الاسم',
            'phone': 'الهاتف',
            'email': 'البريد الإلكتروني',
            'address': 'العنوان',
            'city': 'المدينة',
            'area': 'المنطقة',
            'position': 'المنصب',
            'rate': 'السعر',
            'quantity': 'الكمية',
            'total': 'الإجمالي',
            'subtotal': 'المجموع الفرعي',
            'vat': 'الضريبة',
            'discount': 'الخصم',
            'advance_paid': 'المدفوع مسبقاً',
            'balance': 'الرصيد',
            'payment_method': 'طريقة الدفع',
            'cash': 'نقداً',
            'card': 'بطاقة',
            'bank_transfer': 'تحويل بنكي',
            
            # Reports
            'invoices': 'الفواتير',
            'employees': 'الموظفون',
            'products': 'المنتجات',
            'from_date': 'من تاريخ',
            'to_date': 'إلى تاريخ',
            'bill_number': 'رقم الفاتورة',
            'bill_date': 'تاريخ الفاتورة',
            'delivery_date': 'تاريخ التسليم',
            'customer_name': 'اسم العميل',
            'status': 'الحالة',
            'amount': 'المبلغ',
            'revenue': 'الإيرادات',
            'performance': 'الأداء',
            
            # Setup Wizard
            'shop_type': 'نوع المتجر',
            'shop_name': 'اسم المتجر',
            'contact_number': 'رقم الاتصال',
            'choose_plan': 'اختر الخطة',
            'trial': 'تجريبي',
            'basic': 'أساسي',
            'pro': 'احترافي',
            'days': 'أيام',
            'year': 'سنة',
            'next': 'التالي',
            'previous': 'السابق',
            'finish': 'إنهاء',
            
            # Plans
            'trial_plan': 'الخطة التجريبية',
            'basic_plan': 'الخطة الأساسية',
            'pro_plan': 'الخطة الاحترافية',
            'enterprise_plan': 'خطة المؤسسة',
            'features': 'الميزات',
            'upgrade': 'ترقية',
            'current_plan': 'الخطة الحالية',
            'plan_expires': 'تنتهي الخطة',
            'unlimited': 'غير محدود',
            'limited': 'محدود',
            
            # Settings
            'settings': 'الإعدادات',
            'logo_url': 'رابط الشعار',
            'working_hours': 'ساعات العمل',
            'static_info': 'معلومات ثابتة',
            'invoice_template': 'قالب الفاتورة',
            'dynamic_template': 'قالب ديناميكي',
            'static_template': 'قالب ثابت',
            
            # Authentication
            'login': 'تسجيل الدخول',
            'password': 'كلمة المرور',
            'confirm_password': 'تأكيد كلمة المرور',
            'forgot_password': 'نسيت كلمة المرور؟',
            'remember_me': 'تذكرني',
            'dont_have_account': 'ليس لديك حساب؟',
            'already_have_account': 'لديك حساب بالفعل؟',
            'sign_up_here': 'إنشاء حساب هنا',
            'sign_in_here': 'تسجيل الدخول هنا',
            'mobile_login': 'تسجيل الدخول بالجوال',
            'otp': 'رمز التحقق',
            'send_otp': 'إرسال رمز التحقق',
            'verify_otp': 'التحقق من الرمز',
            'shop_code': 'رمز المتجر',
            'enter_shop_code': 'أدخل رمز المتجر',
            
            # Currency
            'aed': 'درهم',
            'dirhams': 'دراهم',
            'fils': 'فلس',
            'only': 'فقط',
            
            # Time
            'today': 'اليوم',
            'yesterday': 'أمس',
            'this_week': 'هذا الأسبوع',
            'this_month': 'هذا الشهر',
            'this_year': 'هذا العام',
            'last_week': 'الأسبوع الماضي',
            'last_month': 'الشهر الماضي',
            'last_year': 'العام الماضي',
            
            # Charts
            'sales': 'المبيعات',
            'revenue_chart': 'رسم بياني للإيرادات',
            'sales_chart': 'رسم بياني للمبيعات',
            'performance_chart': 'رسم بياني للأداء',
            'heatmap': 'خريطة حرارية',
            
            # Notifications
            'notification': 'إشعار',
            'notifications': 'الإشعارات',
            'new_bill': 'فاتورة جديدة',
            'payment_received': 'تم استلام الدفع',
            'low_stock': 'المخزون منخفض',
            'expiring_plan': 'الخطة تنتهي قريباً',
            
            # Help
            'help': 'المساعدة',
            'support': 'الدعم',
            'documentation': 'الوثائق',
            'contact_us': 'اتصل بنا',
            'feedback': 'التعليقات',
            'bug_report': 'تقرير خطأ',
            'feature_request': 'طلب ميزة',
            
            # Language
            'language': 'اللغة',
            'english': 'الإنجليزية',
            'arabic': 'العربية',
            'switch_language': 'تغيير اللغة',
            
            # Default text
            'default': text
        }
    }
    
    return translations.get(language, {}).get(text, text)

def get_translated_text(text, language=None):
    """Get translated text for current user language"""
    if language is None:
        language = get_user_language()
    return translate_text(text, language)

def generate_zatca_qr_code(seller_name, seller_trn, invoice_number, timestamp, total_with_vat, vat_amount):
    """
    Generate QR code data in ZATCA format for FTA compliance
    Format: Seller Name, TRN, Timestamp, Total with VAT, VAT Amount
    """
    # Create QR data in ZATCA format
    qr_data = f"{seller_name}\n{seller_trn}\n{timestamp}\n{total_with_vat}\n{vat_amount}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create QR code image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    buffer = BytesIO()
    qr_image.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return qr_base64

@app.route('/api/setup/default-products', methods=['GET'])
def get_default_products():
    """Get default product types and products for laundry shop setup"""
    try:
        default_data = {
            'product_types': [
                {'type_name': 'Wash & Iron', 'description': 'Standard wash and iron service'},
                {'type_name': 'Dry Clean', 'description': 'Professional dry cleaning service'},
                {'type_name': 'Press Only', 'description': 'Ironing and pressing service'},
                {'type_name': 'Starch', 'description': 'Starch and iron service'},
                {'type_name': 'Express', 'description': 'Same day service'},
                {'type_name': 'Bulk', 'description': 'Large quantity orders'}
            ],
            'products': [
                # Wash & Iron Products
                {'product_name': 'Shirt Wash & Iron', 'product_type': 'Wash & Iron', 'rate': 8.00, 'description': 'Standard shirt wash and iron'},
                {'product_name': 'Pants Wash & Iron', 'product_type': 'Wash & Iron', 'rate': 10.00, 'description': 'Trousers wash and iron'},
                {'product_name': 'T-Shirt Wash & Iron', 'product_type': 'Wash & Iron', 'rate': 6.00, 'description': 'T-shirt wash and iron'},
                {'product_name': 'Dress Wash & Iron', 'product_type': 'Wash & Iron', 'rate': 12.00, 'description': 'Dress wash and iron'},
                {'product_name': 'Suit Wash & Iron', 'product_type': 'Wash & Iron', 'rate': 25.00, 'description': 'Complete suit wash and iron'},
                
                # Dry Clean Products
                {'product_name': 'Shirt Dry Clean', 'product_type': 'Dry Clean', 'rate': 15.00, 'description': 'Professional shirt dry cleaning'},
                {'product_name': 'Pants Dry Clean', 'product_type': 'Dry Clean', 'rate': 18.00, 'description': 'Trousers dry cleaning'},
                {'product_name': 'Suit Dry Clean', 'product_type': 'Dry Clean', 'rate': 35.00, 'description': 'Complete suit dry cleaning'},
                {'product_name': 'Coat Dry Clean', 'product_type': 'Dry Clean', 'rate': 30.00, 'description': 'Coat dry cleaning'},
                {'product_name': 'Dress Dry Clean', 'product_type': 'Dry Clean', 'rate': 20.00, 'description': 'Dress dry cleaning'},
                
                # Press Only Products
                {'product_name': 'Shirt Press Only', 'product_type': 'Press Only', 'rate': 5.00, 'description': 'Shirt ironing only'},
                {'product_name': 'Pants Press Only', 'product_type': 'Press Only', 'rate': 6.00, 'description': 'Trousers ironing only'},
                {'product_name': 'Dress Press Only', 'product_type': 'Press Only', 'rate': 8.00, 'description': 'Dress ironing only'},
                
                # Starch Products
                {'product_name': 'Shirt with Starch', 'product_type': 'Starch', 'rate': 10.00, 'description': 'Shirt with starch finish'},
                {'product_name': 'Pants with Starch', 'product_type': 'Starch', 'rate': 12.00, 'description': 'Trousers with starch finish'},
                
                # Express Products
                {'product_name': 'Express Shirt', 'product_type': 'Express', 'rate': 12.00, 'description': 'Same day shirt service'},
                {'product_name': 'Express Pants', 'product_type': 'Express', 'rate': 15.00, 'description': 'Same day pants service'},
                {'product_name': 'Express Suit', 'product_type': 'Express', 'rate': 40.00, 'description': 'Same day suit service'},
                
                # Bulk Products
                {'product_name': 'Bulk Shirts (10+)', 'product_type': 'Bulk', 'rate': 6.00, 'description': 'Bulk shirt discount'},
                {'product_name': 'Bulk Pants (10+)', 'product_type': 'Bulk', 'rate': 8.00, 'description': 'Bulk pants discount'},
                {'product_name': 'Bulk Mixed (20+)', 'product_type': 'Bulk', 'rate': 7.00, 'description': 'Mixed bulk discount'}
            ]
        }
        
        return jsonify({
            'success': True,
            'data': default_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/setup/populate-products', methods=['POST'])
def populate_default_products():
    """Populate default products and product types for laundry shop"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        # Get default data
        resp = get_default_products()
        default_data = resp.get_json()['data']
        
        # Insert product types first
        product_type_ids = {}
        for pt in default_data['product_types']:
            cursor = get_db().cursor()
            placeholder = get_placeholder()
            cursor.execute(f'''
                INSERT INTO product_types (type_name, description, user_id) 
                VALUES ({placeholder}, {placeholder}, {placeholder})
            ''', (pt['type_name'], pt['description'], user_id))
            product_type_ids[pt['type_name']] = cursor.lastrowid
            get_db().commit()
        
        # Insert products
        for product in default_data['products']:
            cursor = get_db().cursor()
            placeholder = get_placeholder()
            cursor.execute(f'''
                INSERT INTO products (product_name, product_type_id, rate, description, user_id) 
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            ''', (
                product['product_name'], 
                product_type_ids[product['product_type']], 
                product['rate'], 
                product['description'], 
                user_id
            ))
            get_db().commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully populated {len(default_data["product_types"])} product types and {len(default_data["products"])} products'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
            'vat_percent': float(bill.get('vat_percent', 0)),
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
@app.route('/api/bills/<int:bill_id>/send-email', methods=['POST'])
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

@app.route('/api/email/test', methods=['POST'])
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

@app.route('/api/email/config', methods=['GET'])
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

@app.route('/api/email/config', methods=['PUT'])
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



# WhatsApp Integration Functions
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
    
    # Handle UAE phone numbers properly
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
            # Add 971 prefix
            clean_phone = '971' + clean_phone
    
    # URL encode the message
    import urllib.parse
    encoded_message = urllib.parse.quote(message)
    
    # Generate WhatsApp share link
    whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_message}"
    
    return whatsapp_url

@app.route('/api/bills/<int:bill_id>/whatsapp', methods=['POST'])
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
        import re
        phone_digits = re.sub(r'\D', '', phone_number)
        if len(phone_digits) < 9:
            return jsonify({'success': False, 'error': 'Invalid phone number format. Please enter a valid UAE phone number.'}), 400
        
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

@app.route('/api/whatsapp/test', methods=['POST'])
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



# Admin authentication decorator
def admin_required(f):
    """Decorator to require admin authentication."""
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect('/admin/login')
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/admin/login')
def admin_login():
    """Admin login page."""
    if 'admin_logged_in' in session:
        return redirect('/admin')
    return render_template('admin_login.html')

@app.route('/api/admin/login', methods=['POST'])
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
        
        import bcrypt
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

@app.route('/api/admin/logout', methods=['POST'])
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

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard for plan management."""
    return render_template('admin.html')

# Admin API Endpoints
@app.route('/api/admin/stats')
@admin_required
def admin_stats():
    """Get admin dashboard statistics."""
    try:
        conn = get_db_connection()
        
        # Total shops
        cursor = execute_query(conn, 'SELECT COUNT(*) FROM users WHERE is_active = TRUE')
        result = cursor.fetchone()
        total_shops = result[0] if isinstance(result, tuple) else result['count']
        
        # Active plans (not expired)
        cursor = execute_query(conn, '''
            SELECT COUNT(*) FROM user_plans up
            JOIN users u ON up.user_id = u.user_id
            WHERE up.is_active = TRUE AND u.is_active = TRUE
            AND (up.plan_type = 'pro' OR up.plan_end_date > DATE('now'))
        ''')
        result = cursor.fetchone()
        active_plans = result[0] if isinstance(result, tuple) else result['count']
        
        # Expiring soon (within 7 days)
        cursor = execute_query(conn, '''
            SELECT COUNT(*) FROM user_plans up
            JOIN users u ON up.user_id = u.user_id
            WHERE up.is_active = TRUE AND u.is_active = TRUE
            AND up.plan_type != 'pro'
            AND up.plan_end_date BETWEEN DATE('now') AND DATE('now', '+7 days')
        ''')
        result = cursor.fetchone()
        expiring_soon = result[0] if isinstance(result, tuple) else result['count']
        
        # Expired plans
        cursor = execute_query(conn, '''
            SELECT COUNT(*) FROM user_plans up
            JOIN users u ON up.user_id = u.user_id
            WHERE up.is_active = TRUE AND u.is_active = TRUE
            AND up.plan_type != 'pro'
            AND up.plan_end_date < DATE('now')
        ''')
        result = cursor.fetchone()
        expired_plans = result[0] if isinstance(result, tuple) else result['count']
        
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

@app.route('/api/admin/shops')
@admin_required
def admin_shops():
    """Get all shops with their plan information."""
    try:
        conn = get_db_connection()
        
        cursor = execute_query(conn, '''
            SELECT u.user_id, u.shop_name, u.email, u.mobile, u.created_at,
                   up.plan_type, up.plan_start_date, up.plan_end_date,
                   CASE 
                       WHEN up.plan_type = 'pro' AND up.plan_end_date IS NULL THEN 'Unlimited'
                       WHEN up.plan_end_date IS NULL THEN 0
                       ELSE CAST(JULIANDAY(up.plan_end_date) - JULIANDAY('now') AS INTEGER)
                   END as days_remaining,
                   CASE 
                       WHEN up.plan_type = 'pro' AND up.plan_end_date IS NULL THEN 0
                       WHEN up.plan_end_date IS NULL THEN 1
                       ELSE CASE WHEN up.plan_end_date < DATE('now') THEN 1 ELSE 0 END
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

@app.route('/api/admin/shops/<int:user_id>/plan')
@admin_required
def admin_shop_plan(user_id):
    """Get plan details for a specific shop."""
    try:
        conn = get_db_connection()
        
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT up.plan_type as plan, up.plan_start_date as start_date, 
                   up.plan_end_date as expiry_date,
                   CASE 
                       WHEN up.plan_type = 'pro' AND up.plan_end_date IS NULL THEN 'Unlimited'
                       WHEN up.plan_end_date IS NULL THEN 0
                       ELSE CAST(JULIANDAY(up.plan_end_date) - JULIANDAY('now') AS INTEGER)
                   END as days_remaining,
                   CASE 
                       WHEN up.plan_type = 'pro' AND up.plan_end_date IS NULL THEN 0
                       WHEN up.plan_end_date IS NULL THEN 1
                       ELSE CASE WHEN up.plan_end_date < DATE('now') THEN 1 ELSE 0 END
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

@app.route('/api/admin/plans/upgrade', methods=['POST'])
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
        # Use TRUE/FALSE for PostgreSQL, 1/0 for SQLite
        is_active_value = 'FALSE' if is_postgresql() else '0'
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
        # Use TRUE/FALSE for PostgreSQL, 1/0 for SQLite
        is_active_value = 'TRUE' if is_postgresql() else '1'
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

@app.route('/api/admin/plans/expire', methods=['POST'])
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

@app.route('/api/admin/activity')
@admin_required
def admin_activity():
    """Get recent admin activity."""
    try:
        conn = get_db_connection()
        
        activities = execute_update(conn, '''
            SELECT ua.action, ua.details, ua.timestamp, u.shop_name
            FROM user_actions ua
            LEFT JOIN users u ON ua.user_id = u.user_id
            WHERE ua.action IN ('plan_upgrade', 'plan_expire', 'plan_renew')
            ORDER BY ua.timestamp DESC
            LIMIT 20
        ''').fetchall()
        
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

@app.route('/admin/logs')
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

# Expense Categories API
@app.route('/api/expense-categories', methods=['GET'])
def get_expense_categories():
    """Get all expense categories for current user."""
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    cursor = execute_query(conn, f'''
        SELECT * FROM expense_categories 
        WHERE user_id = {placeholder} AND is_active = TRUE 
        ORDER BY category_name
    ''', (user_id,))
    categories = cursor.fetchall()
    conn.close()
    return jsonify([dict(category) for category in categories])

@app.route('/api/expense-categories', methods=['POST'])
def add_expense_category():
    """Add new expense category."""
    data = request.get_json()
    name = data.get('category_name', '').strip()
    description = data.get('description', '').strip()
    user_id = get_current_user_id()
    
    if not name:
        return jsonify({'error': 'Category name is required'}), 400
    
    conn = get_db_connection()
    try:
        placeholder = get_placeholder()
        sql = f'''
            INSERT INTO expense_categories (user_id, category_name, description) 
            VALUES ({placeholder}, {placeholder}, {placeholder})
        '''
        category_id = execute_with_returning(conn, sql, (user_id, name, description))
        conn.close()
        
        log_user_action('expense_category_added', user_id, {'category_name': name})
        return jsonify({'id': category_id, 'message': 'Category added successfully'})
    except get_db_integrity_error():
        conn.close()
        return jsonify({'error': 'Category already exists'}), 400
    except Exception as e:
        conn.close()
        log_dml_error('INSERT', 'expense_categories', e, user_id, data)
        return jsonify({'error': 'Failed to add category'}), 500

@app.route('/api/expense-categories/<int:category_id>', methods=['PUT'])
def update_expense_category(category_id):
    """Update expense category."""
    data = request.get_json()
    name = data.get('category_name', '').strip()
    description = data.get('description', '').strip()
    user_id = get_current_user_id()
    
    if not name:
        return jsonify({'error': 'Category name is required'}), 400
    
    conn = get_db_connection()
    try:
        # Check if category exists and belongs to user
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT category_id FROM expense_categories 
            WHERE category_id = {placeholder} AND user_id = {placeholder}
        ''', (category_id, user_id))
        category = cursor.fetchone()
        
        if not category:
            conn.close()
            return jsonify({'error': 'Category not found'}), 404
        
        placeholder = get_placeholder()
        sql = f'''
            UPDATE expense_categories 
            SET category_name = {placeholder}, description = {placeholder} 
            WHERE category_id = {placeholder} AND user_id = {placeholder}
        '''
        execute_update(conn, sql, (name, description, category_id, user_id))
        conn.close()
        
        log_user_action('expense_category_updated', user_id, {'category_id': category_id, 'category_name': name})
        return jsonify({'message': 'Category updated successfully'})
    except get_db_integrity_error():
        conn.close()
        return jsonify({'error': 'Category name already exists'}), 400
    except Exception as e:
        conn.close()
        log_dml_error('UPDATE', 'expense_categories', e, user_id, data)
        return jsonify({'error': 'Failed to update category'}), 500

@app.route('/api/expense-categories/<int:category_id>', methods=['DELETE'])
def delete_expense_category(category_id):
    """Delete expense category (soft delete)."""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    try:
        # Check if category has expenses
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT COUNT(*) FROM expenses 
            WHERE category_id = {placeholder} AND user_id = {placeholder}
        ''', (category_id, user_id))
        result = cursor.fetchone()
        # Handle both PostgreSQL (dict) and SQLite (tuple) results
        expense_count = result[0] if isinstance(result, tuple) else result['count']
        
        if expense_count > 0:
            conn.close()
            return jsonify({'error': 'Cannot delete category with existing expenses'}), 400
        
        # Soft delete by setting is_active = 0
        placeholder = get_placeholder()
        # Use TRUE/FALSE for PostgreSQL, 1/0 for SQLite
        is_active_value = 'FALSE' if is_postgresql() else '0'
        sql = f'''
            UPDATE expense_categories 
            SET is_active = {is_active_value} 
            WHERE category_id = {placeholder} AND user_id = {placeholder}
        '''
        execute_update(conn, sql, (category_id, user_id))
        conn.close()
        
        log_user_action('expense_category_deleted', user_id, {'category_id': category_id})
        return jsonify({'message': 'Category deleted successfully'})
    except Exception as e:
        conn.close()
        log_dml_error('DELETE', 'expense_categories', e, user_id, {'category_id': category_id})
        return jsonify({'error': 'Failed to delete category'}), 500

# Expenses API
@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    """Get expenses with optional filtering."""
    user_id = get_current_user_id()
    
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category_id = request.args.get('category_id')
    search = request.args.get('search', '').strip()
    
    conn = get_db_connection()
    
    # Build query with filters
    placeholder = get_placeholder()
    query = f'''
        SELECT e.*, ec.category_name 
        FROM expenses e 
        JOIN expense_categories ec ON e.category_id = ec.category_id 
        WHERE e.user_id = {placeholder} AND ec.user_id = {placeholder}
    '''
    params = [user_id, user_id]
    
    if start_date:
        query += f' AND e.expense_date >= {placeholder}'
        params.append(start_date)
    
    if end_date:
        query += f' AND e.expense_date <= {placeholder}'
        params.append(end_date)
    
    if category_id:
        query += f' AND e.category_id = {placeholder}'
        params.append(category_id)
    
    if search:
        query += f' AND (e.description LIKE {placeholder} OR ec.category_name LIKE {placeholder})'
        search_param = f'%{search}%'
        params.extend([search_param, search_param])
    
    query += ' ORDER BY e.expense_date DESC, e.created_at DESC'
    
    cursor = execute_query(conn, query, params)

    try:
        expenses = cursor.fetchall()
        conn.close()
        
        # Filter out any expenses with invalid dates
        valid_expenses = []
        for expense in expenses:
            try:
                # Convert to dict and validate date
                expense_dict = dict(expense)
                if 'expense_date' in expense_dict and expense_dict['expense_date']:
                    # Try to parse the date to ensure it's valid
                    datetime.strptime(str(expense_dict['expense_date']), '%Y-%m-%d')
                valid_expenses.append(expense_dict)
            except (ValueError, TypeError) as e:
                print(f"Skipping expense with invalid date: {e}")
                continue
        
        return jsonify(valid_expenses)
    except Exception as e:
        conn.close()
        print(f"Error fetching expenses: {e}")
        return jsonify([])

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    """Add new expense."""
    data = request.get_json()
    category_id = data.get('category_id')
    expense_date = data.get('expense_date')
    amount = data.get('amount')
    description = data.get('description', '').strip()
    payment_method = data.get('payment_method', 'Cash')
    receipt_url = data.get('receipt_url', '').strip()
    user_id = get_current_user_id()
    
    # Validation
    if not all([category_id, expense_date, amount]):
        return jsonify({'error': 'Category, date, and amount are required'}), 400
    
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid amount value'}), 400
    
    conn = get_db_connection()
    try:
        # Verify category belongs to user
        placeholder = get_placeholder()
        category = execute_query(conn, f'''
            SELECT category_id FROM expense_categories 
            WHERE category_id = {placeholder} AND user_id = {placeholder} AND is_active = TRUE
        ''', (category_id, user_id)).fetchone()
        
        if not category:
            conn.close()
            return jsonify({'error': 'Invalid category'}), 400
        
        placeholder = get_placeholder()
        sql = f'''
            INSERT INTO expenses (user_id, category_id, expense_date, amount, description, payment_method, receipt_url) 
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        '''
        expense_id = execute_with_returning(conn, sql, (user_id, category_id, expense_date, amount, description, payment_method, receipt_url))
        conn.close()
        
        # Remove the log_user_action call since it doesn't exist
        return jsonify({'id': expense_id, 'message': 'Expense added successfully'})
    except Exception as e:
        conn.close()
        # Remove the log_dml_error call since it doesn't exist
        return jsonify({'error': 'Failed to add expense'}), 500

# Recurring Expenses API
@app.route('/api/recurring-expenses', methods=['GET'])
def get_recurring_expenses():
    """Get recurring expenses for the current user."""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    placeholder = get_placeholder()
    query = f'''
        SELECT re.*, ec.category_name 
        FROM recurring_expenses re 
        JOIN expense_categories ec ON re.category_id = ec.category_id 
        WHERE re.user_id = {placeholder} AND ec.user_id = {placeholder} AND re.is_active = TRUE
        ORDER BY re.created_at DESC
    '''
    
    cursor = execute_query(conn, query, (user_id, user_id))
    recurring_expenses = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(expense) for expense in recurring_expenses])

@app.route('/api/recurring-expenses', methods=['POST'])
def add_recurring_expense():
    """Add new recurring expense."""
    data = request.get_json()
    title = data.get('title')
    amount = data.get('amount')
    description = data.get('description', '').strip()
    category_id = data.get('category_id')
    frequency = data.get('frequency')
    payment_method = data.get('payment_method', 'Cash')
    start_date = data.get('start_date')
    user_id = get_current_user_id()
    
    # Validation
    if not all([title, amount, category_id, frequency, start_date]):
        return jsonify({'error': 'Title, amount, category, frequency, and start date are required'}), 400
    
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid amount value'}), 400
    
    conn = get_db_connection()
    try:
        # Verify category belongs to user
        placeholder = get_placeholder()
        category = execute_query(conn, f'''
            SELECT category_id FROM expense_categories 
            WHERE category_id = {placeholder} AND user_id = {placeholder} AND is_active = TRUE
        ''', (category_id, user_id)).fetchone()
        
        if not category:
            conn.close()
            return jsonify({'error': 'Invalid category'}), 400
        
        # Calculate next_due_date based on start_date and frequency
        from datetime import datetime, timedelta
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        if frequency == 'daily':
            next_due_date = start_date_obj + timedelta(days=1)
        elif frequency == 'weekly':
            next_due_date = start_date_obj + timedelta(weeks=1)
        elif frequency == 'monthly':
            # Add one month (approximate)
            if start_date_obj.month == 12:
                next_due_date = start_date_obj.replace(year=start_date_obj.year + 1, month=1)
            else:
                next_due_date = start_date_obj.replace(month=start_date_obj.month + 1)
        elif frequency == 'yearly':
            next_due_date = start_date_obj.replace(year=start_date_obj.year + 1)
        else:
            next_due_date = start_date_obj + timedelta(days=1)  # Default to daily
        
        placeholder = get_placeholder()
        sql = f'''
            INSERT INTO recurring_expenses (user_id, title, amount, description, category_id, frequency, payment_method, start_date, next_due_date) 
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        '''
        recurring_id = execute_with_returning(conn, sql, (user_id, title, amount, description, category_id, frequency, payment_method, start_date, next_due_date))
        conn.close()
        
        return jsonify({'id': recurring_id, 'message': 'Recurring expense added successfully'})
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Failed to add recurring expense'}), 500

@app.route('/api/invoice-summary', methods=['POST'])
def get_invoice_summary():
    """Get filtered invoice summary data."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    filters = request.json.get('filters', {})
    
    try:
        summary_data = get_filtered_invoice_summary(user_id, filters)
        return jsonify(summary_data)
    except Exception as e:
        print(f"Error in get_invoice_summary: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/expenses/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    """Get specific expense."""
    user_id = get_current_user_id()
    conn = get_db_connection()
    placeholder = get_placeholder()
    expense = execute_query(conn, f'''
        SELECT e.*, ec.category_name 
        FROM expenses e 
        JOIN expense_categories ec ON e.category_id = ec.category_id 
        WHERE e.expense_id = {placeholder} AND e.user_id = {placeholder} AND ec.user_id = {placeholder}
    ''', (expense_id, user_id, user_id)).fetchone()
    conn.close()
    
    if expense:
        return jsonify(dict(expense))
    else:
        return jsonify({'error': 'Expense not found'}), 404

@app.route('/api/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """Update expense."""
    data = request.get_json()
    category_id = data.get('category_id')
    expense_date = data.get('expense_date')
    amount = data.get('amount')
    description = data.get('description', '').strip()
    payment_method = data.get('payment_method', 'Cash')
    receipt_url = data.get('receipt_url', '').strip()
    user_id = get_current_user_id()
    
    # Validation
    if not all([category_id, expense_date, amount]):
        return jsonify({'error': 'Category, date, and amount are required'}), 400
    
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid amount value'}), 400
    
    conn = get_db_connection()
    try:
        # Verify expense and category belong to user
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT expense_id FROM expenses 
            WHERE expense_id = {placeholder} AND user_id = {placeholder}
        ''', (expense_id, user_id))
        expense = cursor.fetchone()
        
        cursor = execute_query(conn, f'''
            SELECT category_id FROM expense_categories 
            WHERE category_id = {placeholder} AND user_id = {placeholder} AND is_active = TRUE
        ''', (category_id, user_id))
        category = cursor.fetchone()
        
        if not expense:
            conn.close()
            return jsonify({'error': 'Expense not found'}), 404
        
        if not category:
            conn.close()
            return jsonify({'error': 'Invalid category'}), 400
        
        placeholder = get_placeholder()
        sql = f'''
            UPDATE expenses 
            SET category_id = {placeholder}, expense_date = {placeholder}, amount = {placeholder}, description = {placeholder}, payment_method = {placeholder}, receipt_url = {placeholder} 
            WHERE expense_id = {placeholder} AND user_id = {placeholder}
        '''
        execute_update(conn, sql, (category_id, expense_date, amount, description, payment_method, receipt_url, expense_id, user_id))
        conn.close()
        
        log_user_action('expense_updated', user_id, {'expense_id': expense_id, 'amount': amount, 'category_id': category_id})
        return jsonify({'message': 'Expense updated successfully'})
    except Exception as e:
        conn.close()
        log_dml_error('UPDATE', 'expenses', e, user_id, data)
        return jsonify({'error': 'Failed to update expense'}), 500

@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """Delete expense."""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    try:
        # Get expense details for logging
        placeholder = get_placeholder()
        cursor = execute_query(conn, f'''
            SELECT amount, category_id FROM expenses 
            WHERE expense_id = {placeholder} AND user_id = {placeholder}
        ''', (expense_id, user_id))
        expense = cursor.fetchone()
        
        if not expense:
            conn.close()
            return jsonify({'error': 'Expense not found'}), 404
        
        placeholder = get_placeholder()
        execute_update(conn, f'DELETE FROM expenses WHERE expense_id = {placeholder} AND user_id = {placeholder}', (expense_id, user_id))
        conn.close()
        
        log_user_action('expense_deleted', user_id, {
            'expense_id': expense_id, 
            'amount': expense['amount'], 
            'category_id': expense['category_id']
        })
        return jsonify({'message': 'Expense deleted successfully'})
    except Exception as e:
        conn.close()
        log_dml_error('DELETE', 'expenses', e, user_id, {'expense_id': expense_id})
        return jsonify({'error': 'Failed to delete expense'}), 500

@app.route('/api/expenses/report', methods=['GET'])
def expense_report():
    """Get expense report with summary data."""
    user_id = get_current_user_id()
    
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category_id = request.args.get('category_id')
    
    conn = get_db_connection()
    
    # Build base query
    base_where = 'WHERE e.user_id = ? AND ec.user_id = ?'
    params = [user_id, user_id]
    
    if start_date:
        base_where += ' AND e.expense_date >= ?'
        params.append(start_date)
    
    if end_date:
        base_where += ' AND e.expense_date <= ?'
        params.append(end_date)
    
    if category_id:
        base_where += ' AND e.category_id = ?'
        params.append(category_id)
    
    # Get total expenses
    total_query = f'''
        SELECT SUM(e.amount) as total_amount, COUNT(*) as total_count
        FROM expenses e 
        JOIN expense_categories ec ON e.category_id = ec.category_id 
        {base_where}
    '''
    cursor = execute_query(conn, total_query, params)

    total_result = cursor.fetchone()
    
    # Get expenses by category
    category_query = f'''
        SELECT ec.category_name, SUM(e.amount) as total_amount, COUNT(*) as count
        FROM expenses e 
        JOIN expense_categories ec ON e.category_id = ec.category_id 
        {base_where}
        GROUP BY ec.category_id, ec.category_name
        ORDER BY total_amount DESC
    '''
    cursor = execute_query(conn, category_query, params)

    category_results = cursor.fetchall()
    
    # Get monthly breakdown
    monthly_query = f'''
        SELECT strftime('%Y-%m', e.expense_date) as month, 
               SUM(e.amount) as total_amount, COUNT(*) as count
        FROM expenses e 
        JOIN expense_categories ec ON e.category_id = ec.category_id 
        {base_where}
        GROUP BY strftime('%Y-%m', e.expense_date)
        ORDER BY month DESC
        LIMIT 12
    '''
    cursor = execute_query(conn, monthly_query, params)

    monthly_results = cursor.fetchall()
    
    conn.close()
    
    return jsonify({
        'summary': {
            'total_amount': float(total_result['total_amount'] or 0),
            'total_count': total_result['total_count'] or 0
        },
        'by_category': [dict(result) for result in category_results],
        'by_month': [dict(result) for result in monthly_results]
    })

@app.route('/api/expenses/download', methods=['GET'])
def download_expenses():
    """Download expenses as CSV."""
    user_id = get_current_user_id()
    
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category_id = request.args.get('category_id')
    
    conn = get_db_connection()
    
    # Build query
    query = '''
        SELECT e.expense_date, ec.category_name, e.amount, e.description, e.payment_method, e.receipt_url
        FROM expenses e 
        JOIN expense_categories ec ON e.category_id = ec.category_id 
        WHERE e.user_id = ? AND ec.user_id = ?
    '''
    params = [user_id, user_id]
    
    if start_date:
        query += ' AND e.expense_date >= ?'
        params.append(start_date)
    
    if end_date:
        query += ' AND e.expense_date <= ?'
        params.append(end_date)
    
    if category_id:
        query += ' AND e.category_id = ?'
        params.append(category_id)
    
    query += ' ORDER BY e.expense_date DESC'
    
    cursor = execute_query(conn, query, params)

    
    expenses = cursor.fetchall()
    conn.close()
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Category', 'Amount', 'Description', 'Payment Method', 'Receipt URL'])
    
    for expense in expenses:
        writer.writerow([
            expense['expense_date'],
            expense['category_name'],
            expense['amount'],
            expense['description'] or '',
            expense['payment_method'],
            expense['receipt_url'] or ''
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=expenses.csv'}
    )

@app.route('/api/admin/setup', methods=['POST'])
def admin_setup():
    """Setup admin user for production environment."""
    try:
        # Import the setup function
        from setup_production_admin import setup_production_admin
        
        success = setup_production_admin()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Admin setup completed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Admin setup failed'
            }), 500
            
    except Exception as e:
        logger.error(f"Admin setup error: {e}")
        return jsonify({
            'success': False,
            'message': f'Admin setup failed: {str(e)}'
        }), 500

@app.route('/static/<path:filename>')
def static_with_cache_busting(filename):
    """Serve static files with cache-busting headers."""
    response = send_from_directory('static', filename)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    # Add timestamp to force cache refresh
    response.headers['Last-Modified'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
    return response

@app.route('/api/catalog/scan', methods=['POST'])
def scan_catalog():
    """Scan existing catalog and suggest product types and products"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        catalog_data = data.get('catalog', [])
        
        if not catalog_data:
            return jsonify({'success': False, 'error': 'No catalog data provided'}), 400
        
        # Analyze catalog data to extract patterns
        product_analysis = analyze_catalog_data(catalog_data)
        
        # Generate suggestions
        suggestions = generate_product_suggestions(product_analysis)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'analysis': product_analysis
        })
        
    except Exception as e:
        logger.error(f"Catalog scan error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/catalog/check-duplicates', methods=['POST'])
def check_catalog_duplicates():
    """Check for duplicates before creating products"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        suggestions = data.get('suggestions', {})
        
        if not suggestions:
            return jsonify({'success': False, 'error': 'No suggestions provided'}), 400
        
        # Check existing items
        existing_items = check_existing_items(user_id, suggestions)
        
        # Find similar products
        similar_products = {}
        for type_suggestion in suggestions.get('product_types', []):
            for product_suggestion in type_suggestion.get('products', []):
                product_name = product_suggestion['name']
                similar = find_similar_products(user_id, product_name)
                if similar:
                    similar_products[product_name] = similar
        
        # Calculate statistics
        total_types = len(suggestions.get('product_types', []))
        total_products = sum(len(t.get('products', [])) for t in suggestions.get('product_types', []))
        
        existing_types = sum(1 for t in existing_items['product_types'].values() if t['exists'])
        existing_products = sum(1 for p in existing_items['products'].values() if p['exists'])
        
        new_types = total_types - existing_types
        new_products = total_products - existing_products
        
        return jsonify({
            'success': True,
            'analysis': {
                'total_types': total_types,
                'total_products': total_products,
                'existing_types': existing_types,
                'existing_products': existing_products,
                'new_types': new_types,
                'new_products': new_products,
                'duplicate_percentage': (existing_products / total_products * 100) if total_products > 0 else 0
            },
            'existing_items': existing_items,
            'similar_products': similar_products
        })
        
    except Exception as e:
        logger.error(f"Duplicate check error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/catalog/auto-create', methods=['POST'])
def auto_create_products():
    """Automatically create product types and products from catalog scan"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        suggestions = data.get('suggestions', {})
        
        if not suggestions:
            return jsonify({'success': False, 'error': 'No suggestions provided'}), 400
        
        conn = get_db_connection()
        created_types = []
        created_products = []
        
        try:
            # Create product types first
            for type_suggestion in suggestions.get('product_types', []):
                type_name = type_suggestion['name']
                description = type_suggestion.get('description', f'Products in {type_name} category')
                
                # Check if type already exists
                placeholder = get_placeholder()
                existing = execute_update(conn, 
                    f'SELECT type_id FROM product_types WHERE user_id = {placeholder} AND type_name = {placeholder}', 
                    (user_id, type_name)
                ).fetchone()
                
                if not existing:
                    cursor = conn.cursor()
                    placeholder = get_placeholder()
                    cursor.execute(
                        f'INSERT INTO product_types (user_id, type_name, description) VALUES ({placeholder}, {placeholder}, {placeholder})',
                        (user_id, type_name, description)
                    )
                    type_id = cursor.lastrowid
                    created_types.append({
                        'type_id': type_id,
                        'name': type_name,
                        'description': description
                    })
                else:
                    type_id = existing['type_id']
                
                # Create products for this type
                for product_suggestion in type_suggestion.get('products', []):
                    product_name = product_suggestion['name']
                    rate = product_suggestion['rate']
                    product_description = product_suggestion.get('description', '')
                    
                    # Check if product already exists
                    placeholder = get_placeholder()
                    existing_product = execute_update(conn, 
                        f'SELECT product_id FROM products WHERE user_id = {placeholder} AND product_name = {placeholder}', 
                        (user_id, product_name)
                    ).fetchone()
                    
                    if not existing_product:
                        cursor = conn.cursor()
                        placeholder = get_placeholder()
                        cursor.execute(
                            f'INSERT INTO products (user_id, type_id, product_name, rate, description) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})',
                            (user_id, type_id, product_name, rate, product_description)
                        )
                        created_products.append({
                            'product_id': cursor.lastrowid,
                            'name': product_name,
                            'type_name': type_name,
                            'rate': rate,
                            'description': product_description
                        })
            return jsonify({
                'success': True,
                'message': f'Successfully created {len(created_types)} product types and {len(created_products)} products',
                'created_types': created_types,
                'created_products': created_products
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Auto-create products error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def analyze_catalog_data(catalog_data):
    """Analyze catalog data to extract patterns and categories"""
    analysis = {
        'total_items': len(catalog_data),
        'categories': {},
        'price_ranges': {},
        'common_patterns': []
    }
    
    for item in catalog_data:
        name = item.get('name', '').lower()
        price = item.get('price', 0)
        category = item.get('category', '')
        
        # Analyze by category
        if category:
            if category not in analysis['categories']:
                analysis['categories'][category] = {
                    'count': 0,
                    'avg_price': 0,
                    'min_price': float('inf'),
                    'max_price': 0,
                    'products': []
                }
            
            cat_data = analysis['categories'][category]
            cat_data['count'] += 1
            cat_data['products'].append({
                'name': item.get('name', ''),
                'price': price,
                'description': item.get('description', '')
            })
            
            # Update price statistics
            total_price = cat_data['avg_price'] * (cat_data['count'] - 1) + price
            cat_data['avg_price'] = total_price / cat_data['count']
            cat_data['min_price'] = min(cat_data['min_price'], price)
            cat_data['max_price'] = max(cat_data['max_price'], price)
        
        # Analyze price ranges
        price_range = get_price_range(price)
        if price_range not in analysis['price_ranges']:
            analysis['price_ranges'][price_range] = 0
        analysis['price_ranges'][price_range] += 1
        
        # Extract common patterns from product names
        patterns = extract_name_patterns(name)
        analysis['common_patterns'].extend(patterns)
    
    # Remove duplicates from patterns
    analysis['common_patterns'] = list(set(analysis['common_patterns']))
    
    return analysis

def get_price_range(price):
    """Categorize price into ranges"""
    if price <= 10:
        return 'Budget (≤10)'
    elif price <= 25:
        return 'Standard (11-25)'
    elif price <= 50:
        return 'Premium (26-50)'
    elif price <= 100:
        return 'High-end (51-100)'
    else:
        return 'Luxury (>100)'

def extract_name_patterns(name):
    """Extract common patterns from product names"""
    patterns = []
    
    # Common keywords that might indicate product types
    keywords = [
        'shirt', 'pants', 'dress', 'suit', 'coat', 'blazer', 'kurti', 'saree',
        'lehenga', 'gown', 'abaya', 'kaftan', 'anarkali', 'palazzo', 'trouser',
        'blouse', 'salwar', 'patiala', 'sharara', 'gharara', 'jumpsuit'
    ]
    
    for keyword in keywords:
        if keyword in name:
            patterns.append(keyword)
    
    # Extract size patterns
    size_patterns = ['xs', 's', 'm', 'l', 'xl', 'xxl', 'plus']
    for size in size_patterns:
        if size in name:
            patterns.append(f'size_{size}')
    
    # Extract material patterns
    material_patterns = ['cotton', 'silk', 'polyester', 'wool', 'linen', 'denim']
    for material in material_patterns:
        if material in name:
            patterns.append(f'material_{material}')
    
    return patterns

def generate_product_suggestions(analysis):
    """Generate product type and product suggestions based on analysis"""
    suggestions = {
        'product_types': [],
        'recommendations': []
    }
    
    # Create product types from categories
    for category, data in analysis['categories'].items():
        if data['count'] >= 2:  # Only suggest types with multiple products
            type_suggestion = {
                'name': category.title(),
                'description': f'Products in {category} category with {data["count"]} items',
                'products': []
            }
            
            # Suggest products for this type
            for product in data['products']:
                product_suggestion = {
                    'name': product['name'],
                    'rate': product['price'],
                    'description': product.get('description', '')
                }
                type_suggestion['products'].append(product_suggestion)
            
            suggestions['product_types'].append(type_suggestion)
    
    # Generate recommendations based on patterns
    if analysis['common_patterns']:
        pattern_recommendations = []
        for pattern in analysis['common_patterns'][:10]:  # Limit to top 10 patterns
            pattern_recommendations.append({
                'pattern': pattern,
                'suggestion': f'Consider creating a "{pattern.title()}" product type'
            })
        suggestions['recommendations'].extend(pattern_recommendations)
    
    # Price range recommendations
    price_recommendations = []
    for price_range, count in analysis['price_ranges'].items():
        if count >= 3:
            price_recommendations.append({
                'price_range': price_range,
                'count': count,
                'suggestion': f'{count} products in {price_range} range - consider bulk pricing'
            })
    suggestions['recommendations'].extend(price_recommendations)
    
    return suggestions

# OCR Configuration and Setup
def setup_ocr():
    """Setup OCR configuration"""
    try:
        # Try to set Tesseract path for Windows
        if os.name == 'nt':  # Windows
            # Common Tesseract installation paths on Windows
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', '')),
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    logger.info(f"Tesseract found at: {path}")
                    break
            else:
                logger.warning("Tesseract not found in common Windows paths. Please install Tesseract OCR.")
        else:
            # Linux/Mac - assume tesseract is in PATH
            logger.info("Using system Tesseract installation")
            
    except Exception as e:
        logger.error(f"Error setting up OCR: {e}")

def preprocess_image(image):
    """Preprocess image for better OCR results"""
    try:
        if not OPENCV_AVAILABLE:
            # Fallback: return image as-is if OpenCV is not available
            logger.warning("OpenCV not available, skipping image preprocessing")
            return image
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply noise reduction
        denoised = cv2.medianBlur(gray, 3)
        
        # Apply thresholding to get binary image
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Apply morphological operations to clean up the image
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
        
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        return image

def extract_text_from_image(image_path):
    """Extract text from image using OCR"""
    try:
        if not OPENCV_AVAILABLE:
            # Fallback: use PIL for image reading if OpenCV is not available
            try:
                from PIL import Image
                image = Image.open(image_path)
                processed_image = image
                logger.info("Using PIL for image processing (OpenCV not available)")
            except ImportError:
                logger.error("Neither OpenCV nor PIL available for image processing")
                return {"text": "", "confidence": 0, "error": "No image processing library available"}
        else:
            # Read image with OpenCV
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not read image file")
            
            # Preprocess image
            processed_image = preprocess_image(image)
        
        # Extract text using Tesseract
        # Try different OCR configurations for better results
        configs = [
            '--oem 3 --psm 6',  # Default configuration
            '--oem 3 --psm 3',  # Fully automatic page segmentation
            '--oem 3 --psm 8',  # Single word
            '--oem 3 --psm 13'  # Raw line
        ]
        
        best_text = ""
        best_confidence = 0
        
        for config in configs:
            try:
                # Extract text with confidence
                data = pytesseract.image_to_data(processed_image, config=config, output_type=pytesseract.Output.DICT)
                
                # Calculate average confidence
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                if confidences:
                    avg_confidence = sum(confidences) / len(confidences)
                    
                    # Extract text
                    text = ' '.join([word for word, conf in zip(data['text'], data['conf']) if int(conf) > 30])
                    
                    if avg_confidence > best_confidence and text.strip():
                        best_confidence = avg_confidence
                        best_text = text
                        
            except Exception as e:
                logger.warning(f"OCR config {config} failed: {e}")
                continue
        
        # If no good results, try simple text extraction
        if not best_text.strip():
            best_text = pytesseract.image_to_string(processed_image)
        
        return {
            'text': best_text.strip(),
            'confidence': best_confidence,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error extracting text from image: {e}")
        return {
            'text': '',
            'confidence': 0,
            'success': False,
            'error': str(e)
        }

# OCR API Endpoints
@app.route('/api/ocr/extract', methods=['POST'])
def ocr_extract_text():
    """Extract text from uploaded image using OCR"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        # Check if file was uploaded
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'success': False, 'error': 'Invalid file type. Please upload an image file.'}), 400
        
        # Create uploads directory if it doesn't exist
        upload_dir = Path('uploads')
        upload_dir.mkdir(exist_ok=True)
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = upload_dir / unique_filename
        
        file.save(str(file_path))
        
        # Extract text using OCR
        result = extract_text_from_image(str(file_path))
        
        # Clean up uploaded file
        try:
            os.remove(str(file_path))
        except:
            pass  # Ignore cleanup errors
        
        if result['success']:
            return jsonify({
                'success': True,
                'text': result['text'],
                'confidence': result['confidence'],
                'message': 'Text extracted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to extract text from image')
            }), 500
            
    except Exception as e:
        logger.error(f"OCR extraction error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ocr/extract-batch', methods=['POST'])
def ocr_extract_batch():
    """Extract text from multiple uploaded images"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        # Check if files were uploaded
        if 'images' not in request.files:
            return jsonify({'success': False, 'error': 'No image files uploaded'}), 400
        
        files = request.files.getlist('images')
        if not files or files[0].filename == '':
            return jsonify({'success': False, 'error': 'No files selected'}), 400
        
        # Validate file types
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
        results = []
        
        # Create uploads directory if it doesn't exist
        upload_dir = Path('uploads')
        upload_dir.mkdir(exist_ok=True)
        
        for file in files:
            if file.filename == '':
                continue
                
            if not ('.' in file.filename and 
                    file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
                results.append({
                    'filename': file.filename,
                    'success': False,
                    'error': 'Invalid file type'
                })
                continue
            
            try:
                # Save uploaded file
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                file_path = upload_dir / unique_filename
                
                file.save(str(file_path))
                
                # Extract text using OCR
                result = extract_text_from_image(str(file_path))
                
                # Clean up uploaded file
                try:
                    os.remove(str(file_path))
                except:
                    pass
                
                results.append({
                    'filename': file.filename,
                    'success': result['success'],
                    'text': result.get('text', ''),
                    'confidence': result.get('confidence', 0),
                    'error': result.get('error', '')
                })
                
            except Exception as e:
                results.append({
                    'filename': file.filename,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'message': f'Processed {len(results)} images'
        })
        
    except Exception as e:
        logger.error(f"Batch OCR extraction error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Add to app.py - Enhanced duplicate detection

def check_existing_items(user_id, suggestions):
    """Check which items already exist in the database"""
    conn = get_db_connection()
    existing_items = {
        'product_types': {},
        'products': {}
    }
    
    try:
        # Check existing product types
        for type_suggestion in suggestions.get('product_types', []):
            type_name = type_suggestion['name']
            placeholder = get_placeholder()
            existing_type = execute_update(conn, 
                f'SELECT type_id, type_name FROM product_types WHERE user_id = {placeholder} AND type_name = {placeholder}', 
                (user_id, type_name)
            ).fetchone()
            
            if existing_type:
                existing_items['product_types'][type_name] = {
                    'exists': True,
                    'type_id': existing_type['type_id'],
                    'type_name': existing_type['type_name']
                }
            else:
                existing_items['product_types'][type_name] = {
                    'exists': False
                }
        
        # Check existing products
        for type_suggestion in suggestions.get('product_types', []):
            for product_suggestion in type_suggestion.get('products', []):
                product_name = product_suggestion['name']
                placeholder = get_placeholder()
                existing_product = execute_update(conn, 
                    f'SELECT product_id, product_name, rate FROM products WHERE user_id = {placeholder} AND product_name = {placeholder}', 
                    (user_id, product_name)
                ).fetchone()
                
                if existing_product:
                    existing_items['products'][product_name] = {
                        'exists': True,
                        'product_id': existing_product['product_id'],
                        'product_name': existing_product['product_name'],
                        'current_rate': existing_product['rate'],
                        'new_rate': product_suggestion['rate']
                    }
                else:
                    existing_items['products'][product_name] = {
                        'exists': False
                    }
        
        return existing_items
        
    finally:
        conn.close()

def find_similar_products(user_id, product_name, threshold=0.8):
    """Find similar products using fuzzy matching"""
    from difflib import SequenceMatcher
    
    conn = get_db_connection()
    similar_products = []
    
    try:
        # Get all existing products
        placeholder = get_placeholder()
        existing_products = execute_update(conn, 
            f'SELECT product_id, product_name, rate FROM products WHERE user_id = {placeholder}', 
            (user_id,)
        ).fetchall()
        
        for product in existing_products:
            similarity = SequenceMatcher(None, product_name.lower(), product['product_name'].lower()).ratio()
            if similarity >= threshold:
                similar_products.append({
                    'product_id': product['product_id'],
                    'product_name': product['product_name'],
                    'rate': product['rate'],
                    'similarity': similarity
                })
        
        # Sort by similarity
        similar_products.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_products
        
    finally:
        conn.close()

def get_invoice_summary_data(user_id, current_date=None):
    """Get comprehensive summary data for invoices."""
    if current_date is None:
        current_date = datetime.now().date()
    
    conn = get_db_connection()
    
    # Get current month data
    current_month_start = current_date.replace(day=1)
    current_month_end = (current_month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # Get current year data
    current_year_start = current_date.replace(month=1, day=1)
    current_year_end = current_date.replace(month=12, day=31)
    
    # Current month summary
    placeholder = get_placeholder()
    month_data = execute_query(conn, f'''
        SELECT 
            COUNT(*) as total_invoices,
            SUM(total_amount) as total_revenue,
            SUM(vat_amount) as total_vat_collected,
            SUM(subtotal) as total_subtotal,
            SUM(0) as total_discounts,
            AVG(total_amount) as avg_invoice_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM bills 
        WHERE user_id = {placeholder} 
        AND DATE(bill_date) BETWEEN {placeholder} AND {placeholder}
    ''', (user_id, current_month_start, current_month_end)).fetchone()
    
    # Current year summary
    year_data = execute_query(conn, f'''
        SELECT 
            COUNT(*) as total_invoices,
            SUM(total_amount) as total_revenue,
            SUM(vat_amount) as total_vat_collected,
            SUM(subtotal) as total_subtotal,
            SUM(0) as total_discounts,
            AVG(total_amount) as avg_invoice_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM bills 
        WHERE user_id = {placeholder} 
        AND DATE(bill_date) BETWEEN {placeholder} AND {placeholder}
    ''', (user_id, current_year_start, current_year_end)).fetchone()
    
    # All time summary
    all_time_data = execute_query(conn, f'''
        SELECT 
            COUNT(*) as total_invoices,
            SUM(total_amount) as total_revenue,
            SUM(vat_amount) as total_vat_collected,
            SUM(subtotal) as total_subtotal,
            SUM(0) as total_discounts,
            AVG(total_amount) as avg_invoice_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM bills 
        WHERE user_id = {placeholder}
    ''', (user_id,)).fetchone()
    
    # Get top selling products (current month)
    top_products = execute_query(conn, f'''
        SELECT 
            bi.product_name,
            SUM(bi.quantity) as total_quantity,
            SUM(bi.total_amount) as total_revenue
        FROM bill_items bi
        JOIN bills b ON bi.bill_id = b.bill_id
        WHERE b.user_id = {placeholder} 
        AND DATE(b.bill_date) BETWEEN {placeholder} AND {placeholder}
        GROUP BY bi.product_name
        ORDER BY total_revenue DESC
        LIMIT 5
    ''', (user_id, current_month_start, current_month_end)).fetchall()
    
    # Get top customers (current month)
    top_customers = execute_query(conn, f'''
        SELECT 
            c.name as customer_name,
            COUNT(b.bill_id) as invoice_count,
            SUM(b.total_amount) as total_spent
        FROM bills b
        JOIN customers c ON b.customer_id = c.customer_id
        WHERE b.user_id = {placeholder} 
        AND DATE(b.bill_date) BETWEEN {placeholder} AND {placeholder}
        GROUP BY c.customer_id, c.name
        ORDER BY total_spent DESC
        LIMIT 5
    ''', (user_id, current_month_start, current_month_end)).fetchall()
    
    conn.close()
    
    return {
        'current_month': dict(month_data),
        'current_year': dict(year_data),
        'all_time': dict(all_time_data),
        'top_products': [dict(product) for product in top_products],
        'top_customers': [dict(customer) for customer in top_customers],
        'summary_date': current_date.strftime('%B %Y')
    }

def get_filtered_invoice_summary(user_id, filters=None):
    """Get summary data for invoices based on filters."""
    if filters is None:
        filters = {}
    
    conn = get_db_connection()
    placeholder = get_placeholder()
    
    # Build WHERE clause based on filters
    where_conditions = [f'b.user_id = {placeholder}']
    params = [user_id]
    
    if filters.get('from_date'):
        where_conditions.append(f'DATE(b.bill_date) >= {placeholder}')
        params.append(filters['from_date'])
    
    if filters.get('to_date'):
        where_conditions.append(f'DATE(b.bill_date) <= {placeholder}')
        params.append(filters['to_date'])
    
    if filters.get('products') and filters['products'] != ['All Products']:
        product_list = filters['products']
        placeholders = ','.join([placeholder for _ in product_list])
        where_conditions.append(f'''EXISTS (
            SELECT 1 FROM bill_items bi2 
            WHERE bi2.bill_id = b.bill_id 
            AND bi2.product_name IN ({placeholders})
        )''')
        params.extend(product_list)
    
    if filters.get('employees') and filters['employees'] != ['All Employees']:
        employee_list = filters['employees']
        placeholders = ','.join([placeholder for _ in employee_list])
        where_conditions.append(f'b.employee_id IN (SELECT employee_id FROM employees WHERE name IN ({placeholders}) AND is_active = TRUE)')
        params.extend(employee_list)
    
    if filters.get('city') and filters['city'] != 'All Cities':
        where_conditions.append(f'c.city = {placeholder}')
        params.append(filters['city'])
    
    if filters.get('area') and filters['area'] != 'All Areas':
        where_conditions.append(f'c.area = {placeholder}')
        params.append(filters['area'])
    
    if filters.get('status') and filters['status'] != 'All':
        where_conditions.append(f'b.status = {placeholder}')
        params.append(filters['status'])
    
    where_clause = ' AND '.join(where_conditions)
    
    # Main summary query
    summary_query = f'''
        SELECT 
            COUNT(*) as total_invoices,
            COALESCE(SUM(b.total_amount), 0) as total_revenue,
            COALESCE(SUM(b.vat_amount), 0) as total_vat_collected,
            COALESCE(SUM(b.subtotal), 0) as total_subtotal,
            COALESCE(SUM(
                (SELECT SUM(bi.rate * bi.quantity * bi.discount / 100) 
                 FROM bill_items bi 
                 WHERE bi.bill_id = b.bill_id)
            ), 0) as total_discounts,
            COALESCE(AVG(b.total_amount), 0) as avg_invoice_value,
            COUNT(DISTINCT b.customer_id) as unique_customers,
            SUM(CASE WHEN b.status = 'Paid' THEN 1 ELSE 0 END) as paid_invoices,
            SUM(CASE WHEN b.status = 'Paid' THEN b.total_amount ELSE 0 END) as paid_amount,
            SUM(CASE WHEN b.status = 'Pending' THEN 1 ELSE 0 END) as pending_invoices,
            SUM(CASE WHEN b.status = 'Pending' THEN b.total_amount ELSE 0 END) as pending_amount
        FROM bills b
        LEFT JOIN customers c ON b.customer_id = c.customer_id
        WHERE {where_clause}
    '''
    
    cursor = execute_query(conn, summary_query, params)

    
    summary_data = cursor.fetchone()
    
    # Top products query
    top_products_query = f'''
        SELECT 
            bi.product_name,
            SUM(bi.quantity) as total_quantity,
            SUM(bi.total_amount) as total_revenue,
            COUNT(DISTINCT b.bill_id) as invoice_count
        FROM bill_items bi
        JOIN bills b ON bi.bill_id = b.bill_id
        LEFT JOIN customers c ON b.customer_id = c.customer_id
        WHERE {where_clause}
        GROUP BY bi.product_name
        ORDER BY total_revenue DESC
        LIMIT 5
    '''
    
    cursor = execute_query(conn, top_products_query, params)

    
    top_products = cursor.fetchall()
    
    # Top customers query
    top_customers_query = f'''
        SELECT 
            c.name as customer_name,
            COUNT(b.bill_id) as invoice_count,
            SUM(b.total_amount) as total_spent,
            AVG(b.total_amount) as avg_invoice_value
        FROM bills b
        JOIN customers c ON b.customer_id = c.customer_id
        WHERE {where_clause}
        GROUP BY c.customer_id, c.name
        ORDER BY total_spent DESC
        LIMIT 5
    '''
    
    cursor = execute_query(conn, top_customers_query, params)

    
    top_customers = cursor.fetchall()
    
    conn.close()
    
    return {
        'summary': dict(summary_data) if summary_data else {},
        'top_products': [dict(product) for product in top_products] if top_products else [],
        'top_customers': [dict(customer) for customer in top_customers] if top_customers else [],
        'filters_applied': filters
    }

# Financial Analytics APIs
@app.route('/api/analytics/financial-overview', methods=['GET'])
def get_financial_overview():
    """Get comprehensive financial overview with key metrics"""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    # Get date range from query params
    from_date = request.args.get('from_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    to_date = request.args.get('to_date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        # Revenue calculations
        placeholder = get_placeholder()
        revenue_data = execute_query(conn, f'''
            SELECT 
                COUNT(*) as total_invoices,
                SUM(total_amount) as total_revenue,
                SUM(subtotal) as gross_revenue,
                SUM(vat_amount) as total_vat,
                AVG(total_amount) as avg_invoice_value,
                COUNT(DISTINCT customer_id) as unique_customers
            FROM bills 
            WHERE user_id = {placeholder} 
            AND DATE(bill_date) BETWEEN {placeholder} AND {placeholder}
        ''', (user_id, from_date, to_date)).fetchone()
        
        # Expense calculations
        expense_data = execute_query(conn, f'''
            SELECT 
                COUNT(*) as total_expenses,
                SUM(amount) as total_expenses_amount,
                AVG(amount) as avg_expense_amount
            FROM expenses 
            WHERE user_id = {placeholder} 
            AND DATE(expense_date) BETWEEN {placeholder} AND {placeholder}
        ''', (user_id, from_date, to_date)).fetchone()
        
        # Calculate profit metrics
        total_revenue = float(revenue_data['total_revenue'] or 0)
        total_expenses = float(expense_data['total_expenses_amount'] or 0)
        net_profit = total_revenue - total_expenses
        gross_profit = float(revenue_data['gross_revenue'] or 0) - total_expenses
        
        # Calculate margins
        gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        net_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Get top revenue sources
        top_products = execute_query(conn, f'''
            SELECT 
                bi.product_name,
                SUM(bi.total_amount) as revenue,
                SUM(bi.quantity) as quantity_sold
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.bill_id
            WHERE b.user_id = {placeholder} 
            AND DATE(b.bill_date) BETWEEN {placeholder} AND {placeholder}
            GROUP BY bi.product_name
            ORDER BY revenue DESC
            LIMIT 5
        ''', (user_id, from_date, to_date)).fetchall()
        
        # Get top expense categories
        top_expense_categories = execute_query(conn, f'''
            SELECT 
                ec.category_name,
                SUM(e.amount) as total_amount,
                COUNT(*) as expense_count
            FROM expenses e
            JOIN expense_categories ec ON e.category_id = ec.category_id
            WHERE e.user_id = {placeholder} 
            AND DATE(e.expense_date) BETWEEN {placeholder} AND {placeholder}
            GROUP BY ec.category_id, ec.category_name
            ORDER BY total_amount DESC
            LIMIT 5
        ''', (user_id, from_date, to_date)).fetchall()
        
        conn.close()
        
        return jsonify({
            'period': {
                'from_date': from_date,
                'to_date': to_date
            },
            'revenue': {
                'total_revenue': total_revenue,
                'gross_revenue': float(revenue_data['gross_revenue'] or 0),
                'total_vat': float(revenue_data['total_vat'] or 0),
                'total_invoices': revenue_data['total_invoices'],
                'avg_invoice_value': float(revenue_data['avg_invoice_value'] or 0),
                'unique_customers': revenue_data['unique_customers']
            },
            'expenses': {
                'total_expenses': total_expenses,
                'total_expense_count': expense_data['total_expenses'],
                'avg_expense_amount': float(expense_data['avg_expense_amount'] or 0)
            },
            'profitability': {
                'gross_profit': gross_profit,
                'net_profit': net_profit,
                'gross_margin': round(gross_margin, 2),
                'net_margin': round(net_margin, 2)
            },
            'top_products': [dict(product) for product in top_products],
            'top_expense_categories': [dict(category) for category in top_expense_categories]
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/revenue-trends', methods=['GET'])
def get_revenue_trends():
    """Get revenue trends over time"""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    # Get period from query params (daily, weekly, monthly)
    period = request.args.get('period', 'monthly')
    months = int(request.args.get('months', 6))
    
    try:
        if period == 'daily':
            # Daily trends for last 30 days
            if is_postgresql():
                trends = execute_query(conn, '''
                    SELECT 
                        DATE(bill_date) as date,
                        SUM(total_amount) as revenue,
                        COUNT(*) as invoices,
                        COUNT(DISTINCT customer_id) as customers
                    FROM bills 
                    WHERE user_id = %s 
                    AND bill_date >= CURRENT_DATE - INTERVAL '30 days'
                    GROUP BY DATE(bill_date)
                    ORDER BY date
                ''', (user_id,)).fetchall()
            else:
                trends = execute_query(conn, '''
                SELECT 
                    DATE(bill_date) as date,
                    SUM(total_amount) as revenue,
                    COUNT(*) as invoices,
                    COUNT(DISTINCT customer_id) as customers
                FROM bills 
                WHERE user_id = ? 
                AND bill_date >= date('now', '-30 days')
                GROUP BY DATE(bill_date)
                ORDER BY date
            ''', (user_id,)).fetchall()
        elif period == 'weekly':
            # Weekly trends for last 12 weeks
            if is_postgresql():
                trends = execute_query(conn, '''
                    SELECT 
                        TO_CHAR(bill_date, 'IYYY-IW') as week,
                        SUM(total_amount) as revenue,
                        COUNT(*) as invoices,
                        COUNT(DISTINCT customer_id) as customers
                    FROM bills 
                    WHERE user_id = %s 
                    AND bill_date >= CURRENT_DATE - INTERVAL '84 days'
                    GROUP BY TO_CHAR(bill_date, 'IYYY-IW')
                    ORDER BY week
                ''', (user_id,)).fetchall()
            else:
                trends = execute_query(conn, '''
                SELECT 
                    strftime('%Y-W%W', bill_date) as week,
                    SUM(total_amount) as revenue,
                    COUNT(*) as invoices,
                    COUNT(DISTINCT customer_id) as customers
                FROM bills 
                WHERE user_id = ? 
                AND bill_date >= date('now', '-84 days')
                GROUP BY strftime('%Y-W%W', bill_date)
                ORDER BY week
            ''', (user_id,)).fetchall()
        else:  # monthly
            # Monthly trends for specified months
            if is_postgresql():
                trends = execute_query(conn, '''
                    SELECT 
                        TO_CHAR(bill_date, 'YYYY-MM') as month,
                        SUM(total_amount) as revenue,
                        COUNT(*) as invoices,
                        COUNT(DISTINCT customer_id) as customers
                    FROM bills 
                    WHERE user_id = %s 
                    AND bill_date >= CURRENT_DATE - INTERVAL '%s months'
                    GROUP BY TO_CHAR(bill_date, 'YYYY-MM')
                    ORDER BY month
                ''', (user_id, months)).fetchall()
            else:
                trends = execute_query(conn, '''
                SELECT 
                    strftime('%Y-%m', bill_date) as month,
                    SUM(total_amount) as revenue,
                    COUNT(*) as invoices,
                    COUNT(DISTINCT customer_id) as customers
                FROM bills 
                WHERE user_id = ? 
                AND bill_date >= date('now', '-' || ? || ' months')
                GROUP BY strftime('%Y-%m', bill_date)
                ORDER BY month
            ''', (user_id, months)).fetchall()
        
        conn.close()
        
        return jsonify({
            'period': period,
            'trends': [dict(trend) for trend in trends]
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/expense-trends', methods=['GET'])
def get_expense_trends():
    """Get expense trends over time"""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    # Get period from query params (daily, weekly, monthly)
    period = request.args.get('period', 'monthly')
    months = int(request.args.get('months', 6))
    
    try:
        if period == 'daily':
            # Daily trends for last 30 days
            if is_postgresql():
                trends = execute_query(conn, '''
                    SELECT 
                        DATE(expense_date) as date,
                        SUM(amount) as expenses,
                        COUNT(*) as expense_count
                    FROM expenses 
                    WHERE user_id = %s 
                    AND expense_date >= CURRENT_DATE - INTERVAL '30 days'
                    GROUP BY DATE(expense_date)
                    ORDER BY date
                ''', (user_id,)).fetchall()
            else:
                trends = execute_query(conn, '''
                SELECT 
                    DATE(expense_date) as date,
                    SUM(amount) as expenses,
                    COUNT(*) as expense_count
                FROM expenses 
                WHERE user_id = ? 
                AND expense_date >= date('now', '-30 days')
                GROUP BY DATE(expense_date)
                ORDER BY date
            ''', (user_id,)).fetchall()
        elif period == 'weekly':
            # Weekly trends for last 12 weeks
            if is_postgresql():
                trends = execute_query(conn, '''
                    SELECT 
                        TO_CHAR(expense_date, 'IYYY-IW') as week,
                        SUM(amount) as expenses,
                        COUNT(*) as expense_count
                    FROM expenses 
                    WHERE user_id = %s 
                    AND expense_date >= CURRENT_DATE - INTERVAL '84 days'
                    GROUP BY TO_CHAR(expense_date, 'IYYY-IW')
                    ORDER BY week
                ''', (user_id,)).fetchall()
            else:
                trends = execute_query(conn, '''
                SELECT 
                    strftime('%Y-W%W', expense_date) as week,
                    SUM(amount) as expenses,
                    COUNT(*) as expense_count
                FROM expenses 
                WHERE user_id = ? 
                AND expense_date >= date('now', '-84 days')
                GROUP BY strftime('%Y-W%W', expense_date)
                ORDER BY week
            ''', (user_id,)).fetchall()
        else:  # monthly
            # Monthly trends for specified months
            if is_postgresql():
                trends = execute_query(conn, '''
                    SELECT 
                        TO_CHAR(expense_date, 'YYYY-MM') as month,
                        SUM(amount) as expenses,
                        COUNT(*) as expense_count
                    FROM expenses 
                    WHERE user_id = %s 
                    AND expense_date >= CURRENT_DATE - INTERVAL '%s months'
                    GROUP BY TO_CHAR(expense_date, 'YYYY-MM')
                    ORDER BY month
                ''', (user_id, months)).fetchall()
            else:
                trends = execute_query(conn, '''
                SELECT 
                    strftime('%Y-%m', expense_date) as month,
                    SUM(amount) as expenses,
                    COUNT(*) as expense_count
                FROM expenses 
                WHERE user_id = ? 
                AND expense_date >= date('now', '-' || ? || ' months')
                GROUP BY strftime('%Y-%m', expense_date)
                ORDER BY month
            ''', (user_id, months)).fetchall()
        
        conn.close()
        
        return jsonify({
            'period': period,
            'trends': [dict(trend) for trend in trends]
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/cash-flow', methods=['GET'])
def get_cash_flow():
    """Get cash flow analysis"""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    from_date = request.args.get('from_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    to_date = request.args.get('to_date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        # Cash inflows (revenue)
        placeholder = get_placeholder()
        cash_inflows = execute_query(conn, f'''
            SELECT 
                SUM(total_amount) as total_inflow,
                SUM(advance_paid) as advance_payments,
                SUM(balance_amount) as pending_payments
            FROM bills 
            WHERE user_id = {placeholder} 
            AND DATE(bill_date) BETWEEN {placeholder} AND {placeholder}
        ''', (user_id, from_date, to_date)).fetchone()
        
        # Cash outflows (expenses)
        cash_outflows = execute_query(conn, f'''
            SELECT 
                SUM(amount) as total_outflow,
                COUNT(*) as expense_count
            FROM expenses 
            WHERE user_id = {placeholder} 
            AND DATE(expense_date) BETWEEN {placeholder} AND {placeholder}
        ''', (user_id, from_date, to_date)).fetchone()
        
        # Payment method analysis
        payment_methods = execute_query(conn, f'''
            SELECT 
                payment_method,
                COUNT(*) as count,
                SUM(total_amount) as amount
            FROM bills 
            WHERE user_id = {placeholder} 
            AND DATE(bill_date) BETWEEN {placeholder} AND {placeholder}
            GROUP BY payment_method
            ORDER BY amount DESC
        ''', (user_id, from_date, to_date)).fetchall()
        
        conn.close()
        
        total_inflow = float(cash_inflows['total_inflow'] or 0)
        total_outflow = float(cash_outflows['total_outflow'] or 0)
        net_cash_flow = total_inflow - total_outflow
        
        return jsonify({
            'period': {
                'from_date': from_date,
                'to_date': to_date
            },
            'cash_flow': {
                'total_inflow': total_inflow,
                'total_outflow': total_outflow,
                'net_cash_flow': net_cash_flow,
                'advance_payments': float(cash_inflows['advance_payments'] or 0),
                'pending_payments': float(cash_inflows['pending_payments'] or 0)
            },
            'payment_methods': [dict(method) for method in payment_methods]
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/business-metrics', methods=['GET'])
def get_business_metrics():
    """Get key business performance metrics"""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    from_date = request.args.get('from_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    to_date = request.args.get('to_date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        placeholder = get_placeholder()
        
        # Customer metrics
        if is_postgresql():
            customer_metrics = execute_query(conn, f'''
                SELECT 
                    COUNT(DISTINCT customer_id) as total_customers,
                    COUNT(DISTINCT CASE WHEN bill_date >= CURRENT_DATE - INTERVAL '7 days' THEN customer_id END) as new_customers_7d,
                    COUNT(DISTINCT CASE WHEN bill_date >= CURRENT_DATE - INTERVAL '30 days' THEN customer_id END) as new_customers_30d,
                    AVG(total_amount) as avg_order_value,
                    SUM(total_amount) / COUNT(DISTINCT customer_id) as revenue_per_customer
                FROM bills 
                WHERE user_id = {placeholder} 
                AND DATE(bill_date) BETWEEN {placeholder} AND {placeholder}
            ''', (user_id, from_date, to_date)).fetchone()
        else:
            customer_metrics = execute_query(conn, f'''
            SELECT 
                COUNT(DISTINCT customer_id) as total_customers,
                COUNT(DISTINCT CASE WHEN bill_date >= date('now', '-7 days') THEN customer_id END) as new_customers_7d,
                COUNT(DISTINCT CASE WHEN bill_date >= date('now', '-30 days') THEN customer_id END) as new_customers_30d,
                AVG(total_amount) as avg_order_value,
                SUM(total_amount) / COUNT(DISTINCT customer_id) as revenue_per_customer
            FROM bills 
                WHERE user_id = {placeholder} 
                AND DATE(bill_date) BETWEEN {placeholder} AND {placeholder}
        ''', (user_id, from_date, to_date)).fetchone()
        
        # Employee performance
        employee_performance = execute_query(conn, f'''
            SELECT 
                e.name as employee_name,
                COUNT(b.bill_id) as bills_handled,
                SUM(b.total_amount) as total_revenue,
                AVG(b.total_amount) as avg_bill_value
            FROM employees e
            LEFT JOIN bills b ON e.employee_id = b.master_id AND b.user_id = e.user_id
            WHERE e.user_id = {placeholder} 
            AND (b.bill_date IS NULL OR DATE(b.bill_date) BETWEEN {placeholder} AND {placeholder})
            GROUP BY e.employee_id, e.name
            ORDER BY total_revenue DESC
        ''', (user_id, from_date, to_date)).fetchall()
        
        # Product performance
        product_performance = execute_query(conn, f'''
            SELECT 
                bi.product_name,
                SUM(bi.quantity) as total_quantity,
                SUM(bi.total_amount) as total_revenue,
                AVG(bi.rate) as avg_price,
                COUNT(DISTINCT b.bill_id) as invoices_count
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.bill_id
            WHERE b.user_id = {placeholder} 
            AND DATE(b.bill_date) BETWEEN {placeholder} AND {placeholder}
            GROUP BY bi.product_name
            ORDER BY total_revenue DESC
            LIMIT 10
        ''', (user_id, from_date, to_date)).fetchall()
        
        conn.close()
        
        return jsonify({
            'period': {
                'from_date': from_date,
                'to_date': to_date
            },
            'customer_metrics': {
                'total_customers': customer_metrics['total_customers'],
                'new_customers_7d': customer_metrics['new_customers_7d'],
                'new_customers_30d': customer_metrics['new_customers_30d'],
                'avg_order_value': float(customer_metrics['avg_order_value'] or 0),
                'revenue_per_customer': float(customer_metrics['revenue_per_customer'] or 0)
            },
            'employee_performance': [dict(emp) for emp in employee_performance],
            'product_performance': [dict(prod) for prod in product_performance]
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/expense-breakdown', methods=['GET'])
def get_expense_breakdown():
    """Get detailed expense breakdown by category"""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    from_date = request.args.get('from_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    to_date = request.args.get('to_date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        placeholder = get_placeholder()
        
        # Expense breakdown by category
        category_breakdown = execute_query(conn, f'''
            SELECT 
                ec.category_name,
                ec.description,
                SUM(e.amount) as total_amount,
                COUNT(*) as expense_count,
                AVG(e.amount) as avg_amount,
                MIN(e.amount) as min_amount,
                MAX(e.amount) as max_amount
            FROM expenses e
            JOIN expense_categories ec ON e.category_id = ec.category_id
            WHERE e.user_id = {placeholder} 
            AND DATE(e.expense_date) BETWEEN {placeholder} AND {placeholder}
            GROUP BY ec.category_id, ec.category_name, ec.description
            ORDER BY total_amount DESC
        ''', (user_id, from_date, to_date)).fetchall()
        
        # Monthly expense trends by category
        if is_postgresql():
            monthly_trends = execute_query(conn, f'''
                SELECT 
                    ec.category_name,
                    TO_CHAR(e.expense_date, 'YYYY-MM') as month,
                    SUM(e.amount) as amount
                FROM expenses e
                JOIN expense_categories ec ON e.category_id = ec.category_id
                WHERE e.user_id = {placeholder} 
                AND e.expense_date >= CURRENT_DATE - INTERVAL '6 months'
                GROUP BY ec.category_id, ec.category_name, TO_CHAR(e.expense_date, 'YYYY-MM')
                ORDER BY month, amount DESC
            ''', (user_id,)).fetchall()
        else:
            monthly_trends = execute_query(conn, f'''
            SELECT 
                ec.category_name,
                strftime('%Y-%m', e.expense_date) as month,
                SUM(e.amount) as amount
            FROM expenses e
            JOIN expense_categories ec ON e.category_id = ec.category_id
                WHERE e.user_id = {placeholder} 
            AND e.expense_date >= date('now', '-6 months')
            GROUP BY ec.category_id, ec.category_name, strftime('%Y-%m', e.expense_date)
            ORDER BY month, amount DESC
        ''', (user_id,)).fetchall()
        
        conn.close()
        
        return jsonify({
            'period': {
                'from_date': from_date,
                'to_date': to_date
            },
            'category_breakdown': [dict(cat) for cat in category_breakdown],
            'monthly_trends': [dict(trend) for trend in monthly_trends]
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/top-products', methods=['GET'])
def get_top_products():
    """Get top performing products by revenue"""
    user_id = get_current_user_id()
    conn = get_db_connection()
    
    from_date = request.args.get('from_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    to_date = request.args.get('to_date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        placeholder = get_placeholder()
        
        # Top products by revenue
        top_products = execute_query(conn, f'''
            SELECT 
                bi.product_name,
                SUM(bi.quantity) as quantity_sold,
                SUM(bi.total_amount) as total_revenue,
                COUNT(DISTINCT b.bill_id) as bill_count,
                AVG(bi.rate) as avg_unit_price
            FROM bill_items bi
            JOIN bills b ON bi.bill_id = b.bill_id
            WHERE b.user_id = {placeholder} 
            AND DATE(b.bill_date) BETWEEN {placeholder} AND {placeholder}
            GROUP BY bi.product_name
            ORDER BY total_revenue DESC
            LIMIT 10
        ''', (user_id, from_date, to_date)).fetchall()
        
        conn.close()
        
        return jsonify({
            'period': {
                'from_date': from_date,
                'to_date': to_date
            },
            'top_products': [dict(product) for product in top_products]
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500



@app.route('/financial-insights')
def financial_insights():
    """Serve the financial insights page"""
    return render_template('financial_insights.html')

@app.route('/debug_mobile_nav')
def debug_mobile_nav():
    return render_template('debug_mobile_nav.html')

@app.route('/test_mobile_nav')
def test_mobile_nav():
    return send_file('templates/test_mobile_nav.html')



@app.route('/check-schema')
def check_schema():
    """Check PostgreSQL database schema and return detailed information."""
    try:
        # Check if we're using PostgreSQL
        if not is_postgresql():
            return jsonify({'error': 'This endpoint is for PostgreSQL databases only'}), 400
        
        # Get database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
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
        
        # 1. Check all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        # Handle both tuple and dict cursor results
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
        # Handle both tuple and dict cursor results
        schema_info['primary_keys'] = [
            f"{pk[0]}.{pk[1]}" if isinstance(pk, tuple) else f"{pk['table_name']}.{pk['column_name']}" 
            for pk in primary_keys
        ]
        
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

@app.route('/db-check')
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

# ============================================================================
# LOYALTY PROGRAM API ENDPOINTS
# ============================================================================

@app.route('/api/loyalty/config', methods=['GET'])
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

@app.route('/api/loyalty/config', methods=['PUT'])
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

@app.route('/api/loyalty/tiers', methods=['GET'])
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

@app.route('/api/loyalty/tiers', methods=['POST'])
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

@app.route('/api/loyalty/customers', methods=['GET'])
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

@app.route('/api/loyalty/customers/<int:customer_id>', methods=['GET'])
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
            WHERE user_id = {placeholder} AND loyalty_id = {placeholder}
            ORDER BY created_at DESC LIMIT 10
        ''', (user_id, loyalty_profile['loyalty_id']))
        
        transactions = cursor.fetchall()
        
        # Get available rewards
        cursor = execute_query(conn, f'''
            SELECT * FROM loyalty_rewards 
            WHERE user_id = {placeholder} AND is_active = TRUE
        ''', (user_id,))
        
        rewards = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'loyalty_profile': dict(loyalty_profile),
            'transactions': [dict(txn) for txn in transactions],
            'rewards': [dict(reward) for reward in rewards]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/loyalty/customers/<int:customer_id>/enroll', methods=['POST'])
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

@app.route('/api/loyalty/transactions', methods=['GET'])
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

@app.route('/api/loyalty/rewards', methods=['GET'])
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

@app.route('/api/loyalty/rewards', methods=['POST'])
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

@app.route('/api/loyalty/offers', methods=['GET'])
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

@app.route('/api/loyalty/analytics', methods=['GET'])
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

# AI API Endpoints
@app.route('/api/ai/customer-segmentation')
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
                c.customer_name,
                c.customer_mobile,
                c.customer_type,
                c.customer_city,
                c.customer_area,
                COUNT(b.bill_id) as total_orders,
                COALESCE(SUM(b.total_amount), 0) as total_spent,
                COALESCE(AVG(b.total_amount), 0) as avg_order_value,
                MAX(b.bill_date) as last_order_date,
                EXTRACT(DAYS FROM NOW() - MAX(b.bill_date)) as days_since_last_order,
                COUNT(DISTINCT b.bill_date::date) as unique_visit_days,
                MIN(b.bill_date) as first_order_date,
                EXTRACT(DAYS FROM MAX(b.bill_date) - MIN(b.bill_date)) as customer_lifetime_days
            FROM customers c
            LEFT JOIN bills b ON c.customer_mobile = b.bill_mobile
            WHERE c.user_id = {placeholder}
            GROUP BY c.customer_id, c.customer_name, c.customer_mobile, c.customer_type, c.customer_city, c.customer_area
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
            
            # Calculate customer value score (RFM analysis)
            recency_score = max(0, 100 - customer_dict['days_since_last_order'] or 0)
            frequency_score = min(100, (customer_dict['total_orders'] or 0) * 10)
            monetary_score = min(100, (customer_dict['total_spent'] or 0) / 10)
            
            customer_value_score = (recency_score * 0.2 + frequency_score * 0.4 + monetary_score * 0.4)
            
            # Determine segment based on value score and behavior
            if customer_value_score >= 80 and customer_dict['total_orders'] >= 10:
                segment = 'Loyal VIPs'
            elif customer_value_score >= 60 and customer_dict['total_orders'] >= 5:
                segment = 'Regular Customers'
            elif customer_dict['days_since_last_order'] > 90:
                segment = 'At-Risk Customers'
            elif customer_dict['customer_lifetime_days'] < 30:
                segment = 'New Customers'
            else:
                segment = 'Occasional Buyers'
            
            customer_dict['segment'] = segment
            customer_dict['segment_label'] = segment
            customer_dict['customer_value_score'] = round(customer_value_score, 2)
            
            segmented_customers.append(customer_dict)
        
        # Group by segments for summary
        segments_summary = {}
        for customer in segmented_customers:
            segment = customer['segment_label']
            if segment not in segments_summary:
                segments_summary[segment] = {
                    'label': segment,
                    'count': 0,
                    'total_spent': 0,
                    'avg_order_value': 0
                }
            
            segments_summary[segment]['count'] += 1
            segments_summary[segment]['total_spent'] += customer['total_spent']
            segments_summary[segment]['avg_order_value'] += customer['avg_order_value']
        
        # Calculate averages
        for segment in segments_summary.values():
            if segment['count'] > 0:
                segment['avg_order_value'] = round(segment['avg_order_value'] / segment['count'], 2)
        
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

@app.route('/api/ai/export-segmentation', methods=['POST'])
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

@app.route('/ai-dashboard')
def ai_dashboard():
    """AI Dashboard page."""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return redirect(url_for('login'))
        
        # Get user plan info for the template
        user_plan_info = get_user_plan_info(user_id)
        
        return render_template('ai-dashboard.html', user_plan_info=user_plan_info)
        
    except Exception as e:
        return redirect(url_for('login'))

if __name__ == '__main__':
    setup_ocr()  # Initialize OCR
    init_db()  # Initialize database and create tables
    app.run(debug=False, host='0.0.0.0', port=5000) 