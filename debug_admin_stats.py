from dotenv import load_dotenv
import os
import json
import datetime

load_dotenv()

from db.connection import get_db_connection, execute_query
import sys

def debug_stats():
    try:
        conn = get_db_connection()
        print("Connected to DB")
        
        # 1. Total shops
        print("Checking Total Shops...")
        sql1 = 'SELECT COUNT(*) FROM users WHERE is_active = TRUE'
        cursor = execute_query(conn, sql1)
        result = cursor.fetchone()
        print(f"Raw result 1: {result}, Type: {type(result)}")
        total_shops = result[0] if isinstance(result, tuple) else result['count']
        print(f"Total Shops: {total_shops}")
        
        # 2. Active plans
        print("\nChecking Active Plans...")
        sql2 = '''
            SELECT COUNT(*) FROM user_plans up
            JOIN users u ON up.user_id = u.user_id
            WHERE up.is_active = TRUE AND u.is_active = TRUE
            AND (up.plan_type = 'pro' OR up.plan_end_date > CURRENT_DATE)
        '''
        cursor = execute_query(conn, sql2)
        result = cursor.fetchone()
        print(f"Raw result 2: {result}")
        active_plans = result[0] if isinstance(result, tuple) else result['count']
        print(f"Active Plans: {active_plans}")
        
        # 3. Expiring soon
        print("\nChecking Expiring Soon...")
        sql3 = '''
            SELECT COUNT(*) FROM user_plans up
            JOIN users u ON up.user_id = u.user_id
            WHERE up.is_active = TRUE AND u.is_active = TRUE
            AND up.plan_type != 'pro'
            AND up.plan_end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
        '''
        cursor = execute_query(conn, sql3)
        result = cursor.fetchone()
        print(f"Raw result 3: {result}")
        expiring_soon = result[0] if isinstance(result, tuple) else result['count']
        print(f"Expiring Soon: {expiring_soon}")
        
        # 4. Expired plans
        print("\nChecking Expired Plans...")
        sql4 = '''
            SELECT COUNT(*) FROM user_plans up
            JOIN users u ON up.user_id = u.user_id
            WHERE up.is_active = TRUE AND u.is_active = TRUE
            AND up.plan_type != 'pro'
            AND up.plan_end_date < CURRENT_DATE
        '''
        cursor = execute_query(conn, sql4)
        result = cursor.fetchone()
        print(f"Raw result 4: {result}")
        expired_plans = result[0] if isinstance(result, tuple) else result['count']
        print(f"Expired Plans: {expired_plans}")
        
        conn.close()
        print("\nSuccess")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_stats()
