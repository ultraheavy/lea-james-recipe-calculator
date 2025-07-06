#!/usr/bin/env python3
"""
Fix pack sizes in inventory table by referencing the original CSV data
"""

import sqlite3
import csv
from pathlib import Path

def fix_pack_sizes():
    """Fix critical pack size issues in inventory table"""
    
    # Connect to database
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    # Critical fixes based on CSV analysis
    pack_size_fixes = [
        # Honey Mustard - 1 gallon containers
        ('Dry Goods, Dressing, Honey Mustard', '1 x 1 gal'),
        
        # Oils - typically 35 lb containers  
        ('Dry Goods, Oil, Canola, Clear, Frying', '1 x 35 lb'),
        
        # Milk - 4 gallon cases
        ('Dairy, Milk, Whole', '4 x 1 gal'),
        
        # Heavy Cream - 12 quart cases
        ('Dairy, Cream, Heavy', '12 x 1 qt'),
        
        # Other common dressings - 1 gallon
        ('Dairy, Sauce, Blue Cheese Dressing, Chunky', '1 x 1 gal'),
        
        # Chicken breading - typically large bags
        ('Dry Goods, Chicken  Breading, Lea Jane Recipe', '1 x 25 lb'),
    ]
    
    print("Fixing critical pack sizes...")
    
    for item_desc, correct_pack_size in pack_size_fixes:
        result = cursor.execute(
            "UPDATE inventory SET pack_size = ? WHERE item_description = ?",
            (correct_pack_size, item_desc)
        )
        
        if result.rowcount > 0:
            print(f"✓ Updated {item_desc}: {correct_pack_size}")
        else:
            print(f"⚠ No match found for: {item_desc}")
    
    conn.commit()
    
    # Now recalculate all affected recipe costs
    print("\nRecalculating recipe costs...")
    
    from unit_converter import UnitConverter
    converter = UnitConverter('restaurant_calculator.db')
    
    # Get all recipe ingredients that need recalculation
    affected_ingredients = cursor.execute("""
        SELECT ri.id, ri.recipe_id, ri.ingredient_id, ri.quantity, ri.unit_of_measure,
               inv.current_price, inv.pack_size, inv.yield_percent, inv.density_g_per_ml, inv.count_to_weight_g
        FROM recipe_ingredients ri
        JOIN inventory inv ON ri.ingredient_id = inv.id
        WHERE inv.item_description IN (?, ?, ?, ?, ?, ?)
    """, [item_desc for item_desc, _ in pack_size_fixes]).fetchall()
    
    print(f"Found {len(affected_ingredients)} ingredient entries to recalculate")
    
    for ingredient in affected_ingredients:
        ing_id, recipe_id, inv_id, quantity, unit = ingredient[:5]
        inventory_data = {
            'current_price': ingredient[5],
            'pack_size': ingredient[6], 
            'yield_percent': ingredient[7] or 100,
            'density_g_per_ml': ingredient[8],
            'count_to_weight_g': ingredient[9]
        }
        
        try:
            new_cost = converter.calculate_ingredient_cost(inventory_data, quantity, unit)
            cursor.execute(
                "UPDATE recipe_ingredients SET cost = ? WHERE id = ?",
                (new_cost, ing_id)
            )
            print(f"  ✓ Updated ingredient cost: ${new_cost:.2f}")
        except Exception as e:
            print(f"  ⚠ Error calculating cost for ingredient {ing_id}: {e}")
    
    # Recalculate total recipe costs
    affected_recipes = cursor.execute("""
        SELECT DISTINCT recipe_id FROM recipe_ingredients ri
        JOIN inventory inv ON ri.ingredient_id = inv.id
        WHERE inv.item_description IN (?, ?, ?, ?, ?, ?)
    """, [item_desc for item_desc, _ in pack_size_fixes]).fetchall()
    
    print(f"\nUpdating {len(affected_recipes)} recipe totals...")
    
    for (recipe_id,) in affected_recipes:
        cursor.execute("""
            UPDATE recipes 
            SET food_cost = (
                SELECT COALESCE(SUM(cost), 0) 
                FROM recipe_ingredients 
                WHERE recipe_id = ?
            )
            WHERE id = ?
        """, (recipe_id, recipe_id))
    
    conn.commit()
    conn.close()
    
    print("✓ Pack size fixes complete!")
    print("\nChecking results...")
    
    # Show the fixed items
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    fixed_recipes = cursor.execute("""
        SELECT recipe_name, food_cost, menu_price, 
               ROUND((food_cost/menu_price)*100, 2) as food_cost_percent
        FROM recipes 
        WHERE recipe_name IN ('DP-03 Honey Mustard', 'Hot Honey - portion', 'Buffalo Sauce - portion')
        AND menu_price > 0
        ORDER BY food_cost_percent DESC
    """).fetchall()
    
    print("\nSauce recipes after fix:")
    for recipe_name, food_cost, menu_price, food_cost_percent in fixed_recipes:
        print(f"{recipe_name}: ${food_cost:.2f} / ${menu_price:.2f} = {food_cost_percent}%")
    
    conn.close()

if __name__ == "__main__":
    fix_pack_sizes()