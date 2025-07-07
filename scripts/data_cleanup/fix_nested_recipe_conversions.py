#!/usr/bin/env python3
"""
Fix unit conversion issues in nested recipe calculations
"""

import sqlite3
from decimal import Decimal
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))
from unit_converter import UnitConverter

DATABASE = 'restaurant_calculator.db'

def fix_recipe_component_costs():
    """Fix recipe component cost calculations with proper unit conversion"""
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    converter = UnitConverter(DATABASE)
    cursor = conn.cursor()
    
    print("Fixing recipe component cost calculations...")
    print("-" * 60)
    
    # Get all recipe components
    components = cursor.execute("""
        SELECT 
            rc.*,
            parent.recipe_name as parent_name,
            comp.recipe_name as component_name,
            comp.prep_recipe_yield,
            comp.prep_recipe_yield_uom,
            comp.food_cost as component_total_cost
        FROM recipe_components rc
        JOIN recipes parent ON rc.parent_recipe_id = parent.id
        JOIN recipes comp ON rc.component_recipe_id = comp.id
    """).fetchall()
    
    updates = []
    
    for comp in components:
        if not comp['prep_recipe_yield'] or not comp['prep_recipe_yield_uom']:
            continue
            
        try:
            # Calculate unit cost of component
            yield_qty = float(comp['prep_recipe_yield'])
            if yield_qty <= 0:
                continue
                
            unit_cost = float(comp['component_total_cost']) / yield_qty
            
            # Convert requested quantity to match yield units if needed
            requested_qty = float(comp['quantity'])
            requested_unit = comp['unit_of_measure']
            yield_unit = comp['prep_recipe_yield_uom']
            
            # If units don't match, try to convert
            if requested_unit != yield_unit:
                # Try to convert the requested quantity to yield units
                converted_qty = converter.convert_between_units(
                    requested_qty, 
                    requested_unit, 
                    yield_unit
                )
                
                if converted_qty:
                    actual_cost = converted_qty * unit_cost
                    print(f"{comp['parent_name']} uses {requested_qty} {requested_unit} of {comp['component_name']}")
                    print(f"  → Converted to {converted_qty:.4f} {yield_unit}")
                    print(f"  → Cost: ${actual_cost:.2f}")
                else:
                    # Fallback: assume units are compatible
                    actual_cost = requested_qty * unit_cost
                    print(f"Warning: Could not convert {requested_unit} to {yield_unit} for {comp['component_name']}")
            else:
                actual_cost = requested_qty * unit_cost
                
            updates.append((actual_cost, comp['id']))
            
        except Exception as e:
            print(f"Error processing {comp['component_name']}: {e}")
    
    # Update the costs
    if updates:
        cursor.executemany("""
            UPDATE recipe_components 
            SET cost = ?,
                updated_date = CURRENT_TIMESTAMP
            WHERE id = ?
        """, updates)
        
        conn.commit()
        print(f"\nUpdated {len(updates)} recipe component costs")
    
    # Now recalculate all parent recipe costs
    print("\nRecalculating parent recipe costs...")
    
    # Get all recipes that have components
    parent_recipes = cursor.execute("""
        SELECT DISTINCT r.id, r.recipe_name
        FROM recipes r
        JOIN recipe_components rc ON r.id = rc.parent_recipe_id
        ORDER BY r.recipe_name
    """).fetchall()
    
    for recipe in parent_recipes:
        # Sum up regular ingredients
        ing_cost = cursor.execute("""
            SELECT COALESCE(SUM(cost), 0) as total
            FROM recipe_ingredients
            WHERE recipe_id = ? AND ingredient_type != 'PrepRecipe'
        """, (recipe['id'],)).fetchone()['total']
        
        # Sum up recipe components
        comp_cost = cursor.execute("""
            SELECT COALESCE(SUM(cost), 0) as total
            FROM recipe_components
            WHERE parent_recipe_id = ?
        """, (recipe['id'],)).fetchone()['total']
        
        total_cost = float(ing_cost) + float(comp_cost)
        
        # Update recipe
        cursor.execute("""
            UPDATE recipes 
            SET food_cost = ?,
                updated_date = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (total_cost, recipe['id']))
        
        print(f"{recipe['recipe_name']:<40} ${total_cost:>8.2f}")
    
    conn.commit()
    conn.close()
    
    print("\nRecipe component cost fixes completed!")

def check_extreme_costs():
    """Check for recipes with extreme costs that might indicate issues"""
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    print("\nChecking for recipes with extreme costs (>$100)...")
    print("-" * 60)
    
    extreme_recipes = cursor.execute("""
        SELECT id, recipe_name, recipe_type, food_cost,
               prep_recipe_yield, prep_recipe_yield_uom
        FROM recipes
        WHERE food_cost > 100
        ORDER BY food_cost DESC
    """).fetchall()
    
    if extreme_recipes:
        print(f"Found {len(extreme_recipes)} recipes with costs > $100:")
        for r in extreme_recipes:
            print(f"{r[1]:<40} ${r[3]:>10.2f} ({r[2]})")
            if r[4]:
                print(f"  Yield: {r[4]} {r[5]}")
    else:
        print("No recipes with extreme costs found.")
    
    conn.close()

if __name__ == '__main__':
    fix_recipe_component_costs()
    check_extreme_costs()