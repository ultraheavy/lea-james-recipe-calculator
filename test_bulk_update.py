#!/usr/bin/env python3
"""Test the bulk_update_menu_items endpoint"""

import requests
import json

# Test adding an item to menu 4
test_data = {
    "items": [
        {
            "item_id": 1,  # A valid menu_item_id
            "action": "add",
            "category": "Test Category",
            "override_price": None
        }
    ]
}

# Send the request
response = requests.post(
    'http://localhost:8888/menus_mgmt/4/items/bulk_update',
    headers={'Content-Type': 'application/json'},
    data=json.dumps(test_data)
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

# Check if it's a JSON response
try:
    data = response.json()
    print(f"JSON Response: {json.dumps(data, indent=2)}")
except:
    print("Response is not JSON")