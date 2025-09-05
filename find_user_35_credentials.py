#!/usr/bin/env python3
"""
Find the login credentials for user_id 35
"""

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os

def find_user_35_credentials():
    print("🔍 Finding Login Credentials for User ID 35")
    
    load_dotenv()
    
    db_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'tajir_pos',
        'user': 'postgres',
        'password': 'aykha123'
    }
    
    conn = None
    try:
        print("\n🔌 Connecting to database...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        print("   ✅ Database connected successfully")
        
        print(f"\n📋 Querying user data for user_id 35...")
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (35,))
        user = cursor.fetchone()
        
        if user:
            print(f"   ✅ Found user_id 35")
            print(f"\n📊 User ID 35 Details:")
            print(f"   📝 user_id: {user['user_id']}")
            print(f"   📝 email: {user['email']}")
            print(f"   📝 name: {user.get('name', 'N/A')}")
            print(f"   📝 phone: {user.get('phone', 'N/A')}")
            print(f"   📝 created_at: {user.get('created_at', 'N/A')}")
            
            # Check if there are other users with similar emails
            print(f"\n🔍 Checking for similar users...")
            cursor.execute("SELECT user_id, email, name FROM users WHERE email LIKE %s OR email LIKE %s", 
                          ('%tumble%', '%dry%'))
            similar_users = cursor.fetchall()
            
            if similar_users:
                print("   📋 Similar users found:")
                for similar_user in similar_users:
                    print(f"   📝 user_id {similar_user['user_id']}: {similar_user['email']} ({similar_user['name']})")
            
        else:
            print(f"   ❌ No user found with id 35")
            
        # Also check user_id 27 for comparison
        print(f"\n📋 Querying user data for user_id 27 (current login)...")
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (27,))
        user_27 = cursor.fetchone()
        
        if user_27:
            print(f"   ✅ Found user_id 27")
            print(f"   📝 email: {user_27['email']}")
            print(f"   📝 name: {user_27.get('name', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    find_user_35_credentials()
