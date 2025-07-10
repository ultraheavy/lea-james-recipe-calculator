#!/usr/bin/env python3
"""
UNIT TESTS - Cost Utilities Module
Tests individual cost calculation functions
"""

import pytest
import sys
import os
from decimal import Decimal

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cost_utils import CostCalculator

class TestCostCalculator:
    """Test the CostCalculator class functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.calculator = CostCalculator()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.calculator.close()
    
    def test_calculator_initialization(self):
        """Test that calculator initializes properly"""
        assert self.calculator.db_path == 'restaurant_calculator.db'
        assert self.calculator.conn is not None
    
    def test_calculate_ingredient_cost_basic(self):
        """Test basic ingredient cost calculation"""
        # Test: 1 lb of ingredient at $5.00/lb
        cost = self.calculator._calculate_ingredient_cost(
            quantity=1.0,
            unit='lb',
            price=5.00,
            pack_size='1 lb',
            purchase_unit='lb',
            recipe_unit='lb'
        )
        
        assert isinstance(cost, Decimal)
        assert cost == Decimal('5.00')
    
    def test_calculate_ingredient_cost_with_pack_size(self):
        """Test ingredient cost calculation with pack sizes"""
        # Test: 0.5 lb from a 5 lb package at $20.00
        cost = self.calculator._calculate_ingredient_cost(
            quantity=0.5,
            unit='lb',
            price=20.00,
            pack_size='5 lb',
            purchase_unit='lb',
            recipe_unit='lb'
        )
        
        expected_cost = Decimal('20.00') / Decimal('5') * Decimal('0.5')  # $2.00
        assert cost == expected_cost
    
    def test_recipe_cost_calculation_real_data(self):
        """Test recipe cost calculation with real database data"""
        # Find a recipe with ingredients to test
        cursor = self.calculator.conn.cursor()
        cursor.execute("""
            SELECT r.id, r.recipe_name 
            FROM recipes r
            JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            WHERE r.food_cost > 0
            GROUP BY r.id
            HAVING COUNT(ri.id) > 0
            LIMIT 1
        """)
        
        recipe = cursor.fetchone()
        
        if recipe:
            recipe_id, recipe_name = recipe
            cost, status = self.calculator.calc_recipe_cost(recipe_id)
            
            assert isinstance(cost, Decimal)
            assert cost >= 0
            assert isinstance(status, str)
            
            print(f"✅ Recipe {recipe_name} cost: ${cost:.2f} - {status}")
        else:
            pytest.skip("No recipes with ingredients found for testing")
    
    def test_recipe_cost_nonexistent_recipe(self):
        """Test cost calculation for non-existent recipe"""
        cost, status = self.calculator.calc_recipe_cost(99999)
        
        assert cost == Decimal('0')
        assert "not found" in status.lower()

class TestCostValidation:
    """Test cost validation and business rules"""
    
    def setup_method(self):
        """Setup test environment"""
        self.calculator = CostCalculator()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.calculator.close()
    
    def test_zero_quantity_handling(self):
        """Test handling of zero quantities"""
        cost = self.calculator._calculate_ingredient_cost(
            quantity=0.0,
            unit='lb',
            price=5.00,
            pack_size='1 lb',
            purchase_unit='lb',
            recipe_unit='lb'
        )
        
        assert cost == Decimal('0')
    
    def test_negative_price_handling(self):
        """Test handling of negative prices (should not happen in production)"""
        with pytest.raises(Exception):
            self.calculator._calculate_ingredient_cost(
                quantity=1.0,
                unit='lb',
                price=-5.00,
                pack_size='1 lb',
                purchase_unit='lb',
                recipe_unit='lb'
            )

@pytest.mark.performance
class TestCostPerformance:
    """Test cost calculation performance benchmarks"""
    
    def setup_method(self):
        """Setup test environment"""
        self.calculator = CostCalculator()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.calculator.close()
    
    def test_recipe_calculation_speed(self):
        """Test that recipe calculation completes within performance benchmark"""
        import time
        
        # Find a recipe to test with
        cursor = self.calculator.conn.cursor()
        cursor.execute("""
            SELECT id FROM recipes 
            WHERE food_cost > 0 
            LIMIT 1
        """)
        
        recipe = cursor.fetchone()
        
        if recipe:
            recipe_id = recipe[0]
            
            start_time = time.time()
            cost, status = self.calculator.calc_recipe_cost(recipe_id)
            end_time = time.time()
            
            calculation_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Performance benchmark: < 100ms per recipe
            assert calculation_time < 100, f"Recipe calculation took {calculation_time:.2f}ms (should be < 100ms)"
            
            print(f"✅ Recipe calculation completed in {calculation_time:.2f}ms")
        else:
            pytest.skip("No recipes found for performance testing")

if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v", "--tb=short"])
