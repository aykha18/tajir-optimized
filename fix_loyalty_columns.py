#!/usr/bin/env python3
"""
Fix Loyalty Column Names
Update JavaScript files to use correct column names
"""

import os
import re

def fix_js_files():
    """Fix column name mismatches in JavaScript files"""
    
    # Files to fix
    js_files = [
        'static/js/modules/loyalty-program.js',
        'static/js/modules/billing-system.js'
    ]
    
    # Column name mappings
    replacements = [
        ('available_points', 'current_points'),
        ('tier_level', 'tier_id'),
        ('join_date', 'enrollment_date'),
        ('lifetime_points', 'total_points')
    ]
    
    for file_path in js_files:
        if os.path.exists(file_path):
            print(f"🔧 Fixing {file_path}...")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply replacements
            for old_name, new_name in replacements:
                content = content.replace(old_name, new_name)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Updated {file_path}")
            else:
                print(f"ℹ️ No changes needed for {file_path}")
        else:
            print(f"⚠️ File not found: {file_path}")

if __name__ == "__main__":
    fix_js_files()
