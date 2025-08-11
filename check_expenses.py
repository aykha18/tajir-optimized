import sqlite3

def check_expense_data():
    """Check expense data in the database"""
    try:
        conn = sqlite3.connect('pos_tailor.db')
        cursor = conn.cursor()
        
        print("=== EXPENSE DATA CHECK ===")
        
        # Check expense categories
        cursor.execute("SELECT COUNT(*) FROM expense_categories WHERE user_id = 1")
        category_count = cursor.fetchone()[0]
        print(f"Expense categories for user_id=1: {category_count}")
        
        if category_count > 0:
            cursor.execute("SELECT category_name FROM expense_categories WHERE user_id = 1")
            categories = cursor.fetchall()
            print("Categories:", [cat[0] for cat in categories])
        
        # Check expenses
        cursor.execute("SELECT COUNT(*) FROM expenses WHERE user_id = 1")
        expense_count = cursor.fetchone()[0]
        print(f"Total expenses for user_id=1: {expense_count}")
        
        if expense_count > 0:
            cursor.execute("""
                SELECT e.expense_id, e.amount, e.expense_date, e.description, 
                       ec.category_name 
                FROM expenses e 
                JOIN expense_categories ec ON e.category_id = ec.category_id 
                WHERE e.user_id = 1 
                ORDER BY e.expense_date DESC 
                LIMIT 5
            """)
            expenses = cursor.fetchall()
            print("\nRecent expenses:")
            for exp in expenses:
                print(f"  ID: {exp[0]}, Amount: AED {exp[1]}, Date: {exp[2]}, Category: {exp[4]}, Desc: {exp[3]}")
        
        # Check today's expenses
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) as total 
            FROM expenses 
            WHERE DATE(expense_date) = DATE('now') AND user_id = 1
        """)
        today_expenses = cursor.fetchone()[0]
        print(f"\nToday's expenses: AED {today_expenses}")
        
        # Check this month's expenses
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) as total 
            FROM expenses 
            WHERE strftime('%Y-%m', expense_date) = strftime('%Y-%m', 'now') AND user_id = 1
        """)
        month_expenses = cursor.fetchone()[0]
        print(f"This month's expenses: AED {month_expenses}")
        
        # Test dashboard query
        print("\n=== DASHBOARD QUERY TEST ===")
        cursor.execute("""
            SELECT 
                COALESCE(SUM(amount), 0) as total_expenses_today,
                (SELECT COALESCE(SUM(amount), 0) 
                 FROM expenses 
                 WHERE strftime('%Y-%m', expense_date) = strftime('%Y-%m', 'now') AND user_id = 1) as total_expenses_month
            FROM expenses 
            WHERE DATE(expense_date) = DATE('now') AND user_id = 1
        """)
        dashboard_data = cursor.fetchone()
        print(f"Dashboard query result: Today={dashboard_data[0]}, Month={dashboard_data[1]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_expense_data()
