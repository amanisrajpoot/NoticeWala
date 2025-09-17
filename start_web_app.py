#!/usr/bin/env python3
"""
Start the React Native Web app for local testing
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🌐 Starting NoticeWala Web App for Local Testing")
    print("=" * 50)
    
    # Change to mobile directory
    mobile_dir = Path(__file__).parent / "mobile"
    if not mobile_dir.exists():
        print("❌ Mobile directory not found!")
        return
    
    # Install dependencies
    print("📦 Installing Node.js dependencies...")
    success, stdout, stderr = run_command("npm install", cwd=mobile_dir)
    if success:
        print("✅ Dependencies installed")
    else:
        print(f"❌ Failed to install dependencies: {stderr}")
        return
    
    # Start the web app
    print("🚀 Starting React Native Web app...")
    print("📍 App will be available at: http://localhost:3000")
    print("📱 The app will open in your default browser")
    print()
    print("Press Ctrl+C to stop the app")
    print("-" * 50)
    
    # Start the web app
    try:
        subprocess.run(["npm", "run", "web"], cwd=mobile_dir)
    except KeyboardInterrupt:
        print("\n👋 Web app stopped by user")
    except Exception as e:
        print(f"\n❌ Web app error: {e}")

if __name__ == "__main__":
    main()
