#!/usr/bin/env python3
"""
Check analytics issue and customer points
"""
import requests
import json

def check_analytics_issue():
    """Check why analytics show 0 points when customers have points"""
    try:
        print("🔍 CHECKING ANALYTICS ISSUE")
        print("=" * 50)
        base_url = "https://tajir.up.railway.app"
        
        # Get loyalty customers
        print("1️⃣ Getting loyalty customers...")
        response = requests.get(f"{base_url}/api/loyalty/customers", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                customers = data.get('customers', [])
                print(f"   Found {len(customers)} customers")
                
                total_points = 0
                for i, customer in enumerate(customers[:5]):
                    name = customer.get('name', 'Unknown')
                    points = customer.get('available_points', 0) or 0
                    total_points += points
                    print(f"   {i+1}. {name}: {points} points")
                
                print(f"   Total points from first 5 customers: {total_points}")
                
                # Get analytics
                print("\n2️⃣ Getting analytics...")
                analytics_response = requests.get(f"{base_url}/api/loyalty/analytics", timeout=10)
                if analytics_response.status_code == 200:
                    analytics_data = analytics_response.json()
                    if analytics_data.get('success'):
                        analytics = analytics_data.get('analytics', {})
                        print(f"   Total Points Issued: {analytics.get('total_points_issued')}")
                        print(f"   Active Points: {analytics.get('active_points')}")
                        print(f"   Total Points Redeemed: {analytics.get('total_points_redeemed')}")
                        print(f"   Total Customers: {analytics.get('total_customers')}")
                        
                        if analytics.get('total_points_issued') == 0 and total_points > 0:
                            print(f"\n❌ ISSUE FOUND: Analytics shows 0 points issued but customers have {total_points} points")
                        else:
                            print(f"\n✅ Analytics data looks correct")
                    else:
                        print(f"   ❌ Failed to get analytics: {analytics_data.get('error')}")
                else:
                    print(f"   ❌ Failed to get analytics: {analytics_response.status_code}")
            else:
                print(f"   ❌ Failed to get customers: {data.get('error')}")
        else:
            print(f"   ❌ Failed to get customers: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_analytics_issue()
