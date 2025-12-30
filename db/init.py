import os
import logging
import json
from datetime import datetime
from db.connection import get_db_connection, execute_query, get_placeholder, execute_with_returning
from api.utils import log_dml_error
import bcrypt

logger = logging.getLogger(__name__)

def init_db():
    need_init = False
    # For PostgreSQL, check if tables exist
    try:
        conn = get_db_connection()
        cursor = execute_query(conn, "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'product_types'")
        result = cursor.fetchone()
        count = result['count'] if result else 0
        if count == 0:
            need_init = True
        conn.close()
    except Exception as e:
        # Table doesn't exist, need to initialize
        need_init = True
    
    if need_init:
        # Use PostgreSQL schema file
        # Path relative to project root (assuming this file is in db/)
        schema_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database_schema_postgresql.sql')
        
        try:
            with open(schema_file, 'r') as f:
                schema = f.read()
        except FileNotFoundError:
            print(f"Schema file {schema_file} not found")
            return
        
        conn = get_db_connection()
        try:
            # For PostgreSQL, execute statements one by one
            statements = schema.split(';')
            cursor = conn.cursor()
            # print(f"Executing {len(statements)} statements from schema file...")
            executed_count = 0
            for i, statement in enumerate(statements):
                statement = statement.strip()
                # print(f"Statement {i+1} (length: {len(statement)}): {statement[:50]}...")
                
                # Skip empty statements
                if not statement:
                    # print(f"Skipping statement {i+1} (empty)")
                    continue
                
                # Skip pure comment statements (lines that are only comments)
                if statement.startswith('--') and not any(keyword in statement.upper() for keyword in ['CREATE', 'INSERT', 'ALTER', 'DROP', 'SELECT', 'UPDATE', 'DELETE']):
                    # print(f"Skipping statement {i+1} (pure comment)")
                    continue
                
                # Execute the statement
                try:
                    # print(f"Executing statement {i+1}: {statement[:100]}...")
                    cursor.execute(statement)
                    executed_count += 1
                    # print(f"✅ Statement {i+1} executed successfully")
                except Exception as stmt_error:
                    # print(f"❌ Warning: Failed to execute statement {i+1}: {stmt_error}")
                    # print(f"Statement: {statement}")
                    # Continue with other statements
                    pass
            
            # print(f"Successfully executed {executed_count} statements")
            conn.commit()  # Commit the transaction
            cursor.close()
            
            # Verify tables were created
            try:
                verify_cursor = conn.cursor()
                verify_cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                tables = verify_cursor.fetchall()
                # print(f"Tables created: {[table[0] for table in tables]}")
                verify_cursor.close()
            except Exception as verify_error:
                # print(f"Error verifying tables: {verify_error}")
                pass
            
            logger.info("PostgreSQL database initialized successfully")
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
        
        try:
            conn = get_db_connection()
            placeholder = get_placeholder()
            cursor = execute_query(conn, f'SELECT user_id FROM users WHERE email = {placeholder}', ('demo@tajir.com',))
            existing = cursor.fetchone()
            if not existing:
                demo_hash = '$2b$12$6yZuSJsAamPc/ZEQbdi5hOkt5Vb7jOS3BUHJtNFGpfG6vNTwqkpGW'
                execute_with_returning(conn, 
                    f'''INSERT INTO users (email, mobile, shop_code, password_hash, shop_name, shop_type, contact_number, email_address, is_active)
                        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, TRUE)''',
                    ('demo@tajir.com', '9768584622', '4GTY5F', demo_hash, 'Ak Dry Services', 'laundry', '9768584622', 'aykha@fatoorx.com'))
            conn.close()
        except Exception as e:
            logger.error(f"Failed to ensure demo user: {e}")
    
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
        
        try:
            conn = get_db_connection()
            placeholder = get_placeholder()
            cursor = execute_query(conn, f'SELECT user_id FROM users WHERE email = {placeholder}', ('demo@tajir.com',))
            existing = cursor.fetchone()
            if not existing:
                demo_hash = '$2b$12$6yZuSJsAamPc/ZEQbdi5hOkt5Vb7jOS3BUHJtNFGpfG6vNTwqkpGW'
                execute_with_returning(conn, 
                    f'''INSERT INTO users (email, mobile, shop_code, password_hash, shop_name, shop_type, contact_number, email_address, is_active)
                        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, TRUE)''',
                    ('demo@tajir.com', '9768584622', '4GTY5F', demo_hash, 'Ak Dry Services', 'laundry', '9768584622', 'aykha@fatoorx.com'))
            conn.close()
        except Exception as e:
            logger.error(f"Failed to ensure demo user: {e}")


def cleanup_corrupted_data(conn):
    """Clean up corrupted data in the database."""
    try:
        cursor = conn.cursor()
        
        # Fix corrupted dates in expenses table
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
        
        conn.commit()
        print("✓ Corrupted data cleaned up successfully")
        
    except Exception as e:
        print(f"⚠ Warning: Failed to clean up corrupted data: {e}")
        conn.rollback()
