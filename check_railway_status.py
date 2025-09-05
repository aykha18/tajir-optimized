#!/usr/bin/env python3
"""
Check Railway deployment status
"""

import subprocess
import sys

def run_railway_command(command):
    """Run a Railway CLI command"""
    try:
        result = subprocess.run(['railway'] + command, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except FileNotFoundError:
        return False, "", "Railway CLI not found"

def check_railway_status():
    """Check Railway deployment status"""
    print("🔍 Checking Railway Deployment Status")
    print("=" * 40)
    
    # Check Railway CLI
    success, stdout, stderr = run_railway_command(['--version'])
    if not success:
        print("❌ Railway CLI not installed")
        print("💡 Install with: npm install -g @railway/cli")
        return False
    
    print(f"✅ Railway CLI: {stdout.strip()}")
    
    # Check login status
    success, stdout, stderr = run_railway_command(['whoami'])
    if not success:
        print("❌ Not logged in to Railway")
        print("💡 Login with: railway login")
        return False
    
    print(f"✅ Logged in as: {stdout.strip()}")
    
    # Check project status
    success, stdout, stderr = run_railway_command(['status'])
    if not success:
        print("❌ Project not linked to Railway")
        print("💡 Link with: railway link")
        return False
    
    print(f"✅ Project status: {stdout.strip()}")
    
    # Check environment variables
    success, stdout, stderr = run_railway_command(['variables'])
    if success:
        print("✅ Environment variables:")
        print(stdout)
    else:
        print("❌ Could not get environment variables")
    
    # Check recent logs
    success, stdout, stderr = run_railway_command(['logs', '--tail', '20'])
    if success:
        print("📋 Recent logs:")
        print(stdout)
    else:
        print("❌ Could not get logs")
    
    return True

if __name__ == "__main__":
    check_railway_status()
