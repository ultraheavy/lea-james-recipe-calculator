#!/usr/bin/env python3
"""
Fix duplicate menu items by keeping only one of each (preferring linked recipes)
"""

import sqlite3

def fix_menu_duplicates():
    conn = sqlite3.connect('restaurant_calculator.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("🔧 Fixing duplicate menu items...")
    
    # Get all duplicates
    duplicates = cursor.execute('''
        SELECT item_name, COUNT(*) as count 
        FROM menu_items 
        GROUP BY item_name 
        HAVING count > 1
    ''').fetchall()
    
    print(f"\nFound {len(duplicates)} duplicate menu items")
    
    removed_count = 0
    
    for dup in duplicates:
        item_name = dup['item_name']
        
        # Get all entries for this item, ordered by recipe_id DESC (non-null first)
        entries = cursor.execute('''
            SELECT id, item_name, recipe_id 
            FROM menu_items 
            WHERE item_name = ?
            ORDER BY CASE WHEN recipe_id IS NULL THEN 1 ELSE 0 END, id
        ''', (item_name,)).fetchall()
        
        # Keep the first one (which has recipe_id if any exist)
        keep_id = entries[0]['id']
        
        # Delete the rest
        for entry in entries[1:]:
            cursor.execute('DELETE FROM menu_items WHERE id = ?', (entry['id'],))
            removed_count += 1
            print(f"  ✓ Removed duplicate: {item_name} (id: {entry['id']})")
    
    conn.commit()
    
    print(f"\n✅ Removed {removed_count} duplicate menu items")
    
    # Show final count
    total_items = cursor.execute('SELECT COUNT(*) FROM menu_items').fetchone()[0]
    print(f"📊 Total menu items now: {total_items}")
    
    conn.close()

if __name__ == "__main__":
    fix_menu_duplicates()