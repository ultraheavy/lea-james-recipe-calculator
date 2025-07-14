#!/usr/bin/env python3
"""Simple test to check inventory staging route"""

import requests

try:
    # Test the route
    response = requests.get('http://localhost:8888/admin/inventory-staging/')
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Route is working!")
        print(f"Response length: {len(response.text)} characters")
        # Check if it's the right page
        if "Inventory Staging Review" in response.text:
            print("✓ Correct page loaded!")
        else:
            print("✗ Wrong page content")
            print("First 500 chars:", response.text[:500])
    else:
        print(f"✗ Error: {response.status_code}")
        print("Response:", response.text[:500])
        
except Exception as e:
    print(f"✗ Connection error: {e}")
    
# Also test if the server is running
try:
    response = requests.get('http://localhost:8888/')
    print(f"\nMain page status: {response.status_code}")
except Exception as e:
    print(f"\nServer not reachable: {e}")