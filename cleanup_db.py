import sqlite3
from datetime import datetime

def cleanup_user_plans():
    try:
        conn = sqlite3.connect('pos_tailor.db')
        
        # Get all user_plans for user_id = 1
        cursor = conn.execute('SELECT * FROM user_plans WHERE user_id = 1 ORDER BY created_at DESC')
        plans = cursor.fetchall()
        
        print(f'Found {len(plans)} plans for user_id = 1')
        
        if len(plans) > 1:
            # Keep only the most recent plan (first one after DESC sort)
            most_recent_plan_id = plans[0][0]  # plan_id is the first column
            
            # Delete all other plans for user_id = 1
            conn.execute('DELETE FROM user_plans WHERE user_id = 1 AND plan_id != ?', (most_recent_plan_id,))
            deleted_count = conn.execute('SELECT changes()').fetchone()[0]
            
            conn.commit()
            print(f'Deleted {deleted_count} duplicate plans. Kept plan_id: {most_recent_plan_id}')
        else:
            print('No duplicates found')
        
        # Verify the cleanup
        cursor = conn.execute('SELECT * FROM user_plans WHERE user_id = 1')
        remaining_plans = cursor.fetchall()
        print(f'Remaining plans for user_id = 1: {len(remaining_plans)}')
        
        conn.close()
        print('Database cleanup completed successfully!')
        
    except Exception as e:
        print(f'Error during cleanup: {e}')

if __name__ == '__main__':
    cleanup_user_plans()