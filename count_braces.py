#!/usr/bin/env python3
"""
Count braces in the main script block to find unmatched ones
"""

def count_braces():
    print("🔍 Reading app.html file...")
    
    with open('templates/app.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Find the script block starting at line 1984 (index 1983)
    script_start = 1983  # 0-based index for line 1984
    script_end = None
    
    # Find where this script block ends
    for i in range(script_start, len(lines)):
        if '</script>' in lines[i]:
            script_end = i
            break
    
    if script_end is None:
        print("❌ Could not find script end")
        return
    
    print(f"📊 Script block: lines {script_start + 1} to {script_end + 1}")
    
    # Extract the script content
    script_lines = lines[script_start:script_end + 1]
    script_content = '\n'.join(script_lines)
    
    # Count braces
    open_braces = script_content.count('{')
    close_braces = script_content.count('}')
    
    print(f"🔧 Open braces: {open_braces}")
    print(f"🔧 Close braces: {close_braces}")
    print(f"🔧 Difference: {open_braces - close_braces}")
    
    if open_braces != close_braces:
        print("❌ Unmatched braces found!")
        
        # Find where the mismatch occurs
        brace_count = 0
        for i, line in enumerate(script_lines):
            line_open = line.count('{')
            line_close = line.count('}')
            brace_count += line_open - line_close
            
            if brace_count < 0:
                print(f"❌ Too many close braces at line {script_start + i + 1}: {line.strip()}")
            
            print(f"Line {script_start + i + 1:4d} (balance: {brace_count:+2d}): {line}")
    else:
        print("✅ Braces are balanced")
    
    # Also count parentheses
    open_parens = script_content.count('(')
    close_parens = script_content.count(')')
    
    print(f"\n🔧 Open parentheses: {open_parens}")
    print(f"🔧 Close parentheses: {close_parens}")
    print(f"🔧 Difference: {open_parens - close_parens}")
    
    if open_parens != close_parens:
        print("❌ Unmatched parentheses found!")
    else:
        print("✅ Parentheses are balanced")

if __name__ == "__main__":
    count_braces()
