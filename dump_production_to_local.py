#!/usr/bin/env python3
"""
Script to dump production database data to local database using Docker
Usage: python dump_production_to_local.py [--yes]
"""

import os
import sys
import subprocess
from urllib.parse import urlparse
from dotenv import load_dotenv

def run_docker_command(cmd, description):
    """Run a Docker command and return the result"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ERROR: {description} failed")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"ERROR: Failed to run {description}: {e}")
        return False

def main():
    # Load environment variables
    load_dotenv()

    # Check for --yes flag
    skip_confirmation = '--yes' in sys.argv

    if not skip_confirmation:
        # Confirmation
        response = input("This will overwrite the local database with production data. Continue? (y/n): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Operation cancelled.")
            sys.exit(0)
    else:
        print("Skipping confirmation due to --yes flag.")

    # Get production database URL
    prod_url = os.getenv('DATABASE_URL')
    if not prod_url:
        print("ERROR: DATABASE_URL not found in environment variables.")
        print("Please set DATABASE_URL in your .env file with the production database URL.")
        sys.exit(1)

    # Parse production URL
    try:
        parsed = urlparse(prod_url)
        prod_host = parsed.hostname
        prod_port = parsed.port or 5432
        prod_db = parsed.path.lstrip('/')
        prod_user = parsed.username
        prod_password = parsed.password

        if not all([prod_host, prod_db, prod_user, prod_password]):
            raise ValueError("Invalid DATABASE_URL format")
    except Exception as e:
        print(f"ERROR: Failed to parse DATABASE_URL: {e}")
        sys.exit(1)

    # Get local database config
    local_host_env = os.getenv('POSTGRES_HOST', 'localhost')
    local_port = int(os.getenv('POSTGRES_PORT', '5432'))
    local_db = os.getenv('POSTGRES_DB', 'tajir_pos')
    local_user = os.getenv('POSTGRES_USER', 'postgres')
    local_password = os.getenv('POSTGRES_PASSWORD')

    # For Docker containers, use host.docker.internal instead of localhost
    local_host = 'host.docker.internal' if local_host_env == 'localhost' else local_host_env

    if not local_password:
        print("ERROR: POSTGRES_PASSWORD not found in environment variables.")
        sys.exit(1)

    print("Production DB:", prod_host, prod_port, prod_db, prod_user)
    print("Local DB:", local_host, local_port, local_db, local_user)

    # Check if local PostgreSQL is running (use localhost for host check)
    print("\nChecking local PostgreSQL connection...")
    test_host = 'localhost' if local_host == 'host.docker.internal' else local_host
    try:
        import psycopg2
        test_conn = psycopg2.connect(
            host=test_host,
            port=local_port,
            database=local_db,
            user=local_user,
            password=local_password,
            connect_timeout=5
        )
        test_conn.close()
        print("Local PostgreSQL is accessible.")
    except Exception as e:
        print(f"ERROR: Cannot connect to local PostgreSQL: {e}")
        print("Please ensure your local PostgreSQL server is running and accessible.")
        print(f"Host: {test_host}:{local_port}, Database: {local_db}, User: {local_user}")
        sys.exit(1)

    # Create temporary container names
    container_name = "tajir_dump_temp"

    try:
        # Step 1: Dump production database schema and data
        print("\n=== STEP 1: Dumping production database ===")

        # Create a temporary container to dump from production
        dump_cmd = [
            "docker", "run", "--rm", "--name", container_name,
            "-e", f"PGPASSWORD={prod_password}",
            "postgres:17",
            "pg_dump",
            f"--host={prod_host}",
            f"--port={prod_port}",
            f"--username={prod_user}",
            f"--dbname={prod_db}",
            "--no-owner", "--no-privileges", "--clean", "--if-exists", "--schema=public"
        ]

        print("Running: docker pg_dump from production...")
        with open('production_dump.sql', 'w') as f:
            result = subprocess.run(dump_cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                print(f"ERROR: Failed to dump production data: {result.stderr}")
                sys.exit(1)

        print("Production database dumped successfully!")

        # Step 2: Restore to local database
        print("\n=== STEP 2: Restoring to local database ===")

        # First, drop all existing tables and recreate schema
        print("Dropping existing schema...")
        drop_cmd = [
            "docker", "run", "--rm",
            "-e", f"PGPASSWORD={local_password}",
            "postgres:17", "psql",
            f"--host={local_host}",
            f"--port={local_port}",
            f"--username={local_user}",
            f"--dbname={local_db}",
            "-c", "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
        ]

        result = subprocess.run(drop_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ERROR: Failed to drop schema: {result.stderr}")
            sys.exit(1)

        # Recreate the schema
        print("Recreating local schema...")
        schema_cmd = [
            "docker", "run", "--rm",
            "-v", f"{os.getcwd()}:/data",
            "-e", f"PGPASSWORD={local_password}",
            "postgres:17", "psql",
            f"--host={local_host}",
            f"--port={local_port}",
            f"--username={local_user}",
            f"--dbname={local_db}",
            "-f", "/data/database_schema_postgresql.sql"
        ]

        result = subprocess.run(schema_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ERROR: Failed to recreate schema: {result.stderr}")
            sys.exit(1)

        # Restore the production data
        print("Restoring production data...")
        restore_cmd = [
            "docker", "run", "--rm",
            "-v", f"{os.getcwd()}:/data",
            "-e", f"PGPASSWORD={local_password}",
            "postgres:17", "psql",
            f"--host={local_host}",
            f"--port={local_port}",
            f"--username={local_user}",
            f"--dbname={local_db}",
            "-f", "/data/production_dump.sql"
        ]

        result = subprocess.run(restore_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ERROR: Failed to restore data: {result.stderr}")
            sys.exit(1)

        print("SUCCESS: Production data restored to local database!")

        # Clean up
        if os.path.exists('production_dump.sql'):
            os.remove('production_dump.sql')
            print("Cleanup completed!")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()