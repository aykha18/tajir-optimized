#!/usr/bin/env python3
"""
PostgreSQL Migration Setup for Tajir POS
This script handles the complete migration from SQLite to PostgreSQL
"""

import os
import sys
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class PostgreSQLMigration:
    def __init__(self):
        self.sqlite_db = 'pos_tailor.db'
        self.pg_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'tajir_pos'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'password')
        }
        
    def test_postgresql_connection(self):
        """Test PostgreSQL connection"""
        try:
            conn = psycopg2.connect(**self.pg_config)
            conn.close()
            logger.info("✅ PostgreSQL connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            return False
    
    def create_database_schema(self):
        """Create PostgreSQL database schema"""
        try:
            conn = psycopg2.connect(**self.pg_config)
            cursor = conn.cursor()
            
            # Create tables in order of dependencies
            tables_sql = [
                # Users table
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    mobile VARCHAR(20),
                    shop_code VARCHAR(50),
                    password_hash VARCHAR(255) NOT NULL,
                    shop_name VARCHAR(255),
                    shop_type VARCHAR(100),
                    contact_number VARCHAR(20),
                    email_address VARCHAR(255),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """,
                
                # User plans table
                """
                CREATE TABLE IF NOT EXISTS user_plans (
                    plan_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                    plan_type VARCHAR(50) NOT NULL,
                    plan_start_date DATE,
                    plan_end_date DATE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """,
                
                # Shop settings table
                """
                CREATE TABLE IF NOT EXISTS shop_settings (
                    setting_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                    shop_name VARCHAR(255),
                    address TEXT,
                    trn VARCHAR(50),
                    logo_url TEXT,
                    shop_mobile VARCHAR(20),
                    working_hours TEXT,
                    invoice_static_info TEXT,
                    use_dynamic_invoice_template BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    city VARCHAR(100),
                    area VARCHAR(100),
                    payment_mode VARCHAR(50),
                    enable_trial_date BOOLEAN DEFAULT FALSE,
                    enable_delivery_date BOOLEAN DEFAULT FALSE,
                    enable_advance_payment BOOLEAN DEFAULT FALSE,
                    enable_customer_notes BOOLEAN DEFAULT FALSE,
                    enable_employee_assignment BOOLEAN DEFAULT FALSE,
                    default_delivery_days INTEGER DEFAULT 7,
                    default_trial_days INTEGER DEFAULT 3,
                    default_employee_id INTEGER
                );
                """,
                
                # OTP codes table
                """
                CREATE TABLE IF NOT EXISTS otp_codes (
                    id SERIAL PRIMARY KEY,
                    mobile VARCHAR(20) NOT NULL,
                    otp_code VARCHAR(10) NOT NULL,
                    is_used BOOLEAN DEFAULT FALSE,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """,
                
                # Product types table
                """
                CREATE TABLE IF NOT EXISTS product_types (
                    type_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                    type_name VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                );
                """,
                
                # Products table
                """
                CREATE TABLE IF NOT EXISTS products (
                    product_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                    type_id INTEGER REFERENCES product_types(type_id) ON DELETE SET NULL,
                    product_name VARCHAR(255) NOT NULL,
                    rate DECIMAL(10,2) NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    barcode VARCHAR(100)
                );
                """,
                
                # Cities table
                """
                CREATE TABLE IF NOT EXISTS cities (
                    city_id SERIAL PRIMARY KEY,
                    city_name VARCHAR(100) NOT NULL
                );
                """,
                
                # City areas table
                """
                CREATE TABLE IF NOT EXISTS city_area (
                    area_id SERIAL PRIMARY KEY,
                    area_name VARCHAR(100) NOT NULL,
                    city_id INTEGER REFERENCES cities(city_id) ON DELETE CASCADE
                );
                """,
                
                # Customers table
                """
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                    name VARCHAR(255) NOT NULL,
                    phone VARCHAR(20),
                    city VARCHAR(100),
                    area VARCHAR(100),
                    email VARCHAR(255),
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    trn VARCHAR(50),
                    customer_type VARCHAR(50),
                    business_name VARCHAR(255),
                    business_address TEXT
                );
                """,
                
                # VAT rates table
                """
                CREATE TABLE IF NOT EXISTS vat_rates (
                    vat_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                    rate_percentage DECIMAL(5,2) NOT NULL,
                    effective_from DATE,
                    effective_to DATE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """,
                
                # Employees table
                """
                CREATE TABLE IF NOT EXISTS employees (
                    employee_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                    name VARCHAR(255) NOT NULL,
                    phone VARCHAR(20),
                    email VARCHAR(255),
                    position VARCHAR(100),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    address TEXT
                );
                """,
                
                # Bills table
                """
                CREATE TABLE IF NOT EXISTS bills (
                    bill_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                    bill_number VARCHAR(50) NOT NULL,
                    customer_id INTEGER REFERENCES customers(customer_id) ON DELETE SET NULL,
                    customer_name VARCHAR(255),
                    customer_phone VARCHAR(20),
                    customer_city VARCHAR(100),
                    customer_area VARCHAR(100),
                    bill_date DATE NOT NULL,
                    delivery_date DATE,
                    payment_method VARCHAR(50),
                    subtotal DECIMAL(10,2) DEFAULT 0,
                    vat_amount DECIMAL(10,2) DEFAULT 0,
                    total_amount DECIMAL(10,2) DEFAULT 0,
                    advance_paid DECIMAL(10,2) DEFAULT 0,
                    balance_amount DECIMAL(10,2) DEFAULT 0,
                    status VARCHAR(50) DEFAULT 'pending',
                    master_id INTEGER,
                    trial_date DATE,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    customer_trn VARCHAR(50),
                    customer_type VARCHAR(50),
                    business_name VARCHAR(255),
                    business_address TEXT,
                    uuid VARCHAR(100)
                );
                """,
                
                # Bill items table
                """
                CREATE TABLE IF NOT EXISTS bill_items (
                    item_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                    bill_id INTEGER REFERENCES bills(bill_id) ON DELETE CASCADE,
                    product_id INTEGER REFERENCES products(product_id) ON DELETE SET NULL,
                    product_name VARCHAR(255) NOT NULL,
                    quantity INTEGER NOT NULL,
                    rate DECIMAL(10,2) NOT NULL,
                    discount DECIMAL(10,2) DEFAULT 0,
                    advance_paid DECIMAL(10,2) DEFAULT 0,
                    total_amount DECIMAL(10,2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    vat_amount DECIMAL(10,2) DEFAULT 0
                );
                """,
                
                # Expense categories table
                """
                CREATE TABLE IF NOT EXISTS expense_categories (
                    category_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                    category_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """,
                
                # Expenses table
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    expense_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                    category_id INTEGER REFERENCES expense_categories(category_id) ON DELETE SET NULL,
                    expense_date DATE NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    description TEXT,
                    payment_method VARCHAR(50),
                    receipt_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """,
                
                # Error logs table
                """
                CREATE TABLE IF NOT EXISTS error_logs (
                    log_id SERIAL PRIMARY KEY,
                    timestamp TEXT,
                    level VARCHAR(20),
                    operation VARCHAR(100),
                    table_name VARCHAR(100),
                    error_message TEXT,
                    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
                    data_snapshot TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """,
                
                # User actions table
                """
                CREATE TABLE IF NOT EXISTS user_actions (
                    action_id SERIAL PRIMARY KEY,
                    timestamp TEXT,
                    action VARCHAR(100),
                    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """,
                
                # Audit log table
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
                    action VARCHAR(100),
                    resource VARCHAR(100),
                    details TEXT,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            ]
            
            for i, sql in enumerate(tables_sql, 1):
                logger.info(f"Creating table {i}/{len(tables_sql)}...")
                cursor.execute(sql)
            
            conn.commit()
            logger.info("✅ PostgreSQL schema created successfully")
            
            # Create indexes for better performance
            indexes_sql = [
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
                "CREATE INDEX IF NOT EXISTS idx_users_shop_code ON users(shop_code);",
                "CREATE INDEX IF NOT EXISTS idx_bills_user_id ON bills(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_bills_bill_date ON bills(bill_date);",
                "CREATE INDEX IF NOT EXISTS idx_bill_items_bill_id ON bill_items(bill_id);",
                "CREATE INDEX IF NOT EXISTS idx_customers_user_id ON customers(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_products_user_id ON products(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(expense_date);",
                "CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);"
            ]
            
            for index_sql in indexes_sql:
                cursor.execute(index_sql)
            
            conn.commit()
            logger.info("✅ PostgreSQL indexes created successfully")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error creating PostgreSQL schema: {e}")
            raise
    
    def migrate_data(self):
        """Migrate data from SQLite to PostgreSQL"""
        try:
            sqlite_conn = sqlite3.connect(self.sqlite_db)
            sqlite_conn.row_factory = sqlite3.Row
            
            pg_conn = psycopg2.connect(**self.pg_config)
            pg_cursor = pg_conn.cursor()
            
            # Migration order (respecting foreign key constraints)
            migration_order = [
                'users',
                'user_plans', 
                'shop_settings',
                'otp_codes',
                'product_types',
                'products',
                'cities',
                'city_area',
                'customers',
                'vat_rates',
                'employees',
                'bills',
                'bill_items',
                'expense_categories',
                'expenses',
                'error_logs',
                'user_actions',
                'audit_log'
            ]
            
            for table_name in migration_order:
                logger.info(f"Migrating table: {table_name}")
                
                # Get data from SQLite
                sqlite_cursor = sqlite_conn.cursor()
                sqlite_cursor.execute(f"SELECT * FROM {table_name}")
                rows = sqlite_cursor.fetchall()
                
                if not rows:
                    logger.info(f"  No data to migrate for {table_name}")
                    continue
                
                # Get column names
                columns = [description[0] for description in sqlite_cursor.description]
                
                # Prepare INSERT statement
                placeholders = ', '.join(['%s'] * len(columns))
                columns_str = ', '.join(columns)
                insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                
                # Migrate data
                for row in rows:
                    values = [row[col] for col in columns]
                    pg_cursor.execute(insert_sql, values)
                
                logger.info(f"  ✅ Migrated {len(rows)} rows from {table_name}")
                
                sqlite_cursor.close()
            
            pg_conn.commit()
            logger.info("✅ Data migration completed successfully")
            
            sqlite_conn.close()
            pg_cursor.close()
            pg_conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error during data migration: {e}")
            raise
    
    def verify_migration(self):
        """Verify the migration by comparing record counts"""
        try:
            sqlite_conn = sqlite3.connect(self.sqlite_db)
            pg_conn = psycopg2.connect(**self.pg_config)
            
            tables = [
                'users', 'user_plans', 'shop_settings', 'otp_codes', 
                'product_types', 'products', 'cities', 'city_area',
                'customers', 'vat_rates', 'employees', 'bills', 
                'bill_items', 'expense_categories', 'expenses',
                'error_logs', 'user_actions', 'audit_log'
            ]
            
            logger.info("Verifying migration...")
            logger.info("Table | SQLite Count | PostgreSQL Count | Status")
            logger.info("-" * 60)
            
            for table in tables:
                # SQLite count
                sqlite_cursor = sqlite_conn.cursor()
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                sqlite_count = sqlite_cursor.fetchone()[0]
                
                # PostgreSQL count
                pg_cursor = pg_conn.cursor()
                pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                pg_count = pg_cursor.fetchone()[0]
                
                status = "✅" if sqlite_count == pg_count else "❌"
                logger.info(f"{table:20} | {sqlite_count:12} | {pg_count:15} | {status}")
                
                sqlite_cursor.close()
                pg_cursor.close()
            
            sqlite_conn.close()
            pg_conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error during verification: {e}")
            raise
    
    def run_migration(self):
        """Run the complete migration process"""
        logger.info("🚀 Starting PostgreSQL Migration for Tajir POS")
        logger.info("=" * 60)
        
        # Step 1: Test PostgreSQL connection
        logger.info("Step 1: Testing PostgreSQL connection...")
        if not self.test_postgresql_connection():
            logger.error("Migration failed: Cannot connect to PostgreSQL")
            return False
        
        # Step 2: Create database schema
        logger.info("Step 2: Creating PostgreSQL schema...")
        self.create_database_schema()
        
        # Step 3: Migrate data
        logger.info("Step 3: Migrating data from SQLite to PostgreSQL...")
        self.migrate_data()
        
        # Step 4: Verify migration
        logger.info("Step 4: Verifying migration...")
        self.verify_migration()
        
        logger.info("=" * 60)
        logger.info("🎉 PostgreSQL Migration completed successfully!")
        logger.info("Next steps:")
        logger.info("1. Update app.py to use PostgreSQL connection")
        logger.info("2. Test the application with PostgreSQL")
        logger.info("3. Backup the old SQLite database")
        
        return True

if __name__ == "__main__":
    migration = PostgreSQLMigration()
    migration.run_migration()
