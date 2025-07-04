#!/usr/bin/env python3
"""
Fix zero-quantity recipe ingredients by:
1. Updating common default quantities based on ingredient patterns
2. Setting a minimum default of 1 for items that still have 0
"""

import sqlite3
import re

def fix_zero_quantities():
    conn = sqlite3.connect('restaurant_calculator.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("🔧 Fixing zero-quantity recipe ingredients...")
    
    # Get all zero-quantity ingredients
    zero_qty_ingredients = cursor.execute('''
        SELECT ri.id, ri.recipe_id, ri.ingredient_id, 
               r.recipe_name, i.item_description, i.unit_measure
        FROM recipe_ingredients ri
        JOIN recipes r ON ri.recipe_id = r.id
        JOIN inventory i ON ri.ingredient_id = i.id
        WHERE ri.quantity = 0 OR ri.quantity IS NULL
    ''').fetchall()
    
    print(f"\nFound {len(zero_qty_ingredients)} ingredients with zero/null quantities")
    
    # Define common quantity patterns
    quantity_patterns = {
        # Oils and liquids (usually measured in ounces or cups)
        r'oil|vinegar|sauce|dressing': 2.0,  # 2 oz default
        r'mayo|aioli|cream': 1.0,  # 1 oz default
        
        # Eggs
        r'egg': 2.0,  # 2 eggs default
        
        # Vegetables
        r'onion|tomato|pepper|cucumber': 1.0,  # 1 unit default
        r'lettuce|kale|spinach|greens': 2.0,  # 2 oz default
        
        # Proteins
        r'chicken|beef|fish|pork|bacon': 4.0,  # 4 oz default
        
        # Cheese
        r'cheese': 1.0,  # 1 oz default
        
        # Spices and seasonings
        r'salt|pepper|spice|seasoning': 0.25,  # 1/4 tsp default
    }
    
    fixed_count = 0
    
    for ingredient in zero_qty_ingredients:
        item_desc = ingredient['item_description'].lower()
        
        # Try to match patterns
        matched = False
        for pattern, default_qty in quantity_patterns.items():
            if re.search(pattern, item_desc, re.IGNORECASE):
                cursor.execute('''
                    UPDATE recipe_ingredients 
                    SET quantity = ? 
                    WHERE id = ?
                ''', (default_qty, ingredient['id']))
                
                print(f"  ✓ {ingredient['recipe_name']} - {ingredient['item_description']}: set to {default_qty}")
                fixed_count += 1
                matched = True
                break
        
        # If no pattern matched, set a default of 1
        if not matched:
            cursor.execute('''
                UPDATE recipe_ingredients 
                SET quantity = 1.0 
                WHERE id = ?
            ''', (ingredient['id'],))
            
            print(f"  ✓ {ingredient['recipe_name']} - {ingredient['item_description']}: set to 1.0 (default)")
            fixed_count += 1
    
    # Update recipe costs
    print("\n📊 Updating recipe costs...")
    cursor.execute('''
        UPDATE recipes 
        SET food_cost = (
            SELECT SUM(ri.quantity * (i.current_price / NULLIF(i.yield_percent, 0) * 100))
            FROM recipe_ingredients ri
            JOIN inventory i ON ri.ingredient_id = i.id
            WHERE ri.recipe_id = recipes.id
        )
    ''')
    
    cursor.execute('''
        UPDATE recipes 
        SET prime_cost = food_cost + COALESCE(labor_cost, 0)
    ''')
    
    # Update recipe_ingredients costs
    cursor.execute('''
        UPDATE recipe_ingredients
        SET cost = quantity * (
            SELECT (current_price / NULLIF(yield_percent, 0) * 100)
            FROM inventory 
            WHERE inventory.id = recipe_ingredients.ingredient_id
        )
    ''')
    
    conn.commit()
    
    print(f"\n✅ Fixed {fixed_count} zero-quantity ingredients")
    
    # Show summary
    remaining_zero = cursor.execute('''
        SELECT COUNT(*) FROM recipe_ingredients 
        WHERE quantity = 0 OR quantity IS NULL
    ''').fetchone()[0]
    
    if remaining_zero > 0:
        print(f"⚠️  {remaining_zero} ingredients still have zero quantity (may need manual review)")
    else:
        print("🎉 All zero-quantity issues resolved!")
    
    conn.close()

if __name__ == "__main__":
    fix_zero_quantities()