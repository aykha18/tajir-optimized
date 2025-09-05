#!/usr/bin/env python3
"""
Find ALL JavaScript syntax errors by validating each script block
"""

import re

def find_all_js_errors():
    print("🔍 Reading app.html file...")
    
    with open('templates/app.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    print(f"📊 Total lines: {len(lines)}")
    
    # Find all script blocks
    script_pattern = r'<script[^>]*>(.*?)</script>'
    script_matches = list(re.finditer(script_pattern, content, re.DOTALL))
    
    print(f"📜 Found {len(script_matches)} script blocks")
    
    for i, match in enumerate(script_matches):
        script_content = match.group(1)
        script_line_start = content[:match.start()].count('\n') + 1
        script_line_end = content[:match.end()].count('\n') + 1
        
        print(f"\n📜 Script block {i+1}: lines {script_line_start} to {script_line_end}")
        
        # Check for common syntax errors
        open_braces = script_content.count('{')
        close_braces = script_content.count('}')
        open_parens = script_content.count('(')
        close_parens = script_content.count(')')
        
        print(f"   Braces: {open_braces} open, {close_braces} close (diff: {open_braces - close_braces})")
        print(f"   Parens: {open_parens} open, {close_parens} close (diff: {open_parens - close_parens})")
        
        if open_braces != close_braces:
            print(f"   ❌ Unmatched braces in script block {i+1}")
        
        if open_parens != close_parens:
            print(f"   ❌ Unmatched parentheses in script block {i+1}")
        
        # Look for specific error patterns
        if 'missing ) after argument list' in script_content:
            print(f"   ❌ Found 'missing ) after argument list' error in script block {i+1}")
        
        # Show content preview
        preview = script_content.strip()[:200]
        if len(preview) < len(script_content.strip()):
            preview += "..."
        print(f"   Content: {preview}")
        
        # Check for problematic onclick patterns
        onclick_pattern = r'onclick="[^"]*"'
        onclick_matches = re.findall(onclick_pattern, script_content)
        for onclick in onclick_matches:
            if onclick.count('(') != onclick.count(')'):
                print(f"   ❌ Unmatched parens in onclick: {onclick}")
    
    # Also check for inline onclick handlers in the HTML
    print(f"\n🔍 Checking inline onclick handlers...")
    onclick_pattern = r'onclick="[^"]*"'
    onclick_matches = list(re.finditer(onclick_pattern, content))
    
    for match in onclick_matches:
        onclick = match.group()
        line_num = content[:match.start()].count('\n') + 1
        
        # Check for unmatched parentheses
        if onclick.count('(') != onclick.count(')'):
            print(f"   ❌ Line {line_num}: Unmatched parens in onclick: {onclick}")
        
        # Check for unmatched quotes
        if onclick.count("'") % 2 != 0:
            print(f"   ❌ Line {line_num}: Unmatched single quotes in onclick: {onclick}")
        
        # Check for specific problematic patterns
        if 'console.log(' in onclick and not onclick.endswith('")'):
            print(f"   ❌ Line {line_num}: Potentially malformed console.log in onclick: {onclick}")
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    find_all_js_errors()
