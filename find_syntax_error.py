#!/usr/bin/env python3
"""
Find the exact JavaScript syntax error by extracting the HTML and analyzing it
"""

import re

def find_syntax_errors():
    print("🔍 Reading app.html file...")
    
    with open('templates/app.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    print(f"📊 Total lines: {len(lines)}")
    print(f"🎯 Checking around line 2426...")
    
    # Check lines around 2426
    start_line = max(0, 2420)
    end_line = min(len(lines), 2440)
    
    for i in range(start_line, end_line):
        line_num = i + 1
        line_content = lines[i]
        print(f"{line_num:4d}: {line_content}")
    
    print("\n🔍 Searching for potential JavaScript syntax issues...")
    
    # Look for common syntax error patterns
    patterns = [
        (r'onclick="[^"]*"[^>]*onclick=', 'Duplicate onclick attributes'),
        (r'onclick="[^"]*[^\\]"[^"]*"', 'Unescaped quotes in onclick'),
        (r'onclick="[^"]*\([^)]*$', 'Unclosed parentheses in onclick'),
        (r'onclick="[^"]*\{[^}]*$', 'Unclosed braces in onclick'),
        (r'onclick="[^"]*\'[^\']*$', 'Unclosed single quotes in onclick'),
        (r'onclick="[^"]*`[^`]*$', 'Unclosed backticks in onclick'),
    ]
    
    error_count = 0
    for pattern, description in patterns:
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            error_count += 1
            # Find line number
            line_num = content[:match.start()].count('\n') + 1
            print(f"❌ {description} at line {line_num}: {match.group()[:100]}...")
    
    if error_count == 0:
        print("✅ No obvious JavaScript syntax errors found in onclick attributes")
    
    print("\n🔍 Searching for JavaScript in script tags...")
    script_pattern = r'<script[^>]*>(.*?)</script>'
    script_matches = re.finditer(script_pattern, content, re.DOTALL)
    
    for match in script_matches:
        script_content = match.group(1)
        script_line_start = content[:match.start()].count('\n') + 1
        print(f"📜 Script block at line {script_line_start}:")
        
        # Check for common syntax errors in the script
        if 'console.log(' in script_content and script_content.count('(') != script_content.count(')'):
            print("   ❌ Unmatched parentheses in console.log")
        
        if 'function(' in script_content and script_content.count('{') != script_content.count('}'):
            print("   ❌ Unmatched braces in function")
        
        # Look for specific problematic patterns
        if 'missing ) after argument list' in script_content:
            print("   ❌ Found 'missing ) after argument list' error")
        
        print(f"   Content preview: {script_content[:200]}...")
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    find_syntax_errors()
