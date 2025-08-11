import sqlite3

try:
    conn = sqlite3.connect('pos_tailor.db')
    cursor = conn.cursor()
    
    # Check if expenses table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'")
    result = cursor.fetchone()
    print('Expenses table exists:', result is not None)
    
    # Check if expense_categories table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expense_categories'")
    result = cursor.fetchone()
    print('Expense categories table exists:', result is not None)
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print('All tables:', [table[0] for table in tables])
    
    conn.close()
except Exception as e:
    print('Error:', e)
