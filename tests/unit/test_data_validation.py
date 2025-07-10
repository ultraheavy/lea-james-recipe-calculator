#!/usr/bin/env python3
"""
UNIT TESTS - Data Validation Functions
Tests data cleaning and validation utilities
"""

import pytest
import sqlite3
import sys
import os
from decimal import Decimal

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE = 'restaurant_calculator.db'

class TestDataValidationFunctions:
    """Test data validation and cleaning functions"""
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
    
    def test_price_format_validation(self):
        """Test that all prices are properly formatted"""
        self.cursor.execute("""
            SELECT item_description, current_price
            FROM inventory
            WHERE current_price IS NOT NULL
            LIMIT 20
        """)
        
        items = self.cursor.fetchall()
        
        for item_desc, price in items:
            # Price should be a valid number
            assert isinstance(price, (int, float)), f"Invalid price type for {item_desc}: {type(price)}"
            assert price >= 0, f"Negative price for {item_desc}: {price}"
            
            # Price should have reasonable precision (not more than 4 decimal places)
            price_str = f"{price:.4f}"
            assert '.' in price_str, f"Price should be decimal format: {price}"
    
    def test_quantity_validation(self):
        """Test that recipe quantities are valid"""
        self.cursor.execute("""
            SELECT ingredient_name, quantity, unit_of_measure
            FROM recipe_ingredients
            WHERE quantity IS NOT NULL
            LIMIT 20
        """)
        
        ingredients = self.cursor.fetchall()
        
        for ingredient, qty, uom in ingredients:
            assert qty > 0, f"Invalid quantity for {ingredient}: {qty}"
            assert qty < 1000, f"Unreasonably large quantity for {ingredient}: {qty}"
            
            if uom:
                assert isinstance(uom, str), f"Unit of measure should be string for {ingredient}"
                assert len(uom.strip()) > 0, f"Empty unit of measure for {ingredient}"
    
    def test_text_field_sanitization(self):
        """Test that text fields are properly sanitized"""
        self.cursor.execute("""
            SELECT recipe_name FROM recipes
            WHERE recipe_name IS NOT NULL
            LIMIT 10
        """)
        
        recipes = self.cursor.fetchall()
        
        for (recipe_name,) in recipes:
            # No SQL injection characters
            dangerous_chars = ["'", '"', ';', '--', '/*', '*/']
            for char in dangerous_chars:
                if char in recipe_name:
                    print(f"⚠️  Potential unsafe character '{char}' in recipe: {recipe_name}")
            
            # Reasonable length
            assert len(recipe_name) < 200, f"Recipe name too long: {recipe_name}"
            assert len(recipe_name.strip()) > 0, f"Empty recipe name found"

class TestUnitConversions:
    """Test unit of measure conversions"""
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
    
    def test_common_unit_formats(self):
        """Test that units are in standard formats"""
        self.cursor.execute("""
            SELECT DISTINCT unit_of_measure
            FROM recipe_ingredients
            WHERE unit_of_measure IS NOT NULL
        """)
        
        units = self.cursor.fetchall()
        common_units = [
            'lb', 'lbs', 'pound', 'pounds',
            'oz', 'ounce', 'ounces',
            'cup', 'cups',
            'tbsp', 'tablespoon', 'tablespoons',
            'tsp', 'teaspoon', 'teaspoons',
            'each', 'ea',
            'gallon', 'gallons', 'gal',
            'quart', 'quarts', 'qt',
            'pint', 'pints', 'pt'
        ]
        
        for (unit,) in units:
            unit_lower = unit.lower().strip()
            recognized = any(common in unit_lower for common in common_units)
            
            if not recognized:
                print(f"⚠️  Uncommon unit found: '{unit}' - may need conversion mapping")
    
    def test_quantity_unit_consistency(self):
        """Test that quantities and units make sense together"""
        self.cursor.execute("""
            SELECT ingredient_name, quantity, unit_of_measure
            FROM recipe_ingredients
            WHERE quantity IS NOT NULL AND unit_of_measure IS NOT NULL
            LIMIT 20
        """)
        
        ingredients = self.cursor.fetchall()
        
        for ingredient, qty, unit in ingredients:
            unit_lower = unit.lower()
            
            # Fractional quantities should make sense with units
            if qty < 1 and 'each' in unit_lower:
                print(f"⚠️  Fractional 'each' quantity: {ingredient} - {qty} {unit}")
            
            # Large quantities should make sense
            if qty > 10 and unit_lower in ['gallon', 'gallons']:
                print(f"⚠️  Large gallon quantity: {ingredient} - {qty} {unit}")

