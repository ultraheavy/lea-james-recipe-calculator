#!/usr/bin/env python3
"""
Fix Nashville Chicken menu item mappings
"""

import sqlite3

def fix_nashville_mapping():
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    print("=== Nashville Chicken Menu Items Before Fix ===")
    cursor.execute('''
        SELECT mi.id, mi.item_name, mi.recipe_id, r.recipe_name 
        FROM menu_items mi 
        LEFT JOIN recipes r ON mi.recipe_id = r.id 
        WHERE mi.item_name LIKE '%Nashville%' OR mi.item_name LIKE '%S-01%' 
        ORDER BY mi.item_name
    ''')
    results = cursor.fetchall()
    for row in results:
        recipe_name = row[3] if row[3] else "No Recipe"
        print(f"Menu ID {row[0]}: \"{row[1]}\" -> Recipe ID {row[2]} (\"{recipe_name}\")")
    
    print("\n=== S-01 Recipe Details ===")
    cursor.execute('''
        SELECT id, recipe_name, recipe_group, food_cost, menu_price 
        FROM recipes 
        WHERE recipe_name LIKE '%S-01%' OR recipe_name LIKE '%Nashville%'
        ORDER BY recipe_name
    ''')
    recipes = cursor.fetchall()
    for recipe in recipes:
        print(f"Recipe ID {recipe[0]}: \"{recipe[1]}\" ({recipe[2]}) - Cost: ${recipe[3]:.2f}, Price: ${recipe[4]:.2f}")
    
    # Find the correct S-01 recipe
    cursor.execute('''
        SELECT id, recipe_name 
        FROM recipes 
        WHERE recipe_name = ' S-01 OG Nashville Chicken'
    ''')
    s01_recipe = cursor.fetchone()
    
    if s01_recipe:
        recipe_id = s01_recipe[0]
        print(f"\n✅ Found S-01 recipe: ID {recipe_id}")
        
        # Fix menu item that has no recipe_id
        cursor.execute('''
            UPDATE menu_items 
            SET recipe_id = ? 
            WHERE item_name = ' S-01 OG Nashville Chicken' AND recipe_id IS NULL
        ''', (recipe_id,))
        
        updated_rows = cursor.rowcount
        if updated_rows > 0:
            print(f"✅ Updated {updated_rows} menu item(s) to link to recipe ID {recipe_id}")
        
        # Check for duplicate menu items
        cursor.execute('''
            SELECT id, item_name, recipe_id
            FROM menu_items 
            WHERE item_name LIKE '%Nashville%' 
            ORDER BY item_name, id
        ''')
        duplicates = cursor.fetchall()
        
        # Group by item_name to find duplicates
        name_groups = {}
        for item in duplicates:
            name = item[1].strip()
            if name not in name_groups:
                name_groups[name] = []
            name_groups[name].append(item)
        
        # Remove duplicates (keep the one with recipe_id)
        for name, items in name_groups.items():
            if len(items) > 1:
                print(f"\n🔍 Found {len(items)} items with name '{name}':")
                for item in items:
                    print(f"  - ID {item[0]}: recipe_id = {item[2]}")
                
                # Keep the one with recipe_id, remove others
                items_with_recipe = [item for item in items if item[2] is not None]
                items_without_recipe = [item for item in items if item[2] is None]
                
                if items_with_recipe and items_without_recipe:
                    # Remove items without recipe
                    for item in items_without_recipe:
                        cursor.execute('DELETE FROM menu_items WHERE id = ?', (item[0],))
                        print(f"✅ Removed duplicate menu item ID {item[0]} (no recipe)")
                elif len(items) > 1 and all(item[2] == items[0][2] for item in items):
                    # All have same recipe_id, remove duplicates except first
                    for item in items[1:]:
                        cursor.execute('DELETE FROM menu_items WHERE id = ?', (item[0],))
                        print(f"✅ Removed duplicate menu item ID {item[0]}")
    
    conn.commit()
    
    print("\n=== Nashville Chicken Menu Items After Fix ===")
    cursor.execute('''
        SELECT mi.id, mi.item_name, mi.recipe_id, r.recipe_name 
        FROM menu_items mi 
        LEFT JOIN recipes r ON mi.recipe_id = r.id 
        WHERE mi.item_name LIKE '%Nashville%' OR mi.item_name LIKE '%S-01%' 
        ORDER BY mi.item_name
    ''')
    results = cursor.fetchall()
    for row in results:
        recipe_name = row[3] if row[3] else "No Recipe"
        print(f"Menu ID {row[0]}: \"{row[1]}\" -> Recipe ID {row[2]} (\"{recipe_name}\")")
    
    conn.close()
    print("\n✅ Nashville Chicken mapping fix complete!")

if __name__ == '__main__':
    fix_nashville_mapping()