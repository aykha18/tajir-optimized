#!/usr/bin/env python3
"""
Extract Complete Database Schema
Extract all tables, columns, and data from local database
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

def extract_schema():
    """Extract complete database schema"""
    
    try:
        # Local PostgreSQL connection
        connection = psycopg2.connect(
            host='localhost',
            port='5432',
            database='tajir_pos',
            user='postgres',
            password='aykha123'
        )
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        print("🔍 Extracting Complete Database Schema...")
        print("=" * 50)
        
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        
        schema_file = "complete_schema.sql"
        with open(schema_file, 'w') as f:
            f.write("-- Complete Database Schema\n")
            f.write("-- Extracted from local PostgreSQL database\n\n")
            
            for table in tables:
                table_name = table['table_name']
                print(f"📋 Extracting schema for table: {table_name}")
                
                # Get table structure
                cursor.execute(f"""
                    SELECT column_name, data_type, is_nullable, column_default, 
                           character_maximum_length, numeric_precision, numeric_scale
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}' 
                    ORDER BY ordinal_position
                """)
                
                columns = cursor.fetchall()
                
                # Get primary key
                cursor.execute(f"""
                    SELECT kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu 
                        ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.constraint_type = 'PRIMARY KEY' 
                    AND tc.table_name = '{table_name}'
                """)
                
                primary_keys = cursor.fetchall()
                pk_columns = [pk['column_name'] for pk in primary_keys]
                
                # Get foreign keys
                cursor.execute(f"""
                    SELECT 
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                    WHERE constraint_type = 'FOREIGN KEY' 
                    AND tc.table_name = '{table_name}'
                """)
                
                foreign_keys = cursor.fetchall()
                
                # Write CREATE TABLE statement
                f.write(f"-- Table: {table_name}\n")
                f.write(f"CREATE TABLE IF NOT EXISTS {table_name} (\n")
                
                column_definitions = []
                for col in columns:
                    col_name = col['column_name']
                    data_type = col['data_type']
                    
                    # Handle specific data types
                    if data_type == 'character varying':
                        if col['character_maximum_length']:
                            data_type = f"VARCHAR({col['character_maximum_length']})"
                        else:
                            data_type = "VARCHAR"
                    elif data_type == 'numeric':
                        if col['numeric_precision'] and col['numeric_scale']:
                            data_type = f"DECIMAL({col['numeric_precision']},{col['numeric_scale']})"
                        elif col['numeric_precision']:
                            data_type = f"DECIMAL({col['numeric_precision']})"
                        else:
                            data_type = "DECIMAL"
                    elif data_type == 'integer':
                        data_type = "INTEGER"
                    elif data_type == 'boolean':
                        data_type = "BOOLEAN"
                    elif data_type == 'timestamp without time zone':
                        data_type = "TIMESTAMP"
                    elif data_type == 'date':
                        data_type = "DATE"
                    elif data_type == 'text':
                        data_type = "TEXT"
                    
                    # Build column definition
                    col_def = f"    {col_name} {data_type}"
                    
                    # Add NOT NULL if applicable
                    if col['is_nullable'] == 'NO':
                        col_def += " NOT NULL"
                    
                    # Add default value if exists
                    if col['column_default']:
                        default = col['column_default']
                        # Handle boolean defaults
                        if default == 'true':
                            default = 'TRUE'
                        elif default == 'false':
                            default = 'FALSE'
                        col_def += f" DEFAULT {default}"
                    
                    column_definitions.append(col_def)
                
                # Add primary key
                if pk_columns:
                    column_definitions.append(f"    PRIMARY KEY ({', '.join(pk_columns)})")
                
                f.write(',\n'.join(column_definitions))
                f.write("\n);\n\n")
                
                # Add foreign key constraints
                for fk in foreign_keys:
                    f.write(f"ALTER TABLE {table_name} ADD CONSTRAINT fk_{table_name}_{fk['column_name']} ")
                    f.write(f"FOREIGN KEY ({fk['column_name']}) REFERENCES {fk['foreign_table_name']}({fk['foreign_column_name']});\n")
                
                if foreign_keys:
                    f.write("\n")
                
                # Get sequences
                cursor.execute(f"""
                    SELECT sequence_name 
                    FROM information_schema.sequences 
                    WHERE sequence_name LIKE '{table_name}_%'
                """)
                
                sequences = cursor.fetchall()
                for seq in sequences:
                    f.write(f"CREATE SEQUENCE IF NOT EXISTS {seq['sequence_name']};\n")
                
                if sequences:
                    f.write("\n")
        
        print(f"✅ Schema extracted to: {schema_file}")
        
        # Also extract sample data for important tables
        print("\n📊 Extracting sample data...")
        
        data_file = "sample_data.sql"
        with open(data_file, 'w') as f:
            f.write("-- Sample Data\n")
            f.write("-- Important data to preserve\n\n")
            
            # Extract users data
            cursor.execute("SELECT * FROM users LIMIT 10")
            users = cursor.fetchall()
            if users:
                f.write("-- Users data\n")
                for user in users:
                    f.write(f"INSERT INTO users (user_id, email, mobile, shop_code, password_hash, shop_name, shop_type, contact_number, email_address, is_active, created_at, updated_at) VALUES ")
                    f.write(f"({user['user_id']}, '{user['email']}', '{user['mobile']}', '{user['shop_code']}', '{user['password_hash']}', '{user['shop_name']}', '{user['shop_type']}', '{user['contact_number']}', '{user['email_address']}', {user['is_active']}, '{user['created_at']}', '{user['updated_at']}');\n")
                f.write("\n")
            
            # Extract shop_settings data
            cursor.execute("SELECT * FROM shop_settings LIMIT 5")
            settings = cursor.fetchall()
            if settings:
                f.write("-- Shop settings data\n")
                for setting in settings:
                    f.write(f"INSERT INTO shop_settings (setting_id, user_id, shop_name, address, trn, logo_url, shop_mobile, working_hours, invoice_static_info, use_dynamic_invoice_template, payment_mode, enable_trial_date, enable_delivery_date, enable_advance_payment, enable_customer_notes, enable_employee_assignment, default_delivery_days, default_trial_days, default_employee_id, city, area, created_at, updated_at) VALUES ")
                    f.write(f"({setting['setting_id']}, {setting['user_id']}, '{setting['shop_name']}', '{setting['address']}', '{setting['trn']}', '{setting['logo_url']}', '{setting['shop_mobile']}', '{setting['working_hours']}', '{setting['invoice_static_info']}', {setting['use_dynamic_invoice_template']}, '{setting['payment_mode']}', {setting['enable_trial_date']}, {setting['enable_delivery_date']}, {setting['enable_advance_payment']}, {setting['enable_customer_notes']}, {setting['enable_employee_assignment']}, {setting['default_delivery_days']}, {setting['default_trial_days']}, {setting['default_employee_id']}, '{setting['city']}', '{setting['area']}', '{setting['created_at']}', '{setting['updated_at']}');\n")
                f.write("\n")
        
        print(f"✅ Sample data extracted to: {data_file}")
        connection.close()
        
    except Exception as e:
        print(f"❌ Error extracting schema: {e}")

if __name__ == "__main__":
    extract_schema()

