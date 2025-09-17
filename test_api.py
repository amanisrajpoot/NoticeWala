#!/usr/bin/env python3
"""
Test script for NoticeWala API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get("http://localhost:8000/health")
    if response.status_code == 200:
        print("✅ Health check passed")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
    print()

def test_register():
    """Test user registration"""
    print("🔍 Testing user registration...")
    user_data = {
        "email": "newuser@example.com",  # Use a new email to avoid conflicts
        "password": "testpassword123",
        "first_name": "New",
        "last_name": "User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    if response.status_code == 201:
        print("✅ User registration successful")
        print(f"   Response: {response.json()}")
        return True
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def test_login():
    """Test user login"""
    print("🔍 Testing user login...")
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        print("✅ User login successful")
        data = response.json()
        print(f"   Token type: {data.get('token_type')}")
        print(f"   Access token: {data.get('access_token')[:50]}...")
        return data.get('access_token')
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_announcements(token=None):
    """Test announcements endpoint"""
    print("🔍 Testing announcements endpoint...")
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    response = requests.get(f"{BASE_URL}/announcements", headers=headers)
    if response.status_code == 200:
        print("✅ Announcements endpoint accessible")
        data = response.json()
        print(f"   Total announcements: {data.get('total', 0)}")
        print(f"   Items: {len(data.get('items', []))}")
    else:
        print(f"❌ Announcements endpoint failed: {response.status_code}")
        print(f"   Error: {response.text}")

def test_user_profile(token):
    """Test user profile endpoint"""
    print("🔍 Testing user profile endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if response.status_code == 200:
        print("✅ User profile accessible")
        data = response.json()
        print(f"   Email: {data.get('email')}")
        print(f"   Name: {data.get('first_name')} {data.get('last_name')}")
    else:
        print(f"❌ User profile failed: {response.status_code}")
        print(f"   Error: {response.text}")

def main():
    """Run all tests"""
    print("🚀 Starting NoticeWala API Tests")
    print("=" * 50)
    
    # Test health
    test_health()
    
    # Test registration
    register_success = test_register()
    
    # Test login
    token = test_login()
    
    if token:
        # Test protected endpoints
        test_user_profile(token)
        test_announcements(token)
    
    print("=" * 50)
    print("🏁 API Tests Complete!")

if __name__ == "__main__":
    main()
