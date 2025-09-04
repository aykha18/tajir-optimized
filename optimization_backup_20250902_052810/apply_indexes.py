#!/usr/bin/env python3
"""
Database Index Application Script
Applies performance optimization indexes to the existing PostgreSQL database
"""

import os
import sys
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Environment variables may not load properly.")
    print("Install with: pip install python-dotenv")

# Try to import PostgreSQL adapter
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    print("❌ psycopg2 not installed. Please install it with: pip install psycopg2-binary")
    POSTGRES_AVAILABLE = False
    sys.exit(1)

def get_db_connection():
    """Get PostgreSQL database connection"""
    try:
        # Try environment variables first
        if os.getenv('DATABASE_URL'):
            return psycopg2.connect(os.getenv('DATABASE_URL'))
        elif os.getenv('POSTGRES_HOST'):
            return psycopg2.connect(
                host=os.getenv('POSTGRES_HOST'),
                port=os.getenv('POSTGRES_PORT', '5432'),
                database=os.getenv('POSTGRES_DB', 'tajir_pos'),
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD', '')
            )
        else:
            # Default local connection
            return psycopg2.connect(
                host='localhost',
                port='5432',
                database='tajir_pos',
                user='postgres',
                password=''
            )
    except psycopg2.Error as e:
        print(f"❌ Database connection failed: {e}")
        return None

