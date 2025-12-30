import os
import re
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    database_url = os.getenv('DATABASE_URL')
    pg_host = os.getenv('PGHOST') or os.getenv('POSTGRES_HOST')

    if database_url:
        return psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    else:
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
        return psycopg2.connect(**pg_config)


def get_db_integrity_error():
    return psycopg2.IntegrityError


def is_postgresql():
    return True


def get_placeholder():
    return '%s'


def execute_with_returning(conn, sql, params=None):
    if sql.strip().upper().startswith('INSERT'):
        table_match = re.search(r'INSERT INTO (\w+)', sql, re.IGNORECASE)
        if table_match:
            table_name = table_match.group(1)
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

            if 'RETURNING' not in sql.upper():
                sql += f' RETURNING {id_column}'

            cursor = conn.cursor()
            cursor.execute(sql, params)
            result = cursor.fetchone()
            conn.commit()
            if result:
                if isinstance(result, dict):
                    return result[id_column]
                else:
                    return result[0]
            return None
        else:
            if 'RETURNING' not in sql.upper():
                sql += ' RETURNING id'
            cursor = conn.cursor()
            cursor.execute(sql, params)
            result = cursor.fetchone()
            conn.commit()
            if result:
                if isinstance(result, dict):
                    return result['id']
                else:
                    return result[0]
            return None
    else:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return None


def execute_query(conn, sql, params=None):
    cursor = conn.cursor()
    cursor.execute(sql, params)
    return cursor


def execute_update(conn, sql, params=None):
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    return cursor.rowcount

