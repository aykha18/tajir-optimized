from plan_manager import PlanManager
import json

def debug_plan_manager():
    try:
        print("Testing PlanManager...")
        
        # Test config loading
        pm = PlanManager()
        print(f"Config loaded: {pm.config}")
        print(f"Pricing plans: {pm.config.get('pricing_plans', 'NOT FOUND')}")
        
        # Test plan status
        result = pm.get_user_plan_status('trial', '2025-07-28')
        print(f"Plan status result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_plan_manager()