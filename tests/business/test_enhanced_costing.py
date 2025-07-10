#!/usr/bin/env python3
"""
ENHANCED RECIPE COSTING ENGINE TESTS
Additional critical tests for cost propagation and yield calculations
"""

import pytest
import sqlite3
import os
import sys
from decimal import Decimal
from typing import List, Tuple

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cost_utils import CostCalculator

DATABASE = 'restaurant_calculator.db'

class TestCostPropagation:
    """Test that price changes properly propagate through the system"""
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
        self.calculator = CostCalculator()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
        self.calculator.close()
    
    def test_ingredient_price_change_propagation(self):
        """Test that ingredient price changes update recipe costs"""
        # Find a recipe with ingredients linked to inventory
        self.cursor.execute("""
            SELECT DISTINCT r.id, r.recipe_name, r.food_cost
            FROM recipes r
            JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            JOIN inventory i ON ri.ingredient_id = i.id
            WHERE r.food_cost > 0 AND i.current_price > 0
            LIMIT 1
        """)
        
        recipe = self.cursor.fetchone()
        
        if not recipe:
            pytest.skip("No suitable recipe found for price propagation test")
        
        recipe_id, recipe_name, original_cost = recipe
        
        # Get the first ingredient for this recipe
        self.cursor.execute("""
            SELECT ri.ingredient_id, i.current_price, ri.quantity
            FROM recipe_ingredients ri
            JOIN inventory i ON ri.ingredient_id = i.id
            WHERE ri.recipe_id = ? AND i.current_price > 0
            LIMIT 1
        """, (recipe_id,))
        
        ingredient = self.cursor.fetchone()
        
        if not ingredient:
            pytest.skip("No suitable ingredient found for price propagation test")
        
        ingredient_id, original_price, quantity = ingredient
        
        # Save original price for restoration
        self.cursor.execute("""
            UPDATE inventory 
            SET current_price = current_price * 1.1 
            WHERE id = ?
        """, (ingredient_id,))
        self.conn.commit()
        
        try:
            # Recalculate recipe cost
            new_cost, status = self.calculator.calc_recipe_cost(recipe_id)
            
            # Verify cost increased (should be higher due to 10% price increase)
            assert new_cost > original_cost, \
                f"Recipe cost should increase when ingredient price increases: {original_cost} -> {new_cost}"
            
            print(f"✅ Price propagation: {recipe_name} cost increased from ${original_cost:.2f} to ${new_cost:.2f}")
            
        finally:
            # Restore original price
            self.cursor.execute("""
                UPDATE inventory 
                SET current_price = ? 
                WHERE id = ?
            """, (original_price, ingredient_id))
            self.conn.commit()

class TestYieldCalculations:
    """Test recipe yield percentage calculations"""
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
        self.calculator = CostCalculator()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
        self.calculator.close()
    
    def test_prep_recipe_yield_validation(self):
        """Test that prep recipe yields are reasonable"""
        self.cursor.execute("""
            SELECT recipe_name, prep_recipe_yield, prep_recipe_yield_uom
            FROM recipes
            WHERE prep_recipe_yield > 0
            LIMIT 10
        """)
        
        recipes = self.cursor.fetchall()
        assert len(recipes) > 0, "No recipes with yield data found"
        
        for recipe_name, yield_qty, yield_uom in recipes:
            assert yield_qty > 0, f"Recipe {recipe_name} has invalid yield: {yield_qty}"
            assert yield_uom is not None, f"Recipe {recipe_name} missing yield UOM"
            
            # Reasonable yield ranges
            if yield_uom and yield_uom.lower() in ['portions', 'each']:
                assert 1 <= yield_qty <= 1000, f"Recipe {recipe_name} unreasonable portion yield: {yield_qty}"
            elif yield_uom and yield_uom.lower() in ['lb', 'lbs', 'pounds']:
                assert 0.1 <= yield_qty <= 100, f"Recipe {recipe_name} unreasonable weight yield: {yield_qty}"
            
            print(f"✅ {recipe_name}: {yield_qty} {yield_uom}")
    
    def test_waste_percentage_calculations(self):
        """Test that waste percentages are calculated correctly"""
        # Find ingredients with prep yield percentages
        self.cursor.execute("""
            SELECT ingredient_name, prep_recipe_yield_percentage
            FROM recipe_ingredients
            WHERE prep_recipe_yield_percentage > 0 AND prep_recipe_yield_percentage < 100
            LIMIT 5
        """)
        
        ingredients = self.cursor.fetchall()
        
        for ingredient_name, yield_percentage in ingredients:
            waste_percentage = 100 - yield_percentage
            
            # Reasonable waste ranges (5% - 50%)
            assert 5 <= waste_percentage <= 50, \
                f"Ingredient {ingredient_name} has unreasonable waste: {waste_percentage}%"
            
            # Yield should account for waste
            assert 50 <= yield_percentage <= 95, \
                f"Ingredient {ingredient_name} has unreasonable yield: {yield_percentage}%"
            
            print(f"✅ {ingredient_name}: {yield_percentage}% yield ({waste_percentage}% waste)")

