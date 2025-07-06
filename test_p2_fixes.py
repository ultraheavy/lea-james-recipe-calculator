#!/usr/bin/env python3
"""
test_p2_fixes.py - Test P2 data quality fixes
"""

import unittest
import sqlite3
import tempfile
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from ingredient_matcher import IngredientMatcher
from etl import ETLPipeline

class TestIngredientMatcher(unittest.TestCase):
    """Test fuzzy matching functionality"""
    
    def setUp(self):
        """Create test database"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.conn = sqlite3.connect(self.db_path)
        
        # Create test schema
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE inventory (
                id INTEGER PRIMARY KEY,
                item_code TEXT UNIQUE,
                item_description TEXT
            );
            
            CREATE TABLE recipes (
                id INTEGER PRIMARY KEY,
                recipe_name TEXT
            );
            
            CREATE TABLE recipe_ingredients (
                id INTEGER PRIMARY KEY,
                recipe_id INTEGER,
                ingredient_name TEXT,
                ingredient_id INTEGER
            );
            
            -- Insert test data
            INSERT INTO inventory VALUES 
                (1, 'KALE01', 'PD KALE CHOPPED'),
                (2, 'RANCH01', 'Dry Goods, Ranch Dressing, with Jalapeno'),
                (3, 'WATER01', 'N/A Bev, Water, Still, Bottles'),
                (4, 'FRIES01', 'Frozen, French Fries, Shoestring');
            
            INSERT INTO recipes VALUES 
                (1, 'Test Recipe 1'),
                (2, 'Test Recipe 2');
            
            INSERT INTO recipe_ingredients VALUES
                (1, 1, 'Kale Kimchi Recipe', NULL),
                (2, 1, 'Charred Onion Ranch', NULL),
                (3, 2, 'Water, Tap', NULL),
                (4, 2, 'French Fries Recipe', NULL);
        """)
        self.conn.commit()
        self.conn.close()
        
        self.matcher = IngredientMatcher(self.db_path)
    
    def tearDown(self):
        """Clean up test database"""
        self.matcher.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_get_mismatched_ingredients(self):
        """Test finding mismatched ingredients"""
        mismatched = self.matcher.get_mismatched_ingredients()
        self.assertEqual(len(mismatched), 4)
        
        # Check first mismatch
        self.assertEqual(mismatched[0]['ingredient_name'], 'Kale Kimchi Recipe')
        self.assertIsNone(mismatched[0]['current_inventory_id'])
    
    def test_normalize_name(self):
        """Test name normalization"""
        test_cases = [
            ('Dry Goods, Ranch Dressing', 'ranch dressing'),
            ('PD KALE CHOPPED', 'kale chopped'),
            ('Water,  Tap', 'water tap'),
            ('Mayonaise - Heavy', 'mayonnaise heavy'),
        ]
        
        for input_name, expected in test_cases:
            with self.subTest(input=input_name):
                result = self.matcher.normalize_name(input_name)
                self.assertEqual(result, expected)
    
    def test_find_matches(self):
        """Test fuzzy matching"""
        inventory = self.matcher.get_inventory_items()
        
        # Test Kale matching
        matches = self.matcher.find_matches('Kale Kimchi Recipe', inventory)
        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0][0], 1)  # Should match KALE01
        
        # Test Ranch matching
        matches = self.matcher.find_matches('Charred Onion Ranch', inventory)
        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0][0], 2)  # Should match RANCH01

class TestETLPriceFixes(unittest.TestCase):
    """Test price backfill functionality"""
    
    def setUp(self):
        """Create test database"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.etl = ETLPipeline(self.db_path)
        
        # Create test schema
        cursor = self.etl.conn.cursor()
        cursor.executescript("""
            CREATE TABLE inventory (
                id INTEGER PRIMARY KEY,
                item_code TEXT UNIQUE,
                item_description TEXT,
                current_price REAL,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE vendor_products (
                id INTEGER PRIMARY KEY,
                inventory_id INTEGER,
                vendor_id INTEGER,
                vendor_price REAL
            );
            
            -- Insert test data
            INSERT INTO inventory (id, item_code, item_description, current_price) VALUES 
                (1, 'ITEM01', 'Item with price', 10.50),
                (2, 'ITEM02', 'Item without price', NULL),
                (3, 'ITEM03', 'Item with zero price', 0),
                (4, 'ITEM04', 'Item no vendor price', NULL);
            
            INSERT INTO vendor_products VALUES
                (1, 2, 1, 15.75),  -- Price for ITEM02
                (2, 2, 1, 14.50),  -- Older price for ITEM02
                (3, 3, 1, 22.00),  -- Price for ITEM03
                (4, 1, 1, 10.50);  -- Price for ITEM01
        """)
        self.etl.conn.commit()
    
    def tearDown(self):
        """Clean up test database"""
        self.etl.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_backfill_prices(self):
        """Test price backfilling"""
        backfilled, still_null = self.etl.backfill_prices()
        
        # Should backfill 2 items (ITEM02 and ITEM03)
        self.assertEqual(backfilled, 2)
        
        # ITEM04 should still be null
        self.assertEqual(len(still_null), 1)
        self.assertEqual(still_null[0]['item_code'], 'ITEM04')
        
        # Verify prices were updated
        cursor = self.etl.conn.cursor()
        
        # ITEM02 should have most recent price
        price = cursor.execute(
            "SELECT current_price FROM inventory WHERE item_code = 'ITEM02'"
        ).fetchone()[0]
        self.assertEqual(price, 15.75)
        
        # ITEM03 should have price from vendor
        price = cursor.execute(
            "SELECT current_price FROM inventory WHERE item_code = 'ITEM03'"
        ).fetchone()[0]
        self.assertEqual(price, 22.00)

if __name__ == '__main__':
    unittest.main()