#!/usr/bin/env python3
"""
Unify the two menu systems:
1. menu_items with menu_versions (Recipe-to-Menu Assignment)
2. menus with menu_menu_items (Menu Management)

This script creates appropriate links between the systems.
"""

import sqlite3
from datetime import datetime

def unify_menu_systems():
    conn = sqlite3.connect('restaurant_calculator.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # First, check if menu_versions match menus
        print("Checking menu systems alignment...")
        
        # Get all menu_versions
        versions = cursor.execute("SELECT * FROM menu_versions ORDER BY id").fetchall()
        print(f"\nFound {len(versions)} menu versions:")
        for v in versions:
            print(f"  Version {v['id']}: {v['version_name']} (Active: {v['is_active']})")
        
        # Get all menus
        menus = cursor.execute("SELECT * FROM menus ORDER BY id").fetchall()
        print(f"\nFound {len(menus)} menus:")
        for m in menus:
            print(f"  Menu {m['id']}: {m['menu_name']} (Active: {m['is_active']})")
        
        # Create mapping between menu_versions and menus based on names
        print("\n\nCreating unified menu system...")
        
        # For each menu_version, ensure there's a corresponding menu
        for version in versions:
            # Check if a menu exists with similar name
            existing_menu = cursor.execute(
                "SELECT * FROM menus WHERE menu_name LIKE ? OR menu_name LIKE ?",
                (f"%{version['version_name']}%", version['version_name'])
            ).fetchone()
            
            if not existing_menu:
                # Create a new menu for this version
                print(f"\nCreating menu for version: {version['version_name']}")
                cursor.execute("""
                    INSERT INTO menus (menu_name, description, is_active, sort_order)
                    VALUES (?, ?, ?, ?)
                """, (
                    version['version_name'],
                    version['description'],
                    version['is_active'],
                    version['id']  # Use version ID as sort order
                ))
                menu_id = cursor.lastrowid
                print(f"  Created menu ID {menu_id}")
                
                # Now link all menu_items from this version to the new menu
                menu_items = cursor.execute(
                    "SELECT * FROM menu_items WHERE version_id = ?",
                    (version['id'],)
                ).fetchall()
                
                print(f"  Linking {len(menu_items)} items to menu...")
                for item in menu_items:
                    # Check if already linked
                    existing_link = cursor.execute(
                        "SELECT * FROM menu_menu_items WHERE menu_id = ? AND menu_item_id = ?",
                        (menu_id, item['id'])
                    ).fetchone()
                    
                    if not existing_link:
                        cursor.execute("""
                            INSERT INTO menu_menu_items 
                            (menu_id, menu_item_id, category, sort_order, is_available)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            menu_id, 
                            item['id'],
                            item['menu_group'],  # Use menu_group as category
                            0,  # Default sort order
                            1   # Available by default
                        ))
            else:
                print(f"\nMenu already exists for version: {version['version_name']} (Menu ID: {existing_menu['id']})")
                
                # Ensure all items from this version are linked to the menu
                menu_items = cursor.execute(
                    "SELECT * FROM menu_items WHERE version_id = ?",
                    (version['id'],)
                ).fetchall()
                
                linked_count = 0
                for item in menu_items:
                    # Check if already linked
                    existing_link = cursor.execute(
                        "SELECT * FROM menu_menu_items WHERE menu_id = ? AND menu_item_id = ?",
                        (existing_menu['id'], item['id'])
                    ).fetchone()
                    
                    if not existing_link:
                        cursor.execute("""
                            INSERT INTO menu_menu_items 
                            (menu_id, menu_item_id, category, sort_order, is_available)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            existing_menu['id'], 
                            item['id'],
                            item['menu_group'],  # Use menu_group as category
                            0,  # Default sort order
                            1   # Available by default
                        ))
                        linked_count += 1
                
                if linked_count > 0:
                    print(f"  Linked {linked_count} new items to existing menu")
                else:
                    print(f"  All items already linked")
        
        # Add menu categories for each unique menu_group
        print("\n\nAdding menu categories...")
        menu_groups = cursor.execute(
            "SELECT DISTINCT menu_group FROM menu_items WHERE menu_group IS NOT NULL"
        ).fetchall()
        
        for menu in menus:
            for group in menu_groups:
                existing_cat = cursor.execute(
                    "SELECT * FROM menu_categories WHERE menu_id = ? AND category_name = ?",
                    (menu['id'], group['menu_group'])
                ).fetchone()
                
                if not existing_cat:
                    cursor.execute("""
                        INSERT INTO menu_categories (menu_id, category_name, sort_order)
                        VALUES (?, ?, ?)
                    """, (menu['id'], group['menu_group'], 0))
                    print(f"  Added category '{group['menu_group']}' to menu '{menu['menu_name']}'")
        
        conn.commit()
        print("\n\nMenu systems unified successfully!")
        
        # Show summary
        print("\n=== SUMMARY ===")
        for menu in cursor.execute("SELECT * FROM menus ORDER BY sort_order").fetchall():
            item_count = cursor.execute(
                "SELECT COUNT(*) as cnt FROM menu_menu_items WHERE menu_id = ?",
                (menu['id'],)
            ).fetchone()['cnt']
            print(f"Menu: {menu['menu_name']} - {item_count} items")
        
    except Exception as e:
        print(f"\nError: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    unify_menu_systems()