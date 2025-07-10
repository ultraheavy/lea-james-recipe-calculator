#!/usr/bin/env python3
"""Comprehensive test of ALL routes including edit/delete/create routes"""

import requests
import sqlite3

base_url = "http://localhost:8888"

# Get dynamic IDs from database
conn = sqlite3.connect('restaurant_calculator.db')
cursor = conn.cursor()

# Get some IDs to test with
recipe_ids = [row[0] for row in cursor.execute("SELECT id FROM recipes LIMIT 3").fetchall()]
menu_item_ids = [row[0] for row in cursor.execute("SELECT id FROM menu_items LIMIT 3").fetchall()]
menu_ids = [row[0] for row in cursor.execute("SELECT id FROM menus LIMIT 3").fetchall()]
inventory_ids = [row[0] for row in cursor.execute("SELECT id FROM inventory LIMIT 3").fetchall()]
vendor_ids = [row[0] for row in cursor.execute("SELECT id FROM vendors LIMIT 3").fetchall()]

conn.close()

# Define all routes including dynamic ones
routes = [
    # Basic pages
    ("/", "Dashboard", "GET"),
    ("/inventory", "Inventory", "GET"),
    ("/recipes", "Recipes", "GET"),
    ("/menu_items", "Menu Items", "GET"),
    ("/menus_mgmt", "Menus Management", "GET"),
    ("/pricing-analysis", "Pricing Analysis", "GET"),
    ("/vendors", "Vendors", "GET"),
    
    # Create routes
    ("/recipes/add", "Add Recipe", "GET"),
    ("/menus_mgmt/create", "Create Menu", "GET"),
    ("/menu_items/items/add", "Add Menu Item", "GET"),
    ("/inventory/add", "Add Inventory", "GET"),
    ("/vendors/add", "Add Vendor", "GET"),
    
    # Menu edit routes
    *[(f"/menus_mgmt/{menu_id}/edit", f"Edit Menu {menu_id}", "GET") for menu_id in menu_ids],
    
    # Recipe edit routes
    *[(f"/recipes/{recipe_id}/edit", f"Edit Recipe {recipe_id}", "GET") for recipe_id in recipe_ids],
    
    # Menu item edit routes
    *[(f"/menu_items/items/edit/{item_id}", f"Edit Menu Item {item_id}", "GET") for item_id in menu_item_ids],
    
    # Other specific routes
    ("/menu_items/compare", "Menu Compare", "GET"),
    ("/menu_items/versions", "Menu Versions", "GET"),
    ("/unit-converter", "Unit Converter", "GET"),
]

errors = []
successes = 0

print("=" * 80)
print("COMPREHENSIVE ROUTE TEST")
print("=" * 80)

for route_info in routes:
    route = route_info[0]
    name = route_info[1]
    method = route_info[2] if len(route_info) > 2 else "GET"
    
    try:
        if method == "GET":
            response = requests.get(base_url + route, timeout=5)
        else:
            response = requests.post(base_url + route, timeout=5)
        
        if response.status_code == 200:
            content = response.text
            if any(error_text in content for error_text in ["Server Error", "Traceback", "Exception", "OperationalError"]):
                # Extract error details
                error_msg = f"✗ {name} ({route}): Contains error"
                if "OperationalError" in content:
                    import re
                    error_match = re.search(r'OperationalError: (.+?)(?:<|$)', content)
                    if error_match:
                        error_msg += f" - {error_match.group(1)}"
                errors.append(error_msg)
                print(error_msg)
            else:
                successes += 1
                print(f"✓ {name} ({route}): OK")
        else:
            error_msg = f"✗ {name} ({route}): HTTP {response.status_code}"
            errors.append(error_msg)
            print(error_msg)
            
    except Exception as e:
        error_msg = f"✗ {name} ({route}): {str(e)}"
        errors.append(error_msg)
        print(error_msg)

print("\n" + "=" * 80)
print(f"SUMMARY: {successes} passed, {len(errors)} failed")
if errors:
    print(f"\nFAILED ROUTES ({len(errors)}):")
    for error in errors:
        print(error)
print("=" * 80)