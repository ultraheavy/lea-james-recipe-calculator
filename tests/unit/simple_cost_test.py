#!/usr/bin/env python3
"""
SIMPLE COST UTILS TESTS - No external dependencies
Tests cost calculation functions without requiring pytest
"""

import sys
import os
from decimal import Decimal

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cost_utils import CostCalculator

class SimpleCostTester:
    """Simple test runner for cost calculations"""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.calculator = CostCalculator()
    
    def assert_test(self, condition: bool, test_name: str, message: str = ""):
        """Simple assertion helper"""
        self.tests_run += 1
        
        if condition:
            print(f"✅ PASS: {test_name}")
            self.tests_passed += 1
        else:
            print(f"❌ FAIL: {test_name} - {message}")
            self.tests_failed += 1
    
    def test_calculator_initialization(self):
        """Test that calculator initializes properly"""
        try:
            self.assert_test(
                self.calculator.db_path == 'restaurant_calculator.db',
                "Calculator Initialization",
                "Database path should be correct"
            )
            
            self.assert_test(
                self.calculator.conn is not None,
                "Database Connection",
                "Database connection should exist"
            )
            
        except Exception as e:
            self.assert_test(False, "Calculator Initialization", str(e))
    
    def test_basic_ingredient_cost_calculation(self):
        """Test basic ingredient cost calculation"""
        try:
            # Test: 1 lb of ingredient at $5.00/lb
            cost = self.calculator._calculate_ingredient_cost(
                quantity=1.0,
                unit='lb',
                price=5.00,
                pack_size='1 lb',
                purchase_unit='lb',
                recipe_unit='lb'
            )
            
            self.assert_test(
                isinstance(cost, Decimal),
                "Cost Type Validation",
                "Cost should be Decimal type"
            )
            
            self.assert_test(
                cost == Decimal('5.00'),
                "Basic Cost Calculation",
                f"1 lb at $5/lb should cost $5.00, got ${cost}"
            )
            
        except Exception as e:
            self.assert_test(False, "Basic Cost Calculation", str(e))
    
    def test_pack_size_cost_calculation(self):
        """Test ingredient cost calculation with pack sizes"""
        try:
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
            
            self.assert_test(
                cost == expected_cost,
                "Pack Size Cost Calculation",
                f"0.5 lb from 5 lb pack at $20 should cost ${expected_cost}, got ${cost}"
            )
            
        except Exception as e:
            self.assert_test(False, "Pack Size Cost Calculation", str(e))
    
    def test_real_recipe_cost_calculation(self):
        """Test recipe cost calculation with real database data"""
        try:
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
                
                self.assert_test(
                    isinstance(cost, Decimal),
                    "Real Recipe Cost Type",
                    "Recipe cost should be Decimal type"
                )
                
                self.assert_test(
                    cost >= 0,
                    "Real Recipe Cost Validation",
                    f"Recipe cost should be non-negative, got ${cost}"
                )
                
                self.assert_test(
                    isinstance(status, str),
                    "Recipe Status Message",
                    "Status should be string"
                )
                
                print(f"   📊 Tested recipe: {recipe_name} = ${cost:.2f} ({status})")
                
            else:
                print("⚠️  No suitable recipes found for testing")
                
        except Exception as e:
            self.assert_test(False, "Real Recipe Cost Calculation", str(e))
    
    def test_zero_quantity_handling(self):
        """Test handling of zero quantities"""
        try:
            cost = self.calculator._calculate_ingredient_cost(
                quantity=0.0,
                unit='lb',
                price=5.00,
                pack_size='1 lb',
                purchase_unit='lb',
                recipe_unit='lb'
            )
            
            self.assert_test(
                cost == Decimal('0'),
                "Zero Quantity Handling",
                f"Zero quantity should result in zero cost, got ${cost}"
            )
            
        except Exception as e:
            self.assert_test(False, "Zero Quantity Handling", str(e))
    
    def test_performance_benchmark(self):
        """Test that recipe calculation meets performance benchmark"""
        try:
            import time
            
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
                
                self.assert_test(
                    calculation_time < 100,
                    "Performance Benchmark",
                    f"Recipe calculation took {calculation_time:.2f}ms (should be < 100ms)"
                )
                
                print(f"   ⚡ Recipe calculation completed in {calculation_time:.2f}ms")
                
            else:
                print("⚠️  No recipes found for performance testing")
                
        except Exception as e:
            self.assert_test(False, "Performance Benchmark", str(e))
    
    def run_all_tests(self):
        """Execute all cost calculation tests"""
        print("🧪 TESTING RECIPE COSTING ENGINE")
        print("=" * 50)
        
        self.test_calculator_initialization()
        self.test_basic_ingredient_cost_calculation()
        self.test_pack_size_cost_calculation()
        self.test_real_recipe_cost_calculation()
        self.test_zero_quantity_handling()
        self.test_performance_benchmark()
        
        print("=" * 50)
        print(f"📊 COST CALCULATION TEST SUMMARY:")
        print(f"   Total: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_failed}")
        
        if self.tests_failed == 0:
            print("🎉 ALL COST CALCULATION TESTS PASSED!")
            return 0
        else:
            print(f"⚠️  {self.tests_failed} tests failed. Review cost calculation logic.")
            return 1
    
    def cleanup(self):
        """Cleanup resources"""
        self.calculator.close()

def main():
    """Main test execution"""
    if not os.path.exists('restaurant_calculator.db'):
        print("❌ Error: Database file not found!")
        return 1
    
    tester = SimpleCostTester()
    try:
        return tester.run_all_tests()
    finally:
        tester.cleanup()

if __name__ == "__main__":
    sys.exit(main())
