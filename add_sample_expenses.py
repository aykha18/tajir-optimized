#!/usr/bin/env python3
"""
Add Sample Expense Categories and Expenses
This script adds sample data to test the expense management functionality.
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

def get_db_connection():
    """Get database connection."""
    database_path = os.getenv('DATABASE_PATH', 'pos_tailor.db')
    return sqlite3.connect(database_path)

def add_sample_expense_categories():
    """Add sample expense categories."""
    print("Adding sample expense categories...")
    
    conn = get_db_connection()
    
    # Sample categories
    categories = [
        ('Office Supplies', 'Paper, pens, printer ink, etc.'),
        ('Utilities', 'Electricity, water, internet, phone'),
        ('Rent', 'Office or shop rent'),
        ('Transportation', 'Fuel, maintenance, public transport'),
        ('Marketing', 'Advertising, promotions, social media'),
        ('Equipment', 'Computers, furniture, tools'),
        ('Insurance', 'Business insurance, liability coverage'),
        ('Professional Services', 'Legal, accounting, consulting'),
        ('Travel', 'Business trips, accommodation'),
        ('Miscellaneous', 'Other business expenses')
    ]
    
    try:
        for category_name, description in categories:
            # Check if category already exists
            existing = conn.execute(
                'SELECT category_id FROM expense_categories WHERE category_name = ? AND user_id = 2',
                (category_name,)
            ).fetchone()
            
            if not existing:
                conn.execute('''
                    INSERT INTO expense_categories (user_id, category_name, description, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (2, category_name, description, datetime.now()))
                print(f"✅ Added category: {category_name}")
            else:
                print(f"⚠️ Category already exists: {category_name}")
        
        conn.commit()
        print("✅ Sample expense categories added successfully!")
        
    except Exception as e:
        print(f"❌ Error adding expense categories: {e}")
        conn.rollback()
    finally:
        conn.close()

def add_sample_expenses():
    """Add sample expenses."""
    print("Adding sample expenses...")
    
    conn = get_db_connection()
    
    try:
        # Get category IDs
        categories = conn.execute(
            'SELECT category_id, category_name FROM expense_categories WHERE user_id = 2'
        ).fetchall()
        
        if not categories:
            print("❌ No expense categories found. Please add categories first.")
            return
        
        # Sample expenses data
        sample_expenses = [
            ('Office Supplies', 150.00, 'Printer ink and paper supplies'),
            ('Utilities', 300.00, 'Monthly electricity and internet bill'),
            ('Rent', 2000.00, 'Monthly office rent'),
            ('Transportation', 200.00, 'Fuel for business vehicle'),
            ('Marketing', 500.00, 'Social media advertising campaign'),
            ('Equipment', 800.00, 'New computer monitor'),
            ('Insurance', 400.00, 'Business liability insurance'),
            ('Professional Services', 300.00, 'Accounting services'),
            ('Travel', 600.00, 'Business trip to client meeting'),
            ('Miscellaneous', 100.00, 'Office cleaning supplies')
        ]
        
        # Add expenses for the last 30 days
        for i, (category_name, amount, description) in enumerate(sample_expenses):
            # Find category ID
            category_id = None
            for cat_id, cat_name in categories:
                if cat_name == category_name:
                    category_id = cat_id
                    break
            
            if category_id:
                # Random date within last 30 days
                days_ago = random.randint(0, 30)
                expense_date = datetime.now() - timedelta(days=days_ago)
                
                # Check if expense already exists
                existing = conn.execute(
                    'SELECT expense_id FROM expenses WHERE description = ? AND user_id = 2',
                    (description,)
                ).fetchone()
                
                if not existing:
                    conn.execute('''
                        INSERT INTO expenses (user_id, category_id, expense_date, amount, description, payment_method, receipt_url, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (2, category_id, expense_date.strftime('%Y-%m-%d'), amount, description, 'Cash', None, datetime.now()))
                    print(f"✅ Added expense: {description} - AED {amount}")
                else:
                    print(f"⚠️ Expense already exists: {description}")
        
        conn.commit()
        print("✅ Sample expenses added successfully!")
        
    except Exception as e:
        print(f"❌ Error adding sample expenses: {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    """Main function to add sample data."""
    print("Starting sample expense data addition...")
    
    try:
        add_sample_expense_categories()
        add_sample_expenses()
        
        print("\n✅ Sample expense data addition completed!")
        print("\nYou can now test the expense management functionality:")
        print("1. Go to https://tajir.up.railway.app/expenses")
        print("2. You should see expense categories and sample expenses")
        print("3. Try adding new expenses and categories")
        
    except Exception as e:
        print(f"\n❌ Error during sample data addition: {e}")

if __name__ == "__main__":
    main()
