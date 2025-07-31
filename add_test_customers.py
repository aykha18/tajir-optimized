import sqlite3
from datetime import datetime

def add_test_customers():
    try:
        conn = sqlite3.connect('pos_tailor.db')
        
        # Add some test customers
        test_customers = [
            (1, 'Ahmed Ali', '0501234567', 'Dubai', 'Deira'),
            (1, 'Fatima Hassan', '0502345678', 'Abu Dhabi', 'Al Ain'),
            (1, 'Mohammed Khan', '0503456789', 'Sharjah', 'Al Qasimiya'),
            (1, 'Aisha Rahman', '0504567890', 'Dubai', 'Jumeirah'),
            (1, 'Omar Saleh', '0505678901', 'Abu Dhabi', 'Khalifa City'),
            (1, 'Layla Ahmed', '0506789012', 'Sharjah', 'Al Majaz'),
            (1, 'Yusuf Ibrahim', '0507890123', 'Dubai', 'Bur Dubai'),
            (1, 'Noor Al-Zahra', '0508901234', 'Abu Dhabi', 'Al Raha'),
        ]
        
        for user_id, name, phone, city, area in test_customers:
            conn.execute('''
                INSERT INTO customers (user_id, name, phone, city, area, email, address) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, name, phone, city, area, '', ''))
        
        conn.commit()
        print(f"Added {len(test_customers)} test customers")
        
        # Verify
        cursor = conn.execute('SELECT * FROM customers WHERE user_id = 1')
        customers = cursor.fetchall()
        print(f"Total customers for user_id = 1: {len(customers)}")
        
        conn.close()
        print("Test customers added successfully!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    add_test_customers()