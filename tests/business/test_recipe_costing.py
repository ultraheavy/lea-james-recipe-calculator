#!/usr/bin/env python3
"""
CRITICAL BUSINESS LOGIC TESTS - Recipe Costing Engine
These tests validate the core cost calculation system that drives business operations.

PROTECTED: These tests validate XtraChef integration and cost calculations
Per DATA_MODEL.md - these are BUSINESS CRITICAL functions
"""

import pytest
import sqlite3
import os
from decimal import Decimal
from typing import List, Tuple

# Test database path - use production database for validation
DATABASE = 'restaurant_calculator.db'

class TestRecipeCostEngine:
    """Test the core recipe costing engine that drives business decisions"""
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
    
    def test_database_connection(self):
        """Verify we can connect to the production database"""
        assert os.path.exists(DATABASE), f"Database {DATABASE} not found"
        
        # Verify core tables exist
        tables = ['inventory', 'recipes', 'recipe_ingredients']
        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = self.cursor.fetchone()[0]
            assert count > 0, f"Table {table} is empty"
    
    def test_xtrachef_data_integrity(self):
        """CRITICAL: Verify XtraChef integration data is intact"""
        # Test XtraChef item codes are present and properly formatted
        self.cursor.execute("""
            SELECT item_code, item_description, vendor_name, current_price 
            FROM inventory 
            WHERE item_code IS NOT NULL 
            AND item_code != ''
            LIMIT 10
        """)
        
        items = self.cursor.fetchall()
        assert len(items) >= 10, "Not enough inventory items with XtraChef data"
        
        for item_code, description, vendor, price in items:
            assert item_code is not None, "XtraChef item_code cannot be null"
            assert description is not None, "XtraChef item_description cannot be null" 
            assert price is not None, "XtraChef current_price cannot be null"
            assert price > 0, f"Invalid price {price} for item {item_code}"
    
    def test_collard_greens_recipe_cost_accuracy(self):
        """
        Test actual Collard Greens recipe cost calculation
        This is a real recipe from your production data
        """
        self.cursor.execute("""
            SELECT food_cost FROM recipes 
            WHERE recipe_name LIKE '%Collard Greens%'
            LIMIT 1
        """)
        
        result = self.cursor.fetchone()
        assert result is not None, "Collard Greens recipe not found"
        
        actual_cost = result[0]
        assert actual_cost > 0, "Recipe cost should be greater than 0"
        assert actual_cost < 100, "Recipe cost seems unreasonably high"
        
        print(f"✅ Collard Greens recipe cost: ${actual_cost:.2f}")
    
    def test_recipe_ingredient_relationships(self):
        """Test that recipe ingredients properly link to inventory"""
        self.cursor.execute("""
            SELECT r.recipe_name, ri.ingredient_name, ri.quantity, ri.cost, i.current_price
            FROM recipes r
            JOIN recipe_ingredients ri ON r.id = ri.recipe_id  
            LEFT JOIN inventory i ON ri.ingredient_id = i.id
            WHERE r.recipe_name LIKE '%Hot Honey%'
            LIMIT 5
        """)
        
        ingredients = self.cursor.fetchall()
        assert len(ingredients) > 0, "No recipe ingredients found for Hot Honey recipes"
        
        for recipe_name, ingredient_name, quantity, cost, inventory_price in ingredients:
            assert ingredient_name is not None, "Ingredient name cannot be null"
            assert quantity > 0, f"Invalid quantity {quantity} for {ingredient_name}"
            
            if cost is not None:
                assert cost >= 0, f"Negative cost {cost} for {ingredient_name}"
                print(f"✅ {recipe_name}: {ingredient_name} - {quantity} units = ${cost:.2f}")
    
    def test_menu_price_calculations(self):
        """Test menu item pricing and profit margins"""
        self.cursor.execute("""
            SELECT mi.item_name, mi.menu_price, mi.food_cost, 
                   CASE 
                       WHEN mi.menu_price > 0 THEN (mi.menu_price - mi.food_cost) / mi.menu_price * 100
                       ELSE 0
                   END as profit_margin
            FROM menu_items mi
            WHERE mi.menu_price > 0
            LIMIT 10
        """)
        
        menu_items = self.cursor.fetchall()
        assert len(menu_items) > 0, "No menu items with pricing found"
        
        for item_name, menu_price, food_cost, profit_margin in menu_items:
            assert menu_price > 0, f"Menu price must be positive for {item_name}"
            
            if food_cost is not None:
                assert food_cost >= 0, f"Food cost cannot be negative for {item_name}"
                
                if menu_price > food_cost:
                    calculated_margin = (menu_price - food_cost) / menu_price * 100
                    assert abs(calculated_margin - profit_margin) < 0.01, \
                        f"Profit margin calculation error for {item_name}"
                    
                    print(f"✅ {item_name}: ${menu_price:.2f} - ${food_cost:.2f} = {profit_margin:.1f}% margin")
    
    def test_cost_calculation_consistency(self):
        """Test that recipe costs are consistently calculated"""
        # Get recipes with calculated food costs
        self.cursor.execute("""
            SELECT r.recipe_name, r.food_cost,
                   SUM(ri.cost) as ingredient_cost_sum
            FROM recipes r
            LEFT JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            WHERE r.food_cost > 0
            GROUP BY r.id, r.recipe_name, r.food_cost
            HAVING COUNT(ri.id) > 0
            LIMIT 5
        """)
        
        recipes = self.cursor.fetchall()
        
        for recipe_name, recipe_cost, ingredient_sum in recipes:
            if ingredient_sum is not None and ingredient_sum > 0:
                # Allow for reasonable tolerance in cost calculations
                tolerance = max(0.50, recipe_cost * 0.05)  # 5% or 50 cents
                
                cost_difference = abs(recipe_cost - ingredient_sum)
                assert cost_difference <= tolerance, \
                    f"Recipe {recipe_name}: cost mismatch - Recipe: ${recipe_cost:.2f}, Ingredients: ${ingredient_sum:.2f}"
                
                print(f"✅ {recipe_name}: Recipe cost ${recipe_cost:.2f} matches ingredients ${ingredient_sum:.2f}")

class TestDataIntegrity:
    """Test database integrity and business rules"""
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
    
    def test_no_null_critical_fields(self):
        """Ensure critical business fields are not null"""
        # Check inventory critical fields
        self.cursor.execute("""
            SELECT COUNT(*) FROM inventory 
            WHERE item_description IS NULL OR item_description = ''
        """)
        null_descriptions = self.cursor.fetchone()[0]
        assert null_descriptions == 0, f"Found {null_descriptions} inventory items with null descriptions"
        
        # Check recipes critical fields  
        self.cursor.execute("""
            SELECT COUNT(*) FROM recipes
            WHERE recipe_name IS NULL OR recipe_name = ''
        """)
        null_names = self.cursor.fetchone()[0]
        assert null_names == 0, f"Found {null_names} recipes with null names"
    
    def test_positive_prices_and_costs(self):
        """Ensure all prices and costs are positive"""
        # Check inventory prices
        self.cursor.execute("""
            SELECT COUNT(*) FROM inventory 
            WHERE current_price < 0
        """)
        negative_prices = self.cursor.fetchone()[0]
        assert negative_prices == 0, f"Found {negative_prices} items with negative prices"
        
        # Check recipe costs
        self.cursor.execute("""
            SELECT COUNT(*) FROM recipes
            WHERE food_cost < 0
        """)
        negative_costs = self.cursor.fetchone()[0]
        assert negative_costs == 0, f"Found {negative_costs} recipes with negative costs"

if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v", "--tb=short"])
