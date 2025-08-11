import sqlite3
import os

def add_expense_tables():
    """Add expense tables to existing database"""
    try:
        conn = sqlite3.connect('pos_tailor.db')
        cursor = conn.cursor()
        
        # Check if tables already exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'")
        if cursor.fetchone():
            print("Expense tables already exist!")
            return
        
        print("Adding expense tables to database...")
        
        # Create expense_categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expense_categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category_name TEXT NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, category_name)
            )
        ''')
        
        # Create expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                expense_date DATE NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                description TEXT,
                payment_method TEXT DEFAULT 'Cash',
                receipt_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (category_id) REFERENCES expense_categories(category_id)
            )
        ''')
        
        # Create indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_expense_categories_user_id 
            ON expense_categories(user_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_expenses_user_id 
            ON expenses(user_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_expenses_category_id 
            ON expenses(category_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_expenses_date 
            ON expenses(expense_date)
        ''')
        
        # Insert default expense categories for user_id = 1
        default_categories = [
            ('Rent', 'Monthly rent payments'),
            ('Utilities', 'Electricity, water, internet bills'),
            ('Supplies', 'Office and business supplies'),
            ('Marketing', 'Advertising and promotional expenses'),
            ('Transportation', 'Fuel, maintenance, and travel costs'),
            ('Insurance', 'Business insurance premiums'),
            ('Maintenance', 'Equipment and facility maintenance'),
            ('Other', 'Miscellaneous expenses')
        ]
        
        for category_name, description in default_categories:
            cursor.execute('''
                INSERT OR IGNORE INTO expense_categories (user_id, category_name, description)
                VALUES (?, ?, ?)
            ''', (1, category_name, description))
        
        conn.commit()
        print("✅ Expense tables created successfully!")
        print("✅ Default categories added for user_id = 1")
        
    except Exception as e:
        print(f"❌ Error creating expense tables: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_expense_tables()
