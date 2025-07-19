#!/usr/bin/env python3
"""
Test script for Plan Manager functionality
"""

from plan_manager import plan_manager
from datetime import datetime, timedelta

def test_plan_manager():
    """Test the plan manager functionality."""
    print("🧪 Testing Plan Manager...")
    
    # Test 1: Trial plan (not expired)
    print("\n1. Testing Trial Plan (Day 1):")
    trial_status = plan_manager.get_user_plan_status('trial', datetime.now().strftime('%Y-%m-%d'))
    print(f"   Plan: {trial_status['plan']}")
    print(f"   Days Remaining: {trial_status['days_remaining']}")
    print(f"   Expired: {trial_status['expired']}")
    print(f"   Enabled Features: {trial_status['enabled_features']}")
    print(f"   Locked Features: {trial_status['locked_features']}")
    
    # Test 2: Trial plan (expired)
    print("\n2. Testing Trial Plan (Day 16 - Expired):")
    expired_date = (datetime.now() - timedelta(days=16)).strftime('%Y-%m-%d')
    expired_trial = plan_manager.get_user_plan_status('trial', expired_date)
    print(f"   Plan: {expired_trial['plan']}")
    print(f"   Days Remaining: {expired_trial['days_remaining']}")
    print(f"   Expired: {expired_trial['expired']}")
    print(f"   Enabled Features: {expired_trial['enabled_features']}")
    print(f"   Locked Features: {expired_trial['locked_features']}")
    
    # Test 3: Basic plan (not expired)
    print("\n3. Testing Basic Plan (Day 1):")
    basic_status = plan_manager.get_user_plan_status('basic', datetime.now().strftime('%Y-%m-%d'))
    print(f"   Plan: {basic_status['plan']}")
    print(f"   Days Remaining: {basic_status['days_remaining']}")
    print(f"   Expired: {basic_status['expired']}")
    print(f"   Enabled Features: {basic_status['enabled_features']}")
    print(f"   Locked Features: {basic_status['locked_features']}")
    
    # Test 4: Basic plan (expired)
    print("\n4. Testing Basic Plan (Day 31 - Expired):")
    expired_basic_date = (datetime.now() - timedelta(days=31)).strftime('%Y-%m-%d')
    expired_basic = plan_manager.get_user_plan_status('basic', expired_basic_date)
    print(f"   Plan: {expired_basic['plan']}")
    print(f"   Days Remaining: {expired_basic['days_remaining']}")
    print(f"   Expired: {expired_basic['expired']}")
    print(f"   Enabled Features: {expired_basic['enabled_features']}")
    print(f"   Locked Features: {expired_basic['locked_features']}")
    
    # Test 5: PRO plan (lifetime)
    print("\n5. Testing PRO Plan (Lifetime):")
    pro_status = plan_manager.get_user_plan_status('pro', datetime.now().strftime('%Y-%m-%d'))
    print(f"   Plan: {pro_status['plan']}")
    print(f"   Days Remaining: {pro_status['days_remaining']}")
    print(f"   Expired: {pro_status['expired']}")
    print(f"   Enabled Features: {pro_status['enabled_features']}")
    print(f"   Locked Features: {pro_status['locked_features']}")
    
    # Test 6: Feature checking
    print("\n6. Testing Feature Access:")
    features_to_test = ['billing', 'dashboard', 'customer_search', 'db_backup_restore']
    for feature in features_to_test:
        trial_enabled = plan_manager.is_feature_enabled('trial', datetime.now().strftime('%Y-%m-%d'), feature)
        basic_enabled = plan_manager.is_feature_enabled('basic', datetime.now().strftime('%Y-%m-%d'), feature)
        pro_enabled = plan_manager.is_feature_enabled('pro', datetime.now().strftime('%Y-%m-%d'), feature)
        print(f"   {feature}: Trial={trial_enabled}, Basic={basic_enabled}, PRO={pro_enabled}")
    
    # Test 7: Upgrade options
    print("\n7. Testing Upgrade Options:")
    trial_upgrades = plan_manager.get_upgrade_options('trial')
    basic_upgrades = plan_manager.get_upgrade_options('basic')
    pro_upgrades = plan_manager.get_upgrade_options('pro')
    print(f"   Trial → {trial_upgrades}")
    print(f"   Basic → {basic_upgrades}")
    print(f"   PRO → {pro_upgrades}")
    
    # Test 8: Expiry warnings
    print("\n8. Testing Expiry Warnings:")
    warning_dates = [5, 3, 1]  # Days before expiry
    for days in warning_dates:
        warning_date = (datetime.now() - timedelta(days=15-days)).strftime('%Y-%m-%d')
        warnings = plan_manager.get_expiry_warnings('trial', warning_date)
        print(f"   Trial {days} days before expiry: {warnings}")
    
    print("\n✅ Plan Manager tests completed!")

if __name__ == "__main__":
    test_plan_manager() 