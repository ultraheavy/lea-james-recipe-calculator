#!/usr/bin/env python3
"""
Unit tests for P1 ETL fixes - pack size parsing and UOM normalization
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl import ETLPipeline

class TestPackSizeParsing(unittest.TestCase):
    """Test pack size parsing functionality"""
    
    def setUp(self):
        self.etl = ETLPipeline(':memory:')  # Use in-memory DB for tests
    
    def test_parse_pack_size_basic(self):
        """Test basic pack size formats"""
        test_cases = [
            # Input, Expected (quantity, unit)
            ("1x4l", (4.0, "l")),
            ("24 × 1 ea", (1.0, "each")),
            ("12x2.5kg", (2.5, "kg")),
            ("1 x 50 lb", (50.0, "lb")),
            ("6 x 32 oz", (32.0, "oz")),
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(input=input_str):
                result = self.etl.parse_pack_size(input_str)
                self.assertEqual(result, expected)
    
    def test_parse_pack_size_simple_format(self):
        """Test simple 'N unit' format"""
        test_cases = [
            ("5 fl oz", (5.0, "fl oz")),
            ("24 ct", (24.0, "each")),  # ct → each
            ("1 count", (1.0, "each")),  # count → each
            ("8 piece", (8.0, "each")),  # piece → each
            ("128 fl oz", (128.0, "fl oz")),
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(input=input_str):
                result = self.etl.parse_pack_size(input_str)
                self.assertEqual(result, expected)
    
    def test_parse_pack_size_missing_unit(self):
        """Test rejection of pack sizes missing units"""
        test_cases = [
            "1 x 1",
            "1 x 4",
            "24 x 16",
            "5 x 1",
        ]
        
        for input_str in test_cases:
            with self.subTest(input=input_str):
                result = self.etl.parse_pack_size(input_str)
                # Should return default and log error
                self.assertEqual(result, (1.0, "each"))
                # Check that error was logged
                self.assertTrue(any(
                    error['value'] == input_str and 'missing unit' in error['error'].lower()
                    for error in self.etl.error_log
                ))
    
    def test_parse_pack_size_with_spaces(self):
        """Test handling of multi-word units"""
        test_cases = [
            ("12 x 32 fl oz", (32.0, "fl oz")),
            ("24 x 16 fl oz", (16.0, "fl oz")),
            ("32 x 0.5 ltr", (0.5, "l")),  # ltr → l
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(input=input_str):
                result = self.etl.parse_pack_size(input_str)
                self.assertEqual(result, expected)

class TestUOMMapping(unittest.TestCase):
    """Test UOM alias mapping"""
    
    def setUp(self):
        self.etl = ETLPipeline(':memory:')
    
    def test_map_uom_alias_basic(self):
        """Test basic UOM alias mappings"""
        test_cases = [
            # Input, Expected
            ("ct", "each"),
            ("count", "each"),
            ("piece", "each"),
            ("slice", "each"),
            ("btl", "each"),
            ("bottle", "each"),
            ("bg", "bag"),
            ("jug", "each"),
            ("unit", "each"),
        ]
        
        for input_uom, expected in test_cases:
            with self.subTest(input=input_uom):
                result = self.etl.map_uom_alias(input_uom)
                self.assertEqual(result, expected)
    
    def test_map_uom_alias_volume(self):
        """Test volume unit aliases"""
        test_cases = [
            ("fl", "ml"),
            ("fl oz", "fl oz"),
            ("fl_oz", "fl oz"),
            ("floz", "fl oz"),
            ("fl ounce", "fl oz"),
            ("ltr", "l"),
            ("ltr.", "l"),
            ("liter", "l"),
            ("gal.", "gal"),
            ("gallon", "gal"),
        ]
        
        for input_uom, expected in test_cases:
            with self.subTest(input=input_uom):
                result = self.etl.map_uom_alias(input_uom)
                self.assertEqual(result, expected)
    
    def test_map_uom_alias_unchanged(self):
        """Test that canonical units are unchanged"""
        canonical_units = ["g", "kg", "lb", "oz", "ml", "l", "gal", "qt", "pt", "each", "bag"]
        
        for unit in canonical_units:
            with self.subTest(unit=unit):
                result = self.etl.map_uom_alias(unit)
                self.assertEqual(result, unit)
    
    def test_map_uom_alias_case_insensitive(self):
        """Test case insensitivity"""
        test_cases = [
            ("CT", "each"),
            ("Ct", "each"),
            ("FL OZ", "fl oz"),
            ("Gallon", "gal"),
        ]
        
        for input_uom, expected in test_cases:
            with self.subTest(input=input_uom):
                result = self.etl.map_uom_alias(input_uom)
                self.assertEqual(result, expected)

class TestETLIntegration(unittest.TestCase):
    """Integration tests for ETL pipeline"""
    
    def setUp(self):
        self.etl = ETLPipeline(':memory:')
        # Create test schema
        cursor = self.etl.conn.cursor()
        cursor.execute("""
            CREATE TABLE inventory (
                id INTEGER PRIMARY KEY,
                item_code TEXT UNIQUE,
                item_description TEXT,
                vendor_name TEXT,
                current_price REAL,
                pack_size TEXT,
                purchase_unit TEXT,
                recipe_cost_unit TEXT,
                yield_percent REAL,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE vendor_products (
                id INTEGER PRIMARY KEY,
                inventory_id INTEGER,
                vendor_id INTEGER,
                pack_size TEXT,
                unit_measure TEXT
            )
        """)
        self.etl.conn.commit()
    
    def test_fix_existing_data(self):
        """Test fixing existing database entries"""
        cursor = self.etl.conn.cursor()
        
        # Insert test data with issues
        cursor.execute("""
            INSERT INTO inventory (item_code, pack_size, purchase_unit, recipe_cost_unit)
            VALUES 
            ('TEST1', '1 x 4', 'ct', 'slice'),
            ('TEST2', '24 ct', 'unit', 'piece'),
            ('TEST3', '12 x 32 fl oz', 'jug', 'fl')
        """)
        
        cursor.execute("""
            INSERT INTO vendor_products (id, pack_size)
            VALUES 
            (1, '1 x 1'),
            (2, '24 x 16'),
            (3, '5 fl oz')
        """)
        
        self.etl.conn.commit()
        
        # Run fixes
        self.etl.fix_existing_data()
        
        # Check inventory fixes
        fixed_inventory = cursor.execute("""
            SELECT item_code, pack_size, purchase_unit, recipe_cost_unit
            FROM inventory
            ORDER BY item_code
        """).fetchall()
        
        # Pack sizes should be fixed (defaulted to "1 each" for missing units)
        self.assertEqual(fixed_inventory[0][1], "1 each")  # TEST1: 1 x 4 → 1 each (error)
        self.assertEqual(fixed_inventory[1][1], "24 each")  # TEST2: 24 ct → 24 each
        self.assertEqual(fixed_inventory[2][1], "32 fl oz")  # TEST3: correct
        
        # Check vendor_products fixes
        fixed_vp = cursor.execute("""
            SELECT id, pack_size FROM vendor_products ORDER BY id
        """).fetchall()
        
        self.assertEqual(fixed_vp[0][1], "1 each")  # 1 x 1 → 1 each (error)
        self.assertEqual(fixed_vp[1][1], "1 each")  # 24 x 16 → 1 each (error)
        self.assertEqual(fixed_vp[2][1], "5 fl oz")  # correct

if __name__ == '__main__':
    unittest.main()