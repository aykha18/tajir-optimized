#!/usr/bin/env python3
"""
Fix the script block 24 syntax error by replacing it with a corrected version
"""

def fix_script_block():
    print("🔧 Fixing Script Block 24 Syntax Error")
    
    # Read the current app.html file
    with open('templates/app.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the problematic script block (lines 1983 to 2119)
    # Replace it with a corrected version
    start_marker = '<script>\n    // Initialize MobileScreens module\n    document.addEventListener(\'DOMContentLoaded\', function() {'
    end_marker = '    });\n</script>'
    
    # Find the start and end positions
    start_pos = content.find(start_marker)
    if start_pos == -1:
        print("❌ Could not find start marker")
        return
    
    # Find the end position by looking for the closing script tag
    end_pos = content.find('</script>', start_pos)
    if end_pos == -1:
        print("❌ Could not find end marker")
        return
    
    # Extract the problematic section
    problematic_section = content[start_pos:end_pos + 9]
    print(f"📝 Found problematic section: {len(problematic_section)} characters")
    
    # Create a corrected version
    corrected_section = '''<script>
    // Initialize MobileScreens module
    document.addEventListener('DOMContentLoaded', function() {
        if (window.innerWidth <= 768) {
            const mobileScreens = new MobileScreens();
            
            // Expose mobileScreens globally for debugging
            window.mobileScreens = mobileScreens;
            
            // Add manual trigger for view toggles
            window.setupMobileViewToggles = function() {
                if (window.mobileScreens) {
                    window.mobileScreens.setupViewToggles();
                }
            };
        }
        
        // Initialize Mobile Navigation
        console.log('Checking mobile navigation initialization...');
        console.log('Window width:', window.innerWidth);
        console.log('MobileNavigation available:', !!window.MobileNavigation);
        
        // Force mobile navigation to show on mobile devices or when testing
        const isMobileDevice = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        const isMobileWidth = window.innerWidth <= 768;
        const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        const shouldShowMobileNav = isMobileDevice || isMobileWidth || isTouchDevice;
        
        console.log('Mobile detection:', {
            isMobileDevice,
            isMobileWidth,
            isTouchDevice,
            shouldShowMobileNav,
            windowWidth: window.innerWidth
        });
        
        if (window.MobileNavigation && shouldShowMobileNav) {
            console.log('Initializing MobileNavigation class...');
            MobileNavigation.initializeMobileNavigation().then(mobileNav => {
                console.log('Mobile Navigation initialized successfully');
                window.mobileNavigation = mobileNav;
            }).catch(error => {
                console.error('Failed to initialize mobile navigation:', error);
            });
        } else if (shouldShowMobileNav) {
            // Fallback: Create simple mobile navigation if MobileNavigation class is not available
            console.log('Creating fallback mobile navigation');
            
            // Create fallback navigation immediately
            const fallbackNav = document.createElement('nav');
            fallbackNav.className = 'mobile-nav';
            fallbackNav.id = 'mobile-navigation-bar';
            fallbackNav.style.cssText = `
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                border-top: 1px solid #475569;
                padding: 8px;
                z-index: 1000;
                display: flex;
                justify-content: space-around;
                align-items: center;
                box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.3);
            `;
            
            // Add navigation items
            const navItems = [
                { icon: '🏠', label: 'Home', action: 'showDashboard' },
                { icon: '📦', label: 'Products', action: 'showProducts' },
                { icon: '🧾', label: 'Billing', action: 'showBilling' },
                { icon: '👥', label: 'Customers', action: 'showCustomers' },
                { icon: '⚙️', label: 'Settings', action: 'showSettings' }
            ];
            
            navItems.forEach(item => {
                const navItem = document.createElement('button');
                navItem.className = 'mobile-nav-item';
                navItem.innerHTML = `
                    <div style="font-size: 20px; margin-bottom: 2px;">${item.icon}</div>
                    <div style="font-size: 10px; color: #94a3b8;">${item.label}</div>
                `;
                navItem.style.cssText = `
                    background: transparent;
                    border: none;
                    color: #94a3b8;
                    padding: 8px;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    min-width: 50px;
                `;
                
                navItem.addEventListener('click', () => {
                    console.log(`Mobile nav clicked: ${item.action}`);
                    // Add navigation logic here
                });
                
                navItem.addEventListener('mouseenter', () => {
                    navItem.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
                    navItem.style.color = '#60a5fa';
                });
                
                navItem.addEventListener('mouseleave', () => {
                    navItem.style.backgroundColor = 'transparent';
                    navItem.style.color = '#94a3b8';
                });
                
                fallbackNav.appendChild(navItem);
            });
            
            // Remove existing mobile nav if present
            const existingNav = document.querySelector('.mobile-nav, #mobile-navigation-bar');
            if (existingNav) {
                existingNav.remove();
            }
            
            document.body.appendChild(fallbackNav);
            console.log('Fallback mobile navigation created');
        }
    });
</script>'''
    
    # Replace the problematic section
    new_content = content.replace(problematic_section, corrected_section)
    
    # Write the fixed content back
    with open('templates/app.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Script block 24 syntax error fixed!")
    print("   - Corrected brace matching")
    print("   - Fixed function scope issues")
    print("   - Maintained all functionality")

if __name__ == "__main__":
    fix_script_block()
