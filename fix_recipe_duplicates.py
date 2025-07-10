#!/usr/bin/env python3
"""
Fix duplicate menu items that use the same recipe
Toast POS constraint: 1 menu item = 1 recipe
"""

import sqlite3

def analyze_duplicates():
    """Find and analyze duplicate recipe assignments"""
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    print("=== ANALYZING RECIPE DUPLICATES ===\n")
    
    # Find recipes used by multiple menu items
    duplicates = cursor.execute("""
        SELECT r.id, r.recipe_name, COUNT(DISTINCT mi.id) as item_count,
               GROUP_CONCAT(mi.id || ':' || mi.item_name || ' (v' || COALESCE(mi.version_id, 'NULL') || ')') as items
        FROM recipes r
        JOIN menu_items mi ON mi.recipe_id = r.id
        GROUP BY r.id
        HAVING COUNT(DISTINCT mi.id) > 1
        ORDER BY item_count DESC
    """).fetchall()
    
    print(f"Found {len(duplicates)} recipes used by multiple menu items:\n")
    
    for recipe_id, recipe_name, count, items in duplicates:
        print(f"Recipe: {recipe_name} (ID: {recipe_id})")
        print(f"  Used by {count} menu items:")
        for item in items.split(','):
            print(f"    - {item}")
        print()
    
    conn.close()
    return duplicates

def fix_duplicates():
    """Fix duplicate recipe assignments by keeping the most recent/active version"""
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    print("\n=== FIXING RECIPE DUPLICATES ===\n")
    
    cursor.execute("BEGIN TRANSACTION")
    
    try:
        # Get duplicates
        duplicates = cursor.execute("""
            SELECT r.id, r.recipe_name
            FROM recipes r
            JOIN menu_items mi ON mi.recipe_id = r.id
            GROUP BY r.id
            HAVING COUNT(DISTINCT mi.id) > 1
        """).fetchall()
        
        for recipe_id, recipe_name in duplicates:
            print(f"Processing: {recipe_name}")
            
            # Get all menu items using this recipe
            items = cursor.execute("""
                SELECT mi.id, mi.item_name, mi.version_id, mi.created_date,
                       COUNT(mmi.menu_id) as menu_count,
                       GROUP_CONCAT(m.menu_name) as in_menus
                FROM menu_items mi
                LEFT JOIN menu_menu_items mmi ON mi.id = mmi.menu_item_id
                LEFT JOIN menus m ON mmi.menu_id = m.id
                WHERE mi.recipe_id = ?
                GROUP BY mi.id
                ORDER BY mi.version_id DESC, mi.created_date DESC
            """, (recipe_id,)).fetchall()
            
            # Keep the first (most recent/highest version) item
            keep_item = items[0]
            print(f"  ✓ Keeping: {keep_item[1]} (ID: {keep_item[0]}, in menus: {keep_item[5]})")
            
            # Remove others
            for item in items[1:]:
                item_id = item[0]
                print(f"  ✗ Removing: {item[1]} (ID: {item_id})")
                
                # Remove from menu associations
                cursor.execute("DELETE FROM menu_menu_items WHERE menu_item_id = ?", (item_id,))
                
                # Delete the menu item
                cursor.execute("DELETE FROM menu_items WHERE id = ?", (item_id,))
            
            print()
        
        cursor.execute("COMMIT")
        print("✓ Successfully fixed all duplicate recipe assignments!")
        
    except Exception as e:
        cursor.execute("ROLLBACK")
        print(f"✗ Error: {e}")
        raise
    
    finally:
        conn.close()

def validate_fix():
    """Validate that no duplicates remain"""
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    print("\n=== VALIDATION ===\n")
    
    # Check for remaining duplicates
    duplicates = cursor.execute("""
        SELECT COUNT(*) 
        FROM (
            SELECT recipe_id 
            FROM menu_items 
            GROUP BY recipe_id 
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    
    if duplicates == 0:
        print("✓ No duplicate recipe assignments found!")
        
        # Show summary
        stats = cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM recipes) as total_recipes,
                (SELECT COUNT(*) FROM menu_items) as total_items,
                (SELECT COUNT(DISTINCT recipe_id) FROM menu_items) as recipes_used
        """).fetchone()
        
        print(f"\nSummary:")
        print(f"  Total recipes: {stats[0]}")
        print(f"  Total menu items: {stats[1]}")
        print(f"  Recipes in use: {stats[2]}")
        print(f"  ✓ All menu items have unique recipes (Toast POS compliant)")
    else:
        print(f"✗ Still found {duplicates} duplicate recipe assignments!")
    
    conn.close()
    return duplicates == 0

if __name__ == "__main__":
    # First analyze
    duplicates = analyze_duplicates()
    
    if duplicates:
        # Fix if needed
        response = input("\nProceed with fixing duplicates? (y/n): ")
        if response.lower() == 'y':
            fix_duplicates()
            
            # Validate
            if validate_fix():
                print("\n🎉 Recipe duplication issues resolved!")
            else:
                print("\n⚠️  Some issues remain")
    else:
        print("\n✓ No duplicate recipe assignments found!")