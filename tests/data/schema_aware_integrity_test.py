#!/usr/bin/env python3
"""
SCHEMA-AWARE DATABASE INTEGRITY TESTS
Adapts to the actual current database schema structure
"""

import sqlite3
import os
import sys
from datetime import datetime

DATABASE = 'restaurant_calculator.db'

class SchemaAwareDatabaseTester:
    """Database integrity testing that adapts to current schema"""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
        
        # Dynamically discover the actual schema
        self.actual_schema = self._discover_schema()
        
    def _discover_schema(self):
        """Discover the actual database schema"""
        schema = {}
        
        # Get all tables
        self.cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%_old'
            ORDER BY name
        """)
        
        tables = [row[0] for row in self.cursor.fetchall()]
        
        # Get schema for each table
        for table in tables:
            self.cursor.execute(f"PRAGMA table_info({table})")
            columns_info = self.cursor.fetchall()
            
            schema[table] = {
                'columns': [col[1] for col in columns_info],  # Column names
                'pk_columns': [col[1] for col in columns_info if col[5] == 1],  # Primary keys
                'required_columns': [col[1] for col in columns_info if col[3] == 1]  # NOT NULL
            }
        
        return schema
    
    def assert_test(self, condition: bool, test_name: str, message: str = ""):
        """Simple assertion helper"""
        self.tests_run += 1
        
        if condition:
            print(f"✅ PASS: {test_name}")
            self.tests_passed += 1
        else:
            print(f"❌ FAIL: {test_name} - {message}")
            self.tests_failed += 1
    
    def test_critical_tables_structure(self):
        """Test structure of critical tables"""
        try:
            critical_tables = {
                'inventory': ['item_code', 'item_description', 'current_price'],
                'recipes_actual': ['recipe_name', 'food_cost'],
                'recipe_ingredients_actual': ['recipe_id'],
                'menu_items_actual': ['item_name', 'current_price'],
                'vendors': ['vendor_name']
            }
            
            for table_name, important_columns in critical_tables.items():
                if table_name in self.actual_schema:
                    table_columns = self.actual_schema[table_name]['columns']
                    
                    missing = [col for col in important_columns if col not in table_columns]
                    
                    self.assert_test(
                        len(missing) == 0,
                        f"Critical Columns: {table_name}",
                        f"Missing important columns: {missing}"
                    )
                    
                    if len(missing) == 0:
                        print(f"   ✅ {table_name}: All critical columns present")
                else:
                    self.assert_test(False, f"Table Exists: {table_name}", "Table not found")
            
        except Exception as e:
            self.assert_test(False, "Critical Tables Structure", str(e))
    
    def test_relationship_integrity(self):
        """Test foreign key relationships with actual schema"""
        try:
            # Test recipe_ingredients -> recipes relationship
            if 'recipe_ingredients_actual' in self.actual_schema and 'recipes_actual' in self.actual_schema:
                self.cursor.execute("""
                    SELECT COUNT(*)
                    FROM recipe_ingredients_actual ri
                    LEFT JOIN recipes_actual r ON ri.recipe_id = r.recipe_id
                    WHERE ri.recipe_id IS NOT NULL AND r.recipe_id IS NULL
                """)
                
                orphaned_ingredients = self.cursor.fetchone()[0]
                
                self.assert_test(
                    orphaned_ingredients == 0,
                    "Recipe-Ingredients Relationship",
                    f"Found {orphaned_ingredients} orphaned recipe ingredients"
                )
            
            # Test menu_items -> recipes relationship
            if 'menu_items_actual' in self.actual_schema and 'recipes_actual' in self.actual_schema:
                self.cursor.execute("""
                    SELECT COUNT(*)
                    FROM menu_items_actual mi
                    LEFT JOIN recipes_actual r ON mi.recipe_id = r.recipe_id
                    WHERE mi.recipe_id IS NOT NULL AND r.recipe_id IS NULL
                """)
                
                orphaned_menu_items = self.cursor.fetchone()[0]
                
                self.assert_test(
                    orphaned_menu_items == 0,
                    "Menu-Recipe Relationship",
                    f"Found {orphaned_menu_items} menu items without recipes"
                )
                
                if orphaned_menu_items == 0:
                    print("   ✅ Menu items properly linked to recipes")
            
        except Exception as e:
            self.assert_test(False, "Relationship Integrity", str(e))
    
    def test_business_data_validation(self):
        """Test business logic validation with current schema"""
        try:
            # Test recipe costs vs menu prices (using actual column names)
            if 'recipes_actual' in self.actual_schema:
                recipe_columns = self.actual_schema['recipes_actual']['columns']
                
                # Check if both food_cost and menu_price exist
                if 'food_cost' in recipe_columns and 'menu_price' in recipe_columns:
                    self.cursor.execute("""
                        SELECT COUNT(*)
                        FROM recipes_actual
                        WHERE menu_price > 0 AND food_cost > 0
                        AND menu_price <= food_cost
                    """)
                    
                    unprofitable_recipes = self.cursor.fetchone()[0]
                    
                    if unprofitable_recipes > 0:
                        print(f"   ⚠️  Found {unprofitable_recipes} recipes priced at or below cost")
                    else:
                        print(f"   ✅ All recipes priced above cost")
            
            # Test menu item pricing (using actual column names)
            if 'menu_items_actual' in self.actual_schema:
                menu_columns = self.actual_schema['menu_items_actual']['columns']
                
                if 'current_price' in menu_columns:
                    self.cursor.execute("""
                        SELECT COUNT(*)
                        FROM menu_items_actual
                        WHERE current_price <= 0
                    """)
                    
                    free_items = self.cursor.fetchone()[0]
                    
                    self.assert_test(
                        free_items == 0,
                        "No Free Menu Items",
                        f"Found {free_items} menu items with zero/negative prices"
                    )
            
            # Test inventory prices
            self.cursor.execute("""
                SELECT COUNT(*)
                FROM inventory
                WHERE current_price < 0
            """)
            
            negative_prices = self.cursor.fetchone()[0]
            
            self.assert_test(
                negative_prices == 0,
                "No Negative Inventory Prices",
                f"Found {negative_prices} inventory items with negative prices"
            )
            
        except Exception as e:
            self.assert_test(False, "Business Data Validation", str(e))
    
    def test_data_completeness(self):
        """Test data completeness across tables"""
        try:
            # Test inventory completeness
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN item_description IS NOT NULL AND item_description != '' THEN 1 END) as with_desc,
                    COUNT(CASE WHEN current_price > 0 THEN 1 END) as with_price
                FROM inventory
            """)
            
            total, with_desc, with_price = self.cursor.fetchone()
            
            desc_rate = (with_desc / total * 100) if total > 0 else 0
            price_rate = (with_price / total * 100) if total > 0 else 0
            
            self.assert_test(
                desc_rate >= 95,
                "Inventory Description Completeness",
                f"Description completeness: {desc_rate:.1f}% (should be ≥95%)"
            )
            
            self.assert_test(
                price_rate >= 90,
                "Inventory Price Completeness",
                f"Price completeness: {price_rate:.1f}% (should be ≥90%)"
            )
            
            print(f"   📊 Inventory: {desc_rate:.1f}% descriptions, {price_rate:.1f}% prices")
            
            # Test recipe completeness
            if 'recipes_actual' in self.actual_schema:
                self.cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(CASE WHEN recipe_name IS NOT NULL AND recipe_name != '' THEN 1 END) as with_name,
                        COUNT(CASE WHEN food_cost > 0 THEN 1 END) as with_cost
                    FROM recipes_actual
                """)
                
                total, with_name, with_cost = self.cursor.fetchone()
                
                name_rate = (with_name / total * 100) if total > 0 else 0
                cost_rate = (with_cost / total * 100) if total > 0 else 0
                
                print(f"   📊 Recipes: {name_rate:.1f}% named, {cost_rate:.1f}% costed")
            
        except Exception as e:
            self.assert_test(False, "Data Completeness", str(e))
    
    def test_schema_evolution_health(self):
        """Test schema evolution and migration health"""
        try:
            # Check for old tables (should be cleaned up eventually)
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name LIKE '%_old'
            """)
            
            old_tables = self.cursor.fetchall()
            
            if old_tables:
                print(f"   ℹ️  Found {len(old_tables)} old tables (migration artifacts)")
                for (table_name,) in old_tables[:3]:  # Show first 3
                    print(f"      • {table_name}")
            
            # Check for migration tracking
            migration_indicators = ['migrated_from_old_id', 'version_id', 'created_at', 'updated_at']
            tables_with_migration = 0
            
            for table_name, schema_info in self.actual_schema.items():
                if any(indicator in schema_info['columns'] for indicator in migration_indicators):
                    tables_with_migration += 1
            
            self.assert_test(
                tables_with_migration >= 3,
                "Migration Tracking Present",
                f"Only {tables_with_migration} tables have migration tracking"
            )
            
            print(f"   📊 {tables_with_migration} tables have migration tracking")
            
        except Exception as e:
            self.assert_test(False, "Schema Evolution Health", str(e))
    
    def test_performance_indicators(self):
        """Test database performance indicators"""
        try:
            # Check for indexes on critical columns
            self.cursor.execute("""
                SELECT name, tbl_name, sql
                FROM sqlite_master
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
            """)
            
            indexes = self.cursor.fetchall()
            indexed_tables = list(set([idx[1] for idx in indexes]))
            
            critical_tables = ['inventory', 'recipes_actual', 'recipe_ingredients_actual', 'menu_items_actual']
            indexed_critical = [table for table in critical_tables if table in indexed_tables]
            
            index_coverage = len(indexed_critical) / len(critical_tables) * 100
            
            self.assert_test(
                index_coverage >= 50,
                "Critical Table Index Coverage",
                f"Index coverage: {index_coverage:.1f}% of critical tables"
            )
            
            print(f"   📊 Performance: {len(indexes)} indexes, {index_coverage:.1f}% critical table coverage")
            
            # Test query performance on large table
            import time
            start_time = time.time()
            
            self.cursor.execute("""
                SELECT COUNT(*) FROM inventory 
                WHERE current_price > 0
            """)
            
            result = self.cursor.fetchone()[0]
            end_time = time.time()
            
            query_time = (end_time - start_time) * 1000
            
            self.assert_test(
                query_time < 100,
                "Query Performance",
                f"Simple query took {query_time:.2f}ms (should be <100ms)"
            )
            
        except Exception as e:
            self.assert_test(False, "Performance Indicators", str(e))
    
    def run_all_tests(self):
        """Execute all schema-aware database integrity tests"""
        print("🗄️  SCHEMA-AWARE DATABASE INTEGRITY TESTS")
        print("=" * 60)
        print(f"Testing {len(self.actual_schema)} tables with current schema")
        print("=" * 60)
        
        self.test_critical_tables_structure()
        self.test_relationship_integrity()
        self.test_business_data_validation()
        self.test_data_completeness()
        self.test_schema_evolution_health()
        self.test_performance_indicators()
        
        print("=" * 60)
        print(f"🗄️  SCHEMA-AWARE TEST SUMMARY:")
        print(f"   Total: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_failed}")
        
        # Show discovered schema summary
        print(f"\n📊 DISCOVERED SCHEMA SUMMARY:")
        for table_name, info in self.actual_schema.items():
            if not table_name.endswith('_old'):  # Skip old tables in summary
                print(f"   • {table_name}: {len(info['columns'])} columns, PK: {info['pk_columns']}")
        
        if self.tests_failed == 0:
            print("\n🎉 ALL SCHEMA-AWARE TESTS PASSED!")
            print("✅ Database structure is healthy and properly evolved")
            return 0
        else:
            print(f"\n⚠️  {self.tests_failed} issues found")
            print("❌ Database may need attention but structure is discoverable")
            return 1
    
    def cleanup(self):
        """Cleanup resources"""
        self.conn.close()

def main():
    """Main test execution"""
    if not os.path.exists(DATABASE):
        print("❌ Error: Database file not found!")
        return 1
    
    tester = SchemaAwareDatabaseTester()
    try:
        return tester.run_all_tests()
    finally:
        tester.cleanup()

if __name__ == "__main__":
    sys.exit(main())