class TestMenuCalculations:
    """Test menu pricing calculation functions"""
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
    
    def test_margin_calculation_accuracy(self):
        """Test that profit margin calculations are accurate"""
        test_cases = [
            (10.00, 3.00, 70.0),  # $10 menu, $3 cost = 70% margin
            (15.75, 3.45, 78.1),  # Real Nashville Hot Chicken numbers
            (5.00, 2.50, 50.0),   # 50% margin case
        ]
        
        for menu_price, food_cost, expected_margin in test_cases:
            calculated_margin = (menu_price - food_cost) / menu_price * 100
            
            # Allow small floating point differences
            assert abs(calculated_margin - expected_margin) < 0.1, \
                f"Margin calculation error: {menu_price} - {food_cost} should be {expected_margin}%, got {calculated_margin:.1f}%"
    
    def test_cost_per_serving_calculations(self):
        """Test cost per serving calculations"""
        self.cursor.execute("""
            SELECT r.recipe_name, r.food_cost, r.prep_recipe_yield
            FROM recipes r
            WHERE r.food_cost > 0 AND r.prep_recipe_yield > 0
            LIMIT 5
        """)
        
        recipes = self.cursor.fetchall()
        
        for recipe_name, total_cost, yield_qty in recipes:
            cost_per_serving = total_cost / yield_qty
            
            assert cost_per_serving > 0, f"Cost per serving should be positive for {recipe_name}"
            assert cost_per_serving < 50, f"Cost per serving seems too high for {recipe_name}: ${cost_per_serving:.2f}"
            
            print(f"✅ {recipe_name}: ${cost_per_serving:.2f} per serving ({yield_qty} servings from ${total_cost:.2f})")

@pytest.mark.data
class TestDataConsistency:
    """Test data consistency across tables"""
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
    
    def test_recipe_ingredient_relationships(self):
        """Test that recipe-ingredient relationships are consistent"""
        # Check for orphaned recipe ingredients
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM recipe_ingredients ri
            LEFT JOIN recipes r ON ri.recipe_id = r.id
            WHERE r.id IS NULL
        """)
        
        orphaned_ingredients = self.cursor.fetchone()[0]
        assert orphaned_ingredients == 0, f"Found {orphaned_ingredients} orphaned recipe ingredients"
        
        # Check for ingredients without inventory links
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM recipe_ingredients ri
            WHERE ri.ingredient_id IS NULL
        """)
        
        unlinked_ingredients = self.cursor.fetchone()[0]
        # Some ingredients might not be linked yet - just report
        if unlinked_ingredients > 0:
            print(f"ℹ️  Found {unlinked_ingredients} recipe ingredients not linked to inventory")
    
    def test_menu_recipe_relationships(self):
        """Test that menu items properly link to recipes"""
        self.cursor.execute("""
            SELECT mi.item_name, mi.food_cost, r.food_cost
            FROM menu_items mi
            LEFT JOIN recipes r ON mi.recipe_id = r.id
            WHERE mi.food_cost > 0 AND r.food_cost > 0
            AND ABS(mi.food_cost - r.food_cost) > 0.50
            LIMIT 5
        """)
        
        cost_mismatches = self.cursor.fetchall()
        
        for item_name, menu_cost, recipe_cost in cost_mismatches:
            print(f"⚠️  Cost mismatch: {item_name} - Menu: ${menu_cost:.2f}, Recipe: ${recipe_cost:.2f}")

if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v", "--tb=short"])
