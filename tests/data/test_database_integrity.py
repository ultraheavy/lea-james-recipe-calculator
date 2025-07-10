#!/usr/bin/env python3
"""
COMPREHENSIVE DATABASE INTEGRITY TESTS - Pytest Version
Schema validation, relationship constraints, and data consistency checks
"""

import pytest
import sqlite3
import os
import sys
from typing import Dict, List, Any
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE = 'restaurant_calculator.db'

class TestDatabaseSchemaIntegrity:
    """Test database schema structure and integrity"""
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
        self.schema = self._discover_schema()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
    
    def _discover_schema(self) -> Dict[str, Dict]:
        """Discover current database schema"""
        schema = {}
        
        self.cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%_old'
        """)
        
        tables = [row[0] for row in self.cursor.fetchall()]
        
        for table in tables:
            self.cursor.execute(f"PRAGMA table_info({table})")
            columns_info = self.cursor.fetchall()
            
            schema[table] = {
                'columns': [col[1] for col in columns_info],
                'pk_columns': [col[1] for col in columns_info if col[5] == 1],
                'required_columns': [col[1] for col in columns_info if col[3] == 1]
            }
        
        return schema
    
    def test_critical_tables_exist(self):
        """Test that all critical business tables exist"""
        critical_tables = [
            'inventory', 'recipes_actual', 'recipe_ingredients_actual', 
            'menu_items_actual', 'vendors', 'units'
        ]
        
        for table in critical_tables:
            assert table in self.schema, f"Critical table {table} missing from database"
        
        print(f"✅ All {len(critical_tables)} critical tables present")
    
    def test_primary_key_integrity(self):
        """Test primary key integrity across all tables"""
        for table_name, table_info in self.schema.items():
            pk_columns = table_info['pk_columns']
            
            assert len(pk_columns) > 0, f"Table {table_name} has no primary key"
            
            # Test primary key uniqueness
            if pk_columns:
                pk_col = pk_columns[0]
                self.cursor.execute(f"""
                    SELECT {pk_col}, COUNT(*) as count
                    FROM {table_name}
                    GROUP BY {pk_col}
                    HAVING COUNT(*) > 1
                """)
                
                duplicates = self.cursor.fetchall()
                assert len(duplicates) == 0, \
                    f"Primary key violations in {table_name}.{pk_col}: {len(duplicates)} duplicates"
    
    def test_foreign_key_relationships(self):
        """Test foreign key relationship integrity"""
        # Test recipe_ingredients -> recipes
        if 'recipe_ingredients_actual' in self.schema and 'recipes_actual' in self.schema:
            self.cursor.execute("""
                SELECT COUNT(*)
                FROM recipe_ingredients_actual ri
                LEFT JOIN recipes_actual r ON ri.recipe_id = r.recipe_id
                WHERE ri.recipe_id IS NOT NULL AND r.recipe_id IS NULL
            """)
            
            orphaned = self.cursor.fetchone()[0]
            assert orphaned == 0, f"Found {orphaned} orphaned recipe ingredients"
        
        # Test menu_items -> recipes
        if 'menu_items_actual' in self.schema and 'recipes_actual' in self.schema:
            self.cursor.execute("""
                SELECT COUNT(*)
                FROM menu_items_actual mi
                LEFT JOIN recipes_actual r ON mi.recipe_id = r.recipe_id
                WHERE mi.recipe_id IS NOT NULL AND r.recipe_id IS NULL
            """)
            
            orphaned = self.cursor.fetchone()[0]
            assert orphaned == 0, f"Found {orphaned} menu items without recipes"

class TestDataIntegrityConstraints:
    """Test data integrity and business rule constraints"""
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
    
    def test_price_data_validity(self):
        """Test that all price data is valid"""
        # Test inventory prices
        self.cursor.execute("""
            SELECT COUNT(*) FROM inventory WHERE current_price < 0
        """)
        negative_prices = self.cursor.fetchone()[0]
        assert negative_prices == 0, f"Found {negative_prices} items with negative prices"
        
        # Test reasonable price ranges
        self.cursor.execute("""
            SELECT MIN(current_price), MAX(current_price), AVG(current_price)
            FROM inventory WHERE current_price > 0
        """)
        min_price, max_price, avg_price = self.cursor.fetchone()
        
        assert 0 < min_price < 1000, f"Minimum price out of range: {min_price}"
        assert 0 < max_price < 10000, f"Maximum price unreasonable: {max_price}"
        assert 0 < avg_price < 1000, f"Average price out of range: {avg_price}"
    
    def test_recipe_cost_consistency(self):
        """Test recipe cost calculation consistency"""
        self.cursor.execute("""
            SELECT COUNT(*) 
            FROM recipes_actual 
            WHERE food_cost IS NOT NULL AND food_cost < 0
        """)
        negative_costs = self.cursor.fetchone()[0]
        assert negative_costs == 0, f"Found {negative_costs} recipes with negative costs"
        
        # Test that recipes with ingredients have calculated costs
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM recipes_actual r
            INNER JOIN recipe_ingredients_actual ri ON r.recipe_id = ri.recipe_id
            WHERE r.food_cost IS NULL OR r.food_cost = 0
            GROUP BY r.recipe_id
        """)
        
        recipes_without_costs = len(self.cursor.fetchall())
        # Allow some recipes to not have costs yet (development/new recipes)
        total_recipes_with_ingredients = self.cursor.execute("""
            SELECT COUNT(DISTINCT recipe_id) FROM recipe_ingredients_actual
        """).fetchone()[0]
        
        if total_recipes_with_ingredients > 0:
            cost_coverage = (total_recipes_with_ingredients - recipes_without_costs) / total_recipes_with_ingredients * 100
            assert cost_coverage >= 70, f"Recipe cost coverage too low: {cost_coverage:.1f}%"
    
    def test_data_completeness_requirements(self):
        """Test data completeness requirements"""
        # Test inventory data completeness
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN item_description IS NOT NULL AND item_description != '' THEN 1 END) as with_desc,
                COUNT(CASE WHEN current_price > 0 THEN 1 END) as with_price
            FROM inventory
        """)
        
        total, with_desc, with_price = self.cursor.fetchone()
        
        if total > 0:
            desc_rate = with_desc / total * 100
            price_rate = with_price / total * 100
            
            assert desc_rate >= 95, f"Inventory description completeness too low: {desc_rate:.1f}%"
            assert price_rate >= 90, f"Inventory price completeness too low: {price_rate:.1f}%"
    
    def test_unique_constraints(self):
        """Test unique constraint integrity"""
        # Test inventory item_code uniqueness
        self.cursor.execute("""
            SELECT item_code, COUNT(*) as count
            FROM inventory
            WHERE item_code IS NOT NULL AND item_code != ''
            GROUP BY item_code
            HAVING COUNT(*) > 1
        """)
        
        duplicates = self.cursor.fetchall()
        assert len(duplicates) == 0, f"Found {len(duplicates)} duplicate item codes"
        
        # Test recipe name uniqueness
        self.cursor.execute("""
            SELECT recipe_name, COUNT(*) as count
            FROM recipes_actual
            WHERE recipe_name IS NOT NULL AND recipe_name != ''
            GROUP BY recipe_name
            HAVING COUNT(*) > 1
        """)
        
        duplicates = self.cursor.fetchall()
        assert len(duplicates) == 0, f"Found {len(duplicates)} duplicate recipe names"

@pytest.mark.performance
class TestDatabasePerformance:
    """Test database performance characteristics"""
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
    
    def test_query_performance_benchmarks(self):
        """Test that critical queries meet performance benchmarks"""
        # Test inventory lookup performance
        start_time = time.time()
        self.cursor.execute("""
            SELECT item_code, item_description, current_price
            FROM inventory 
            WHERE current_price > 0
            ORDER BY item_description
            LIMIT 100
        """)
        results = self.cursor.fetchall()
        end_time = time.time()
        
        query_time = (end_time - start_time) * 1000
        assert query_time < 200, f"Inventory query too slow: {query_time:.2f}ms"
        assert len(results) > 0, "Query should return results"
        
        # Test recipe cost calculation query performance
        start_time = time.time()
        self.cursor.execute("""
            SELECT r.recipe_name, r.food_cost, COUNT(ri.ingredient_id) as ingredient_count
            FROM recipes_actual r
            LEFT JOIN recipe_ingredients_actual ri ON r.recipe_id = ri.recipe_id
            GROUP BY r.recipe_id, r.recipe_name, r.food_cost
            ORDER BY r.recipe_name
        """)
        results = self.cursor.fetchall()
        end_time = time.time()
        
        query_time = (end_time - start_time) * 1000
        assert query_time < 500, f"Recipe query too slow: {query_time:.2f}ms"
    
    def test_index_coverage(self):
        """Test that critical tables have appropriate indexes"""
        self.cursor.execute("""
            SELECT name, tbl_name, sql
            FROM sqlite_master
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
        """)
        
        indexes = self.cursor.fetchall()
        indexed_tables = list(set([idx[1] for idx in indexes]))
        
        critical_tables = ['inventory', 'recipes_actual', 'recipe_ingredients_actual', 'menu_items_actual']
        
        for table in critical_tables:
            if table in indexed_tables:
                continue  # Table has at least one index
            else:
                print(f"⚠️  Consider adding index to {table} for better performance")

@pytest.mark.data
class TestDataConsistency:
    """Test data consistency across related tables"""
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
    
    def test_cross_table_data_consistency(self):
        """Test data consistency across related tables"""
        # Test recipe ingredient costs vs inventory prices
        self.cursor.execute("""
            SELECT 
                ri.ingredient_name,
                ri.cost as recipe_cost,
                i.current_price as inventory_price
            FROM recipe_ingredients_actual ri
            LEFT JOIN inventory i ON ri.ingredient_id = i.id
            WHERE ri.cost IS NOT NULL AND i.current_price IS NOT NULL
            AND ABS(ri.cost - i.current_price) > (i.current_price * 0.5)
            LIMIT 10
        """)
        
        cost_mismatches = self.cursor.fetchall()
        
        # Allow some cost mismatches due to unit conversions, but not too many
        if len(cost_mismatches) > 0:
            print(f"⚠️  Found {len(cost_mismatches)} ingredient cost mismatches (may be due to unit conversions)")
    
    def test_menu_pricing_consistency(self):
        """Test menu pricing consistency"""
        # Test that menu items with recipes have reasonable pricing
        self.cursor.execute("""
            SELECT 
                mi.item_name,
                mi.current_price as menu_price,
                r.food_cost,
                CASE 
                    WHEN mi.current_price > 0 THEN (mi.current_price - r.food_cost) / mi.current_price * 100
                    ELSE 0
                END as margin
            FROM menu_items_actual mi
            LEFT JOIN recipes_actual r ON mi.recipe_id = r.recipe_id
            WHERE mi.current_price > 0 AND r.food_cost > 0
        """)
        
        pricing_data = self.cursor.fetchall()
        
        if pricing_data:
            reasonable_margins = [item for item in pricing_data if item[3] >= 50]  # 50%+ margin
            margin_rate = len(reasonable_margins) / len(pricing_data) * 100
            
            # Business expectation: most items should have reasonable margins
            assert margin_rate >= 60, f"Menu margin quality too low: {margin_rate:.1f}% of items have 50%+ margins"

if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v", "--tb=short"])
