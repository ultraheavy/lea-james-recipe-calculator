#!/usr/bin/env python3
"""
test_portions_yield.py - Test portions yield handling
"""

import unittest
import sqlite3
import tempfile
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cost_utils import CostCalculator

class TestPortionsYield(unittest.TestCase):
    """Test handling of portions as yield UOM"""
    
    def setUp(self):
        """Create test database"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.conn = sqlite3.connect(self.db_path)
        
        # Create test schema
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE inventory (
                id INTEGER PRIMARY KEY,
                item_code TEXT,
                item_description TEXT,
                current_price REAL,
                pack_size TEXT,
                purchase_unit TEXT,
                recipe_cost_unit TEXT
            );
            
            CREATE TABLE recipes (
                id INTEGER PRIMARY KEY,
                recipe_name TEXT,
                prep_recipe_yield REAL,
                prep_recipe_yield_uom TEXT,
                food_cost REAL
            );
            
            CREATE TABLE recipe_ingredients (
                id INTEGER PRIMARY KEY,
                recipe_id INTEGER,
                ingredient_name TEXT,
                ingredient_id INTEGER,
                quantity REAL,
                unit_of_measure TEXT,
                cost REAL
            );
            
            -- Insert test data
            INSERT INTO inventory VALUES 
                (1, 'FLOUR01', 'Flour', 25.00, '50 lb', 'bag', 'lb');
            
            INSERT INTO recipes VALUES 
                (1, 'Test Recipe', 10, 'portions', 0),
                (2, 'Test Recipe 2', 24, 'each', 0);
            
            INSERT INTO recipe_ingredients VALUES
                (1, 1, 'Flour', 1, 2.5, 'lb', 0),
                (2, 2, 'Flour', 1, 5.0, 'lb', 0);
        """)
        self.conn.commit()
        self.conn.close()
        
        self.calc = CostCalculator(self.db_path)
    
    def tearDown(self):
        """Clean up test database"""
        self.calc.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_portions_yield_conversion(self):
        """Test that portions yield UOM is converted to each"""
        # Calculate cost for recipe with portions yield
        cost, status = self.calc.calc_recipe_cost(1)
        
        # Check that calculation succeeded
        self.assertIn("OK", status)
        self.assertGreater(cost, 0)
        
        # Verify recipe was updated
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        recipe = cursor.execute("""
            SELECT food_cost FROM recipes WHERE id = 1
        """).fetchone()
        
        self.assertIsNotNone(recipe)
        self.assertGreater(recipe[0], 0)
        
        conn.close()
    
    def test_regular_yield_uom(self):
        """Test that regular yield UOMs work unchanged"""
        # Calculate cost for recipe with 'each' yield
        cost, status = self.calc.calc_recipe_cost(2)
        
        # Check that calculation succeeded
        self.assertIn("OK", status)
        self.assertGreater(cost, 0)
    
    def test_yield_uom_case_insensitive(self):
        """Test that PORTIONS, Portions, etc. all work"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update to uppercase
        cursor.execute("""
            UPDATE recipes SET prep_recipe_yield_uom = 'PORTIONS' WHERE id = 1
        """)
        conn.commit()
        conn.close()
        
        # Should still work
        cost, status = self.calc.calc_recipe_cost(1)
        self.assertIn("OK", status)

if __name__ == '__main__':
    unittest.main()