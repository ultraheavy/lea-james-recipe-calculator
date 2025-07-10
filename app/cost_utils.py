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
            SELECT recipe_name, portions, portions_uom
            FROM recipes
            WHERE id = ?
        """, (recipe_id,)).fetchone()
        
        if not recipe:
            return Decimal('0'), "Recipe not found"
        
        recipe_name, portions, portions_uom = recipe
        logger.info(f"Calculating cost for recipe: {recipe_name}")
        
        # Get recipe ingredients with vendor product details
        ingredients = cursor.execute("""
            SELECT 
                ri.quantity,
                ri.uom,
                i.ingredient_name,
                vp.case_price,
                vp.pack_size,
                vp.purchase_unit
            FROM recipe_ingredients ri
            JOIN inventory_items i ON ri.inventory_id = i.id
            LEFT JOIN vendor_products vp ON i.primary_vendor_product_id = vp.id
            WHERE ri.recipe_id = ?
        """, (recipe_id,)).fetchall()
        
        total_cost = Decimal('0')
        messages = []
        
        for ing_qty, ing_uom, ing_name, case_price, pack_size, purchase_unit in ingredients:
            if not all([case_price, pack_size, purchase_unit]):
                messages.append(f"⚠️ {ing_name}: Missing vendor pricing")
                continue
            
            try:
                # Calculate unit cost
                unit_cost = Decimal(str(case_price)) / Decimal(str(pack_size))
                
                # Calculate ingredient cost
                ingredient_cost = Decimal(str(ing_qty)) * unit_cost
                total_cost += ingredient_cost
                
                logger.debug(f"{ing_name}: {ing_qty} {ing_uom} × ${unit_cost:.4f} = ${ingredient_cost:.4f}")
                
            except Exception as e:
                messages.append(f"❌ {ing_name}: Calculation error - {str(e)}")
                logger.error(f"Error calculating cost for {ing_name}: {e}")
        
        # Calculate cost per portion
        if portions and total_cost > 0:
            cost_per_portion = total_cost / Decimal(str(portions))
            status = f"✅ Total: ${total_cost:.2f} | Per {portions_uom}: ${cost_per_portion:.2f}"
        else:
            status = f"Total: ${total_cost:.2f}"
        
        if messages:
            status += " | " + " | ".join(messages[:2])  # Limit to 2 messages
        
        return total_cost, status
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()


def calculate_recipe_cost(db_path: str, recipe_id: int) -> Tuple[Decimal, str]:
    """
    Convenience function for recipe cost calculation
    """
    calculator = CostCalculator(db_path)
    return calculator.calc_recipe_cost(recipe_id)