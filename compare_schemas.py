#!/usr/bin/env python3
"""
Schema comparison script to identify differences between local SQLite and Railway PostgreSQL
loyalty table schemas.
"""

import sqlite3
import psycopg2
import os
from typing import Dict, List, Tuple

def get_local_schema() -> Dict[str, List[Tuple]]:
    """Get schema from local SQLite database"""
    schema = {}
    try:
        conn = sqlite3.connect('pos_tailor.db')
        cursor = conn.cursor()
        
        # Get loyalty tables
        loyalty_tables = ['loyalty_tiers', 'customer_loyalty', 'loyalty_transactions', 'loyalty_rewards']
        
        for table in loyalty_tables:
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                schema[table] = columns
                print(f"✓ Local {table}: {len(columns)} columns")
            except sqlite3.OperationalError as e:
                print(f"✗ Local {table}: {e}")
                schema[table] = []
        
        conn.close()
        return schema
    except Exception as e:
        print(f"Error connecting to local database: {e}")
        return {}

def get_railway_schema() -> Dict[str, List[Tuple]]:
    """Get schema from Railway PostgreSQL database"""
    schema = {}
    try:
        # Railway PostgreSQL connection
        conn = psycopg2.connect(
            host="hopper.proxy.rlwy.net",
            port="46337",
            database="tajir_pos",
            user="postgres",
            password="SrOOzrgZLlfdlWAfnqTWiWdvClajCDBd"
        )
        cursor = conn.cursor()
        
        # Get loyalty tables
        loyalty_tables = ['loyalty_tiers', 'customer_loyalty', 'loyalty_transactions', 'loyalty_rewards']
        
        for table in loyalty_tables:
            try:
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = %s 
                    ORDER BY ordinal_position
                """, (table,))
                columns = cursor.fetchall()
                schema[table] = columns
                print(f"✓ Railway {table}: {len(columns)} columns")
            except Exception as e:
                print(f"✗ Railway {table}: {e}")
                schema[table] = []
        
        conn.close()
        return schema
    except Exception as e:
        print(f"Error connecting to Railway database: {e}")
        return {}

def compare_schemas(local_schema: Dict, railway_schema: Dict):
    """Compare schemas and show differences"""
    print("\n" + "="*80)
    print("SCHEMA COMPARISON RESULTS")
    print("="*80)
    
    all_tables = set(local_schema.keys()) | set(railway_schema.keys())
    
    for table in all_tables:
        print(f"\n📋 TABLE: {table}")
        print("-" * 60)
        
        local_columns = {col[1]: col for col in local_schema.get(table, [])}  # SQLite: (cid, name, type, notnull, dflt_value, pk)
        railway_columns = {col[0]: col for col in railway_schema.get(table, [])}  # PostgreSQL: (name, type, nullable, default)
        
        all_columns = set(local_columns.keys()) | set(railway_columns.keys())
        
        differences_found = False
        
        for col in sorted(all_columns):
            local_col = local_columns.get(col)
            railway_col = railway_columns.get(col)
            
            if local_col and railway_col:
                # Both exist - check for differences
                local_type = local_col[2]  # SQLite type
                railway_type = railway_col[1]  # PostgreSQL type
                local_nullable = "NULL" if local_col[3] == 0 else "NOT NULL"  # SQLite notnull
                railway_nullable = railway_col[2]  # PostgreSQL nullable
                
                if local_type != railway_type or local_nullable != railway_nullable:
                    print(f"  🔄 {col}:")
                    print(f"     Local:    {local_type} {local_nullable}")
                    print(f"     Railway:  {railway_type} {railway_nullable}")
                    differences_found = True
                else:
                    print(f"  ✓ {col}: {local_type} {local_nullable}")
            elif local_col:
                print(f"  ➕ {col}: {local_col[2]} (Local only)")
                differences_found = True
            elif railway_col:
                print(f"  ➖ {col}: {railway_col[1]} (Railway only)")
                differences_found = True
        
        if not differences_found:
            print("  ✅ Schemas match perfectly!")
        else:
            print(f"  ⚠️  Differences found in {table}")

def main():
    print("🔍 COMPARING LOYALTY SCHEMAS")
    print("="*50)
    
    print("\n📊 Getting local SQLite schema...")
    local_schema = get_local_schema()
    
    print("\n☁️  Getting Railway PostgreSQL schema...")
    railway_schema = get_railway_schema()
    
    if not local_schema or not railway_schema:
        print("\n❌ Failed to retrieve one or both schemas")
        return
    
    compare_schemas(local_schema, railway_schema)
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("This comparison shows the exact differences between your local and Railway databases.")
    print("The dual-schema approach in app.py handles these differences dynamically.")
    print("For a permanent solution, consider migrating Railway to match the local schema.")

if __name__ == "__main__":
    main()

