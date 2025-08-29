#!/usr/bin/env python3
"""
Debug Railway app not reflecting updated loyalty data
"""

import requests
import psycopg2
import json

def check_railway_app_status():
    """Check if Railway app is working and responding"""
    try:
        print("🔍 CHECKING RAILWAY APP STATUS")
        print("=" * 50)
        
        # Test basic endpoints
        endpoints = [
            "https://tajir-pos-production.up.railway.app/",
            "https://tajir-pos-production.up.railway.app/api/customers",
            "https://tajir-pos-production.up.railway.app/api/loyalty/customers"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=10)
                print(f"✅ {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
            except Exception as e:
                print(f"❌ {endpoint}: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error checking Railway app: {e}")
        return False

def check_abdullah_loyalty():
    """Check Abdullah Al Falasi's loyalty data specifically"""
    try:
        print("\n🔍 CHECKING ABDULLAH AL FALASI")
        print("=" * 50)
        
        # Connect to Railway database
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        # Find Abdullah Al Falasi
        cursor.execute("""
            SELECT customer_id, name, phone 
            FROM customers 
            WHERE name ILIKE '%Abdullah%' OR name ILIKE '%Falasi%'
        """)
        abdullah = cursor.fetchone()
        
        if abdullah:
            customer_id = abdullah[0]
            print(f"✅ Found: {abdullah[1]} (ID: {customer_id}, Phone: {abdullah[2]})")
            
            # Check loyalty data
            cursor.execute("""
                SELECT tier_level, total_spent, total_purchases, available_points, last_purchase_date
                FROM customer_loyalty 
                WHERE customer_id = %s
            """, (customer_id,))
            loyalty = cursor.fetchone()
            
            if loyalty:
                print(f"✅ Loyalty Data:")
                print(f"   Tier: {loyalty[0]}")
                print(f"   Total Spent: AED {loyalty[1]}")
                print(f"   Total Purchases: {loyalty[2]}")
                print(f"   Available Points: {loyalty[3]}")
                print(f"   Last Purchase: {loyalty[4]}")
            else:
                print("❌ No loyalty data found")
            
            # Check bills
            cursor.execute("""
                SELECT COUNT(*), SUM(total_amount), MAX(created_at)
                FROM bills 
                WHERE customer_id = %s
            """, (customer_id,))
            bills = cursor.fetchone()
            
            if bills:
                print(f"✅ Bills Data:")
                print(f"   Count: {bills[0]}")
                print(f"   Total Amount: AED {bills[1] or 0}")
                print(f"   Last Bill: {bills[2]}")
            
            conn.close()
            return customer_id
        else:
            print("❌ Abdullah Al Falasi not found in customers table")
            conn.close()
            return None
            
    except Exception as e:
        print(f"❌ Error checking Abdullah: {e}")
        return None

def test_railway_api_for_customer(customer_id):
    """Test Railway API for specific customer"""
    try:
        print(f"\n🌐 TESTING RAILWAY API FOR CUSTOMER {customer_id}")
        print("=" * 50)
        
        # Test loyalty customers endpoint
        response = requests.get("https://tajir-pos-production.up.railway.app/api/loyalty/customers")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                customers = data.get('customers', [])
                print(f"✅ Found {len(customers)} customers in loyalty API")
                
                # Find Abdullah
                abdullah_api = None
                for customer in customers:
                    if customer.get('customer_id') == customer_id:
                        abdullah_api = customer
                        break
                
                if abdullah_api:
                    print(f"✅ Abdullah found in API:")
                    print(f"   Name: {abdullah_api.get('name')}")
                    print(f"   Total Spent: {abdullah_api.get('total_spent')}")
                    print(f"   Available Points: {abdullah_api.get('available_points')}")
                    print(f"   Total Purchases: {abdullah_api.get('total_purchases')}")
                    print(f"   Tier Level: {abdullah_api.get('tier_level')}")
                else:
                    print(f"❌ Abdullah (ID: {customer_id}) not found in API response")
                    
                    # Show first few customers for debugging
                    print(f"\n📋 First 3 customers in API:")
                    for i, customer in enumerate(customers[:3]):
                        print(f"   {i+1}. ID {customer.get('customer_id')}: {customer.get('name')} - AED {customer.get('total_spent')}")
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ API Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing Railway API: {e}")

def check_railway_deployment():
    """Check if Railway deployment is up to date"""
    try:
        print("\n🚀 CHECKING RAILWAY DEPLOYMENT")
        print("=" * 50)
        
        # Test if the app is using the latest code
        response = requests.get("https://tajir-pos-production.up.railway.app/api/loyalty/config")
        if response.status_code == 200:
            print("✅ Loyalty config endpoint working")
            data = response.json()
            if data.get('success'):
                config = data.get('config', {})
                print(f"   Points per AED: {config.get('points_per_aed')}")
                print(f"   Enabled: {config.get('enabled')}")
        else:
            print(f"❌ Loyalty config failed: {response.status_code}")
        
        # Test if the app is connecting to the right database
        response = requests.get("https://tajir-pos-production.up.railway.app/api/customers")
        if response.status_code == 200:
            print("✅ Customers endpoint working")
            data = response.json()
            if data.get('success'):
                customers = data.get('customers', [])
                print(f"   Total customers: {len(customers)}")
        else:
            print(f"❌ Customers endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking deployment: {e}")

def force_refresh_loyalty_data():
    """Force refresh loyalty data by updating the database"""
    try:
        print("\n🔄 FORCING LOYALTY DATA REFRESH")
        print("=" * 50)
        
        conn = psycopg2.connect(
            "postgresql://postgres:SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd@hopper.proxy.rlwy.net:46337/tajir_pos"
        )
        cursor = conn.cursor()
        
        # Find Abdullah
        cursor.execute("""
            SELECT customer_id, name 
            FROM customers 
            WHERE name ILIKE '%Abdullah%' OR name ILIKE '%Falasi%'
        """)
        abdullah = cursor.fetchone()
        
        if abdullah:
            customer_id = abdullah[0]
            print(f"🔄 Refreshing data for {abdullah[1]} (ID: {customer_id})")
            
            # Get current bills total
            cursor.execute("""
                SELECT COUNT(*), SUM(total_amount), MAX(created_at)
                FROM bills 
                WHERE customer_id = %s
            """, (customer_id,))
            bills = cursor.fetchone()
            
            if bills and bills[1]:
                total_spent = bills[1]
                bill_count = bills[0]
                last_purchase = bills[2]
                
                # Update loyalty data
                cursor.execute("""
                    UPDATE customer_loyalty 
                    SET total_spent = %s,
                        total_purchases = %s,
                        available_points = %s,
                        total_points = %s,
                        last_purchase_date = %s,
                        tier_level = CASE 
                            WHEN %s >= 5000 THEN 'Gold'
                            WHEN %s >= 1000 THEN 'Silver'
                            ELSE 'Bronze'
                        END
                    WHERE customer_id = %s
                """, (total_spent, bill_count, int(total_spent), int(total_spent), last_purchase, total_spent, total_spent, customer_id))
                
                conn.commit()
                print(f"✅ Updated loyalty data:")
                print(f"   Total Spent: AED {total_spent}")
                print(f"   Total Purchases: {bill_count}")
                print(f"   Points: {int(total_spent)}")
                print(f"   Last Purchase: {last_purchase}")
            else:
                print("⚠️  No bills found for this customer")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error refreshing data: {e}")

if __name__ == "__main__":
    print("🔧 DEBUGGING RAILWAY APP ISSUE")
    print("=" * 80)
    
    # Check Railway app status
    check_railway_app_status()
    
    # Check Abdullah's data
    customer_id = check_abdullah_loyalty()
    
    if customer_id:
        # Test Railway API
        test_railway_api_for_customer(customer_id)
        
        # Check deployment
        check_railway_deployment()
        
        # Force refresh
        force_refresh_loyalty_data()
        
        # Test API again after refresh
        print("\n🔄 TESTING API AFTER REFRESH")
        test_railway_api_for_customer(customer_id)
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("This debug will help identify why the Railway app is not showing updated loyalty data.")
    print("Check if the app is connecting to the right database and if the data is being cached.")

