#!/usr/bin/env python3
"""
Test Railway PostgreSQL Variables
"""

import os

def test_railway_variables():
    """Test if Railway PostgreSQL variables are available"""
    
    print("Testing Railway PostgreSQL Variables:")
    print("-" * 50)
    
    # Check Railway's PG_ variables
    pg_vars = {
        'PGHOST': os.getenv('PGHOST'),
        'PGPORT': os.getenv('PGPORT'),
        'PGDATABASE': os.getenv('PGDATABASE'),
        'PGUSER': os.getenv('PGUSER'),
        'PGPASSWORD': os.getenv('PGPASSWORD')
    }
    
    print("Railway PG_ variables:")
    for var, value in pg_vars.items():
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: Not set")
    
    print("\nOur custom POSTGRES_ variables:")
    # Check our custom POSTGRES_ variables
    postgres_vars = {
        'POSTGRES_HOST': os.getenv('POSTGRES_HOST'),
        'POSTGRES_PORT': os.getenv('POSTGRES_PORT'),
        'POSTGRES_DB': os.getenv('POSTGRES_DB'),
        'POSTGRES_USER': os.getenv('POSTGRES_USER'),
        'POSTGRES_PASSWORD': os.getenv('POSTGRES_PASSWORD')
    }
    
    for var, value in postgres_vars.items():
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: Not set")
    
    print("\nFinal configuration that will be used:")
    # Show final configuration
    final_config = {
        'host': os.getenv('PGHOST') or os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('PGPORT') or os.getenv('POSTGRES_PORT', '5432'),
        'database': os.getenv('PGDATABASE') or os.getenv('POSTGRES_DB', 'tajir_pos'),
        'user': os.getenv('PGUSER') or os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('PGPASSWORD') or os.getenv('POSTGRES_PASSWORD', 'password')
    }
    
    for key, value in final_config.items():
        if key == 'password':
            print(f"  {key}: {'*' * len(value)}")
        else:
            print(f"  {key}: {value}")

if __name__ == "__main__":
    test_railway_variables()
