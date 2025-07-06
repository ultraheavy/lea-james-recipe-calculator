#!/usr/bin/env python3
"""
test_pack_size.py - Test pack size parsing
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from etl import ETLPipeline

class TestPackSizeParsing(unittest.TestCase):
    """Test pack size parsing with new patterns"""
    
    def setUp(self):
        self.etl = ETLPipeline(':memory:')
    
    def test_single_token_pack_sizes(self):
        """Test single-token pack sizes like '128 fl oz'"""
        test_cases = [
            ("128 fl oz", (128.0, "ml")),
            ("32 fl oz", (32.0, "ml")),
            ("5 fl oz", (5.0, "ml")),
            ("16 fl oz", (16.0, "ml")),
            ("8.5 fl oz", (8.5, "ml")),
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(input=input_str):
                result = self.etl.parse_pack_size(input_str)
                self.assertEqual(result, expected)
    
    def test_multi_pack_formats(self):
        """Test N x N unit formats"""
        test_cases = [
            ("12x2.5kg", (2.5, "kg")),
            ("1x4l", (4.0, "l")),
            ("24 x 1 ea", (1.0, "each")),
            ("6 x 32 oz", (32.0, "oz")),
            ("12 x 16 fl oz", (16.0, "ml")),
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(input=input_str):
                result = self.etl.parse_pack_size(input_str)
                self.assertEqual(result, expected)
    
    def test_invalid_pack_sizes(self):
        """Test rejection of invalid formats"""
        test_cases = [
            "1 x 4",      # Missing unit
            "24 x 16",    # Missing unit
            "5 x 1",      # Missing unit
        ]
        
        for input_str in test_cases:
            with self.subTest(input=input_str):
                result = self.etl.parse_pack_size(input_str)
                # Should return default
                self.assertEqual(result, (1.0, "each"))
                # Should log error
                self.assertTrue(any(
                    'missing unit' in error['error'].lower()
                    for error in self.etl.error_log
                ))
    
    def test_edge_cases(self):
        """Test edge cases"""
        test_cases = [
            ("", (1.0, "each")),
            ("   ", (1.0, "each")),
            ("24 ct", (24.0, "each")),
            ("1 loaf", (1.0, "each")),
            ("5 tbsp", (5.0, "ml")),
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(input=input_str):
                result = self.etl.parse_pack_size(input_str)
                self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()