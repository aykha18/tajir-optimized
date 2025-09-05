#!/usr/bin/env python3
"""
Fix Railway deployment for tajirtech.com
"""

import os
import subprocess
import sys

def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Railway CLI found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Railway CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI not installed")
        return False

def install_railway_cli():
    """Install Railway CLI"""
    print("📦 Installing Railway CLI...")
    try:
        subprocess.run(['npm', 'install', '-g', '@railway/cli'], check=True)
        print("✅ Railway CLI installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Railway CLI")
        return False

def check_railway_login():
    """Check if logged in to Railway"""
    try:
        result = subprocess.run(['railway', 'whoami'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Logged in to Railway as: {result.stdout.strip()}")
            return True
        else:
            print("❌ Not logged in to Railway")
            return False
    except:
        print("❌ Railway CLI error")
        return False

def login_to_railway():
    """Login to Railway"""
    print("🔐 Please login to Railway...")
    try:
        subprocess.run(['railway', 'login'], check=True)
        print("✅ Successfully logged in to Railway")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to login to Railway")
        return False

def check_railway_project():
    """Check if project is linked to Railway"""
    try:
        result = subprocess.run(['railway', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Project is linked to Railway")
            print(f"📊 Status: {result.stdout.strip()}")
            return True
        else:
            print("❌ Project not linked to Railway")
            return False
    except:
        print("❌ Railway CLI error")
        return False

def link_railway_project():
    """Link project to Railway"""
    print("🔗 Linking project to Railway...")
    try:
        subprocess.run(['railway', 'link'], check=True)
        print("✅ Project linked to Railway")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to link project to Railway")
        return False

def set_environment_variables():
    """Set required environment variables"""
    print("🔧 Setting environment variables...")
    
    env_vars = {
        'FLASK_ENV': 'production',
        'PORT': '5000',
        'TESSERACT_ENABLED': 'true',
        'RAILWAY_ENVIRONMENT': 'production',
        'SECRET_KEY': 'your-secret-key-change-in-production-railway-2024'
    }
    
    for key, value in env_vars.items():
        try:
            subprocess.run(['railway', 'variables', 'set', f'{key}={value}'], check=True)
            print(f"✅ Set {key}={value}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to set {key}")

def deploy_to_railway():
    """Deploy to Railway"""
    print("🚀 Deploying to Railway...")
    try:
        subprocess.run(['railway', 'up'], check=True)
        print("✅ Deployment successful!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Deployment failed")
        return False

def check_deployment_logs():
    """Check deployment logs"""
    print("📋 Checking deployment logs...")
    try:
        result = subprocess.run(['railway', 'logs'], capture_output=True, text=True)
        if result.returncode == 0:
            print("📊 Recent logs:")
            print(result.stdout[-1000:])  # Last 1000 characters
        else:
            print("❌ Failed to get logs")
    except:
        print("❌ Error getting logs")

def main():
    print("🔧 Railway Deployment Fix for tajirtech.com")
    print("=" * 50)
    
    # Check Railway CLI
    if not check_railway_cli():
        if not install_railway_cli():
            print("❌ Cannot proceed without Railway CLI")
            return False
    
    # Check login
    if not check_railway_login():
        if not login_to_railway():
            print("❌ Cannot proceed without Railway login")
            return False
    
    # Check project link
    if not check_railway_project():
        if not link_railway_project():
            print("❌ Cannot proceed without project link")
            return False
    
    # Set environment variables
    set_environment_variables()
    
    # Deploy
    if deploy_to_railway():
        print("\n🎉 Deployment completed!")
        print("🌐 Your site should be available at: https://tajirtech.com")
        print("📊 Check logs with: railway logs")
        return True
    else:
        print("\n❌ Deployment failed")
        check_deployment_logs()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
