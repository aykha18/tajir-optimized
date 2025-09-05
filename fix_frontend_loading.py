#!/usr/bin/env python3
"""
Fix the frontend loading issue by adding cache-busting and debugging
"""

def fix_frontend_loading():
    print("🔧 Fixing Frontend Loading Issue")
    
    # Read the current shop-settings.js file
    with open('static/js/modules/shop-settings.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add cache-busting and debugging to the loadShopSettings function
    fixed_content = content.replace(
        'async function loadShopSettings() {',
        '''async function loadShopSettings() {
    console.log('🔄 loadShopSettings called');
    '''
    )
    
    # Add debugging to the fetch request
    fixed_content = fixed_content.replace(
        "const response = await fetch('/api/shop-settings');",
        '''const response = await fetch('/api/shop-settings?' + Date.now(), {
        cache: 'no-cache',
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
      });
      console.log('📡 API response status:', response.status);'''
    )
    
    # Add debugging to the populateShopSettingsForm function
    fixed_content = fixed_content.replace(
        'function populateShopSettingsForm(settings) {',
        '''function populateShopSettingsForm(settings) {
    console.log('📝 populateShopSettingsForm called with:', settings);
    '''
    )
    
    # Add debugging to checkbox setting
    fixed_content = fixed_content.replace(
        'if (input.type === \'checkbox\') {\n        input.checked = Boolean(value);',
        '''if (input.type === \'checkbox\') {
        console.log(`🔲 Setting checkbox ${name}: ${value} (Boolean: ${Boolean(value)})`);
        input.checked = Boolean(value);'''
    )
    
    # Write the fixed content back
    with open('static/js/modules/shop-settings.js', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("✅ Added cache-busting and debugging to shop-settings.js")
    print("   - Added cache: 'no-cache' to API requests")
    print("   - Added timestamp to prevent caching")
    print("   - Added console logging for debugging")
    print("   - Added Cache-Control headers")

if __name__ == "__main__":
    fix_frontend_loading()
