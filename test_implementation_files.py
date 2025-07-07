# test_data_integrity.py - PRIORITY 1 IMPLEMENTATION
"""
Critical data integrity tests for restaurant management system.
Run before and after any AI-assisted changes.
"""

import sqlite3
import csv
import os
import sys
from datetime import datetime
import json

class DataIntegrityTester:
    def __init__(self, db_path="restaurant_calculator.db"):
        self.db_path = db_path
        self.test_results = {}
        self.baseline_file = "test_baseline.json"
        
    def run_all_tests(self):
        """Run all critical data integrity tests"""
        print("🧪 RUNNING CRITICAL DATA INTEGRITY TESTS")
        print("=" * 50)
        
        tests = [
            self.test_database_connectivity,
            self.test_table_relationships,
            self.test_cost_calculation_accuracy,
            self.test_recipe_ingredient_integrity,
            self.test_xtra_chef_mapping
        ]
        
        all_passed = True
        for test in tests:
            try:
                result = test()
                self.test_results[test.__name__] = result
                status = "✅ PASS" if result['passed'] else "❌ FAIL"
                print(f"{status} {test.__name__}: {result['message']}")
                if not result['passed']:
                    all_passed = False
            except Exception as e:
                print(f"❌ ERROR {test.__name__}: {str(e)}")
                all_passed = False
                
        print("\n" + "=" * 50)
        if all_passed:
            print("✅ ALL DATA INTEGRITY TESTS PASSED")
        else:
            print("❌ DATA INTEGRITY TESTS FAILED - SYSTEM UNSAFE")
            
        return all_passed
    
    def test_database_connectivity(self):
        """Test basic database connectivity"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return {"passed": True, "message": "Database connection successful"}
        except Exception as e:
            return {"passed": False, "message": f"Database connection failed: {e}"}
    
    def test_table_relationships(self):
        """Test critical foreign key relationships"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check recipe_ingredients relationships
                cursor.execute("""
                    SELECT COUNT(*) FROM recipe_ingredients ri
                    LEFT JOIN recipes r ON ri.recipe_id = r.id
                    LEFT JOIN inventory i ON ri.ingredient_id = i.id
                    WHERE r.id IS NULL OR i.id IS NULL
                """)
                orphaned_ingredients = cursor.fetchone()[0]
                
                if orphaned_ingredients > 0:
                    return {"passed": False, "message": f"{orphaned_ingredients} orphaned recipe ingredients found"}
                
                return {"passed": True, "message": "All relationships intact"}
        except Exception as e:
            return {"passed": False, "message": f"Relationship check failed: {e}"}
    
    def test_cost_calculation_accuracy(self):
        """Test known recipe cost calculations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Test a known recipe (if it exists)
                cursor.execute("""
                    SELECT r.id, r.recipe_name, r.food_cost,
                           SUM(ri.quantity * i.current_price) as calculated_cost
                    FROM recipes r
                    JOIN recipe_ingredients ri ON r.id = ri.recipe_id
                    JOIN inventory i ON ri.ingredient_id = i.id
                    WHERE r.recipe_name LIKE '%Nashville%'
                    GROUP BY r.id, r.recipe_name, r.food_cost
                    LIMIT 1
                """)
                
                result = cursor.fetchone()
                if result:
                    recipe_id, name, stored_cost, calculated_cost = result
                    if abs(stored_cost - calculated_cost) < 0.01:  # Within 1 cent
                        return {"passed": True, "message": f"Cost calculation accurate for {name}"}
                    else:
                        return {"passed": False, "message": f"Cost mismatch: stored={stored_cost}, calculated={calculated_cost}"}
                else:
                    return {"passed": True, "message": "No test recipes found - skipping cost validation"}
                    
        except Exception as e:
            return {"passed": False, "message": f"Cost calculation test failed: {e}"}
    
    def test_recipe_ingredient_integrity(self):
        """Test recipe-ingredient data integrity"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check for recipes without ingredients
                cursor.execute("""
                    SELECT COUNT(*) FROM recipes r
                    LEFT JOIN recipe_ingredients ri ON r.id = ri.recipe_id
                    WHERE ri.recipe_id IS NULL
                """)
                recipes_without_ingredients = cursor.fetchone()[0]
                
                # Check for zero quantity ingredients
                cursor.execute("""
                    SELECT COUNT(*) FROM recipe_ingredients
                    WHERE quantity <= 0
                """)
                zero_quantity_ingredients = cursor.fetchone()[0]
                
                issues = []
                if recipes_without_ingredients > 0:
                    issues.append(f"{recipes_without_ingredients} recipes without ingredients")
                if zero_quantity_ingredients > 0:
                    issues.append(f"{zero_quantity_ingredients} zero quantity ingredients")
                
                if issues:
                    return {"passed": False, "message": "; ".join(issues)}
                else:
                    return {"passed": True, "message": "Recipe ingredient integrity verified"}
                    
        except Exception as e:
            return {"passed": False, "message": f"Recipe integrity test failed: {e}"}
    
    def test_xtra_chef_mapping(self):
        """Test XtraChef data mapping integrity"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check for items without item_code (XtraChef mapping)
                cursor.execute("""
                    SELECT COUNT(*) FROM inventory
                    WHERE item_code IS NULL OR item_code = ''
                """)
                missing_codes = cursor.fetchone()[0]
                
                # Check for duplicate item codes
                cursor.execute("""
                    SELECT item_code, COUNT(*) as count FROM inventory
                    WHERE item_code IS NOT NULL AND item_code != ''
                    GROUP BY item_code
                    HAVING COUNT(*) > 1
                """)
                duplicates = cursor.fetchall()
                
                issues = []
                if missing_codes > 0:
                    issues.append(f"{missing_codes} items missing XtraChef codes")
                if duplicates:
                    issues.append(f"{len(duplicates)} duplicate item codes")
                
                if issues:
                    return {"passed": False, "message": "; ".join(issues)}
                else:
                    return {"passed": True, "message": "XtraChef mapping integrity verified"}
                    
        except Exception as e:
            return {"passed": False, "message": f"XtraChef mapping test failed: {e}"}
    
    def create_baseline(self):
        """Create baseline for regression testing"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            baseline = {
                "timestamp": datetime.now().isoformat(),
                "inventory_count": cursor.execute("SELECT COUNT(*) FROM inventory").fetchone()[0],
                "recipe_count": cursor.execute("SELECT COUNT(*) FROM recipes").fetchone()[0],
                "ingredient_link_count": cursor.execute("SELECT COUNT(*) FROM recipe_ingredients").fetchone()[0],
                "sample_recipe_costs": {}
            }
            
            # Store costs for a few sample recipes
            cursor.execute("""
                SELECT recipe_name, food_cost FROM recipes 
                WHERE food_cost > 0 
                ORDER BY recipe_name 
                LIMIT 5
            """)
            
            for name, cost in cursor.fetchall():
                baseline["sample_recipe_costs"][name] = cost
            
            with open(self.baseline_file, 'w') as f:
                json.dump(baseline, f, indent=2)
            
            print(f"✅ Baseline created: {baseline}")
            return baseline
    
    def compare_to_baseline(self):
        """Compare current state to baseline"""
        if not os.path.exists(self.baseline_file):
            print("⚠️  No baseline found - creating new baseline")
            return self.create_baseline()
        
        with open(self.baseline_file, 'r') as f:
            baseline = json.load(f)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            current = {
                "inventory_count": cursor.execute("SELECT COUNT(*) FROM inventory").fetchone()[0],
                "recipe_count": cursor.execute("SELECT COUNT(*) FROM recipes").fetchone()[0],
                "ingredient_link_count": cursor.execute("SELECT COUNT(*) FROM recipe_ingredients").fetchone()[0],
            }
        
        changes = []
        for key in ["inventory_count", "recipe_count", "ingredient_link_count"]:
            if current[key] != baseline[key]:
                changes.append(f"{key}: {baseline[key]} → {current[key]}")
        
        if changes:
            print("📊 CHANGES DETECTED:")
            for change in changes:
                print(f"  {change}")
        else:
            print("✅ No structural changes detected")
        
        return current, baseline


