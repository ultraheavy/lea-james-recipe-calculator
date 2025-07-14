#!/usr/bin/env python3
"""
DATABASE INTEGRITY TESTS - Simple Version (No Dependencies)
Critical tests for schema validation, relationship constraints, and data consistency

These tests ensure database integrity for Lea Jane's Hot Chicken system
"""

import sqlite3
import os
import sys
from datetime import datetime

DATABASE = 'restaurant_calculator.db'

class DatabaseIntegrityTester:
    """Comprehensive database integrity testing"""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
        
        # Define critical tables and their expected relationships
        self.CRITICAL_TABLES = {
            'inventory': ['id', 'item_code', 'item_description', 'current_price'],
            'recipes_actual': ['id', 'recipe_name', 'food_cost'],
            'recipe_ingredients_actual': ['id', 'recipe_id', 'ingredient_id', 'quantity'],
            'menu_items_actual': ['id', 'item_name', 'menu_price', 'food_cost'],
            'vendors': ['id', 'vendor_name'],
            'units': ['id', 'unit_name', 'unit_type']
        }
        
        # Define expected foreign key relationships
        self.FOREIGN_KEY_RELATIONSHIPS = [
            ('recipe_ingredients_actual', 'recipe_id', 'recipes_actual', 'id'),
            ('recipe_ingredients_actual', 'ingredient_id', 'inventory', 'id'),
            ('menu_items_actual', 'recipe_id', 'recipes_actual', 'id')
        ]
    
    def assert_test(self, condition: bool, test_name: str, message: str = ""):
        """Simple assertion helper"""
        self.tests_run += 1
        
        if condition:
            print(f"✅ PASS: {test_name}")
            self.tests_passed += 1
        else:
            print(f"❌ FAIL: {test_name} - {message}")
            self.tests_failed += 1
    
    def test_critical_tables_exist(self):
        """Test that all critical tables exist in the database"""
        try:
            # Get all table names
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            
            existing_tables = [row[0] for row in self.cursor.fetchall()]
            
            # Check critical tables
            for table_name, required_columns in self.CRITICAL_TABLES.items():
                self.assert_test(
                    table_name in existing_tables,
                    f"Critical Table: {table_name}",
                    f"Required table '{table_name}' missing from database"
                )
            
            print(f"   📊 Found {len(existing_tables)} total tables in database")
            
        except Exception as e:
            self.assert_test(False, "Critical Tables Existence", str(e))
    
    def test_table_schema_integrity(self):
        """Test that critical tables have required columns"""
        try:
            for table_name, required_columns in self.CRITICAL_TABLES.items():
                # Check if table exists first
                self.cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name = ?
                """, (table_name,))
                
                if not self.cursor.fetchone():
                    continue  # Skip if table doesn't exist
                
                # Get table schema
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = self.cursor.fetchall()
                existing_columns = [col[1] for col in columns_info]  # col[1] is column name
                
                # Check required columns
                missing_columns = []
                for required_col in required_columns:
                    if required_col not in existing_columns:
                        missing_columns.append(required_col)
                
                self.assert_test(
                    len(missing_columns) == 0,
                    f"Schema: {table_name}",
                    f"Missing columns in {table_name}: {missing_columns}"
                )
                
                if len(missing_columns) == 0:
                    print(f"   ✅ {table_name}: {len(existing_columns)} columns present")
                
        except Exception as e:
            self.assert_test(False, "Table Schema Integrity", str(e))
    
    def test_primary_key_constraints(self):
        """Test that primary keys are properly defined and unique"""
        try:
            for table_name in self.CRITICAL_TABLES.keys():
                # Check if table exists
                self.cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name = ?
                """, (table_name,))
                
                if not self.cursor.fetchone():
                    continue
                
                # Get primary key info
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = self.cursor.fetchall()
                
                # Find primary key column(s)
                pk_columns = [col[1] for col in columns_info if col[5] == 1]  # col[5] is pk flag
                
                self.assert_test(
                    len(pk_columns) > 0,
                    f"Primary Key: {table_name}",
                    f"No primary key defined for {table_name}"
                )
                
                if pk_columns:
                    # Test primary key uniqueness
                    pk_col = pk_columns[0]  # Use first PK column
                    self.cursor.execute(f"""
                        SELECT {pk_col}, COUNT(*) as count
                        FROM {table_name}
                        GROUP BY {pk_col}
                        HAVING COUNT(*) > 1
                    """)
                    
                    duplicates = self.cursor.fetchall()
                    
                    self.assert_test(
                        len(duplicates) == 0,
                        f"PK Uniqueness: {table_name}.{pk_col}",
                        f"Found {len(duplicates)} duplicate primary key values"
                    )
                
        except Exception as e:
            self.assert_test(False, "Primary Key Constraints", str(e))
    
    def test_foreign_key_relationships(self):
        """Test foreign key relationship integrity"""
        try:
            for child_table, fk_column, parent_table, pk_column in self.FOREIGN_KEY_RELATIONSHIPS:
                # Check if both tables exist
                tables_exist = True
                for table in [child_table, parent_table]:
                    self.cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name = ?
                    """, (table,))
                    if not self.cursor.fetchone():
                        tables_exist = False
                        break
                
                if not tables_exist:
                    continue
                
                # Check for orphaned records (foreign key violations)
                self.cursor.execute(f"""
                    SELECT COUNT(*)
                    FROM {child_table} c
                    LEFT JOIN {parent_table} p ON c.{fk_column} = p.{pk_column}
                    WHERE c.{fk_column} IS NOT NULL AND p.{pk_column} IS NULL
                """)
                
                orphaned_count = self.cursor.fetchone()[0]
                
                self.assert_test(
                    orphaned_count == 0,
                    f"FK Integrity: {child_table}.{fk_column} -> {parent_table}.{pk_column}",
                    f"Found {orphaned_count} orphaned records"
                )
                
                if orphaned_count == 0:
                    print(f"   ✅ {child_table}.{fk_column} -> {parent_table}.{pk_column}: OK")
                
        except Exception as e:
            self.assert_test(False, "Foreign Key Relationships", str(e))
    
    def test_data_type_consistency(self):
        """Test data type consistency across related fields"""
        try:
            # Test price fields are numeric
            price_tables = [
                ('inventory', 'current_price'),
                ('recipes_actual', 'food_cost'),
                ('menu_items_actual', 'menu_price'),
                ('menu_items_actual', 'food_cost')
            ]
            
            for table_name, price_column in price_tables:
                # Check if table exists
                self.cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name = ?
                """, (table_name,))
                
                if not self.cursor.fetchone():
                    continue
                
                # Check for non-numeric price values
                self.cursor.execute(f"""
                    SELECT COUNT(*)
                    FROM {table_name}
                    WHERE {price_column} IS NOT NULL
                    AND (
                        typeof({price_column}) NOT IN ('real', 'integer')
                        OR {price_column} < 0
                    )
                """)
                
                invalid_prices = self.cursor.fetchone()[0]
                
                self.assert_test(
                    invalid_prices == 0,
                    f"Data Type: {table_name}.{price_column}",
                    f"Found {invalid_prices} invalid price values"
                )
            
        except Exception as e:
            self.assert_test(False, "Data Type Consistency", str(e))
    
    def test_business_rule_constraints(self):
        """Test business rule constraints"""
        try:
            # Test 1: Menu prices should be higher than food costs
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name = 'menu_items_actual'
            """)
            
            if self.cursor.fetchone():
                self.cursor.execute("""
                    SELECT COUNT(*)
                    FROM menu_items_actual
                    WHERE menu_price > 0 AND food_cost > 0
                    AND menu_price <= food_cost
                """)
                
                unprofitable_items = self.cursor.fetchone()[0]
                
                # This is a business warning, not a hard constraint failure
                if unprofitable_items > 0:
                    print(f"   ⚠️  Found {unprofitable_items} menu items priced at or below cost")
                else:
                    print(f"   ✅ All menu items priced above cost")
            
            # Test 2: Recipe ingredients should have positive quantities
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name = 'recipe_ingredients_actual'
            """)
            
            if self.cursor.fetchone():
                self.cursor.execute("""
                    SELECT COUNT(*)
                    FROM recipe_ingredients_actual
                    WHERE quantity IS NOT NULL AND quantity <= 0
                """)
                
                invalid_quantities = self.cursor.fetchone()[0]
                
                self.assert_test(
                    invalid_quantities == 0,
                    "Business Rule: Positive Quantities",
                    f"Found {invalid_quantities} recipe ingredients with zero/negative quantities"
                )
            
            # Test 3: Item codes should be unique where present
            self.cursor.execute("""
                SELECT item_code, COUNT(*) as count
                FROM inventory
                WHERE item_code IS NOT NULL AND item_code != ''
                GROUP BY item_code
                HAVING COUNT(*) > 1
            """)
            
            duplicate_codes = self.cursor.fetchall()
            
            self.assert_test(
                len(duplicate_codes) == 0,
                "Business Rule: Unique Item Codes",
                f"Found {len(duplicate_codes)} duplicate item codes"
            )
            
        except Exception as e:
            self.assert_test(False, "Business Rule Constraints", str(e))
    
    def test_index_performance(self):
        """Test that critical indexes exist for performance"""
        try:
            # Get existing indexes
            self.cursor.execute("""
                SELECT name, tbl_name, sql
                FROM sqlite_master
                WHERE type='index' AND name NOT LIKE 'sqlite_%'
            """)
            
            indexes = self.cursor.fetchall()
            
            # Check for critical indexes
            critical_indexes = [
                ('inventory', 'item_code'),
                ('recipes_actual', 'recipe_name'),
                ('recipe_ingredients_actual', 'recipe_id'),
                ('menu_items_actual', 'item_name')
            ]
            
            existing_index_tables = [idx[1] for idx in indexes]
            
            for table, column in critical_indexes:
                # Check if table exists first
                self.cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name = ?
                """, (table,))
                
                if not self.cursor.fetchone():
                    continue
                
                # Look for index on this table
                table_has_index = table in existing_index_tables
                
                if not table_has_index:
                    print(f"   ⚠️  Consider adding index on {table}.{column} for performance")
            
            print(f"   📊 Found {len(indexes)} indexes in database")
            
        except Exception as e:
            self.assert_test(False, "Index Performance", str(e))
    
    def test_database_statistics(self):
        """Test database statistics and health metrics"""
        try:
            # Get table row counts
            table_stats = {}
            
            for table_name in self.CRITICAL_TABLES.keys():
                # Check if table exists
                self.cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name = ?
                """, (table_name,))
                
                if not self.cursor.fetchone():
                    continue
                
                self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = self.cursor.fetchone()[0]
                table_stats[table_name] = count
            
            # Validate minimum expected data
            min_expectations = {
                'inventory': 100,      # Should have at least 100 inventory items
                'recipes_actual': 10,  # Should have at least 10 recipes
                'menu_items_actual': 20 # Should have at least 20 menu items
            }
            
            for table, min_count in min_expectations.items():
                if table in table_stats:
                    actual_count = table_stats[table]
                    
                    self.assert_test(
                        actual_count >= min_count,
                        f"Data Volume: {table}",
                        f"Expected at least {min_count} records, found {actual_count}"
                    )
                    
                    print(f"   📊 {table}: {actual_count} records")
            
        except Exception as e:
            self.assert_test(False, "Database Statistics", str(e))
    
    def test_database_file_integrity(self):
        """Test database file integrity"""
        try:
            # Check database file size
            db_size = os.path.getsize(DATABASE)
            
            self.assert_test(
                db_size > 1024 * 100,  # At least 100KB
                "Database File Size",
                f"Database file seems too small: {db_size} bytes"
            )
            
            # Run PRAGMA integrity_check
            self.cursor.execute("PRAGMA integrity_check")
            integrity_result = self.cursor.fetchone()[0]
            
            self.assert_test(
                integrity_result == "ok",
                "Database Integrity Check",
                f"SQLite integrity check failed: {integrity_result}"
            )
            
            # Check for database corruption indicators
            self.cursor.execute("PRAGMA quick_check")
            quick_check = self.cursor.fetchone()[0]
            
            self.assert_test(
                quick_check == "ok",
                "Database Quick Check",
                f"SQLite quick check failed: {quick_check}"
            )
            
            print(f"   📊 Database file size: {db_size / 1024:.1f} KB")
            
        except Exception as e:
            self.assert_test(False, "Database File Integrity", str(e))
    
    def run_all_tests(self):
        """Execute all database integrity tests"""
        print("🗄️  DATABASE INTEGRITY TESTS")
        print("=" * 50)
        print("Testing schema validation, relationships, and data consistency")
        print("=" * 50)
        
        self.test_critical_tables_exist()
        self.test_table_schema_integrity()
        self.test_primary_key_constraints()
        self.test_foreign_key_relationships()
        self.test_data_type_consistency()
        self.test_business_rule_constraints()
        self.test_index_performance()
        self.test_database_statistics()
        self.test_database_file_integrity()
        
        print("=" * 50)
        print(f"🗄️  DATABASE INTEGRITY TEST SUMMARY:")
        print(f"   Total: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_failed}")
        
        if self.tests_failed == 0:
            print("🎉 ALL DATABASE INTEGRITY TESTS PASSED!")
            print("✅ Database structure is sound and relationships are intact")
            return 0
        else:
            print(f"⚠️  {self.tests_failed} database integrity issues found")
            print("❌ Database may need maintenance or schema fixes")
            return 1
    
    def cleanup(self):
        """Cleanup resources"""
        self.conn.close()

def main():
    """Main test execution"""
    if not os.path.exists(DATABASE):
        print("❌ Error: Database file not found!")
        print("Database integrity tests require the restaurant database.")
        return 1
    
    tester = DatabaseIntegrityTester()
    try:
        return tester.run_all_tests()
    finally:
        tester.cleanup()

if __name__ == "__main__":
    sys.exit(main())
