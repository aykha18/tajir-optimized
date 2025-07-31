import sqlite3
from datetime import datetime

def check_database():
    try:
        conn = sqlite3.connect('pos_tailor.db')
        cursor = conn.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = [row[0] for row in cursor.fetchall()]
        print('Tables:', tables)
        
        # Check if user_plans table exists
        if 'user_plans' in tables:
            print('\nuser_plans table structure:')
            cursor = conn.execute('PRAGMA table_info(user_plans)')
            columns = cursor.fetchall()
            for col in columns:
                print(f'  {col[1]} ({col[2]})')
            
            # Check user_plans data
            print('\nuser_plans data:')
            cursor = conn.execute('SELECT * FROM user_plans')
            rows = cursor.fetchall()
            for row in rows:
                print(f'  {row}')
        else:
            print('\nuser_plans table does not exist!')
        
        conn.close()
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    check_database()