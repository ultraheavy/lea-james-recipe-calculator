#!/usr/bin/env python3
"""
Enforce Master Menu rule - ensure all menu items belong to the Master Menu.
The Master Menu serves as a complete reference list of all possible menu items.
"""

import sqlite3
import sys
from datetime import datetime

def enforce_master_menu():
    """Add all menu items to the Master Menu"""
    
    try:
        conn = sqlite3.connect('restaurant_calculator.db')
        cursor = conn.cursor()
        
        # Get Master Menu ID
        cursor.execute("SELECT id FROM menus WHERE menu_name = 'Master Menu'")
        result = cursor.fetchone()
        if not result:
            print("ERROR: Master Menu not found!")
            return False
            
        master_menu_id = result[0]
        print(f"Master Menu ID: {master_menu_id}")
        
        # Get all menu items
        cursor.execute("SELECT id, item_name FROM menu_items ORDER BY menu_group, item_name")
        all_items = cursor.fetchall()
        print(f"Total menu items: {len(all_items)}")
        
        # Get current Master Menu assignments
        cursor.execute("""
            SELECT menu_item_id 
            FROM menu_menu_items 
            WHERE menu_id = ?
        """, (master_menu_id,))
        current_assignments = set([row[0] for row in cursor.fetchall()])
        print(f"Current Master Menu assignments: {len(current_assignments)}")
        
        # Add missing items to Master Menu
        added_count = 0
        for item_id, item_name in all_items:
            if item_id not in current_assignments:
                cursor.execute("""
                    INSERT INTO menu_menu_items (menu_id, menu_item_id, sort_order)
                    VALUES (?, ?, ?)
                """, (master_menu_id, item_id, added_count))
                added_count += 1
                print(f"Added to Master Menu: {item_name} (ID: {item_id})")
        
        # Commit changes
        conn.commit()
        
        # Verify final count
        cursor.execute("""
            SELECT COUNT(DISTINCT menu_item_id) 
            FROM menu_menu_items 
            WHERE menu_id = ?
        """, (master_menu_id,))
        final_count = cursor.fetchone()[0]
        
        print(f"\nSummary:")
        print(f"- Items added to Master Menu: {added_count}")
        print(f"- Total items in Master Menu: {final_count}")
        print(f"- Total menu items in system: {len(all_items)}")
        
        if final_count == len(all_items):
            print("✓ SUCCESS: All menu items are now in the Master Menu")
        else:
            print("⚠ WARNING: Count mismatch - please investigate")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if enforce_master_menu():
        sys.exit(0)
    else:
        sys.exit(1)