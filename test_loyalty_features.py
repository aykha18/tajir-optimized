#!/usr/bin/env python3
"""
Comprehensive Loyalty Features Testing Script
Tests all loyalty program features including:
- Configuration management
- Customer enrollment
- Points earning and redemption
- Tier management
- Rewards system
- Analytics and reporting
"""

import requests
import json
import time
import random
import string
from datetime import datetime, timedelta

class LoyaltyTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        return success
    
    def login_test_user(self):
        """Login as test user"""
        try:
            # First, try to get current user
            response = self.session.get(f"{self.base_url}/api/user")
            if response.status_code == 200:
                user_data = response.json()
                if user_data.get('user_id'):
                    print(f"✅ Already logged in as user {user_data['user_id']}")
                    return True
            
            # If not logged in, try to login
            login_data = {
                'method': 'email',
                'email': 'demo@tajir.com',
                'password': 'aykha123'
            }
            response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
            if response.status_code == 200:
                print("✅ Login successful")
                return True
            else:
                print("❌ Login failed")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_loyalty_configuration(self):
        """Test loyalty program configuration"""
        print("\n🎯 Testing Loyalty Configuration")
        print("=" * 40)
        
        # Test 1: Get current configuration
        try:
            response = self.session.get(f"{self.base_url}/api/loyalty/config")
            if response.status_code == 200:
                config = response.json()
                self.log_test("Get Loyalty Config", True, f"Program: {config.get('program_name', 'N/A')}")
            else:
                self.log_test("Get Loyalty Config", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Loyalty Config", False, str(e))
            return False
        
        # Test 2: Update configuration
        try:
            new_config = {
                'program_name': 'Test Loyalty Program',
                'is_active': True,
                'points_per_aed': 2.0,
                'aed_per_point': 0.02,
                'min_points_redemption': 50,
                'max_points_redemption_percent': 25,
                'birthday_bonus_points': 100,
                'anniversary_bonus_points': 200,
                'referral_bonus_points': 300
            }
            response = self.session.put(f"{self.base_url}/api/loyalty/config", 
                                      json=new_config)
            if response.status_code == 200:
                self.log_test("Update Loyalty Config", True, "Configuration updated")
            else:
                self.log_test("Update Loyalty Config", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Update Loyalty Config", False, str(e))
        
        return True
    
    def test_loyalty_tiers(self):
        """Test loyalty tiers management"""
        print("\n🎯 Testing Loyalty Tiers")
        print("=" * 40)
        
        # Test 1: Get existing tiers
        try:
            response = self.session.get(f"{self.base_url}/api/loyalty/tiers")
            if response.status_code == 200:
                tiers = response.json()
                self.log_test("Get Loyalty Tiers", True, f"Found {len(tiers)} tiers")
            else:
                self.log_test("Get Loyalty Tiers", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Loyalty Tiers", False, str(e))
            return False
        
        # Test 2: Create new tier (only if it doesn't exist)
        try:
            # Check if Platinum tier already exists
            response_data = response.json() if response.status_code == 200 else {}
            existing_tiers = response_data.get('tiers', []) if isinstance(response_data, dict) else []
            platinum_exists = any(tier.get('tier_level') == 'Platinum' for tier in existing_tiers)
            
            if not platinum_exists:
                new_tier = {
                    'tier_name': 'Premium Platinum',
                    'tier_level': 'Platinum',
                    'points_threshold': 20000,
                    'discount_percent': 20.0,
                    'bonus_points_multiplier': 2.5,
                    'free_delivery': True,
                    'priority_service': True,
                    'exclusive_offers': True,
                    'color_code': '#B9F2FF'
                }
                response = self.session.post(f"{self.base_url}/api/loyalty/tiers", 
                                           json=new_tier)
                if response.status_code == 200:
                    self.log_test("Create New Tier", True, "Platinum tier created")
                else:
                    self.log_test("Create New Tier", False, f"Status: {response.status_code}")
            else:
                self.log_test("Create New Tier", True, "Platinum tier already exists")
        except Exception as e:
            self.log_test("Create New Tier", False, str(e))
        
        return True
    
    def test_customer_management(self):
        """Test customer loyalty management"""
        print("\n🎯 Testing Customer Management")
        print("=" * 40)
        
        # Test 1: Get loyalty customers
        try:
            response = self.session.get(f"{self.base_url}/api/loyalty/customers")
            if response.status_code == 200:
                customers = response.json()
                self.log_test("Get Loyalty Customers", True, f"Found {len(customers)} customers")
            else:
                self.log_test("Get Loyalty Customers", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Loyalty Customers", False, str(e))
            return False
        
        # Test 2: Create test customer first (or use existing)
        try:
            customer_data = {
                'name': 'Test Loyalty Customer',
                'phone': f'{random.randint(500000000, 599999999)}',
                'email': f'test.loyalty.{random.randint(1000, 9999)}@example.com',
                'address': 'Test Address, Dubai'
            }
            response = self.session.post(f"{self.base_url}/api/customers", json=customer_data)
            if response.status_code == 200:
                customer = response.json()
                customer_id = customer.get('id') or customer.get('customer_id')
                self.log_test("Create Test Customer", True, f"Customer ID: {customer_id}")
            elif response.status_code == 400 and "already exists" in response.text:
                # Try to find existing customer with similar name
                search_response = self.session.get(f"{self.base_url}/api/customers?search=Test Loyalty")
                if search_response.status_code == 200:
                    customers = search_response.json()
                    if customers:
                        customer_id = customers[0]['customer_id']
                        self.log_test("Create Test Customer", True, f"Using existing customer ID: {customer_id}")
                    else:
                        self.log_test("Create Test Customer", False, "Could not find existing test customer")
                        return False
                else:
                    self.log_test("Create Test Customer", False, f"Status: {response.status_code}")
                    return False
            else:
                self.log_test("Create Test Customer", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Create Test Customer", False, str(e))
            return False
        
        # Test 3: Enroll customer in loyalty program
        try:
            enrollment_data = {
                'birthday': '1990-01-15',
                'anniversary_date': '2020-06-20'
            }
            response = self.session.post(f"{self.base_url}/api/loyalty/customers/{customer_id}/enroll", 
                                       json=enrollment_data)
            if response.status_code == 200:
                result = response.json()
                self.log_test("Enroll Customer", True, f"Referral code: {result.get('referral_code', 'N/A')}")
            else:
                self.log_test("Enroll Customer", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Enroll Customer", False, str(e))
        
        # Test 4: Get customer loyalty details
        try:
            response = self.session.get(f"{self.base_url}/api/loyalty/customers/{customer_id}")
            if response.status_code == 200:
                loyalty_data = response.json()
                self.log_test("Get Customer Loyalty", True, 
                            f"Points: {loyalty_data.get('available_points', 0)}, "
                            f"Tier: {loyalty_data.get('tier_level', 'N/A')}")
            else:
                self.log_test("Get Customer Loyalty", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get Customer Loyalty", False, str(e))
        
        return customer_id
    
    def test_points_earning(self, customer_id):
        """Test points earning through purchases"""
        print("\n🎯 Testing Points Earning")
        print("=" * 40)
        
        # Test 1: Create a bill to earn points
        try:
            # First, get some products
            response = self.session.get(f"{self.base_url}/api/products")
            if response.status_code == 200:
                products = response.json()
                if products:
                    product = products[0]
                    bill_data = {
                        'customer_id': customer_id,
                        'items': [
                            {
                                'product_id': product['product_id'],
                                'quantity': 2,
                                'unit_price': 50.0,
                                'discount': 0.0
                            }
                        ],
                        'payment_mode': 'cash',
                        'total_amount': 100.0
                    }
                    
                    response = self.session.post(f"{self.base_url}/api/bills", json=bill_data)
                    if response.status_code == 200:
                        bill = response.json()
                        bill_id = bill['bill_id']
                        points_earned = bill.get('loyalty_points_earned', 0)
                        self.log_test("Create Bill with Points", True, 
                                    f"Bill ID: {bill_id}, Points earned: {points_earned}")
                    else:
                        self.log_test("Create Bill with Points", False, f"Status: {response.status_code}")
                else:
                    self.log_test("Create Bill with Points", False, "No products available")
            else:
                self.log_test("Create Bill with Points", False, "Could not fetch products")
        except Exception as e:
            self.log_test("Create Bill with Points", False, str(e))
        
        # Test 2: Check loyalty transactions
        try:
            response = self.session.get(f"{self.base_url}/api/loyalty/transactions")
            if response.status_code == 200:
                transactions = response.json()
                self.log_test("Get Loyalty Transactions", True, f"Found {len(transactions)} transactions")
            else:
                self.log_test("Get Loyalty Transactions", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get Loyalty Transactions", False, str(e))
        
        return True
    
    def test_rewards_system(self):
        """Test rewards management"""
        print("\n🎯 Testing Rewards System")
        print("=" * 40)
        
        # Test 1: Get existing rewards
        try:
            response = self.session.get(f"{self.base_url}/api/loyalty/rewards")
            if response.status_code == 200:
                rewards = response.json()
                self.log_test("Get Loyalty Rewards", True, f"Found {len(rewards)} rewards")
            else:
                self.log_test("Get Loyalty Rewards", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get Loyalty Rewards", False, str(e))
        
        # Test 2: Create new reward
        try:
            new_reward = {
                'reward_name': 'Test Discount Reward',
                'reward_type': 'discount',
                'points_cost': 500,
                'discount_percent': 10.0,
                'description': '10% discount on next purchase'
            }
            response = self.session.post(f"{self.base_url}/api/loyalty/rewards", 
                                       json=new_reward)
            if response.status_code == 200:
                self.log_test("Create New Reward", True, "Test reward created")
            else:
                self.log_test("Create New Reward", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Create New Reward", False, str(e))
        
        return True
    
    def test_personalized_offers(self):
        """Test personalized offers"""
        print("\n🎯 Testing Personalized Offers")
        print("=" * 40)
        
        try:
            response = self.session.get(f"{self.base_url}/api/loyalty/offers")
            if response.status_code == 200:
                offers = response.json()
                self.log_test("Get Personalized Offers", True, f"Found {len(offers)} offers")
            else:
                self.log_test("Get Personalized Offers", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get Personalized Offers", False, str(e))
        
        return True
    
    def test_analytics(self):
        """Test loyalty analytics"""
        print("\n🎯 Testing Loyalty Analytics")
        print("=" * 40)
        
        try:
            response = self.session.get(f"{self.base_url}/api/loyalty/analytics")
            if response.status_code == 200:
                analytics = response.json()
                self.log_test("Get Loyalty Analytics", True, 
                            f"Total customers: {analytics.get('total_customers', 0)}, "
                            f"Total points: {analytics.get('total_points', 0)}")
            else:
                self.log_test("Get Loyalty Analytics", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get Loyalty Analytics", False, str(e))
        
        return True
    
    def test_referral_system(self, customer_id):
        """Test referral system"""
        print("\n🎯 Testing Referral System")
        print("=" * 40)
        
        # Test 1: Get customer's referral code
        try:
            response = self.session.get(f"{self.base_url}/api/loyalty/customers/{customer_id}")
            if response.status_code == 200:
                loyalty_data = response.json()
                referral_code = loyalty_data.get('referral_code')
                if referral_code:
                    self.log_test("Get Referral Code", True, f"Code: {referral_code}")
                else:
                    self.log_test("Get Referral Code", False, "No referral code found")
            else:
                self.log_test("Get Referral Code", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Get Referral Code", False, str(e))
        
        return True
    
    def run_all_tests(self):
        """Run all loyalty feature tests"""
        print("🚀 Starting Comprehensive Loyalty Features Testing")
        print("=" * 60)
        
        # Login first
        if not self.login_test_user():
            print("❌ Cannot proceed without login")
            return False
        
        # Run all test suites
        self.test_loyalty_configuration()
        self.test_loyalty_tiers()
        customer_id = self.test_customer_management()
        if customer_id:
            self.test_points_earning(customer_id)
            self.test_referral_system(customer_id)
        self.test_rewards_system()
        self.test_personalized_offers()
        self.test_analytics()
        
        # Print summary
        self.print_test_summary()
        
        return True
    
    def print_test_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 LOYALTY FEATURES TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        # Save results to file
        with open('loyalty_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Detailed results saved to: loyalty_test_results.json")

def main():
    """Main function"""
    import sys
    
    # Get base URL from command line or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    print(f"🎯 Testing Loyalty Features at: {base_url}")
    
    tester = LoyaltyTester(base_url)
    tester.run_all_tests()

if __name__ == "__main__":
    main()
