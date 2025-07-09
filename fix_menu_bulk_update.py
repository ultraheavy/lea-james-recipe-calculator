#!/usr/bin/env python3
"""
Fix the bulk_update_menu_items function to use menu_assignments table instead of menu_menu_items view
"""

import re

# Read the app.py file
with open('app.py', 'r') as f:
    content = f.read()

# Find and replace the bulk_update_menu_items function
# Replace menu_menu_items with menu_assignments in the bulk update function
pattern = r'(@app\.route\(\'/menus_mgmt/<int:menu_id>/items/bulk_update\'.*?def bulk_update_menu_items.*?return jsonify.*?\n)'

def replace_function(match):
    func_content = match.group(1)
    # Replace table references
    func_content = func_content.replace('FROM menu_menu_items', 'FROM menu_assignments')
    func_content = func_content.replace('UPDATE menu_menu_items', 'UPDATE menu_assignments')
    func_content = func_content.replace('INSERT INTO menu_menu_items', 'INSERT INTO menu_assignments')
    func_content = func_content.replace('DELETE FROM menu_menu_items', 'DELETE FROM menu_assignments')
    
    # Fix column names
    # category -> category_section
    func_content = func_content.replace("SET category = ?", "SET category_section = ?")
    func_content = func_content.replace("(menu_id, menu_item_id, category, sort_order, override_price)", 
                                       "(menu_id, menu_item_id, category_section, sort_order, price_override)")
    
    # Fix SELECT id to SELECT assignment_id
    func_content = func_content.replace("SELECT id FROM menu_assignments", "SELECT assignment_id FROM menu_assignments")
    
    return func_content

# Apply the fix
content = re.sub(pattern, replace_function, content, flags=re.DOTALL)

# Write back
with open('app.py', 'w') as f:
    f.write(content)

print("Fixed bulk_update_menu_items to use menu_assignments table")