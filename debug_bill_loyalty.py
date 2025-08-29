#!/usr/bin/env python3
"""
Debug bill loyalty query
"""

import psycopg2

def debug_bill_loyalty():
    """Debug the loyalty query used in bill creation"""
    try:
        print("🔍 DEBUGGING BILL LOYALTY QUERY")
        print("=" * 50)
        
        # Connect to Railway database
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database")
        
        # Test the exact query used in bill creation
        user_id = 1
        customer_id = 63  # Abdullah Al Falasi
        
        print(f"Testing loyalty query for user_id={user_id}, customer_id={customer_id}")
        
        # Query 1: Check if customer is enrolled
        cursor.execute("""
            SELECT cl.customer_id, cl.tier_level, cl.available_points,
                   lc.points_per_currency, lc.currency_per_point
            FROM customer_loyalty cl
            LEFT JOIN loyalty_config lc ON cl.user_id = lc.user_id
            WHERE cl.user_id = %s AND cl.customer_id = %s
        """, (user_id, customer_id))
        
        loyalty_info = cursor.fetchone()
        
        if loyalty_info:
            print(f"✅ Customer loyalty found:")
            print(f"   Customer ID: {loyalty_info[0]}")
            print(f"   Tier Level: {loyalty_info[1]}")
            print(f"   Available Points: {loyalty_info[2]}")
            print(f"   Points per Currency: {loyalty_info[3]}")
            print(f"   Currency per Point: {loyalty_info[4]}")
            
            # Query 2: Check tier multiplier
            tier_level = loyalty_info[1]
            cursor.execute("""
                SELECT bonus_points_multiplier FROM loyalty_tiers 
                WHERE user_id = %s AND tier_level = %s
            """, (user_id, tier_level))
            
            tier_info = cursor.fetchone()
            if tier_info:
                print(f"✅ Tier multiplier found: {tier_info[0]}")
            else:
                print(f"❌ Tier multiplier not found for tier: {tier_level}")
                
                # Check what tiers exist
                cursor.execute("SELECT tier_level FROM loyalty_tiers WHERE user_id = %s", (user_id,))
                tiers = cursor.fetchall()
                print(f"Available tiers: {[t[0] for t in tiers]}")
        else:
            print(f"❌ Customer loyalty not found")
            
            # Check if customer exists in customer_loyalty
            cursor.execute("SELECT customer_id, tier_level FROM customer_loyalty WHERE customer_id = %s", (customer_id,))
            customer_check = cursor.fetchone()
            if customer_check:
                print(f"Customer exists in customer_loyalty: {customer_check}")
            else:
                print(f"Customer not found in customer_loyalty")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_bill_loyalty()

