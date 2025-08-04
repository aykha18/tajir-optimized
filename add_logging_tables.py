#!/usr/bin/env python3
"""
Script to add logging tables to existing database
"""

import sqlite3
import os

def add_logging_tables():
    """Add logging tables to existing database."""
    
    # Database path
    db_path = 'pos_tailor.db'
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        # Check if logging tables already exist
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('error_logs', 'user_actions')")
        existing_tables = [row['name'] for row in cursor.fetchall()]
        
        if 'error_logs' in existing_tables and 'user_actions' in existing_tables:
            print("Logging tables already exist!")
            return
        
        print("Adding logging tables to database...")
        
        # Create error_logs table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS error_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                operation TEXT NOT NULL,
                table_name TEXT NOT NULL,
                error_message TEXT NOT NULL,
                user_id INTEGER,
                data_snapshot TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Create user_actions table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_actions (
                action_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                user_id INTEGER,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Create indexes for logging tables
        conn.execute('CREATE INDEX IF NOT EXISTS idx_error_logs_timestamp ON error_logs(timestamp)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_error_logs_user_id ON error_logs(user_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_error_logs_operation ON error_logs(operation)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_user_actions_timestamp ON user_actions(timestamp)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_user_actions_user_id ON user_actions(user_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_user_actions_action ON user_actions(action)')
        
        conn.commit()
        print("✅ Logging tables added successfully!")
        
        # Verify tables were created
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('error_logs', 'user_actions')")
        created_tables = [row['name'] for row in cursor.fetchall()]
        print(f"Created tables: {created_tables}")
        
    except Exception as e:
        print(f"❌ Error adding logging tables: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_logging_tables() 