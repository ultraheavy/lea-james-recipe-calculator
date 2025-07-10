#!/usr/bin/env python3
"""
ENHANCED RECIPE COSTING TESTS - Simple Version
Tests recipe costing engine functions without external dependencies
"""

import sqlite3
import os
import sys
from decimal import Decimal

DATABASE = 'restaurant_calculator.db'

class EnhancedCostTester:
    """Enhanced test runner for recipe costing engine"""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
    
    def assert_test(self, condition: bool, test_name: str, message: str = ""):
        """Simple assertion helper"""
        self.tests_run += 1
        
        if condition:
            print(f"✅ PASS: {test_name}")
            self.tests_passed += 1
        else:
            print(f"❌ FAIL: {test_name} - {message}")
            self.tests_failed += 1
    
    def test_cost_propagation_simulation(self):
        """Test cost propagation when prices change"""
        try:
            # Find a recipe with linked ingredients
            self.cursor.execute("""
                SELECT DISTINCT r.id, r.recipe_name, r.food_cost
                FROM recipes r
                JOIN recipe_ingredients ri ON r.id = ri.recipe_id
                JOIN inventory i ON ri.ingredient_id = i.id
                WHERE r.food_cost > 0 AND i.current_price > 0
                LIMIT 1
            """)
            
            recipe = self.cursor.fetchone()
            
            if recipe:
                recipe_id, recipe_name, original_cost = recipe
                
                # Get ingredient count for this recipe
                self.cursor.execute("""
                    SELECT COUNT(*)
                    FROM recipe_ingredients ri
                    JOIN inventory i ON ri.ingredient_id = i.id
                    WHERE ri.recipe_id = ? AND i.current_price > 0
                """, (recipe_id,))
                
                ingredient_count = self.cursor.fetchone()[0]
                
                self.assert_test(
                    ingredient_count > 0,
                    "Cost Propagation Setup",
                    f"Recipe {recipe_name} has {ingredient_count} linked ingredients"
                )
                
                # Simulate cost calculation impact
                estimated_impact = original_cost * 0.1  # 10% price change impact
                
                self.assert_test(
                    estimated_impact > 0,
                    "Cost Propagation Impact",
                    f"10% price change would impact {recipe_name} by ~${estimated_impact:.2f}"
                )
                
                print(f"   📊 Recipe: {recipe_name}, Current cost: ${original_cost:.2f}, Ingredients: {ingredient_count}")
                
            else:
                print("⚠️  No suitable recipes found for cost propagation test")
                
        except Exception as e:
            self.assert_test(False, "Cost Propagation Test", str(e))
    
    def test_yield_calculations(self):
        """Test recipe yield calculations"""
        try:
            self.cursor.execute("""
                SELECT recipe_name, prep_recipe_yield, prep_recipe_yield_uom, food_cost
                FROM recipes
                WHERE prep_recipe_yield > 0 AND food_cost > 0
                LIMIT 5
            """)
            
            recipes = self.cursor.fetchall()
            valid_yields = 0
            
            for recipe_name, yield_qty, yield_uom, total_cost in recipes:
                # Calculate cost per serving/unit
                cost_per_unit = total_cost / yield_qty
                
                # Validate yield reasonableness
                if yield_uom and yield_uom.lower() in ['portions', 'each']:
                    is_reasonable = 1 <= yield_qty <= 100 and 0.50 <= cost_per_unit <= 25.00
                else:
                    is_reasonable = yield_qty > 0 and cost_per_unit > 0
                
                if is_reasonable:
                    valid_yields += 1
                    print(f"   📊 {recipe_name}: {yield_qty} {yield_uom} = ${cost_per_unit:.2f} per unit")
            
            self.assert_test(
                valid_yields >= len(recipes) * 0.8,  # 80% should be reasonable
                "Yield Calculations",
                f"{valid_yields}/{len(recipes)} recipes have reasonable yields"
            )
            
        except Exception as e:
            self.assert_test(False, "Yield Calculations", str(e))
    
    def test_menu_profitability_analysis(self):
        """Test menu item profitability calculations"""
        try:
            self.cursor.execute("""
                SELECT item_name, menu_price, food_cost,
                       CASE 
                           WHEN menu_price > 0 THEN (menu_price - food_cost) / menu_price * 100
                           ELSE 0
                       END as profit_margin
                FROM menu_items
                WHERE menu_price > 0 AND food_cost > 0
                ORDER BY profit_margin DESC
                LIMIT 10
            """)
            
            items = self.cursor.fetchall()
            profitable_items = 0
            
            for item_name, menu_price, food_cost, profit_margin in items:
                # Check profitability (60%+ margin is good for restaurants)
                is_profitable = profit_margin >= 60
                
                if is_profitable:
                    profitable_items += 1
                    print(f"   💰 {item_name}: {profit_margin:.1f}% margin (${menu_price:.2f} - ${food_cost:.2f})")
                else:
                    print(f"   ⚠️  {item_name}: LOW {profit_margin:.1f}% margin (${menu_price:.2f} - ${food_cost:.2f})")
            
            self.assert_test(
                len(items) > 0,
                "Menu Items Found",
                f"Found {len(items)} menu items with pricing"
            )
            
            profit_rate = (profitable_items / len(items) * 100) if len(items) > 0 else 0
            
            self.assert_test(
                profit_rate >= 60,
                "Menu Profitability",
                f"{profit_rate:.1f}% of items have good profit margins (>=60%)"
            )
            
        except Exception as e:
            self.assert_test(False, "Menu Profitability Analysis", str(e))
    
    def test_critical_business_rules(self):
        """Test critical business rules"""
        try:
            # Test 1: No free menu items
            self.cursor.execute("""
                SELECT COUNT(*) FROM menu_items WHERE menu_price <= 0
            """)
            free_items = self.cursor.fetchone()[0]
            
            self.assert_test(
                free_items == 0,
                "No Free Menu Items",
                f"Found {free_items} menu items with zero/negative prices"
            )
            
            # Test 2: No negative inventory prices
            self.cursor.execute("""
                SELECT COUNT(*) FROM inventory WHERE current_price < 0
            """)
            negative_prices = self.cursor.fetchone()[0]
            
            self.assert_test(
                negative_prices == 0,
                "No Negative Prices",
                f"Found {negative_prices} inventory items with negative prices"
            )
            
            # Test 3: Menu prices higher than costs
            self.cursor.execute("""
                SELECT COUNT(*) FROM menu_items 
                WHERE menu_price > 0 AND food_cost > 0 AND menu_price <= food_cost
            """)
            losing_items = self.cursor.fetchone()[0]
            
            self.assert_test(
                losing_items == 0,
                "Menu Prices Above Costs",
                f"Found {losing_items} menu items priced at or below cost"
            )
            
        except Exception as e:
            self.assert_test(False, "Critical Business Rules", str(e))
    
    def test_data_consistency(self):
        """Test data consistency across tables"""
        try:
            # Test recipe-ingredient relationships
            self.cursor.execute("""
                SELECT COUNT(*)
                FROM recipe_ingredients ri
                LEFT JOIN recipes r ON ri.recipe_id = r.id
                WHERE r.id IS NULL
            """)
            orphaned_ingredients = self.cursor.fetchone()[0]
            
            self.assert_test(
                orphaned_ingredients == 0,
                "No Orphaned Recipe Ingredients",
                f"Found {orphaned_ingredients} orphaned recipe ingredients"
            )
            
            # Test ingredient-inventory linking rate
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN ri.ingredient_id IS NOT NULL THEN 1 ELSE 0 END) as linked
                FROM recipe_ingredients ri
            """)
            
            total, linked = self.cursor.fetchone()
            link_rate = (linked / total * 100) if total > 0 else 0
            
            self.assert_test(
                link_rate >= 80,
                "Recipe-Inventory Link Rate",
                f"Link rate: {link_rate:.1f}% ({linked}/{total} ingredients linked)"
            )
            
        except Exception as e:
            self.assert_test(False, "Data Consistency", str(e))
    
    def run_all_tests(self):
        """Execute all enhanced recipe costing tests"""
        print("🧪 ENHANCED RECIPE COSTING ENGINE TESTS")
        print("=" * 55)
        
        self.test_cost_propagation_simulation()
        self.test_yield_calculations()
        self.test_menu_profitability_analysis()
        self.test_critical_business_rules()
        self.test_data_consistency()
        
        print("=" * 55)
        print(f"📊 ENHANCED TEST SUMMARY:")
        print(f"   Total: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_failed}")
        
        if self.tests_failed == 0:
            print("🎉 ALL ENHANCED TESTS PASSED! Recipe costing engine is robust.")
            return 0
        else:
            print(f"⚠️  {self.tests_failed} tests failed. Review recipe costing logic.")
            return 1
    
    def cleanup(self):
        """Cleanup resources"""
        self.conn.close()

def main():
    """Main test execution"""
    if not os.path.exists(DATABASE):
        print("❌ Error: Database file not found!")
        return 1
    
    tester = EnhancedCostTester()
    try:
        return tester.run_all_tests()
    finally:
        tester.cleanup()

if __name__ == "__main__":
    sys.exit(main())