def apply_indexes():
    """Apply performance optimization indexes to the PostgreSQL database"""
    if not POSTGRES_AVAILABLE:
        return False
    
    print("🔗 Connecting to PostgreSQL database...")
    print(f"Host: {os.getenv('POSTGRES_HOST', 'localhost')}")
    print(f"Database: {os.getenv('POSTGRES_DB', 'tajir_pos')}")
    print(f"User: {os.getenv('POSTGRES_USER', 'postgres')}")
    
    conn = get_db_connection()
    
    if not conn:
        print("❌ Could not connect to database!")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Test connection
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✅ Connected to PostgreSQL: {version[0].split(',')[0]}")
        
        # List of new indexes to create (PostgreSQL syntax without CONCURRENTLY)
        new_indexes = [
            # Composite indexes for multi-column queries
            ("idx_products_user_active", "CREATE INDEX IF NOT EXISTS idx_products_user_active ON products(user_id, is_active)"),
            ("idx_products_user_type_active", "CREATE INDEX IF NOT EXISTS idx_products_user_type_active ON products(user_id, type_id, is_active)"),
            ("idx_customers_user_type", "CREATE INDEX IF NOT EXISTS idx_customers_user_type ON customers(user_id, customer_type)"),
            ("idx_bills_user_status", "CREATE INDEX IF NOT EXISTS idx_bills_user_status ON bills(user_id, status)"),
            ("idx_bills_user_date_status", "CREATE INDEX IF NOT EXISTS idx_bills_user_date_status ON bills(user_id, bill_date, status)"),
            ("idx_bill_items_user_bill", "CREATE INDEX IF NOT EXISTS idx_bill_items_user_bill ON bill_items(user_id, bill_id)"),
            ("idx_bill_items_user_product", "CREATE INDEX IF NOT EXISTS idx_bill_items_user_product ON bill_items(user_id, product_id)"),
            
            # Text search indexes for customer search optimization
            ("idx_customers_name_search", "CREATE INDEX IF NOT EXISTS idx_customers_name_search ON customers(user_id, name)"),
            ("idx_customers_business_search", "CREATE INDEX IF NOT EXISTS idx_customers_business_search ON customers(user_id, business_name)"),
            ("idx_customers_phone_search", "CREATE INDEX IF NOT EXISTS idx_customers_phone_search ON customers(user_id, phone)"),
            ("idx_customers_trn_search", "CREATE INDEX IF NOT EXISTS idx_customers_trn_search ON customers(user_id, trn)"),
            
            # Date-based indexes for analytics and reporting
            ("idx_bills_created_at", "CREATE INDEX IF NOT EXISTS idx_bills_created_at ON bills(user_id, created_at)"),
            ("idx_bills_delivery_date", "CREATE INDEX IF NOT EXISTS idx_bills_delivery_date ON bills(user_id, delivery_date)"),
            ("idx_bills_trial_date", "CREATE INDEX IF NOT EXISTS idx_bills_trial_date ON bills(user_id, trial_date)"),
            ("idx_expenses_date_user", "CREATE INDEX IF NOT EXISTS idx_expenses_date_user ON expenses(user_id, expense_date)"),
            
            # Product search and filtering indexes
            ("idx_products_name_search", "CREATE INDEX IF NOT EXISTS idx_products_name_search ON products(user_id, product_name)"),
            ("idx_products_barcode", "CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(user_id, barcode)"),
            ("idx_product_types_name", "CREATE INDEX IF NOT EXISTS idx_product_types_name ON product_types(user_id, type_name)"),
            
            # Employee and customer relationship indexes
            ("idx_bills_master_id", "CREATE INDEX IF NOT EXISTS idx_bills_master_id ON bills(user_id, master_id)"),
            ("idx_customers_city_area", "CREATE INDEX IF NOT EXISTS idx_customers_city_area ON customers(user_id, city, area)"),
            
            # Indexes for aggregation queries
            ("idx_bill_items_amount", "CREATE INDEX IF NOT EXISTS idx_bill_items_amount ON bill_items(user_id, total_amount)"),
            ("idx_bills_amount", "CREATE INDEX IF NOT EXISTS idx_bills_amount ON bills(user_id, total_amount, bill_date)"),
            ("idx_expenses_amount", "CREATE INDEX IF NOT EXISTS idx_expenses_amount ON expenses(user_id, amount, expense_date)"),
            
            # Indexes for foreign key relationships (performance)
            ("idx_bills_customer_fk", "CREATE INDEX IF NOT EXISTS idx_bills_customer_fk ON bills(customer_id, user_id)"),
            ("idx_bills_employee_fk", "CREATE INDEX IF NOT EXISTS idx_bills_employee_fk ON bills(master_id, user_id)"),
            ("idx_bill_items_product_fk", "CREATE INDEX IF NOT EXISTS idx_bill_items_product_fk ON bill_items(product_id, user_id)"),
            ("idx_bill_items_bill_fk", "CREATE INDEX IF NOT EXISTS idx_bill_items_bill_fk ON bill_items(bill_id, user_id)"),
            ("idx_products_type_fk", "CREATE INDEX IF NOT EXISTS idx_products_type_fk ON products(type_id, user_id)"),
            ("idx_expenses_category_fk", "CREATE INDEX IF NOT EXISTS idx_expenses_category_fk ON expenses(category_id, user_id)"),
            
            # PostgreSQL-specific optimizations
            ("idx_products_name_gin", "CREATE INDEX IF NOT EXISTS idx_products_name_gin ON products USING gin(to_tsvector('english', product_name))"),
            ("idx_customers_name_gin", "CREATE INDEX IF NOT EXISTS idx_customers_name_gin ON customers USING gin(to_tsvector('english', name))"),
            ("idx_customers_business_gin", "CREATE INDEX IF NOT EXISTS idx_customers_business_gin ON customers USING gin(to_tsvector('english', business_name))"),
            
            # Partial indexes for active records (PostgreSQL optimization)
            ("idx_products_active_only", "CREATE INDEX IF NOT EXISTS idx_products_active_only ON products(user_id, type_id, product_name) WHERE is_active = true"),
            ("idx_bills_pending_only", "CREATE INDEX IF NOT EXISTS idx_bills_pending_only ON bills(user_id, bill_date, customer_id) WHERE status = 'Pending'")
        ]
        
        print(f"🚀 Applying {len(new_indexes)} performance indexes...")
        print("⏳ This may take a few minutes for large tables...")
        
        # Track progress
        created_count = 0
        existing_count = 0
        error_count = 0
        
        for index_name, sql in new_indexes:
            try:
                cursor.execute(sql)
                conn.commit()
                
                # Check if index was actually created
                cursor.execute("SELECT indexname FROM pg_indexes WHERE indexname = %s", (index_name,))
                if cursor.fetchone():
                    print(f"✅ {index_name}")
                    created_count += 1
                else:
                    print(f"⚠️  {index_name} (already exists)")
                    existing_count += 1
                    
            except psycopg2.Error as e:
                print(f"❌ {index_name}: {e}")
                error_count += 1
                conn.rollback()
        
        # Show summary
        print("\n" + "="*50)
        print("📊 INDEX APPLICATION SUMMARY")
        print("="*50)
        print(f"✅ New indexes created: {created_count}")
        print(f"⚠️  Existing indexes: {existing_count}")
        print(f"❌ Errors: {error_count}")
        print(f"⏰ Applied at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show current index count
        cursor.execute("SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public'")
        total_indexes = cursor.fetchone()[0]
        print(f"📈 Total indexes in database: {total_indexes}")
        
        # Show table sizes for reference
        print("\n📊 Table Sizes:")
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
            FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        """)
        
        tables = cursor.fetchall()
        for table in tables:
            print(f"   {table[1]}: {table[2]}")
        
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def show_existing_indexes():
    """Show existing indexes in the PostgreSQL database"""
    if not POSTGRES_AVAILABLE:
        return
    
    conn = get_db_connection()
    
    if not conn:
        print("❌ Could not connect to database!")
        return
    
    try:
        cursor = conn.cursor()
        
        print("📋 Existing indexes in PostgreSQL database:")
        print("-" * 50)
        
        cursor.execute("""
            SELECT 
                indexname,
                tablename,
                indexdef
            FROM pg_indexes 
            WHERE schemaname = 'public' 
            ORDER BY indexname
        """)
        
        indexes = cursor.fetchall()
        
        if not indexes:
            print("No indexes found")
        else:
            for name, table, definition in indexes:
                print(f"🔍 {name}")
                print(f"   └─ Table: {table}")
                if definition:
                    # Extract key parts of the definition
                    if 'ON' in definition:
                        parts = definition.split('ON')
                        if len(parts) > 1:
                            table_part = parts[1].strip()
                            print(f"   └─ {table_part}")
                print()
        
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error reading indexes: {e}")

def analyze_tables():
    """Run ANALYZE on tables to update statistics"""
    if not POSTGRES_AVAILABLE:
        return
    
    conn = get_db_connection()
    
    if not conn:
        print("❌ Could not connect to database!")
        return
    
    try:
        cursor = conn.cursor()
        
        print("📊 Running ANALYZE on tables to update statistics...")
        
        # Get all tables
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        
        tables = cursor.fetchall()
        
        for table in tables:
            try:
                cursor.execute(f"ANALYZE {table[0]}")
                print(f"✅ Analyzed {table[0]}")
            except psycopg2.Error as e:
                print(f"❌ Failed to analyze {table[0]}: {e}")
        
        conn.commit()
        conn.close()
        
        print("🎉 Table analysis completed!")
        
    except psycopg2.Error as e:
        print(f"❌ Error analyzing tables: {e}")

if __name__ == "__main__":
    print("🚀 TAJIR POS - PostgreSQL Database Index Optimizer")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--show":
            show_existing_indexes()
        elif sys.argv[1] == "--analyze":
            analyze_tables()
        else:
            print("Usage: python apply_indexes.py [--show|--analyze]")
            sys.exit(1)
    else:
        success = apply_indexes()
        if success:
            print("\n🎉 Index optimization completed successfully!")
            print("💡 Your PostgreSQL database queries should now be significantly faster!")
            print("\n💡 Consider running: python apply_indexes.py --analyze")
            print("   to update table statistics for optimal query planning")
        else:
            print("\n💥 Index optimization failed!")
            sys.exit(1)
