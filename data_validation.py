#!/usr/bin/env python3
"""
Comprehensive data validation script for restaurant management system
Checks data integrity, Toast POS compliance, and system consistency
"""

import sqlite3
from datetime import datetime
from decimal import Decimal

class DataValidator:
    def __init__(self, db_path='restaurant_calculator.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.issues = []
        self.warnings = []
        self.info = []
    
    def run_all_checks(self):
        """Run all validation checks"""
        print("=== RESTAURANT DATA VALIDATION REPORT ===")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Menu System Checks
        self.check_menu_system()
        
        # Recipe Checks
        self.check_recipes()
        
        # Menu Item Checks
        self.check_menu_items()
        
        # Toast POS Compliance
        self.check_toast_compliance()
        
        # Cost Calculations
        self.check_cost_calculations()
        
        # Data Relationships
        self.check_relationships()
        
        # Generate report
        self.generate_report()
    
    def check_menu_system(self):
        """Validate menu system integrity"""
        print("Checking Menu System...")
        
        # Check for duplicate menu names
        dupes = self.conn.execute("""
            SELECT menu_name, COUNT(*) as cnt 
            FROM menus 
            GROUP BY menu_name 
            HAVING cnt > 1
        """).fetchall()
        
        if dupes:
            for d in dupes:
                self.issues.append(f"Duplicate menu name: {d['menu_name']} ({d['cnt']} instances)")
        
        # Check active menu count
        active = self.conn.execute("SELECT COUNT(*) as cnt FROM menus WHERE is_active = 1").fetchone()
        if active['cnt'] != 1:
            self.issues.append(f"Expected 1 active menu, found {active['cnt']}")
        
        # Check for orphaned menu items
        orphans = self.conn.execute("""
            SELECT COUNT(*) as cnt FROM menu_items 
            WHERE id NOT IN (SELECT menu_item_id FROM menu_menu_items)
        """).fetchone()
        
        if orphans['cnt'] > 0:
            self.warnings.append(f"{orphans['cnt']} menu items not assigned to any menu")
        
        print(f"  ✓ Completed menu system checks\n")
    
    def check_recipes(self):
        """Validate recipe data"""
        print("Checking Recipes...")
        
        # Check for prep recipes with menu prices
        prep_with_price = self.conn.execute("""
            SELECT COUNT(*) as cnt FROM recipes 
            WHERE recipe_type = 'PrepRecipe' AND menu_price > 0
        """).fetchone()
        
        if prep_with_price['cnt'] > 0:
            self.issues.append(f"{prep_with_price['cnt']} prep recipes have menu prices (should be 0)")
        
        # Check for recipes with extreme food cost percentages
        extreme_costs = self.conn.execute("""
            SELECT recipe_name, food_cost_percentage, recipe_type
            FROM recipes 
            WHERE food_cost_percentage > 100 OR food_cost_percentage < 0
        """).fetchall()
        
        for r in extreme_costs:
            self.issues.append(f"Recipe '{r['recipe_name']}' has invalid food cost: {r['food_cost_percentage']}%")
        
        # Check for missing recipe status
        no_status = self.conn.execute("""
            SELECT COUNT(*) as cnt FROM recipes 
            WHERE status IS NULL OR status = ''
        """).fetchone()
        
        if no_status['cnt'] > 0:
            self.warnings.append(f"{no_status['cnt']} recipes missing status (Draft/Complete)")
        
        print(f"  ✓ Completed recipe checks\n")
    
    def check_menu_items(self):
        """Validate menu items"""
        print("Checking Menu Items...")
        
        # Check for menu items without recipes
        no_recipe = self.conn.execute("""
            SELECT COUNT(*) as cnt FROM menu_items 
            WHERE recipe_id IS NULL OR recipe_id = 0
        """).fetchone()
        
        if no_recipe['cnt'] > 0:
            self.issues.append(f"{no_recipe['cnt']} menu items without recipes")
        
        # Check for menu items with zero price
        zero_price = self.conn.execute("""
            SELECT item_name FROM menu_items 
            WHERE menu_price = 0 OR menu_price IS NULL
        """).fetchall()
        
        if zero_price:
            for item in zero_price[:5]:  # Show first 5
                self.warnings.append(f"Menu item '{item['item_name']}' has no price")
        
        # Check food cost percentages
        high_cost = self.conn.execute("""
            SELECT item_name, food_cost_percent 
            FROM menu_items 
            WHERE food_cost_percent > 50
            ORDER BY food_cost_percent DESC
            LIMIT 10
        """).fetchall()
        
        if high_cost:
            self.info.append(f"{len(high_cost)} menu items with >50% food cost (may need review)")
        
        print(f"  ✓ Completed menu item checks\n")
    
    def check_toast_compliance(self):
        """Check Toast POS compliance rules"""
        print("Checking Toast POS Compliance...")
        
        # Rule: 1 menu item = 1 recipe
        violations = self.conn.execute("""
            SELECT recipe_id, COUNT(DISTINCT id) as item_count
            FROM menu_items
            WHERE recipe_id IS NOT NULL
            GROUP BY recipe_id
            HAVING item_count > 1
        """).fetchall()
        
        if violations:
            self.issues.append(f"{len(violations)} recipes used by multiple menu items (Toast requires 1:1)")
        
        # Check recipe naming conventions
        bad_names = self.conn.execute("""
            SELECT recipe_name FROM recipes
            WHERE recipe_name LIKE '%  %' OR recipe_name LIKE '% ' OR recipe_name LIKE ' %'
        """).fetchall()
        
        if bad_names:
            self.warnings.append(f"{len(bad_names)} recipes with extra spaces in names")
        
        print(f"  ✓ Completed Toast compliance checks\n")
    
    def check_cost_calculations(self):
        """Validate cost calculations"""
        print("Checking Cost Calculations...")
        
        # Check for mismatched costs between recipes and menu items
        mismatches = self.conn.execute("""
            SELECT mi.item_name, mi.food_cost as mi_cost, r.food_cost as r_cost
            FROM menu_items mi
            JOIN recipes r ON mi.recipe_id = r.id
            WHERE ABS(mi.food_cost - r.food_cost) > 0.01
        """).fetchall()
        
        if mismatches:
            self.warnings.append(f"{len(mismatches)} menu items with cost mismatches vs recipes")
        
        # Check for invalid percentages
        invalid_pct = self.conn.execute("""
            SELECT item_name, food_cost, menu_price, food_cost_percent,
                   ROUND((food_cost / NULLIF(menu_price, 0)) * 100, 2) as calc_percent
            FROM menu_items
            WHERE menu_price > 0 
            AND ABS(food_cost_percent - ROUND((food_cost / menu_price) * 100, 2)) > 0.1
        """).fetchall()
        
        if invalid_pct:
            for item in invalid_pct[:3]:
                self.issues.append(
                    f"Menu item '{item['item_name']}' has incorrect food cost %: "
                    f"{item['food_cost_percent']}% (should be {item['calc_percent']}%)"
                )
        
        print(f"  ✓ Completed cost calculation checks\n")
    
    def check_relationships(self):
        """Check data relationships and foreign keys"""
        print("Checking Data Relationships...")
        
        # Check for invalid recipe references
        invalid_refs = self.conn.execute("""
            SELECT mi.item_name, mi.recipe_id
            FROM menu_items mi
            LEFT JOIN recipes r ON mi.recipe_id = r.id
            WHERE mi.recipe_id IS NOT NULL AND r.id IS NULL
        """).fetchall()
        
        if invalid_refs:
            for ref in invalid_refs:
                self.issues.append(f"Menu item '{ref['item_name']}' references non-existent recipe ID {ref['recipe_id']}")
        
        # Check menu_menu_items integrity
        invalid_menu = self.conn.execute("""
            SELECT COUNT(*) as cnt FROM menu_menu_items mmi
            WHERE NOT EXISTS (SELECT 1 FROM menus m WHERE m.id = mmi.menu_id)
        """).fetchone()
        
        if invalid_menu['cnt'] > 0:
            self.issues.append(f"{invalid_menu['cnt']} menu assignments reference non-existent menus")
        
        print(f"  ✓ Completed relationship checks\n")
    
    def generate_report(self):
        """Generate final validation report"""
        print("=== VALIDATION SUMMARY ===\n")
        
        # Issues (must fix)
        if self.issues:
            print(f"❌ CRITICAL ISSUES ({len(self.issues)}):")
            for issue in self.issues:
                print(f"   - {issue}")
            print()
        else:
            print("✅ No critical issues found!\n")
        
        # Warnings (should review)
        if self.warnings:
            print(f"⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"   - {warning}")
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more")
            print()
        
        # Info (FYI)
        if self.info:
            print(f"ℹ️  INFORMATION ({len(self.info)}):")
            for info in self.info:
                print(f"   - {info}")
            print()
        
        # Summary statistics
        stats = self.conn.execute("""
            SELECT 
                (SELECT COUNT(*) FROM recipes) as recipes,
                (SELECT COUNT(*) FROM menu_items) as menu_items,
                (SELECT COUNT(*) FROM menus) as menus,
                (SELECT COUNT(*) FROM menu_menu_items) as assignments
        """).fetchone()
        
        print("📊 DATABASE STATISTICS:")
        print(f"   - Total Recipes: {stats['recipes']}")
        print(f"   - Total Menu Items: {stats['menu_items']}")
        print(f"   - Total Menus: {stats['menus']}")
        print(f"   - Total Menu Assignments: {stats['assignments']}")
        
        # V3 Menu Status
        v3_status = self.conn.execute("""
            SELECT m.*, COUNT(mmi.menu_item_id) as item_count
            FROM menus m
            LEFT JOIN menu_menu_items mmi ON m.id = mmi.menu_id
            WHERE m.menu_name LIKE '%V3%'
            GROUP BY m.id
        """).fetchone()
        
        if v3_status:
            print(f"\n📋 V3 PLANNING MENU STATUS:")
            print(f"   - Status: {'Active' if v3_status['is_active'] else 'Inactive'}")
            print(f"   - Items: {v3_status['item_count']}")
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    """Run validation"""
    validator = DataValidator()
    try:
        validator.run_all_checks()
    finally:
        validator.close()

if __name__ == "__main__":
    main()