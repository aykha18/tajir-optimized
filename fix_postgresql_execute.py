#!/usr/bin/env python3
"""
Script to automatically fix all conn.execute() calls in app.py to work with PostgreSQL
"""

import re

def fix_conn_execute_calls():
    """Replace all conn.execute() calls with proper cursor-based approach"""
    
    # Read the file
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match conn.execute() calls
    # This pattern matches:
    # - conn.execute(sql, params).fetchone()
    # - conn.execute(sql, params).fetchall()
    # - conn.execute(sql, params)
    # - conn.execute(sql)
    
    # First, let's find all the patterns
    patterns = [
        # Pattern 1: conn.execute(sql, params).fetchone()
        (r'(\s+)conn\.execute\(([^)]+)\)\.fetchone\(\)', r'\1cursor = execute_query(conn, \2)\n\1result = cursor.fetchone()'),
        
        # Pattern 2: conn.execute(sql, params).fetchall()
        (r'(\s+)conn\.execute\(([^)]+)\)\.fetchall\(\)', r'\1cursor = execute_query(conn, \2)\n\1result = cursor.fetchall()'),
        
        # Pattern 3: conn.execute(sql, params) (without fetch)
        (r'(\s+)conn\.execute\(([^)]+)\)(?!\.)', r'\1execute_update(conn, \2)'),
        
        # Pattern 4: conn.execute(sql) (without params)
        (r'(\s+)conn\.execute\(([^)]+)\)(?!\.)', r'\1execute_update(conn, \2)'),
    ]
    
    # Apply patterns
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Write back to file
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed conn.execute() calls in app.py")

if __name__ == "__main__":
    fix_conn_execute_calls()
