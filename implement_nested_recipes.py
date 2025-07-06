#!/usr/bin/env python3
"""
Implement nested/prep recipe support with proper cost calculation
"""

import sqlite3
from decimal import Decimal
from typing import Dict, List, Tuple, Optional
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))
from unit_converter import UnitConverter

DATABASE = 'restaurant_calculator.db'

class NestedRecipeCalculator:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.converter = UnitConverter(db_path)
        self.calculation_cache = {}
        
    def run_migration(self):
        """Run the SQL migration to create recipe_components table"""
        migration_path = Path('migrations/add_recipe_components.sql')
        
        if not migration_path.exists():
            print("Migration file not found!")
            return False
            
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
            
        try:
            # Execute migration
            cursor = self.conn.cursor()
            cursor.executescript(migration_sql)
            self.conn.commit()
            
            # Get migration results
            result = cursor.execute("""
                SELECT COUNT(*) as migrated_count 
                FROM recipe_components 
                WHERE notes = 'Migrated from recipe_ingredients'
            """).fetchone()
            
            print(f"✓ Migration completed successfully")
            print(f"✓ Migrated {result['migrated_count']} prep recipe relationships")
            
            return True
            
        except sqlite3.Error as e:
            print(f"Migration error: {e}")
            self.conn.rollback()
            return False
    
    def calculate_prep_recipe_unit_cost(self, recipe_id: int) -> Tuple[Decimal, str]:
        """
        Calculate the unit cost of a prep recipe based on yield
        Returns (cost_per_unit, unit)
        """
        # Check cache first
        if recipe_id in self.calculation_cache:
            return self.calculation_cache[recipe_id]
            
        cursor = self.conn.cursor()
        
        # Get recipe details
        recipe = cursor.execute("""
            SELECT id, recipe_name, recipe_type, food_cost, 
                   prep_recipe_yield, prep_recipe_yield_uom
            FROM recipes 
            WHERE id = ?
        """, (recipe_id,)).fetchone()
        
        if not recipe:
            return Decimal('0'), 'each'
            
        # Calculate total cost including components
        total_cost = self.calculate_recipe_cost(recipe_id)
        
        # Determine unit cost based on yield
        if recipe['prep_recipe_yield'] and recipe['prep_recipe_yield_uom']:
            try:
                yield_qty = Decimal(str(recipe['prep_recipe_yield']))
                if yield_qty > 0:
                    unit_cost = total_cost / yield_qty
                    unit = recipe['prep_recipe_yield_uom']
                else:
                    unit_cost = total_cost
                    unit = 'batch'
            except:
                unit_cost = total_cost
                unit = 'batch'
        else:
            unit_cost = total_cost
            unit = 'batch'
            
        # Cache the result
        self.calculation_cache[recipe_id] = (unit_cost, unit)
        
        return unit_cost, unit
    
    def calculate_recipe_cost(self, recipe_id: int, depth: int = 0) -> Decimal:
        """
        Recursively calculate recipe cost including nested prep recipes
        """
        if depth > 10:  # Prevent infinite recursion
            print(f"Warning: Max nesting depth reached for recipe {recipe_id}")
            return Decimal('0')
            
        cursor = self.conn.cursor()
        total_cost = Decimal('0')
        
        # 1. Calculate cost from regular ingredients
        ingredients = cursor.execute("""
            SELECT ri.*, i.current_price, i.pack_size, i.yield_percent
            FROM recipe_ingredients ri
            LEFT JOIN inventory i ON ri.ingredient_id = i.id
            WHERE ri.recipe_id = ? AND ri.ingredient_type != 'PrepRecipe'
        """, (recipe_id,)).fetchall()
        
        for ing in ingredients:
            if ing['ingredient_id'] and ing['current_price']:
                try:
                    # Create inventory item dict for converter
                    inv_item = {
                        'current_price': ing['current_price'],
                        'pack_size': ing['pack_size'],
                        'yield_percent': ing['yield_percent'] or 100
                    }
                    
                    cost = self.converter.calculate_ingredient_cost(
                        inv_item,
                        float(ing['quantity']),
                        ing['unit_of_measure']
                    )
                    total_cost += Decimal(str(cost))
                except Exception as e:
                    print(f"Error calculating cost for ingredient {ing['ingredient_name']}: {e}")
        
        # 2. Calculate cost from recipe components (new table)
        components = cursor.execute("""
            SELECT rc.*, r.recipe_name
            FROM recipe_components rc
            JOIN recipes r ON rc.component_recipe_id = r.id
            WHERE rc.parent_recipe_id = ?
        """, (recipe_id,)).fetchall()
        
        for comp in components:
            # Get the unit cost of the component recipe
            comp_unit_cost, comp_unit = self.calculate_prep_recipe_unit_cost(
                comp['component_recipe_id']
            )
            
            # Convert quantity if needed
            try:
                if comp['unit_of_measure'] != comp_unit:
                    # Try to convert units
                    # For now, assume same unit (this would need enhancement)
                    quantity = Decimal(str(comp['quantity']))
                else:
                    quantity = Decimal(str(comp['quantity']))
                    
                comp_cost = comp_unit_cost * quantity
                total_cost += comp_cost
                
            except Exception as e:
                print(f"Error calculating component cost for {comp['component_recipe_name']}: {e}")
        
        # 3. Also check old-style prep recipe ingredients for completeness
        prep_ingredients = cursor.execute("""
            SELECT ri.*, r.id as prep_recipe_id, r.recipe_name as prep_recipe_name
            FROM recipe_ingredients ri
            JOIN recipes r ON ri.ingredient_name = r.recipe_name
            WHERE ri.recipe_id = ? 
              AND ri.ingredient_type = 'PrepRecipe'
              AND r.recipe_type = 'PrepRecipe'
              AND NOT EXISTS (
                  SELECT 1 FROM recipe_components rc 
                  WHERE rc.parent_recipe_id = ri.recipe_id 
                    AND rc.component_recipe_id = r.id
              )
        """, (recipe_id,)).fetchall()
        
        for prep_ing in prep_ingredients:
            # Get the unit cost of the prep recipe
            prep_unit_cost, prep_unit = self.calculate_prep_recipe_unit_cost(
                prep_ing['prep_recipe_id']
            )
            
            try:
                quantity = Decimal(str(prep_ing['quantity']))
                prep_cost = prep_unit_cost * quantity
                total_cost += prep_cost
            except Exception as e:
                print(f"Error calculating prep recipe cost for {prep_ing['prep_recipe_name']}: {e}")
        
        return total_cost
    
    def update_all_recipe_costs(self):
        """Recalculate all recipe costs with proper nesting support"""
        cursor = self.conn.cursor()
        
        # Get all recipes, starting with prep recipes
        recipes = cursor.execute("""
            SELECT id, recipe_name, recipe_type 
            FROM recipes 
            ORDER BY 
                CASE WHEN recipe_type = 'PrepRecipe' THEN 0 ELSE 1 END,
                recipe_name
        """).fetchall()
        
        updated_count = 0
        
        print("\nRecalculating recipe costs with nested recipe support...")
        print("-" * 60)
        
        for recipe in recipes:
            old_cost = cursor.execute(
                "SELECT food_cost FROM recipes WHERE id = ?", 
                (recipe['id'],)
            ).fetchone()[0] or 0
            
            new_cost = float(self.calculate_recipe_cost(recipe['id']))
            
            # Update the recipe
            cursor.execute("""
                UPDATE recipes 
                SET food_cost = ?,
                    updated_date = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_cost, recipe['id']))
            
            if abs(old_cost - new_cost) > 0.01:
                updated_count += 1
                print(f"{recipe['recipe_name']:<40} ${old_cost:>8.2f} → ${new_cost:>8.2f}")
        
        self.conn.commit()
        print(f"\nUpdated {updated_count} recipe costs")
    
    def generate_nesting_report(self):
        """Generate a report showing recipe nesting structure"""
        cursor = self.conn.cursor()
        
        print("\n" + "="*80)
        print("RECIPE NESTING STRUCTURE REPORT")
        print("="*80)
        
        # Find all recipes that use other recipes
        nested_recipes = cursor.execute("""
            SELECT DISTINCT
                parent.id as parent_id,
                parent.recipe_name as parent_name,
                parent.recipe_type as parent_type,
                parent.food_cost as parent_cost
            FROM recipes parent
            WHERE EXISTS (
                SELECT 1 FROM recipe_components rc WHERE rc.parent_recipe_id = parent.id
            )
            OR EXISTS (
                SELECT 1 FROM recipe_ingredients ri 
                WHERE ri.recipe_id = parent.id AND ri.ingredient_type = 'PrepRecipe'
            )
            ORDER BY parent.recipe_name
        """).fetchall()
        
        for parent in nested_recipes:
            print(f"\n{parent['parent_name']} ({parent['parent_type']})")
            print(f"Total Cost: ${parent['parent_cost']:.2f}")
            print("  Components:")
            
            # Get components from new table
            components = cursor.execute("""
                SELECT 
                    r.recipe_name,
                    r.recipe_type,
                    rc.quantity,
                    rc.unit_of_measure,
                    rc.cost,
                    r.food_cost as unit_cost
                FROM recipe_components rc
                JOIN recipes r ON rc.component_recipe_id = r.id
                WHERE rc.parent_recipe_id = ?
                ORDER BY r.recipe_name
            """, (parent['parent_id'],)).fetchall()
            
            for comp in components:
                print(f"    - {comp['quantity']} {comp['unit_of_measure']} {comp['recipe_name']}")
                print(f"      (Unit cost: ${comp['unit_cost']:.2f})")
            
            # Also check old-style prep ingredients
            prep_ings = cursor.execute("""
                SELECT 
                    ri.ingredient_name,
                    ri.quantity,
                    ri.unit_of_measure,
                    ri.cost
                FROM recipe_ingredients ri
                WHERE ri.recipe_id = ? AND ri.ingredient_type = 'PrepRecipe'
                ORDER BY ri.ingredient_name
            """, (parent['parent_id'],)).fetchall()
            
            for prep in prep_ings:
                if not any(c['recipe_name'] == prep['ingredient_name'] for c in components):
                    print(f"    - {prep['quantity']} {prep['unit_of_measure']} {prep['ingredient_name']} (legacy)")
    
    def close(self):
        self.conn.close()

def main():
    calc = NestedRecipeCalculator(DATABASE)
    
    # Run migration
    if calc.run_migration():
        # Update all recipe costs
        calc.update_all_recipe_costs()
        
        # Generate report
        calc.generate_nesting_report()
    
    calc.close()

if __name__ == '__main__':
    main()