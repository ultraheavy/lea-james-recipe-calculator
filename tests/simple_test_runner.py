#!/usr/bin/env python3
"""
SIMPLE TEST RUNNER - No external dependencies
Runs critical business tests without requiring pytest
"""

import sqlite3
import os
import sys
from datetime import datetime

DATABASE = 'restaurant_calculator.db'

class SimpleTestRunner:
    """Simple test runner for critical business functions"""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        
    def assert_test(self, condition: bool, test_name: str, message: str = ""):
        """Simple assertion helper"""
        self.tests_run += 1
        
        if condition:
            print(f"✅ PASS: {test_name}")
            self.tests_passed += 1
        else:
            print(f"❌ FAIL: {test_name} - {message}")
            self.tests_failed += 1
    
    def test_database_connection(self):
        """Test database connectivity"""
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM inventory")
            count = cursor.fetchone()[0]
            conn.close()
            
            self.assert_test(count > 0, "Database Connection", "Database connected and has inventory data")
            return True
        except Exception as e:
            self.assert_test(False, "Database Connection", str(e))
            return False
    
    def test_xtrachef_data_integrity(self):
        """Test XtraChef data integrity"""
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            
            # Check XtraChef data
            cursor.execute("""
                SELECT COUNT(*) FROM inventory 
                WHERE item_code IS NOT NULL AND current_price > 0
            """)
            items_with_data = cursor.fetchone()[0]
            
            conn.close()
            
            self.assert_test(items_with_data >= 200, "XtraChef Data Integrity", 
                           f"Found {items_with_data} items with XtraChef data")
            
        except Exception as e:
            self.assert_test(False, "XtraChef Data Integrity", str(e))
    
    def test_recipe_costing_engine(self):
        """Test recipe costing engine"""
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            
            # Test specific recipe cost
            cursor.execute("""
                SELECT food_cost FROM recipes 
                WHERE recipe_name LIKE '%Collard Greens%'
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            if result:
                cost = result[0]
                self.assert_test(cost > 0 and cost < 100, "Recipe Cost Calculation", 
                               f"Collard Greens cost: ${cost:.2f}")
            else:
                self.assert_test(False, "Recipe Cost Calculation", "Collard Greens recipe not found")
            
            # Test ingredient relationships
            cursor.execute("""
                SELECT COUNT(*) FROM recipe_ingredients ri
                LEFT JOIN inventory i ON ri.ingredient_id = i.id  
                WHERE i.id IS NOT NULL
            """)
            linked_ingredients = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM recipe_ingredients")
            total_ingredients = cursor.fetchone()[0]
            
            link_rate = (linked_ingredients / total_ingredients * 100) if total_ingredients > 0 else 0
            
            self.assert_test(link_rate > 95, "Recipe-Inventory Links", 
                           f"Link rate: {link_rate:.1f}% ({linked_ingredients}/{total_ingredients})")
            
            conn.close()
            
        except Exception as e:
            self.assert_test(False, "Recipe Costing Engine", str(e))
    
    def test_menu_calculations(self):
        """Test menu item pricing and profit margins"""
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            
            # Check menu items with pricing
            cursor.execute("""
                SELECT COUNT(*) FROM menu_items 
                WHERE menu_price > 0 AND food_cost > 0
            """)
            items_with_complete_data = cursor.fetchone()[0]
            
            self.assert_test(items_with_complete_data > 50, "Menu Pricing Data", 
                           f"Found {items_with_complete_data} menu items with complete pricing")
            
            # Test profit margin calculation
            cursor.execute("""
                SELECT item_name, menu_price, food_cost,
                       (menu_price - food_cost) / menu_price * 100 as margin
                FROM menu_items 
                WHERE menu_price > food_cost AND food_cost > 0
                LIMIT 5
            """)
            
            profit_items = cursor.fetchall()
            valid_margins = 0
            
            for item_name, menu_price, food_cost, margin in profit_items:
                if 10 <= margin <= 90:  # Reasonable profit margin range
                    valid_margins += 1
                    print(f"   📊 {item_name}: ${menu_price:.2f} - ${food_cost:.2f} = {margin:.1f}% margin")
            
            self.assert_test(valid_margins > 0, "Profit Margin Calculations",
                           f"{valid_margins} items with valid profit margins")
            
            conn.close()
            
        except Exception as e:
            self.assert_test(False, "Menu Calculations", str(e))
    
    def test_data_quality(self):
        """Test overall data quality"""
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            
            # Check for null critical fields
            cursor.execute("""
                SELECT COUNT(*) FROM inventory 
                WHERE item_description IS NULL OR item_description = ''
            """)
            null_descriptions = cursor.fetchone()[0]
            
            self.assert_test(null_descriptions == 0, "Data Quality - No Null Descriptions",
                           f"Found {null_descriptions} items with null descriptions")
            
            # Check for negative prices
            cursor.execute("""
                SELECT COUNT(*) FROM inventory 
                WHERE current_price < 0
            """)
            negative_prices = cursor.fetchone()[0]
            
            self.assert_test(negative_prices == 0, "Data Quality - No Negative Prices",
                           f"Found {negative_prices} items with negative prices")
            
            conn.close()
            
        except Exception as e:
            self.assert_test(False, "Data Quality", str(e))
    
    def run_all_tests(self):
        """Execute all critical tests"""
        print("🧪 STARTING CRITICAL BUSINESS TESTS")
        print("=" * 50)
        
        # Only run other tests if database connection works
        if self.test_database_connection():
            self.test_xtrachef_data_integrity()
            self.test_recipe_costing_engine()
            self.test_menu_calculations()
            self.test_data_quality()
        
        print("=" * 50)
        print(f"📊 TEST SUMMARY:")
        print(f"   Total: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_failed}")
        
        if self.tests_failed == 0:
            print("🎉 ALL TESTS PASSED! System is healthy.")
            return 0
        else:
            print(f"⚠️  {self.tests_failed} tests failed. System needs attention.")
            return 1

def main():
    """Main test execution"""
    if not os.path.exists(DATABASE):
        print(f"❌ Error: Database file {DATABASE} not found!")
        print("Make sure you're running this from the project root directory.")
        return 1
    
    runner = SimpleTestRunner()
    return runner.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
