#!/usr/bin/env python3
"""
Test announcements endpoint
"""

import requests
import json

def test_announcements():
    try:
        response = requests.get('http://localhost:8000/api/v1/announcements')
        print(f'Status: {response.status_code}')
        print(f'Headers: {dict(response.headers)}')
        print(f'Text: {response.text}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'Success! Found {len(data.get("items", []))} announcements')
        else:
            print(f'Error: {response.status_code}')
            
    except Exception as e:
        print(f'Exception: {e}')

if __name__ == "__main__":
    test_announcements()
