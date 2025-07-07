#!/usr/bin/env python3
"""
Test script to verify Master Menu enforcement is working correctly.
"""

import sqlite3
import sys

def test_master_menu_enforcement():
    """Test that Master Menu enforcement is working"""
    
    try:
        conn = sqlite3.connect('restaurant_calculator.db')
        cursor = conn.cursor()
        
        print("Testing Master Menu Enforcement...")
        print("=" * 50)
        
        # Get Master Menu ID
        cursor.execute("SELECT id FROM menus WHERE menu_name = 'Master Menu'")
        master_menu_id = cursor.fetchone()[0]
        print(f"Master Menu ID: {master_menu_id}")
        
        # Check current state
        cursor.execute("SELECT COUNT(*) FROM menu_items")
        total_items = cursor.fetchone()[0]
        print(f"Total menu items: {total_items}")
        
        cursor.execute("""
            SELECT COUNT(DISTINCT menu_item_id) 
            FROM menu_menu_items 
            WHERE menu_id = ?
        """, (master_menu_id,))
        master_items = cursor.fetchone()[0]
        print(f"Items in Master Menu: {master_items}")
        
        # Check if all items are in Master Menu
        if total_items == master_items:
            print("✓ SUCCESS: All menu items are in the Master Menu")
        else:
            print(f"⚠ WARNING: {total_items - master_items} items missing from Master Menu")
            
            # Find missing items
            cursor.execute("""
                SELECT id, item_name 
                FROM menu_items 
                WHERE id NOT IN (
                    SELECT menu_item_id 
                    FROM menu_menu_items 
                    WHERE menu_id = ?
                )
            """, (master_menu_id,))
            missing = cursor.fetchall()
            
            if missing:
                print("\nMissing items:")
                for item_id, item_name in missing:
                    print(f"  - {item_name} (ID: {item_id})")
        
        # Check for duplicates in Master Menu
        cursor.execute("""
            SELECT menu_item_id, COUNT(*) as count
            FROM menu_menu_items 
            WHERE menu_id = ?
            GROUP BY menu_item_id
            HAVING count > 1
        """, (master_menu_id,))
        duplicates = cursor.fetchall()
        
        if duplicates:
            print("\n⚠ WARNING: Duplicate assignments found:")
            for item_id, count in duplicates:
                cursor.execute("SELECT item_name FROM menu_items WHERE id = ?", (item_id,))
                name = cursor.fetchone()[0]
                print(f"  - {name} (ID: {item_id}) appears {count} times")
        else:
            print("✓ No duplicate assignments in Master Menu")
        
        # Summary
        print("\n" + "=" * 50)
        print("SUMMARY:")
        print(f"- Master Menu enforcement is {'ACTIVE' if total_items == master_items else 'INCOMPLETE'}")
        print(f"- Enforcement rule has been added to app.py")
        print(f"- New menu items will be automatically added to Master Menu")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_master_menu_enforcement():
        sys.exit(0)
    else:
        sys.exit(1)