#!/usr/bin/env python3
"""
Recalculate all recipe costs using proper unit conversion
This fixes the broken cost calculations in existing recipes
"""

import sqlite3
from unit_converter import UnitConverter

DATABASE = 'restaurant_calculator.db'

def recalculate_all_recipe_costs():
    """Recalculate costs for all recipes using proper unit conversion"""
    
    converter = UnitConverter(DATABASE)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Get all recipes
        recipes = cursor.execute('SELECT id, recipe_name FROM recipes').fetchall()
        print(f"Found {len(recipes)} recipes to recalculate\n")
        
        updated_count = 0
        error_count = 0
        
        for recipe in recipes:
            recipe_id = recipe['id']
            recipe_name = recipe['recipe_name']
            
            print(f"Processing recipe: {recipe_name}")
            
            # Get all ingredients for this recipe
            ingredients = cursor.execute('''
                SELECT ri.*, i.*
                FROM recipe_ingredients ri
                JOIN inventory i ON ri.ingredient_id = i.id
                WHERE ri.recipe_id = ?
            ''', (recipe_id,)).fetchall()
            
            total_cost = 0
            ingredient_updates = []
            
            for ing in ingredients:
                try:
                    # Calculate proper cost
                    cost = converter.calculate_ingredient_cost(
                        dict(ing),  # Contains inventory fields
                        ing['quantity'],
                        ing['unit_of_measure']
                    )
                    
                    total_cost += cost
                    ingredient_updates.append((cost, ing['id']))
                    
                    print(f"  - {ing['ingredient_name']}: {ing['quantity']} {ing['unit_of_measure']} = ${cost:.4f}")
                    
                except Exception as e:
                    print(f"  ERROR calculating {ing['ingredient_name']}: {e}")
                    error_count += 1
                    # Keep existing cost
                    total_cost += ing['cost'] or 0
                    ingredient_updates.append((ing['cost'] or 0, ing['id']))
            
            # Update individual ingredient costs
            for cost, ing_id in ingredient_updates:
                cursor.execute('''
                    UPDATE recipe_ingredients 
                    SET cost = ? 
                    WHERE id = ?
                ''', (cost, ing_id))
            
            # Update recipe total cost
            cursor.execute('''
                UPDATE recipes 
                SET food_cost = ?,
                    prime_cost = ? + COALESCE(labor_cost, 0)
                WHERE id = ?
            ''', (total_cost, total_cost, recipe_id))
            
            print(f"  Total cost: ${total_cost:.2f}\n")
            updated_count += 1
            
        conn.commit()
        
        print("="*50)
        print(f"Recalculation complete!")
        print(f"Updated: {updated_count} recipes")
        print(f"Errors: {error_count} ingredients")
        
    except Exception as e:
        print(f"Fatal error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print("Recipe Cost Recalculation")
    print("="*50)
    print("This will recalculate all recipe costs using proper unit conversion.")
    print("This fixes the previous incorrect calculations that didn't account for")
    print("pack sizes, units of measure, and yields.\n")
    
    response = input("Continue? (y/n): ")
    if response.lower() == 'y':
        recalculate_all_recipe_costs()
    else:
        print("Cancelled.")