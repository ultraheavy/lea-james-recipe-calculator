#!/usr/bin/env python3
"""
cost_utils.py - Recipe cost calculation utilities
"""

import sqlite3
from decimal import Decimal
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class CostCalculator:
    """Handle recipe cost calculations with unit conversions"""
    
    def __init__(self, db_path: str = 'restaurant_calculator.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
    
    def calc_recipe_cost(self, recipe_id: int) -> Tuple[Decimal, str]:
        """
        Calculate total cost for a recipe
        
        Returns (total_cost, status_message)
        """
        cursor = self.conn.cursor()
        
        # Get recipe info
        recipe = cursor.execute("""
            SELECT recipe_name, prep_recipe_yield, prep_recipe_yield_uom
            FROM recipes
            WHERE id = ?
        """, (recipe_id,)).fetchone()
        
        if not recipe:
            return Decimal('0'), "Recipe not found"
        
        recipe_name, yield_qty, yield_uom = recipe
        
        # Handle portions yield UOM
        if yield_uom and yield_uom.lower() == 'portions':
            yield_uom = 'each'
        
        # Get ingredients
        ingredients = cursor.execute("""
            SELECT 
                ri.id,
                ri.ingredient_name,
                ri.quantity,
                ri.unit_of_measure,
                ri.ingredient_id,
                i.current_price,
                i.pack_size,
                i.purchase_unit,
                i.recipe_cost_unit
            FROM recipe_ingredients ri
            LEFT JOIN inventory i ON ri.ingredient_id = i.id
            WHERE ri.recipe_id = ?
        """, (recipe_id,)).fetchall()
        
        total_cost = Decimal('0')
        errors = []
        
        for ing in ingredients:
            ing_id, ing_name, qty, uom, inv_id, price, pack_size, purchase_unit, recipe_unit = ing
            
            if not inv_id or not price:
                errors.append(f"Missing price for {ing_name}")
                continue
            
            try:
                # Calculate ingredient cost
                ing_cost = self._calculate_ingredient_cost(
                    qty, uom, price, pack_size, purchase_unit, recipe_unit
                )
                total_cost += ing_cost
                
                # Update ingredient cost
                cursor.execute("""
                    UPDATE recipe_ingredients
                    SET cost = ?
                    WHERE id = ?
                """, (float(ing_cost), ing_id))
                
            except Exception as e:
                errors.append(f"Error calculating {ing_name}: {str(e)}")
        
        # Update recipe total cost
        cursor.execute("""
            UPDATE recipes
            SET food_cost = ?
            WHERE id = ?
        """, (float(total_cost), recipe_id))
        
        self.conn.commit()
        
        status = "OK" if not errors else f"Warnings: {'; '.join(errors)}"
        return total_cost, status
    
    def _calculate_ingredient_cost(self, quantity: float, unit: str, 
                                 price: float, pack_size: str, 
                                 purchase_unit: str, recipe_unit: str) -> Decimal:
        """Calculate cost for a single ingredient"""
        # Parse pack size to get quantity and unit
        from etl import ETLPipeline
        etl = ETLPipeline(':memory:')  # Just for parsing
        pack_qty, pack_unit = etl.parse_pack_size(pack_size) if pack_size else (1.0, purchase_unit)
        
        # Calculate cost per unit
        if pack_qty > 0:
            cost_per_unit = Decimal(str(price)) / Decimal(str(pack_qty))
        else:
            cost_per_unit = Decimal(str(price))
        
        # Simple calculation (would need unit conversion in real implementation)
        return cost_per_unit * Decimal(str(quantity))
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    """Test cost calculations"""
    calc = CostCalculator()
    
    # Example: Calculate cost for recipe 93 (Chilli Oil)
    cost, status = calc.calc_recipe_cost(93)
    print(f"Recipe 93 cost: ${cost:.2f} - {status}")
    
    calc.close()

if __name__ == '__main__':
    main()