def run_pre_ai_tests():
    """Run tests before AI changes"""
    print("🤖 PRE-AI CHANGE VALIDATION")
    tester = DataIntegrityTester()
    
    # Create baseline
    tester.create_baseline()
    
    # Run integrity tests
    if tester.run_all_tests():
        print("✅ SYSTEM READY FOR AI CHANGES")
        return True
    else:
        print("❌ SYSTEM NOT SAFE FOR AI CHANGES")
        return False


def run_post_ai_tests():
    """Run tests after AI changes"""
    print("🤖 POST-AI CHANGE VALIDATION")
    tester = DataIntegrityTester()
    
    # Compare to baseline
    tester.compare_to_baseline()
    
    # Run integrity tests
    if tester.run_all_tests():
        print("✅ AI CHANGES VALIDATED SUCCESSFULLY")
        return True
    else:
        print("❌ AI CHANGES BROKE SYSTEM - ROLLBACK REQUIRED")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--pre-ai":
            run_pre_ai_tests()
        elif sys.argv[1] == "--post-ai":
            run_post_ai_tests()
        elif sys.argv[1] == "--baseline":
            tester = DataIntegrityTester()
            tester.create_baseline()
        else:
            print("Usage: python test_data_integrity.py [--pre-ai|--post-ai|--baseline]")
    else:
        # Default: run all tests
        tester = DataIntegrityTester()
        tester.run_all_tests()