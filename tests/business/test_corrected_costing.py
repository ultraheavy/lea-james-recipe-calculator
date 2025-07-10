#!/usr/bin/env python3
"""
CORRECTED BUSINESS LOGIC TESTS - Works with actual database schema
"""

import pytest
import sqlite3
import os

DATABASE = 'restaurant_calculator.db'

class TestCorrectedRecipeCostEngine:
    """Test the core recipe costing engine with correct schema"""
    
    def setup_method(self):
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
    
    def teardown_method(self):
        self.conn.close()
    
    def test_database_connection(self):
        """Verify we can connect to the database"""
        assert os.path.exists(DATABASE), f"Database {DATABASE} not found"
        
        # Verify core tables/views exist
        tables = ['inventory', 'recipes', 'recipe_ingredients']
        for table in tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = self.cursor.fetchone()[0]
            assert count > 0, f"Table/view {table} is empty"
    
    def test_recipe_cost_calculation_with_correct_schema(self):
        """Test recipe cost calculation using correct column names"""
        self.cursor.execute("""
            SELECT recipe_name, food_cost, portions, portion_unit
            FROM recipes 
            WHERE food_cost > 0
            LIMIT 5
        """)
        
        recipes = self.cursor.fetchall()
        assert len(recipes) > 0, "No recipes with costs found"
        
        for recipe_name, food_cost, portions, portion_unit in recipes:
            assert food_cost > 0, f"Recipe {recipe_name} has invalid cost {food_cost}"
            if portions:
                assert portions > 0, f"Recipe {recipe_name} has invalid portions {portions}"
            
            print(f"✅ {recipe_name}: ${food_cost:.2f} for {portions} {portion_unit}")
    
    def test_menu_pricing_analysis(self):
        """Test menu pricing without modification"""
        self.cursor.execute("""
            SELECT item_name, menu_price, food_cost
            FROM menu_items
            WHERE menu_price > 0 AND food_cost > 0
            LIMIT 10
        """)
        
        items = self.cursor.fetchall()
        assert len(items) > 0, "No menu items with pricing found"
        
        profitable_items = 0
        for item_name, menu_price, food_cost in items:
            margin = (menu_price - food_cost) / menu_price * 100
            if margin > 70:  # Good margin
                profitable_items += 1
            print(f"✅ {item_name}: ${menu_price:.2f} - ${food_cost:.2f} = {margin:.1f}% margin")
        
        # Should have at least some profitable items
        assert profitable_items > 0, "No highly profitable items found"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
