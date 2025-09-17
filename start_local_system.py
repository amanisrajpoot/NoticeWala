#!/usr/bin/env python3
"""
Complete local system startup script for NoticeWala
This script starts all services needed for local testing
"""

import subprocess
import sys
import time
import threading
import requests
import os
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Run a command and return the result."""
    try:
        if shell:
            result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        else:
            result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
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

def wait_for_service(url, name, timeout=60):
    """Wait for a service to be ready."""
    print(f"⏳ Waiting for {name} to be ready...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_service(url):
            print(f"✅ {name} is ready!")
            return True
        time.sleep(2)
    print(f"❌ {name} failed to start within {timeout} seconds")
    return False

def start_docker_services():
    """Start Docker services."""
    print("🐳 Starting Docker services...")
    
    # Check if Docker is running
    success, _, _ = run_command("docker --version")
    if not success:
        print("❌ Docker is not installed or not running!")
        print("Please install Docker Desktop and start it.")
        return False
    
    # Start infrastructure services
    infra_dir = Path(__file__).parent / "infrastructure"
    success, stdout, stderr = run_command(
        "docker-compose up -d postgres redis elasticsearch", 
        cwd=infra_dir
    )
    
    if success:
        print("✅ Docker services started")
        print("⏳ Waiting for services to be ready...")
        time.sleep(10)  # Give services time to start
        return True
    else:
        print(f"❌ Failed to start Docker services: {stderr}")
        return False

def setup_backend():
    """Set up and start the backend."""
    print("🔧 Setting up backend...")
    
    backend_dir = Path(__file__).parent / "backend"
    
    # Create .env file if it doesn't exist
    env_file = backend_dir / ".env"
    if not env_file.exists():
        env_example = backend_dir / "env.example"
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ Created .env file")
    
    # Install Python dependencies
    print("📦 Installing Python dependencies...")
    success, _, stderr = run_command("pip install -r requirements.txt", cwd=backend_dir)
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    
    # Run migrations
    print("🗄️ Running database migrations...")
    success, _, stderr = run_command("alembic upgrade head", cwd=backend_dir)
    if not success:
        print(f"⚠️ Migration warning (normal if DB not ready): {stderr}")
    
    return True

def start_backend():
    """Start the backend server."""
    print("🌐 Starting backend server...")
    
    backend_dir = Path(__file__).parent / "backend"
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], cwd=backend_dir)
    except KeyboardInterrupt:
        print("\n👋 Backend server stopped")
    except Exception as e:
        print(f"\n❌ Backend server error: {e}")

def setup_mobile_web():
    """Set up the mobile web app."""
    print("📱 Setting up mobile web app...")
    
    mobile_dir = Path(__file__).parent / "mobile"
    
    # Install Node.js dependencies
    print("📦 Installing Node.js dependencies...")
    success, _, stderr = run_command("npm install", cwd=mobile_dir)
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    
    return True

def start_mobile_web():
    """Start the mobile web app."""
    print("🚀 Starting mobile web app...")
    
    mobile_dir = Path(__file__).parent / "mobile"
    
    try:
        subprocess.run(["npm", "run", "web"], cwd=mobile_dir)
    except KeyboardInterrupt:
        print("\n👋 Mobile web app stopped")
    except Exception as e:
        print(f"\n❌ Mobile web app error: {e}")

def main():
    print("🚀 NoticeWala Local System Startup")
    print("=" * 50)
    print()
    
    # Step 1: Start Docker services
    if not start_docker_services():
        print("❌ Failed to start Docker services. Exiting.")
        return
    
    # Step 2: Setup backend
    if not setup_backend():
        print("❌ Failed to setup backend. Exiting.")
        return
    
    # Step 3: Setup mobile web app
    if not setup_mobile_web():
        print("❌ Failed to setup mobile web app. Exiting.")
        return
    
    print()
    print("🎉 Setup completed successfully!")
    print("=" * 50)
    print("📍 Services will be available at:")
    print("   • Backend API: http://localhost:8000")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • Health Check: http://localhost:8000/health")
    print("   • Mobile Web App: http://localhost:3000")
    print()
    print("🚀 Starting services...")
    print("Press Ctrl+C to stop all services")
    print("-" * 50)
    
    try:
        # Start backend and mobile web in separate threads
        backend_thread = threading.Thread(target=start_backend)
        mobile_thread = threading.Thread(target=start_mobile_web)
        
        backend_thread.start()
        time.sleep(5)  # Give backend time to start
        
        mobile_thread.start()
        
        # Wait for threads to complete
        backend_thread.join()
        mobile_thread.join()
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down all services...")
        print("✅ All services stopped")

if __name__ == "__main__":
    main()
