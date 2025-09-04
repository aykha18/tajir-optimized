#!/usr/bin/env python3
"""
Fix missing shop settings on Railway deployment
Using the correct Railway connection parameters
"""

import os
import psycopg2
import sys

def fix_railway_shop_settings():
    """Create missing shop settings for users on Railway."""
    
    print("🚀 Fixing Railway Missing Shop Settings")
    print("=" * 50)
    
    # Railway connection parameters
    db_params = {
        'host': 'hopper.proxy.rlwy.net',
        'port': 46337,
        'database': 'tajir_pos',
        'user': 'postgres',
        'password': 'SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd'
    }
    
    print(f"📡 Connecting to Railway database...")
    print(f"   Host: {db_params['host']}")
    print(f"   Port: {db_params['port']}")
    print(f"   Database: {db_params['database']}")
    
    try:
        # Connect to Railway PostgreSQL database
        conn = psycopg2.connect(**db_params)
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        
        # Find users without shop settings
        cursor.execute("""
            SELECT u.user_id, u.shop_code, u.shop_name, u.mobile, u.email
            FROM users u 
            LEFT JOIN shop_settings s ON u.user_id = s.user_id 
            WHERE s.user_id IS NULL
        """)
        missing_users = cursor.fetchall()
        
        if not missing_users:
            print("✅ All users already have shop settings")
            conn.close()
            return
        
        print(f"Found {len(missing_users)} users without shop settings:")
        for user_id, shop_code, shop_name, mobile, email in missing_users:
            print(f"  User ID: {user_id}, Shop Code: {shop_code}, Shop Name: {shop_name}")
        
        print(f"\n🔧 Creating shop settings for missing users...")
        
        created_count = 0
        for user_id, shop_code, shop_name, mobile, email in missing_users:
            try:
                # Create shop settings for this user
                cursor.execute("""
                    INSERT INTO shop_settings (
                        user_id, shop_name, shop_mobile, trn, address, 
                        invoice_static_info, use_dynamic_invoice_template,
                        currency_code, currency_symbol, timezone, 
                        date_format, time_format
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_id,
                    shop_name or 'My Shop',
                    mobile or '',
                    '',  # TRN
                    '',  # Address
                    f"Shop Code: {shop_code}",
                    True,  # Enable dynamic invoice template
                    'AED',  # Default currency
                    'د.إ',  # Default currency symbol
                    'Asia/Dubai',  # Default timezone
                    'DD/MM/YYYY',  # Default date format
                    '24h'  # Default time format
                ))
                created_count += 1
                print(f"✅ Created shop settings for User ID: {user_id} ({shop_name})")
                
            except Exception as e:
                print(f"❌ Failed to create shop settings for User ID: {user_id}: {e}")
        
        # Commit all changes
        conn.commit()
        print(f"\n✅ Successfully created shop settings for {created_count} users")
        
        # Verify the fix
        cursor.execute("""
            SELECT COUNT(*) FROM users u 
            LEFT JOIN shop_settings s ON u.user_id = s.user_id 
            WHERE s.user_id IS NULL
        """)
        remaining_missing = cursor.fetchone()[0]
        
        if remaining_missing == 0:
            print("✅ All users now have shop settings!")
        else:
            print(f"⚠️  {remaining_missing} users still missing shop settings")
        
        conn.close()
        print(f"\n🎉 Railway shop settings fix completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        sys.exit(1)

if __name__ == "__main__":
    fix_railway_shop_settings()