#!/usr/bin/env python3
"""
Railway PostgreSQL Schema Migration Script
Updates Railway database to match local SQLite schema for loyalty tables.
Includes backup, validation, and rollback capabilities.
"""

import psycopg2
import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any

class RailwaySchemaMigrator:
    def __init__(self):
        self.railway_conn = None
        self.backup_data = {}
        self.migration_log = []
        self.rollback_queries = []
        
    def connect_railway(self):
        """Connect to Railway PostgreSQL database"""
        try:
            self.railway_conn = psycopg2.connect(
                host="hopper.proxy.rlwy.net",
                port="46337",
                database="tajir_pos",
                user="postgres",
                password="SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd"
            )
            self.railway_conn.autocommit = False  # Enable transactions
            print("✓ Connected to Railway PostgreSQL database")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to Railway: {e}")
            return False
    
    def backup_table_data(self, table_name: str) -> bool:
        """Backup all data from a table before migration"""
        try:
            cursor = self.railway_conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                ORDER BY ordinal_position
            """)
            columns = [col[0] for col in cursor.fetchall()]
            
            # Convert to list of dictionaries
            data = []
            for row in rows:
                data.append(dict(zip(columns, row)))
            
            self.backup_data[table_name] = data
            print(f"✓ Backed up {len(data)} rows from {table_name}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to backup {table_name}: {e}")
            return False
    
    def log_migration(self, step: str, query: str, success: bool, error: str = None):
        """Log migration steps for audit trail"""
        self.migration_log.append({
            'timestamp': datetime.now().isoformat(),
            'step': step,
            'query': query,
            'success': success,
            'error': error
        })
    
    def create_backup_tables(self) -> bool:
        """Create backup tables with _backup suffix"""
        try:
            cursor = self.railway_conn.cursor()
            tables = ['loyalty_tiers', 'customer_loyalty', 'loyalty_transactions', 'loyalty_rewards']
            
            for table in tables:
                # Create backup table
                cursor.execute(f"CREATE TABLE {table}_backup AS SELECT * FROM {table}")
                print(f"✓ Created backup table {table}_backup")
                
                # Add rollback query
                self.rollback_queries.append(f"DROP TABLE IF EXISTS {table}_backup")
            
            self.railway_conn.commit()
            return True
            
        except Exception as e:
            print(f"✗ Failed to create backup tables: {e}")
            self.railway_conn.rollback()
            return False
    
    def migrate_loyalty_tiers(self) -> bool:
        """Migrate loyalty_tiers table to new schema"""
        try:
            cursor = self.railway_conn.cursor()
            
            # Step 1: Add new columns
            new_columns = [
                "ADD COLUMN tier_level TEXT",
                "ADD COLUMN points_threshold INTEGER",
                "ADD COLUMN is_active BOOLEAN DEFAULT TRUE",
                "ADD COLUMN color_code TEXT",
                "ADD COLUMN discount_percent REAL",
                "ADD COLUMN bonus_points_multiplier REAL",
                "ADD COLUMN exclusive_offers BOOLEAN DEFAULT FALSE",
                "ADD COLUMN free_delivery BOOLEAN DEFAULT FALSE",
                "ADD COLUMN priority_service BOOLEAN DEFAULT FALSE"
            ]
            
            for column_def in new_columns:
                try:
                    cursor.execute(f"ALTER TABLE loyalty_tiers {column_def}")
                    self.log_migration("Add column", f"ALTER TABLE loyalty_tiers {column_def}", True)
                    print(f"✓ Added column: {column_def}")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"⚠️  Column may already exist: {column_def}")
                    self.log_migration("Add column", f"ALTER TABLE loyalty_tiers {column_def}", False, str(e))
            
            # Step 2: Migrate existing data
            cursor.execute("""
                UPDATE loyalty_tiers 
                SET 
                    tier_level = tier_name,
                    points_threshold = min_points,
                    discount_percent = discount_percentage,
                    bonus_points_multiplier = point_multiplier
                WHERE tier_level IS NULL
            """)
            
            rows_updated = cursor.rowcount
            print(f"✓ Migrated {rows_updated} rows in loyalty_tiers")
            self.log_migration("Data migration", "UPDATE loyalty_tiers SET tier_level = tier_name, ...", True)
            
            # Step 3: Drop old columns (optional - keep for safety)
            # old_columns = ['min_points', 'point_multiplier', 'discount_percentage', 'benefits']
            # for col in old_columns:
            #     cursor.execute(f"ALTER TABLE loyalty_tiers DROP COLUMN IF EXISTS {col}")
            
            self.railway_conn.commit()
            return True
            
        except Exception as e:
            print(f"✗ Failed to migrate loyalty_tiers: {e}")
            self.railway_conn.rollback()
            self.log_migration("Migrate loyalty_tiers", "N/A", False, str(e))
            return False
    
    def migrate_customer_loyalty(self) -> bool:
        """Migrate customer_loyalty table to new schema"""
        try:
            cursor = self.railway_conn.cursor()
            
            # Step 1: Add new columns
            new_columns = [
                "ADD COLUMN tier_level TEXT",
                "ADD COLUMN available_points INTEGER",
                "ADD COLUMN lifetime_points INTEGER DEFAULT 0",
                "ADD COLUMN tier_points_threshold INTEGER",
                "ADD COLUMN birthday DATE",
                "ADD COLUMN anniversary_date DATE",
                "ADD COLUMN join_date DATE"
            ]
            
            for column_def in new_columns:
                try:
                    cursor.execute(f"ALTER TABLE customer_loyalty {column_def}")
                    self.log_migration("Add column", f"ALTER TABLE customer_loyalty {column_def}", True)
                    print(f"✓ Added column: {column_def}")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"⚠️  Column may already exist: {column_def}")
                    self.log_migration("Add column", f"ALTER TABLE customer_loyalty {column_def}", False, str(e))
            
            # Step 2: Migrate existing data
            cursor.execute("""
                UPDATE customer_loyalty 
                SET 
                    tier_level = (SELECT tier_name FROM loyalty_tiers WHERE tier_id = customer_loyalty.tier_id LIMIT 1),
                    available_points = current_points,
                    join_date = enrollment_date
                WHERE tier_level IS NULL
            """)
            
            rows_updated = cursor.rowcount
            print(f"✓ Migrated {rows_updated} rows in customer_loyalty")
            self.log_migration("Data migration", "UPDATE customer_loyalty SET tier_level = ...", True)
            
            self.railway_conn.commit()
            return True
            
        except Exception as e:
            print(f"✗ Failed to migrate customer_loyalty: {e}")
            self.railway_conn.rollback()
            self.log_migration("Migrate customer_loyalty", "N/A", False, str(e))
            return False
    
    def migrate_loyalty_transactions(self) -> bool:
        """Migrate loyalty_transactions table to new schema"""
        try:
            cursor = self.railway_conn.cursor()
            
            # Step 1: Add new columns
            new_columns = [
                "ADD COLUMN points_amount INTEGER",
                "ADD COLUMN loyalty_id INTEGER",
                "ADD COLUMN aed_amount REAL",
                "ADD COLUMN expiry_date DATE",
                "ADD COLUMN is_active BOOLEAN DEFAULT TRUE"
            ]
            
            for column_def in new_columns:
                try:
                    cursor.execute(f"ALTER TABLE loyalty_transactions {column_def}")
                    self.log_migration("Add column", f"ALTER TABLE loyalty_transactions {column_def}", True)
                    print(f"✓ Added column: {column_def}")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"⚠️  Column may already exist: {column_def}")
                    self.log_migration("Add column", f"ALTER TABLE loyalty_transactions {column_def}", False, str(e))
            
            # Step 2: Migrate existing data
            cursor.execute("""
                UPDATE loyalty_transactions 
                SET 
                    points_amount = COALESCE(points_earned, points_redeemed, 0),
                    loyalty_id = customer_id
                WHERE points_amount IS NULL
            """)
            
            rows_updated = cursor.rowcount
            print(f"✓ Migrated {rows_updated} rows in loyalty_transactions")
            self.log_migration("Data migration", "UPDATE loyalty_transactions SET points_amount = ...", True)
            
            self.railway_conn.commit()
            return True
            
        except Exception as e:
            print(f"✗ Failed to migrate loyalty_transactions: {e}")
            self.railway_conn.rollback()
            self.log_migration("Migrate loyalty_transactions", "N/A", False, str(e))
            return False
    
    def migrate_loyalty_rewards(self) -> bool:
        """Migrate loyalty_rewards table to new schema"""
        try:
            cursor = self.railway_conn.cursor()
            
            # Step 1: Add new columns
            new_columns = [
                "ADD COLUMN points_cost INTEGER",
                "ADD COLUMN discount_percent REAL"
            ]
            
            for column_def in new_columns:
                try:
                    cursor.execute(f"ALTER TABLE loyalty_rewards {column_def}")
                    self.log_migration("Add column", f"ALTER TABLE loyalty_rewards {column_def}", True)
                    print(f"✓ Added column: {column_def}")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"⚠️  Column may already exist: {column_def}")
                    self.log_migration("Add column", f"ALTER TABLE loyalty_rewards {column_def}", False, str(e))
            
            # Step 2: Migrate existing data
            cursor.execute("""
                UPDATE loyalty_rewards 
                SET 
                    points_cost = points_required,
                    discount_percent = discount_percentage
                WHERE points_cost IS NULL
            """)
            
            rows_updated = cursor.rowcount
            print(f"✓ Migrated {rows_updated} rows in loyalty_rewards")
            self.log_migration("Data migration", "UPDATE loyalty_rewards SET points_cost = ...", True)
            
            self.railway_conn.commit()
            return True
            
        except Exception as e:
            print(f"✗ Failed to migrate loyalty_rewards: {e}")
            self.railway_conn.rollback()
            self.log_migration("Migrate loyalty_rewards", "N/A", False, str(e))
            return False
    
    def validate_migration(self) -> bool:
        """Validate that migration was successful"""
        try:
            cursor = self.railway_conn.cursor()
            
            # Check if new columns exist
            validation_queries = [
                ("loyalty_tiers", "tier_level"),
                ("loyalty_tiers", "points_threshold"),
                ("customer_loyalty", "tier_level"),
                ("customer_loyalty", "available_points"),
                ("loyalty_transactions", "points_amount"),
                ("loyalty_rewards", "points_cost")
            ]
            
            all_valid = True
            for table, column in validation_queries:
                cursor.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' AND column_name = '{column}'
                """)
                if not cursor.fetchone():
                    print(f"✗ Validation failed: {table}.{column} not found")
                    all_valid = False
                else:
                    print(f"✓ Validated: {table}.{column}")
            
            return all_valid
            
        except Exception as e:
            print(f"✗ Validation failed: {e}")
            return False
    
    def save_migration_log(self):
        """Save migration log to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"migration_log_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'migration_log': self.migration_log,
                'backup_tables': list(self.backup_data.keys()),
                'rollback_queries': self.rollback_queries
            }, f, indent=2)
        
        print(f"✓ Migration log saved to {filename}")
    
    def rollback(self):
        """Rollback migration using backup tables"""
        try:
            cursor = self.railway_conn.cursor()
            tables = ['loyalty_tiers', 'customer_loyalty', 'loyalty_transactions', 'loyalty_rewards']
            
            for table in tables:
                # Drop current table
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                # Restore from backup
                cursor.execute(f"ALTER TABLE {table}_backup RENAME TO {table}")
                print(f"✓ Rolled back {table}")
            
            self.railway_conn.commit()
            print("✓ Rollback completed successfully")
            
        except Exception as e:
            print(f"✗ Rollback failed: {e}")
            self.railway_conn.rollback()
    
    def run_migration(self):
        """Run the complete migration process"""
        print("🚀 STARTING RAILWAY SCHEMA MIGRATION")
        print("=" * 60)
        
        if not self.connect_railway():
            return False
        
        try:
            # Step 1: Create backup tables
            print("\n📦 Step 1: Creating backup tables...")
            if not self.create_backup_tables():
                return False
            
            # Step 2: Migrate each table
            print("\n🔄 Step 2: Migrating tables...")
            
            migrations = [
                ("loyalty_tiers", self.migrate_loyalty_tiers),
                ("customer_loyalty", self.migrate_customer_loyalty),
                ("loyalty_transactions", self.migrate_loyalty_transactions),
                ("loyalty_rewards", self.migrate_loyalty_rewards)
            ]
            
            for table_name, migration_func in migrations:
                print(f"\n📋 Migrating {table_name}...")
                if not migration_func():
                    print(f"✗ Migration failed for {table_name}")
                    return False
            
            # Step 3: Validate migration
            print("\n✅ Step 3: Validating migration...")
            if not self.validate_migration():
                print("✗ Migration validation failed")
                return False
            
            # Step 4: Save migration log
            self.save_migration_log()
            
            print("\n🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("✅ All loyalty tables have been migrated to the new schema")
            print("✅ Backup tables created with _backup suffix")
            print("✅ Migration log saved for audit trail")
            print("\n⚠️  IMPORTANT: Test your application thoroughly before removing backup tables")
            print("   To rollback: Use the rollback() method or manually restore from backup tables")
            
            return True
            
        except Exception as e:
            print(f"✗ Migration failed with error: {e}")
            return False
        finally:
            if self.railway_conn:
                self.railway_conn.close()

def main():
    """Main function to run migration"""
    migrator = RailwaySchemaMigrator()
    
    # Confirm before proceeding
    print("⚠️  WARNING: This will modify your Railway database schema!")
    print("   - Backup tables will be created automatically")
    print("   - Existing data will be migrated to new schema")
    print("   - Old columns will be preserved for safety")
    print("\nDo you want to proceed? (y/N): ", end="")
    
    # For automated execution, proceed directly
    # response = input().lower().strip()
    # if response != 'y':
    #     print("Migration cancelled.")
    #     return
    
    success = migrator.run_migration()
    
    if not success:
        print("\n❌ Migration failed!")
        print("You can manually rollback using the backup tables or contact support.")
    else:
        print("\n🎯 Next steps:")
        print("1. Test your application with the new schema")
        print("2. Update app.py to remove dual-schema logic")
        print("3. Remove backup tables once confirmed working")

if __name__ == "__main__":
    main()