class TestMenuProfitability:
    """Test menu item profitability calculations"""
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
    
    def test_profit_margin_validation(self):
        """Test that all menu items have reasonable profit margins"""
        self.cursor.execute("""
            SELECT item_name, menu_price, food_cost,
                   CASE 
                       WHEN menu_price > 0 THEN (menu_price - food_cost) / menu_price * 100
                       ELSE 0
                   END as profit_margin
            FROM menu_items
            WHERE menu_price > 0 AND food_cost > 0
        """)
        
        items = self.cursor.fetchall()
        assert len(items) > 0, "No menu items with complete pricing found"
        
        profitable_items = 0
        
        for item_name, menu_price, food_cost, profit_margin in items:
            # Business validation: profit margin should be between 60-90%
            if profit_margin >= 60:
                profitable_items += 1
                print(f"✅ {item_name}: {profit_margin:.1f}% margin (${menu_price:.2f} - ${food_cost:.2f})")
            else:
                print(f"⚠️  {item_name}: LOW {profit_margin:.1f}% margin (${menu_price:.2f} - ${food_cost:.2f})")
        
        # At least 70% of items should have good profit margins
        profit_rate = profitable_items / len(items) * 100
        assert profit_rate >= 70, \
            f"Only {profit_rate:.1f}% of items have good profit margins (should be >=70%)"
    
    def test_menu_price_vs_cost_relationship(self):
        """Test that menu prices are always higher than food costs"""
        self.cursor.execute("""
            SELECT item_name, menu_price, food_cost
            FROM menu_items
            WHERE menu_price > 0 AND food_cost > 0
        """)
        
        items = self.cursor.fetchall()
        
        for item_name, menu_price, food_cost in items:
            assert menu_price > food_cost, \
                f"Menu item {item_name} is priced below cost: ${menu_price:.2f} <= ${food_cost:.2f}"
            
            # Menu price should be at least 2x food cost (minimum 50% margin)
            minimum_price = food_cost * 2
            if menu_price < minimum_price:
                print(f"⚠️  {item_name}: Price ${menu_price:.2f} may be too low (cost: ${food_cost:.2f})")

@pytest.mark.business
class TestCriticalBusinessRules:
    """Test critical business rules that must never be violated"""
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
    
    def test_no_free_menu_items(self):
        """Ensure no menu items are priced at zero or negative"""
        self.cursor.execute("""
            SELECT item_name, menu_price 
            FROM menu_items 
            WHERE menu_price <= 0
        """)
        
        free_items = self.cursor.fetchall()
        assert len(free_items) == 0, f"Found menu items with zero/negative prices: {free_items}"
    
    def test_inventory_price_sanity(self):
        """Test that inventory prices are within reasonable ranges"""
        self.cursor.execute("""
            SELECT item_description, current_price
            FROM inventory
            WHERE current_price > 1000 OR current_price < 0
        """)
        
        extreme_prices = self.cursor.fetchall()
        
        # Allow some high-priced items (like specialty ingredients) but flag for review
        if extreme_prices:
            for item, price in extreme_prices:
                print(f"⚠️  Extreme price detected: {item} = ${price:.2f}")
        
        # No negative prices allowed
        self.cursor.execute("""
            SELECT COUNT(*) FROM inventory WHERE current_price < 0
        """)
        negative_count = self.cursor.fetchone()[0]
        assert negative_count == 0, f"Found {negative_count} items with negative prices"

if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v", "--tb=short"])
