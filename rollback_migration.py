#!/usr/bin/env python3
"""
Rollback script for Railway schema migration
Restores database from backup tables if migration needs to be reverted.
"""

import psycopg2

def rollback_migration():
    """Rollback the migration by restoring from backup tables"""
    try:
        # Connect to Railway
        conn = psycopg2.connect(
            host="hopper.proxy.rlwy.net",
            port="46337",
            database="tajir_pos",
            user="postgres",
            password="SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd"
        )
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("🔄 ROLLING BACK RAILWAY SCHEMA MIGRATION")
        print("=" * 50)
        
        tables = ['loyalty_tiers', 'customer_loyalty', 'loyalty_transactions', 'loyalty_rewards']
        
        for table in tables:
            print(f"\n📋 Rolling back {table}...")
            
            # Check if backup table exists
            cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}_backup')")
            backup_exists = cursor.fetchone()[0]
            
            if not backup_exists:
                print(f"⚠️  Backup table {table}_backup not found, skipping...")
                continue
            
            # Drop current table
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"✓ Dropped current {table}")
            
            # Restore from backup
            cursor.execute(f"ALTER TABLE {table}_backup RENAME TO {table}")
            print(f"✓ Restored {table} from backup")
        
        conn.commit()
        print("\n✅ Rollback completed successfully!")
        print("All tables have been restored from backup.")
        
    except Exception as e:
        print(f"✗ Rollback failed: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("⚠️  WARNING: This will restore your Railway database from backup tables!")
    print("   This will undo all schema changes made by the migration.")
    print("   Make sure you want to proceed before continuing.")
    print("\nDo you want to proceed with rollback? (y/N): ", end="")
    
    # For automated execution, proceed directly
    # response = input().lower().strip()
    # if response != 'y':
    #     print("Rollback cancelled.")
    #     exit()
    
    rollback_migration()

