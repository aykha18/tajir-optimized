#!/usr/bin/env python3
"""
Test if user has shop settings in database
"""

import psycopg2
import os
from dotenv import load_dotenv

def test_user_shop_settings():
    print("🧪 Testing User Shop Settings in Database")
    
    # Load environment variables
    load_dotenv()
    
    # Database connection
    conn = psycopg2.connect(
        host='localhost',
        database='tajir_pos',
        user='postgres',
        password='aykha123'
    )
    
    try:
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT user_id, email FROM users WHERE email = %s", ('td@tajir.com',))
        user = cursor.fetchone()
        
        if user:
            user_id = user[0]
            email = user[1]
            print(f"✅ User found: ID={user_id}, Email={email}")
            
            # Check if shop settings exist
            cursor.execute("SELECT * FROM shop_settings WHERE user_id = %s", (user_id,))
            shop_settings = cursor.fetchone()
            
            if shop_settings:
                print("✅ Shop settings found:")
                # Get column names
                cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'shop_settings' ORDER BY ordinal_position")
                columns = [row[0] for row in cursor.fetchall()]
                
                for i, column in enumerate(columns):
                    if i < len(shop_settings):
                        value = shop_settings[i]
                        print(f"   {column}: {value}")
            else:
                print("❌ No shop settings found for this user")
                
        else:
            print("❌ User not found")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_user_shop_settings()
