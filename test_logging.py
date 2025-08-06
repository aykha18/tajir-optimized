#!/usr/bin/env python3
"""
Script to test the logging system
"""

import sqlite3
from datetime import datetime
import json

def test_logging():
    """Test the logging system by adding sample data."""
    
    db_path = 'pos_tailor.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        # Add sample error log
        conn.execute('''
            INSERT INTO error_logs (timestamp, level, operation, table_name, error_message, user_id, data_snapshot)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            'ERROR',
            'CREATE',
            'bills',
            'Test error message for logging system',
            1,
            json.dumps({'test': 'data', 'amount': 100.50})
        ))
        
        # Add sample user action
        conn.execute('''
            INSERT INTO user_actions (timestamp, action, user_id, details)
            VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            'TEST_ACTION',
            1,
            json.dumps({'action': 'test', 'user': 'admin'})
        ))
        
        conn.commit()
        print("✅ Test logging data added successfully!")
        
        # Verify data was added
        error_count = conn.execute("SELECT COUNT(*) FROM error_logs").fetchone()[0]
        action_count = conn.execute("SELECT COUNT(*) FROM user_actions").fetchone()[0]
        
        print(f"Error logs: {error_count}")
        print(f"User actions: {action_count}")
        
    except Exception as e:
        print(f"❌ Error testing logging: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    test_logging() 