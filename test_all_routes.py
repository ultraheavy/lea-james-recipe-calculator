#!/usr/bin/env python3
"""Test all routes in the Flask application"""

import requests
import sys

base_url = "http://localhost:8888"

# Define all routes to test
routes = [
    # Basic pages
    ("/", "Dashboard"),
    ("/inventory", "Inventory"),
    ("/recipes", "Recipes"),
    ("/menu_items", "Menu Items"),
    ("/menus_mgmt", "Menus Management"),
    ("/pricing-analysis", "Pricing Analysis"),
    ("/vendors", "Vendors"),
    
    # Menu items with version parameters
    ("/menu_items?version_id=1", "Menu Items v1"),
    ("/menu_items?version_id=2", "Menu Items v2"),
    ("/menu_items?version_id=3", "Menu Items v3"),
    ("/menu_items?version_id=4", "Menu Items v4"),
    ("/menu_items?version_id=5", "Menu Items v5"),
    ("/menu_items?version_id=6", "Menu Items v6"),
    
    # Other menu routes
    ("/menu_items/compare", "Menu Compare"),
    ("/menu_items/versions", "Menu Versions"),
    
    # Recipe routes with parameters
    ("/recipes?status=Active", "Active Recipes"),
    ("/recipes?status=Inactive", "Inactive Recipes"),
    ("/recipes?group=Entrees", "Entrees"),
    
    # Pricing analysis with parameters
    ("/pricing-analysis?version_id=1", "Pricing v1"),
    ("/pricing-analysis?version_id=4", "Pricing v4"),
]

errors = []
successes = 0

print("=" * 60)
print("TESTING ALL ROUTES")
print("=" * 60)

for route, name in routes:
    try:
        response = requests.get(base_url + route, timeout=5)
        
        if response.status_code == 200:
            # Check for error indicators in the response
            content = response.text
            if any(error_text in content for error_text in ["Server Error", "Traceback", "Exception", "OperationalError"]):
                errors.append(f"✗ {name} ({route}): Contains error messages")
                print(f"✗ {name} ({route}): Contains error messages")
                # Extract the error message
                if "OperationalError" in content:
                    import re
                    error_match = re.search(r'OperationalError: (.+?)<', content)
                    if error_match:
                        print(f"  Error: {error_match.group(1)}")
            else:
                successes += 1
                print(f"✓ {name} ({route}): OK")
        else:
            errors.append(f"✗ {name} ({route}): HTTP {response.status_code}")
            print(f"✗ {name} ({route}): HTTP {response.status_code}")
            
    except Exception as e:
        errors.append(f"✗ {name} ({route}): {str(e)}")
        print(f"✗ {name} ({route}): {str(e)}")

print("\n" + "=" * 60)
print(f"SUMMARY: {successes} passed, {len(errors)} failed")
if errors:
    print("\nFAILED ROUTES:")
    for error in errors:
        print(error)
print("=" * 60)

sys.exit(0 if len(errors) == 0 else 1)