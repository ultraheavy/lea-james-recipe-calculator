#!/usr/bin/env python3
"""Add missing ingredients to recipes based on recipe names"""

import sqlite3
import sys
from datetime import datetime

# Recipe ingredient mappings based on recipe names
RECIPE_INGREDIENTS = {
    97: {  # 24 Hour Chili Brined Chicken Thigh
        'recipe_name': '24 Hour Chili Brined Chicken Thigh',
        'ingredients': [
            ('Protein, Chicken, Thighs', 6.0, 'oz'),  # Chicken thighs
            ('salt', 0.5, 'oz'),  # For brine
            ('Spices', 0.25, 'oz'),  # Chili spices
            ('Dairy,  Clarified Butter', 0.5, 'oz'),  # For cooking
        ]
    },
    100: {  # Comeback Sauce - Updated 2025
        'recipe_name': 'Comeback Sauce - Updated 2025',
        'ingredients': [
            ('Mayonnaise', 4.0, 'oz'),
            ('Ketchup', 1.0, 'oz'),
            ('Hot Sauce', 0.5, 'oz'),
            ('Worcestershire Sauce', 0.25, 'oz'),
            ('Spices', 0.1, 'oz'),  # Various spices
        ]
    },
    102: {  # Coleslaw
        'recipe_name': 'Coleslaw',
        'ingredients': [
            ('Produce, Cabbage, Green', 8.0, 'oz'),
            ('Produce, Carrots, Whole, peeled', 2.0, 'oz'),
            ('Mayonnaise', 3.0, 'oz'),
            ('Vinegar', 0.5, 'oz'),
            ('SUGAR EFG GRANULATED 403522', 0.5, 'oz'),
        ]
    },
    105: {  # Hot Honey - 2025
        'recipe_name': 'Hot Honey - 2025',
        'ingredients': [
            ('Honey', 8.0, 'oz'),
            ('Hot Sauce', 1.0, 'oz'),
            ('Vinegar', 0.25, 'oz'),
            ('Spices', 0.1, 'oz'),  # Red pepper flakes, etc.
        ]
    }
}

def get_ingredient_info(conn, ingredient_name):
    """Find best matching ingredient from inventory"""
    # Try exact match first
    cursor = conn.cursor()
    result = cursor.execute('''
        SELECT id, item_description, current_price, unit_measure
        FROM inventory 
        WHERE LOWER(item_description) = LOWER(?)
        LIMIT 1
    ''', (ingredient_name,)).fetchone()
    
    if result:
        return result
    
    # Try partial match
    result = cursor.execute('''
        SELECT id, item_description, current_price, unit_measure
        FROM inventory 
        WHERE LOWER(item_description) LIKE LOWER(?)
        ORDER BY LENGTH(item_description)
        LIMIT 1
    ''', (f'%{ingredient_name}%',)).fetchone()
    
    return result

def calculate_cost(current_price, pack_size, quantity, unit):
    """Simple cost calculation"""
    # Extract numeric value from pack_size
    try:
        # Handle formats like "5 lb", "50 each", etc.
        parts = pack_size.split()
        if len(parts) >= 1:
            pack_qty = float(parts[0])
        else:
            pack_qty = 1.0
            
        # Simple calculation: (price / pack_qty) * quantity
        unit_price = current_price / pack_qty if pack_qty > 0 else current_price
        cost = unit_price * quantity
        return round(cost, 2)
    except:
        # Fallback to simple calculation
        return round((current_price * quantity) / 10, 2)  # Rough estimate

def add_ingredients_to_recipe(conn, recipe_id, recipe_data):
    """Add ingredients to a recipe"""
    cursor = conn.cursor()
    added = 0
    skipped = 0
    
    print(f"\nProcessing Recipe {recipe_id}: {recipe_data['recipe_name']}")
    print("-" * 60)
    
    for ingredient_name, quantity, unit in recipe_data['ingredients']:
        # Find matching inventory item
        inv_item = get_ingredient_info(conn, ingredient_name)
        
        if not inv_item:
            print(f"  ⚠️  Skipped: {ingredient_name} - not found in inventory")
            skipped += 1
            continue
        
        inv_id, inv_desc, current_price, unit_measure = inv_item
        
        # Get pack size
        pack_size_result = cursor.execute('''
            SELECT pack_size FROM inventory WHERE id = ?
        ''', (inv_id,)).fetchone()
        
        pack_size = pack_size_result[0] if pack_size_result else '1 each'
        
        # Calculate cost
        cost = calculate_cost(current_price or 0, pack_size, quantity, unit)
        
        # Insert ingredient
        try:
            cursor.execute('''
                INSERT INTO recipe_ingredients 
                (recipe_id, ingredient_id, ingredient_name, quantity, unit_of_measure, cost)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (recipe_id, inv_id, inv_desc, quantity, unit, cost))
            
            print(f"  ✓ Added: {inv_desc} - {quantity} {unit} @ ${cost:.2f}")
            added += 1
            
        except sqlite3.IntegrityError:
            print(f"  ⚠️  Already exists: {inv_desc}")
            skipped += 1
    
    # Update recipe food cost
    total_cost = cursor.execute('''
        SELECT SUM(cost) FROM recipe_ingredients WHERE recipe_id = ?
    ''', (recipe_id,)).fetchone()[0] or 0
    
    # Get menu price for percentage calculation
    menu_price = cursor.execute('''
        SELECT menu_price FROM recipes WHERE id = ?
    ''', (recipe_id,)).fetchone()[0] or 0
    
    food_cost_percentage = (total_cost / menu_price * 100) if menu_price > 0 else 0
    
    cursor.execute('''
        UPDATE recipes 
        SET food_cost = ?,
            food_cost_percentage = ?,
            updated_date = ?
        WHERE id = ?
    ''', (total_cost, food_cost_percentage, datetime.now().isoformat(), recipe_id))
    
    print(f"\n  Total Food Cost: ${total_cost:.2f}")
    print(f"  Food Cost %: {food_cost_percentage:.1f}%")
    print(f"  Summary: {added} added, {skipped} skipped")
    
    return added, skipped

def main():
    """Main function"""
    conn = sqlite3.connect('restaurant_calculator.db')
    conn.row_factory = sqlite3.Row
    
    print("Adding Missing Ingredients to Recipes")
    print("=" * 60)
    
    total_added = 0
    total_skipped = 0
    
    for recipe_id, recipe_data in RECIPE_INGREDIENTS.items():
        added, skipped = add_ingredients_to_recipe(conn, recipe_id, recipe_data)
        total_added += added
        total_skipped += skipped
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"Complete! Total: {total_added} ingredients added, {total_skipped} skipped")

if __name__ == "__main__":
    main()