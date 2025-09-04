#!/usr/bin/env python3
"""
Advanced Caching Features Test Script
Tests all the new caching endpoints and functionality implemented in Step 10
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"
USER_ID = 1

def print_section(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def test_endpoint(method, endpoint, data=None, description=""):
    """Test an endpoint and return the response"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        else:
            print(f"❌ Unsupported method: {method}")
            return None
            
        print(f"✅ {description}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)}")
                return result
            except json.JSONDecodeError:
                print(f"   Response: {response.text}")
                return response.text
        else:
            print(f"   Error: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {description}")
        print(f"   Error: {e}")
        return None

def test_cache_performance():
    """Test cache performance improvements"""
    print_section("Testing Cache Performance")
    
    # Test products endpoint multiple times
    print("Testing products endpoint performance...")
    
    # First call (cache miss)
    start_time = time.time()
    test_endpoint("GET", f"/api/products/aggregated?user_id={USER_ID}", description="First call (cache miss)")
    first_call_time = time.time() - start_time
    
    # Second call (cache hit)
    start_time = time.time()
    test_endpoint("GET", f"/api/products/aggregated?user_id={USER_ID}", description="Second call (cache hit)")
    second_call_time = time.time() - start_time
    
    # Third call (cache hit)
    start_time = time.time()
    test_endpoint("GET", f"/api/products/aggregated?user_id={USER_ID}", description="Third call (cache hit)")
    third_call_time = time.time() - start_time
    
    print(f"\nPerformance Results:")
    print(f"First call (cache miss): {first_call_time:.3f}s")
    print(f"Second call (cache hit): {second_call_time:.3f}s")
    print(f"Third call (cache hit): {third_call_time:.3f}s")
    
    if second_call_time < first_call_time:
        improvement = ((first_call_time - second_call_time) / first_call_time) * 100
        print(f"✅ Cache hit improvement: {improvement:.1f}%")
    else:
        print("❌ No performance improvement detected")

def main():
    print("🚀 Advanced Caching Features Test Suite")
    print(f"Testing against: {BASE_URL}")
    print(f"User ID: {USER_ID}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Test health and resources
    print_section("1. Health & Resource Monitoring")
    test_endpoint("GET", "/api/monitor/health", description="Health Check")
    test_endpoint("GET", "/api/monitor/resources", description="Resource Monitoring")
    
    # 2. Test cache statistics
    print_section("2. Cache Statistics")
    test_endpoint("GET", "/api/cache/stats", description="Cache Statistics")
    
    # 3. Test cache warming
    print_section("3. Cache Warming")
    test_endpoint("POST", "/api/cache/warm", 
                  data={"cache_type": "all", "user_id": USER_ID}, 
                  description="Warm All Caches")
    
    # 4. Test cached endpoints
    print_section("4. Cached Endpoints")
    test_endpoint("GET", f"/api/products/aggregated?user_id={USER_ID}", description="Products Aggregated")
    test_endpoint("GET", f"/api/dashboard/aggregated?user_id={USER_ID}", description="Dashboard Aggregated")
    test_endpoint("GET", f"/api/customers/paginated?user_id={USER_ID}&page=1&per_page=10", description="Customers Paginated")
    
    # 5. Test cache performance
    test_cache_performance()
    
    # 6. Check cache statistics after usage
    print_section("5. Cache Statistics After Usage")
    test_endpoint("GET", "/api/cache/stats", description="Updated Cache Statistics")
    
    # 7. Test cache invalidation
    print_section("6. Cache Invalidation")
    test_endpoint("POST", "/api/cache/clear", 
                  data={"cache_type": "products", "user_id": USER_ID}, 
                  description="Clear Products Cache")
    
    # 8. Test cache optimization
    print_section("7. Cache Optimization")
    test_endpoint("POST", "/api/cache/optimize", 
                  data={"user_id": USER_ID}, 
                  description="Cache Optimization")
    
    # 9. Final cache statistics
    print_section("8. Final Cache Statistics")
    test_endpoint("GET", "/api/cache/stats", description="Final Cache Statistics")
    
    print_section("Test Summary")
    print("✅ Advanced caching features test completed!")
    print("Check the results above to verify all features are working correctly.")
    print("\nNext steps:")
    print("1. Review cache hit rates and performance improvements")
    print("2. Test in browser to verify frontend integration")
    print("3. Monitor Redis memory usage if needed")
    print("4. Proceed to the next optimization step when ready")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        print("Make sure your Flask app is running and Redis is accessible")
