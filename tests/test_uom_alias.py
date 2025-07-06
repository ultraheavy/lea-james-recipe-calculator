#!/usr/bin/env python3
"""
test_uom_alias.py - Test UOM alias mapping
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from etl import ETLPipeline

class TestUOMAlias(unittest.TestCase):
    """Test UOM alias mapping and conversions"""
    
    def setUp(self):
        self.etl = ETLPipeline(':memory:')
    
    def test_new_aliases(self):
        """Test new P1.1 aliases"""
        test_cases = [
            # Volume units to ml
            ("tbsp", "ml"),
            ("tablespoon", "ml"),
            ("tblsp", "ml"),
            ("fl oz", "ml"),
            ("floz", "ml"),
            ("fl_oz", "ml"),
            ("fl-oz", "ml"),
            ("fl", "ml"),
            
            # Count units
            ("loaf", "each"),
            ("portions", "each"),
        ]
        
        for input_uom, expected in test_cases:
            with self.subTest(input=input_uom):
                result = self.etl.map_uom_alias(input_uom)
                self.assertEqual(result, expected)
    
    def test_canonical_uom_conversions(self):
        """Test canonical UOM with conversion factors"""
        test_cases = [
            ("tbsp", ("ml", 14.786)),
            ("tablespoon", ("ml", 14.786)),
            ("tsp", ("ml", 4.929)),
            ("fl oz", ("ml", 29.573)),
            ("cup", ("ml", 236.588)),
            ("pt", ("ml", 473.176)),
            ("qt", ("ml", 946.353)),
            ("gal", ("ml", 3785.412)),
            ("lb", ("lb", 453.592)),  # Maps to lb first, then factor
            ("oz", ("oz", 28.350)),    # Maps to oz first, then factor
            ("each", ("each", 1.0)),
            ("loaf", ("each", 1.0)),
        ]
        
        for input_uom, expected in test_cases:
            with self.subTest(input=input_uom):
                canonical, factor = self.etl.canonical_uom(input_uom)
                self.assertEqual(canonical, expected[0])
                self.assertAlmostEqual(factor, expected[1], places=3)
    
    def test_case_insensitive(self):
        """Test case insensitivity"""
        test_cases = [
            ("TBSP", "ml"),
            ("Tablespoon", "ml"),
            ("FL OZ", "ml"),
            ("Loaf", "each"),
            ("PORTIONS", "each"),
        ]
        
        for input_uom, expected in test_cases:
            with self.subTest(input=input_uom):
                result = self.etl.map_uom_alias(input_uom)
                self.assertEqual(result, expected)
    
    def test_existing_aliases_preserved(self):
        """Ensure P1 aliases still work"""
        test_cases = [
            ("ct", "each"),
            ("count", "each"),
            ("piece", "each"),
            ("slice", "each"),
            ("btl", "each"),
            ("bg", "bag"),
            ("ltr", "l"),
            ("gallon", "gal"),
        ]
        
        for input_uom, expected in test_cases:
            with self.subTest(input=input_uom):
                result = self.etl.map_uom_alias(input_uom)
                self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()