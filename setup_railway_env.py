#!/usr/bin/env python3
"""
Railway Environment Variables Setup Script
Helps set up environment variables for Tajir POS on Railway
"""

import os
import secrets
import subprocess
import sys

def generate_secret_key():
    """Generate a secure 32-byte secret key."""
    return secrets.token_hex(32)

def check_railway_cli():
    """Check if Railway CLI is installed."""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_railway_cli():
    """Install Railway CLI if not present."""
    print("Installing Railway CLI...")
    try:
        subprocess.run(['npm', 'install', '-g', '@railway/cli'], check=True)
        print("SUCCESS: Railway CLI installed")
        return True
    except subprocess.CalledProcessError:
        print("ERROR: Failed to install Railway CLI")
        print("Please install manually: npm install -g @railway/cli")
        return False

def login_railway():
    """Login to Railway."""
    print("Logging into Railway...")
    try:
        subprocess.run(['railway', 'login'], check=True)
        print("SUCCESS: Logged into Railway")
        return True
    except subprocess.CalledProcessError:
        print("ERROR: Failed to login to Railway")
        return False

def link_project():
    """Link to Railway project."""
    print("Linking to Railway project...")
    try:
        subprocess.run(['railway', 'link'], check=True)
        print("SUCCESS: Linked to Railway project")
        return True
    except subprocess.CalledProcessError:
        print("ERROR: Failed to link to Railway project")
        return False

def set_environment_variables():
    """Set all environment variables."""
    secret_key = generate_secret_key()
    
    variables = {
        'SECRET_KEY': secret_key,
        'SESSION_TIMEOUT_HOURS': '8',
        'MAX_LOGIN_ATTEMPTS': '5',
        'RATE_LIMIT_PER_MINUTE': '50',
        'DATABASE_PATH': 'pos_tailor.db',
        'WHATSAPP_NUMBER_1': '+971503904508',
        'WHATSAPP_NUMBER_2': '+971524566488'
    }
    
    print("Setting environment variables...")
    
    for key, value in variables.items():
        try:
            subprocess.run(['railway', 'variables', 'set', f'{key}={value}'], check=True)
            print(f"SUCCESS: Set {key}")
        except subprocess.CalledProcessError:
            print(f"ERROR: Failed to set {key}")
            return False
    
    return True

def verify_variables():
    """Verify that variables are set correctly."""
    print("Verifying environment variables...")
    try:
        result = subprocess.run(['railway', 'variables'], capture_output=True, text=True, check=True)
        print("Current Railway variables:")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError:
        print("ERROR: Failed to verify variables")
        return False

def create_env_file():
    """Create a local .env file for reference."""
    secret_key = generate_secret_key()
    
    env_content = f"""# Tajir POS Environment Configuration
# This file is for reference only - DO NOT commit to version control
# Use Railway variables for production

SECRET_KEY={secret_key}
SESSION_TIMEOUT_HOURS=8
MAX_LOGIN_ATTEMPTS=5
RATE_LIMIT_PER_MINUTE=50
DATABASE_PATH=pos_tailor.db
WHATSAPP_NUMBER_1=+971503904508
WHATSAPP_NUMBER_2=+971524566488
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_content)
    
    print("SUCCESS: Created .env.example file for reference")

def main():
    """Main setup function."""
    print("Railway Environment Variables Setup")
    print("=" * 50)
    
    # Check if Railway CLI is installed
    if not check_railway_cli():
        print("Railway CLI not found. Installing...")
        if not install_railway_cli():
            sys.exit(1)
    
    # Login to Railway
    if not login_railway():
        sys.exit(1)
    
    # Link project
    if not link_project():
        sys.exit(1)
    
    # Set environment variables
    if not set_environment_variables():
        sys.exit(1)
    
    # Verify variables
    verify_variables()
    
    # Create local .env.example file
    create_env_file()
    
    print("\n" + "=" * 50)
    print("SUCCESS: Railway environment variables setup completed!")
    print("\nNEXT STEPS:")
    print("1. Deploy your application: railway up")
    print("2. Test the application in production")
    print("3. Monitor logs: railway logs")
    print("4. Check variables: railway variables")
    
    print("\nIMPORTANT:")
    print("- Keep your SECRET_KEY secure and private")
    print("- Never commit .env files to version control")
    print("- Monitor your application logs for any issues")
    print("- Test all functionality after deployment")

if __name__ == "__main__":
    main()
