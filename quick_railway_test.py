#!/usr/bin/env python3
"""
Quick test to check Railway app status and loyalty data
"""

import requests
import psycopg2

def test_railway_app():
    """Test Railway app endpoints"""
    try:
        print("🔍 QUICK RAILWAY TEST")
        print("=" * 50)
        
        # Test basic endpoints
        endpoints = [
            "https://tajir-pos-production.up.railway.app/api/customers",
            "https://tajir-pos-production.up.railway.app/api/loyalty/customers"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=10)
                print(f"✅ {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    if 'customers' in data:
                        customers = data['customers']
                        print(f"   Found {len(customers)} customers")
                        if customers:
                            # Show first customer
                            first = customers[0]
                            print(f"   First: {first.get('name', 'N/A')} - AED {first.get('total_spent', 'N/A')}")
            except Exception as e:
                print(f"❌ {endpoint}: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_database():
    """Check database directly"""
    try:
        print("\n🔗 DATABASE CHECK")
        print("=" * 50)
        
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        # Check loyalty customers
        cursor.execute("""
            SELECT customer_id, name, total_spent, available_points, tier_level 
            FROM customer_loyalty 
            ORDER BY total_spent DESC 
            LIMIT 5
        """)
        loyalty_customers = cursor.fetchall()
        
        print(f"Top 5 Loyalty Customers:")
        for customer in loyalty_customers:
            print(f"   {customer[1]}: AED {customer[2]}, {customer[3]} points, {customer[4]} tier")
        
        # Check if Abdullah exists
        cursor.execute("""
            SELECT customer_id, name, total_spent 
            FROM customer_loyalty 
            WHERE name ILIKE '%Abdullah%'
        """)
        abdullah = cursor.fetchone()
        
        if abdullah:
            print(f"\n✅ Abdullah found: {abdullah[1]} - AED {abdullah[2]}")
        else:
            print(f"\n❌ Abdullah not found in loyalty program")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    test_railway_app()
    check_database()

