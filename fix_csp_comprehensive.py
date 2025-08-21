#!/usr/bin/env python3
"""
Comprehensive CSP Policy Fix
This script updates the CSP policy to allow all necessary external resources.
"""

import re

def fix_csp_policy_comprehensive():
    """Update the CSP policy to allow all necessary external resources."""
    print("Fixing CSP policy comprehensively...")
    
    # Read the current app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find the current CSP policy
    csp_pattern = r'csp_policy\s*=\s*\(\s*"([^"]+)"'
    match = re.search(csp_pattern, content, re.DOTALL)
    
    if match:
        # Update the CSP policy to allow all necessary resources
        new_csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://unpkg.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.tailwindcss.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https://images.unsplash.com https://*.unsplash.com; "
            "connect-src 'self' https://cdn.tailwindcss.com https://fonts.googleapis.com https://fonts.gstatic.com https://unpkg.com https://cdn.jsdelivr.net; "
            "worker-src 'self' blob:; "
            "child-src 'self' blob:;"
        )
        
        # Replace the CSP policy
        content = re.sub(
            r'csp_policy\s*=\s*\(\s*"[^"]+"',
            f'csp_policy = ("{new_csp_policy}"',
            content,
            flags=re.DOTALL
        )
        
        # Write back to app.py
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Comprehensive CSP policy updated successfully!")
        print("   - Added all necessary external domains")
        print("   - Added 'unsafe-eval' for Chart.js compatibility")
        print("   - Added worker-src and child-src for PWA support")
        print("   - Added connect-src for external API calls")
    else:
        print("❌ Could not find CSP policy in app.py")

def main():
    """Main function to fix CSP issues comprehensively."""
    print("Starting comprehensive CSP policy fix...")
    
    try:
        fix_csp_policy_comprehensive()
        print("\n✅ Comprehensive CSP policy fix completed!")
        print("\nNext steps:")
        print("1. Deploy to Railway: railway up")
        print("2. Test all external resources loading")
        print("3. Verify Chart.js, Lucide icons, and Tailwind CSS work")
        
    except Exception as e:
        print(f"\n❌ Error during comprehensive CSP fix: {e}")

if __name__ == "__main__":
    main()
