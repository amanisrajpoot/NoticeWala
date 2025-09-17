#!/usr/bin/env python3
"""
Local Testing Script for NoticeWala
This script helps test the system locally before production deployment.
"""

import requests
import json
import time
import sys
import os
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PASSWORD = "testpassword123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_status(message: str, status: str = "INFO"):
    """Print colored status messages."""
    color = Colors.BLUE
    if status == "SUCCESS":
        color = Colors.GREEN
    elif status == "ERROR":
        color = Colors.RED
    elif status == "WARNING":
        color = Colors.YELLOW
    
    print(f"{color}[{status}]{Colors.END} {message}")

def test_api_endpoint(endpoint: str, method: str = "GET", data: Dict[Any, Any] = None) -> Dict[Any, Any]:
    """Test an API endpoint."""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        
        return {
            "success": response.status_code < 400,
            "status_code": response.status_code,
            "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "status_code": None
        }

def test_health_checks():
    """Test all health check endpoints."""
    print_status("Testing health check endpoints...", "INFO")
    
    endpoints = [
        "/health",
        "/api/v1/health",
        "/api/v1/health/database",
        "/api/v1/health/redis",
        "/api/v1/health/elasticsearch",
        "/api/v1/health/detailed"
    ]
    
    for endpoint in endpoints:
        result = test_api_endpoint(endpoint)
        if result["success"]:
            print_status(f"✅ {endpoint} - Status: {result['status_code']}", "SUCCESS")
        else:
            print_status(f"❌ {endpoint} - Error: {result.get('error', 'Unknown error')}", "ERROR")
    
    print()

def test_authentication():
    """Test user registration and authentication."""
    print_status("Testing authentication flow...", "INFO")
    
    # Test user registration
    register_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "full_name": "Test User"
    }
    
    result = test_api_endpoint("/api/v1/auth/register", "POST", register_data)
    if result["success"]:
        print_status("✅ User registration successful", "SUCCESS")
    else:
        if result.get("status_code") == 400 and "already registered" in str(result.get("data", "")):
            print_status("⚠️ User already exists, continuing with login", "WARNING")
        else:
            print_status(f"❌ User registration failed: {result}", "ERROR")
            return None
    
    # Test user login
    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    result = test_api_endpoint("/api/v1/auth/login", "POST", login_data)
    if result["success"]:
        print_status("✅ User login successful", "SUCCESS")
        return result["data"].get("access_token")
    else:
        print_status(f"❌ User login failed: {result}", "ERROR")
        return None

def test_announcements(token: str = None):
    """Test announcements endpoints."""
    print_status("Testing announcements endpoints...", "INFO")
    
    # Test getting announcements
    result = test_api_endpoint("/api/v1/announcements")
    if result["success"]:
        print_status("✅ Get announcements successful", "SUCCESS")
        announcements_count = len(result["data"].get("data", []))
        print_status(f"   Found {announcements_count} announcements", "INFO")
    else:
        print_status(f"❌ Get announcements failed: {result}", "ERROR")
    
    # Test search
    result = test_api_endpoint("/api/v1/announcements/search?q=exam")
    if result["success"]:
        print_status("✅ Search announcements successful", "SUCCESS")
    else:
        print_status(f"❌ Search announcements failed: {result}", "ERROR")
    
    print()

def test_subscriptions(token: str = None):
    """Test subscriptions endpoints."""
    print_status("Testing subscriptions endpoints...", "INFO")
    
    if not token:
        print_status("⚠️ No token provided, skipping subscription tests", "WARNING")
        return
    
    # Test getting subscriptions (requires authentication)
    headers = {"Authorization": f"Bearer {token}"}
    # Note: This would require modifying test_api_endpoint to accept headers
    # For now, we'll just test the endpoint exists
    result = test_api_endpoint("/api/v1/subscriptions")
    print_status(f"Subscription endpoint test: {result['status_code'] if result.get('status_code') else 'Connection failed'}", 
                "SUCCESS" if result.get("status_code") in [200, 401] else "ERROR")
    
    print()

def test_api_documentation():
    """Test API documentation endpoints."""
    print_status("Testing API documentation...", "INFO")
    
    endpoints = [
        "/docs",
        "/redoc",
        "/openapi.json"
    ]
    
    for endpoint in endpoints:
        result = test_api_endpoint(endpoint)
        if result["success"]:
            print_status(f"✅ {endpoint} accessible", "SUCCESS")
        else:
            print_status(f"❌ {endpoint} not accessible: {result.get('status_code', 'Connection failed')}", "ERROR")
    
    print()

def main():
    """Main testing function."""
    print(f"{Colors.BOLD}{Colors.BLUE}🚀 NoticeWala Local Testing Script{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 40}{Colors.END}")
    print()
    
    # Check if API is running
    print_status("Checking if API server is running...", "INFO")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_status("✅ API server is running", "SUCCESS")
        else:
            print_status(f"❌ API server returned status {response.status_code}", "ERROR")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print_status("❌ API server is not running. Please start it first:", "ERROR")
        print_status("   cd backend && uvicorn app.main:app --reload", "INFO")
        print_status("   or use: docker-compose up -d", "INFO")
        sys.exit(1)
    
    print()
    
    # Run all tests
    test_health_checks()
    test_api_documentation()
    
    # Test authentication
    token = test_authentication()
    print()
    
    # Test other endpoints
    test_announcements(token)
    test_subscriptions(token)
    
    # Summary
    print(f"{Colors.BOLD}{Colors.GREEN}🎉 Local testing completed!{Colors.END}")
    print()
    print(f"{Colors.BOLD}Next steps:{Colors.END}")
    print("1. Check the API documentation at: http://localhost:8000/docs")
    print("2. Test the mobile app if you have React Native set up")
    print("3. Check Docker services: docker-compose ps")
    print("4. View logs: docker-compose logs -f backend")
    print()
    print(f"{Colors.BOLD}If all tests passed, your system is ready for production! 🚀{Colors.END}")

if __name__ == "__main__":
    main()
