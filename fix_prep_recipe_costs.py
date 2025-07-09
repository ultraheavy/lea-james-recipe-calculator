#!/usr/bin/env python3
"""
Fix prep recipe cost percentages
Prep recipes should show cost per yield unit, not food cost percentage
"""

import sqlite3
from decimal import Decimal

def fix_prep_recipe_costs():
    """Fix cost calculations for prep recipes"""
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    # Start transaction
    cursor.execute("BEGIN TRANSACTION")
    
    try:
        # Get all prep recipes with incorrect food cost percentages
        prep_recipes = cursor.execute("""
            SELECT id, recipe_name, recipe_type, food_cost, menu_price, 
                   food_cost_percentage, prep_recipe_yield, prep_recipe_yield_uom
            FROM recipes 
            WHERE recipe_type = 'PrepRecipe' AND food_cost_percentage > 100
        """).fetchall()
        
        print(f"Found {len(prep_recipes)} prep recipes with incorrect cost percentages")
        
        for recipe in prep_recipes:
            recipe_id, name, recipe_type, food_cost, menu_price, old_pct, yield_qty, yield_uom = recipe
            
            # For prep recipes, we don't calculate food_cost_percentage
            # Instead, we show cost per yield unit
            if yield_qty and float(yield_qty) > 0:
                cost_per_unit = Decimal(str(food_cost)) / Decimal(str(yield_qty))
                
                # Set food_cost_percentage to 0 for prep recipes (not applicable)
                cursor.execute("""
                    UPDATE recipes 
                    SET food_cost_percentage = 0
                    WHERE id = ?
                """, (recipe_id,))
                
                print(f"Fixed {name}: ${food_cost:.2f} for {yield_qty} {yield_uom} = ${cost_per_unit:.2f}/{yield_uom}")
        
        # Commit transaction
        cursor.execute("COMMIT")
        print("\nSuccessfully fixed prep recipe costs")
        
    except Exception as e:
        cursor.execute("ROLLBACK")
        print(f"Error: {e}")
        raise
    
    finally:
        conn.close()

def validate_recipe_costs():
    """Validate all recipe costs are reasonable"""
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    # Check for any remaining high percentages
    issues = cursor.execute("""
        SELECT recipe_name, recipe_type, food_cost_percentage
        FROM recipes 
        WHERE food_cost_percentage > 100
        ORDER BY food_cost_percentage DESC
    """).fetchall()
    
    if issues:
        print("\nRemaining recipes with >100% food cost:")
        for name, rtype, pct in issues:
            print(f"  {name} ({rtype}): {pct:.1f}%")
    else:
        print("\nAll recipe cost percentages are now reasonable")
    
    conn.close()

if __name__ == "__main__":
    print("Fixing prep recipe cost calculations...")
    fix_prep_recipe_costs()
    validate_recipe_costs()