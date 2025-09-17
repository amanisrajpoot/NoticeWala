#!/usr/bin/env python3
"""
Simple backend startup script for local testing
"""

import subprocess
import sys
import time
import requests
import os
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_service(url, timeout=5):
    """Check if a service is running."""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def main():
    print("🚀 Starting NoticeWala Backend for Local Testing")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return
    
    # Check if .env file exists
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("📝 Creating .env file from template...")
        env_example = backend_dir / "env.example"
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ .env file created")
        else:
            print("❌ env.example not found!")
            return
    
    # Install dependencies
    print("📦 Installing Python dependencies...")
    success, stdout, stderr = run_command("pip install -r requirements.txt", cwd=backend_dir)
    if success:
        print("✅ Dependencies installed")
    else:
        print(f"❌ Failed to install dependencies: {stderr}")
        return
    
    # Run database migrations
    print("🗄️ Running database migrations...")
    success, stdout, stderr = run_command("alembic upgrade head", cwd=backend_dir)
    if success:
        print("✅ Database migrations completed")
    else:
        print(f"⚠️ Migration warning (this is normal if database is not running): {stderr}")
    
    # Start the server
    print("🌐 Starting FastAPI server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("❤️ Health Check: http://localhost:8000/health")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Start uvicorn server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], cwd=backend_dir)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

if __name__ == "__main__":
    main()
