#!/usr/bin/env python3
"""
Mobile Testing Script
Starts Flask app with ngrok tunnel for mobile testing
"""

from pyngrok import ngrok
import subprocess
import time
import sys

def start_mobile_test():
    print("🚀 Starting Mobile Test Server...")
    
    # Start Flask app in background
    print("📱 Starting Flask app...")
    flask_process = subprocess.Popen([sys.executable, "app.py"], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
    
    # Wait for Flask to start
    time.sleep(3)
    
    try:
        # Create ngrok tunnel
        print("🌐 Creating ngrok tunnel...")
        public_url = ngrok.connect(5000)
        print(f"✅ Mobile test URL: {public_url}")
        print("\n📱 Mobile Testing Instructions:")
        print("1. Open this URL on your phone: " + public_url)
        print("2. Test the mobile features:")
        print("   - Tap hamburger menu (☰) to open sidebar")
        print("   - Try swipe gestures on table rows")
        print("   - Test voice input (microphone icon)")
        print("   - Try Quick Add Mode button")
        print("\n🔄 Press Ctrl+C to stop the server")
        
        # Keep the tunnel open
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping mobile test server...")
        ngrok.kill()
        flask_process.terminate()
        print("✅ Server stopped")

if __name__ == "__main__":
    start_mobile_test() 