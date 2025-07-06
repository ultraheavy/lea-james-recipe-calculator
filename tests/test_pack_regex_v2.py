"""Test enhanced pack size parsing with strict unit requirements"""

import pytest
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from etl import ETLPipeline

@pytest.fixture
def etl():
    """Create ETL pipeline instance"""
    return ETLPipeline(':memory:')

def test_pack_size_with_unit():
    """Test that pack sizes with units parse correctly"""
    etl = ETLPipeline(':memory:')
    
    valid_cases = [
        ("1 x 4 ea", (4.0, "each")),
        ("24 x 1 each", (1.0, "each")),
        ("12 x 2.5 kg", (2.5, "kg")),
        ("1x4l", (4.0, "l")),
        ("128 fl oz", (128.0, "ml")),
        ("5 each", (5.0, "each")),
        ("10 lb", (10.0, "lb")),
        ("500 ml", (500.0, "ml")),
    ]
    
    for pack_size, expected in valid_cases:
        result = etl.parse_pack_size(pack_size)
        assert result == expected, f"Failed for {pack_size}: got {result}"

def test_pack_size_without_unit_fails():
    """Test that pack sizes without units fail"""
    etl = ETLPipeline(':memory:')
    
    invalid_cases = [
        "1 x 4",
        "24 x 12",
        "5 x 5",
        "1x4",
        "10 x 10",
    ]
    
    for pack_size in invalid_cases:
        result = etl.parse_pack_size(pack_size)
        # Should return default (1.0, "each") and log error
        assert result == (1.0, "each"), f"Should fail for {pack_size}"
        # Check that error was logged
        assert any(
            error['value'] == pack_size and 'missing unit' in error['error']
            for error in etl.error_log
        )

def test_uom_aliasing():
    """Test that UOM aliases work correctly"""
    etl = ETLPipeline(':memory:')
    
    alias_cases = [
        ("128 fl oz", (128.0, "ml")),
        ("5 ct", (5.0, "each")),
        ("10 count", (10.0, "each")),
        ("1 bottle", (1.0, "each")),
        ("2 btl", (2.0, "each")),
    ]
    
    for pack_size, expected in alias_cases:
        result = etl.parse_pack_size(pack_size)
        assert result == expected, f"Alias failed for {pack_size}: got {result}"

def test_edge_cases():
    """Test edge cases and malformed inputs"""
    etl = ETLPipeline(':memory:')
    
    edge_cases = [
        ("", (1.0, "each")),  # Empty string
        ("   ", (1.0, "each")),  # Whitespace
        ("abc", (1.0, "each")),  # No numbers
        ("1.5.5 kg", (1.0, "each")),  # Malformed number
    ]
    
    for pack_size, expected in edge_cases:
        result = etl.parse_pack_size(pack_size)
        assert result == expected, f"Edge case failed for '{pack_size}'"

def test_multiplication_symbols():
    """Test various multiplication symbols are normalized"""
    etl = ETLPipeline(':memory:')
    
    mult_cases = [
        ("1 × 4 ea", (4.0, "each")),
        ("1 ✕ 4 ea", (4.0, "each")),
        ("1 ✖ 4 ea", (4.0, "each")),
        ("1 ⨯ 4 ea", (4.0, "each")),
    ]
    
    for pack_size, expected in mult_cases:
        result = etl.parse_pack_size(pack_size)
        assert result == expected, f"Mult symbol failed for {pack_size}"