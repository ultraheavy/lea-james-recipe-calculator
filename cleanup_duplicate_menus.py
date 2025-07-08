#!/usr/bin/env python3
"""
Clean up duplicate menus created by unification script.
Merge items from duplicate menus into the original ones.
"""

import sqlite3

def cleanup_duplicate_menus():
    conn = sqlite3.connect('restaurant_calculator.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        print("Cleaning up duplicate menus...")
        
        # Mapping of duplicates to originals
        merge_map = {
            7: 4,  # Master List -> Master Menu
            8: 6,  # Planning Menu -> Future Menu  
            9: 6   # Experimental Menu -> Future Menu
        }
        
        for dup_id, orig_id in merge_map.items():
            dup_menu = cursor.execute("SELECT * FROM menus WHERE id = ?", (dup_id,)).fetchone()
            orig_menu = cursor.execute("SELECT * FROM menus WHERE id = ?", (orig_id,)).fetchone()
            
            if dup_menu and orig_menu:
                print(f"\nMerging '{dup_menu['menu_name']}' into '{orig_menu['menu_name']}'...")
                
                # Get items from duplicate menu
                dup_items = cursor.execute("""
                    SELECT * FROM menu_menu_items WHERE menu_id = ?
                """, (dup_id,)).fetchall()
                
                moved_count = 0
                for item in dup_items:
                    # Check if item already exists in original menu
                    existing = cursor.execute("""
                        SELECT * FROM menu_menu_items 
                        WHERE menu_id = ? AND menu_item_id = ?
                    """, (orig_id, item['menu_item_id'])).fetchone()
                    
                    if not existing:
                        # Move item to original menu
                        cursor.execute("""
                            UPDATE menu_menu_items 
                            SET menu_id = ? 
                            WHERE id = ?
                        """, (orig_id, item['id']))
                        moved_count += 1
                
                print(f"  Moved {moved_count} items")
                
                # Delete duplicate menu
                cursor.execute("DELETE FROM menus WHERE id = ?", (dup_id,))
                print(f"  Deleted duplicate menu")
        
        # Also update Future Menu to be named "Planning Menu" for clarity
        cursor.execute("""
            UPDATE menus 
            SET menu_name = 'Planning Menu', 
                description = 'Menu items being planned for future implementation'
            WHERE id = 6
        """)
        
        conn.commit()
        print("\nCleanup complete!")
        
        # Show final state
        print("\n=== FINAL MENU STATE ===")
        menus = cursor.execute("""
            SELECT m.*, COUNT(mmi.id) as item_count 
            FROM menus m 
            LEFT JOIN menu_menu_items mmi ON m.id = mmi.menu_id 
            GROUP BY m.id 
            ORDER BY m.sort_order, m.id
        """).fetchall()
        
        for menu in menus:
            print(f"Menu {menu['id']}: {menu['menu_name']} - {menu['item_count']} items (Active: {menu['is_active']})")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup_duplicate_menus()