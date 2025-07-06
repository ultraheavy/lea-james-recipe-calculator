#!/usr/bin/env python3
"""
Fix recipe costs by recalculating with proper unit conversions
"""

import sqlite3
from unit_converter import UnitConverter

DATABASE = 'restaurant_calculator.db'

def recalculate_recipe_costs():
    """Recalculate all recipe costs with proper unit conversions"""
    
    converter = UnitConverter(DATABASE)
    
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all recipes
        recipes = cursor.execute('SELECT id, recipe_name FROM recipes').fetchall()
        
        print(f"Recalculating costs for {len(recipes)} recipes...")
        
        for recipe in recipes:
            recipe_id = recipe['id']
            recipe_name = recipe['recipe_name']
            
            # Get all ingredients for this recipe
            ingredients = cursor.execute('''
                SELECT ri.*, i.* 
                FROM recipe_ingredients ri
                JOIN inventory i ON ri.ingredient_id = i.id
                WHERE ri.recipe_id = ?
            ''', (recipe_id,)).fetchall()
            
            total_cost = 0
            
            for ingredient in ingredients:
                # Get ingredient info
                quantity = ingredient['quantity']
                unit = ingredient['unit_of_measure']
                
                # Convert Row to dict for the converter
                inventory_item = dict(ingredient)
                
                try:
                    # Calculate cost using proper unit conversion
                    cost = converter.calculate_ingredient_cost(
                        inventory_item,
                        quantity,
                        unit
                    )
                    
                    # Update ingredient cost
                    cursor.execute('''
                        UPDATE recipe_ingredients 
                        SET cost = ?
                        WHERE recipe_id = ? AND ingredient_id = ?
                    ''', (cost, recipe_id, ingredient['ingredient_id']))
                    
                    total_cost += cost
                    
                    print(f"  {ingredient['item_description']}: {quantity} {unit} = ${cost:.2f}")
                    
                except Exception as e:
                    print(f"  ERROR with {ingredient['item_description']}: {e}")
            
            # Update recipe total cost
            cursor.execute('''
                UPDATE recipes 
                SET food_cost = ?,
                    prime_cost = ? + COALESCE(labor_cost, 0)
                WHERE id = ?
            ''', (total_cost, total_cost, recipe_id))
            
            print(f"{recipe_name}: Total cost = ${total_cost:.2f}\n")
        
        conn.commit()
        print("Recipe costs recalculated successfully!")

def fix_pack_sizes():
    """Fix pack sizes that are missing units"""
    
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get items with problematic pack sizes
        items = cursor.execute('''
            SELECT id, item_code, item_description, pack_size, unit_measure
            FROM inventory 
            WHERE pack_size LIKE '% x %' AND pack_size NOT LIKE '%lb%' 
               AND pack_size NOT LIKE '%kg%' AND pack_size NOT LIKE '%oz%'
               AND pack_size NOT LIKE '%g%' AND pack_size NOT LIKE '%ml%'
               AND pack_size NOT LIKE '%l%'
        ''').fetchall()
        
        print(f"Found {len(items)} items with ambiguous pack sizes")
        
        for item in items:
            print(f"\n{item['item_description']}")
            print(f"  Current pack_size: {item['pack_size']}")
            print(f"  Unit measure: {item['unit_measure']}")
            
            # Try to infer unit from unit_measure
            if item['unit_measure']:
                unit = item['unit_measure'].lower()
                if unit in ['cs', 'case', 'ca']:
                    # For cases, check the item description for clues
                    if 'lb' in item['item_description'].lower():
                        # Likely pounds
                        new_pack_size = item['pack_size'].replace(' x ', ' x ') + ' lb'
                    else:
                        # Keep as is for now
                        continue
                elif unit in ['lb', 'kg', 'oz', 'g']:
                    # Add the unit to pack size
                    new_pack_size = item['pack_size'] + ' ' + unit
                else:
                    continue
                    
                print(f"  -> Updating to: {new_pack_size}")
                cursor.execute('''
                    UPDATE inventory SET pack_size = ? WHERE id = ?
                ''', (new_pack_size, item['id']))
        
        conn.commit()

if __name__ == '__main__':
    # First fix pack sizes
    fix_pack_sizes()
    
    # Then recalculate costs
    recalculate_recipe_costs()