#!/usr/bin/env python3
"""
ENHANCED XTRACHEF INTEGRATION TESTS - CSV Import and Data Mapping
Additional critical tests for CSV import functionality and advanced data validation
"""

import pytest
import sqlite3
import os
import sys
import json
import csv
import tempfile
from decimal import Decimal
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE = 'restaurant_calculator.db'

class TestXtraChefCSVImport:
    """Test XtraChef CSV import functionality and data mapping"""
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
    
    def test_csv_field_mapping_integrity(self):
        """Test that CSV import mapping follows DATA_MODEL.md specifications"""
        # Define expected CSV to database field mapping
        expected_mapping = {
            'Invoice Item Code': 'item_code',
            'Product Name': 'item_description',
            'Vendor': 'vendor_name',
            'Price': 'current_price',
            'Invoice Date': 'last_purchased_date',
            'Pack Size': 'pack_size',
            'UOM': 'purchase_unit',
            'Item UOM': 'recipe_cost_unit'
        }
        
        # Verify all expected database fields exist
        self.cursor.execute("PRAGMA table_info(inventory)")
        db_columns = [col[1] for col in self.cursor.fetchall()]
        
        for csv_field, db_field in expected_mapping.items():
            assert db_field in db_columns, \
                f"CRITICAL: CSV mapping field '{db_field}' missing from database"
            
        print("✅ CSV to database field mapping verified")
    
    def test_etl_module_functionality(self):
        """Test that ETL module can be imported and has required functions"""
        try:
            # This test validates ETL module structure without actually importing
            # (to avoid dependency issues in testing environment)
            
            etl_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'etl.py')
            assert os.path.exists(etl_file_path), "ETL module file must exist"
            
            # Read ETL file and check for required classes/functions
            with open(etl_file_path, 'r') as f:
                etl_content = f.read()
            
            required_components = [
                'class ETLPipeline',
                'def process_inventory_csv',
                'def parse_pack_size',
                'def map_uom_alias'
            ]
            
            for component in required_components:
                assert component in etl_content, \
                    f"Required ETL component missing: {component}"
            
            print("✅ ETL module structure validated")
            
        except Exception as e:
            pytest.fail(f"ETL module validation failed: {str(e)}")
    
    def test_uom_aliases_configuration(self):
        """Test UOM aliases configuration for CSV import processing"""
        uom_file = 'uom_aliases.json'
        
        if os.path.exists(uom_file):
            with open(uom_file, 'r') as f:
                uom_data = json.load(f)
            
            # Validate structure
            assert 'aliases' in uom_data, "UOM aliases must contain 'aliases' key"
            assert 'canonical_units' in uom_data, "UOM aliases must contain 'canonical_units' key"
            
            aliases = uom_data['aliases']
            canonical = uom_data['canonical_units']
            
            # Check for common aliases
            common_aliases = ['lb', 'lbs', 'oz', 'each', 'ea', 'ct', 'count']
            found_aliases = 0
            
            for alias in common_aliases:
                if alias in aliases:
                    found_aliases += 1
            
            assert found_aliases >= 5, f"Expected at least 5 common aliases, found {found_aliases}"
            
            print(f"✅ UOM aliases configuration: {len(aliases)} aliases, {len(canonical)} canonical units")
        else:
            print("⚠️  UOM aliases file not found - may impact import processing")

class TestDataMappingIntegrity:
    """Test data mapping integrity between XtraChef imports and database"""
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
    
    def test_pack_size_format_consistency(self):
        """Test pack size format consistency after import processing"""
        self.cursor.execute("""
            SELECT pack_size, COUNT(*) as count
            FROM inventory 
            WHERE pack_size IS NOT NULL AND pack_size != ''
            GROUP BY pack_size
            ORDER BY count DESC
            LIMIT 20
        """)
        
        pack_sizes = self.cursor.fetchall()
        
        if pack_sizes:
            print(f"Found {len(pack_sizes)} distinct pack size formats:")
            
            valid_formats = 0
            for pack_size, count in pack_sizes:
                # Check for expected format patterns
                has_number = any(c.isdigit() for c in pack_size)
                has_unit = any(c.isalpha() for c in pack_size)
                
                if has_number and has_unit:
                    valid_formats += 1
                    print(f"✅ {pack_size}: {count} items")
                else:
                    print(f"⚠️  {pack_size}: {count} items (unusual format)")
            
            format_rate = (valid_formats / len(pack_sizes) * 100)
            assert format_rate >= 80, f"Pack size format quality too low: {format_rate:.1f}%"
        else:
            print("⚠️  No pack size data found")
    
    def test_vendor_mapping_consistency(self):
        """Test vendor name mapping consistency"""
        # Check for vendor name variations that might indicate mapping issues
        self.cursor.execute("""
            SELECT vendor_name, COUNT(*) as item_count
            FROM inventory 
            WHERE vendor_name IS NOT NULL
            GROUP BY UPPER(vendor_name)
            HAVING COUNT(*) > 5
            ORDER BY item_count DESC
        """)
        
        vendors = self.cursor.fetchall()
        
        # Look for potential duplicates (similar names)
        vendor_names = [v[0].upper() for v in vendors]
        potential_duplicates = []
        
        for i, name1 in enumerate(vendor_names):
            for j, name2 in enumerate(vendor_names[i+1:], i+1):
                # Simple similarity check
                if name1 in name2 or name2 in name1:
                    if abs(len(name1) - len(name2)) <= 3:  # Similar length
                        potential_duplicates.append((vendors[i][0], vendors[j][0]))
        
        if potential_duplicates:
            print(f"⚠️  Found {len(potential_duplicates)} potential vendor name duplicates:")
            for name1, name2 in potential_duplicates[:5]:  # Show first 5
                print(f"   • '{name1}' vs '{name2}'")
        
        assert len(vendors) >= 3, f"Expected at least 3 major vendors, found {len(vendors)}"
        
        print(f"✅ Vendor mapping: {len(vendors)} distinct vendors")
    
    def test_price_data_mapping_accuracy(self):
        """Test price data mapping accuracy and consistency"""
        # Check price data distribution
        self.cursor.execute("""
            SELECT 
                MIN(current_price) as min_price,
                MAX(current_price) as max_price,
                AVG(current_price) as avg_price,
                COUNT(CASE WHEN current_price > 0 THEN 1 END) as items_with_price,
                COUNT(*) as total_items
            FROM inventory
        """)
        
        stats = self.cursor.fetchone()
        min_price, max_price, avg_price, with_price, total = stats
        
        # Validate price distribution
        assert min_price >= 0, f"Minimum price should be non-negative: {min_price}"
        assert max_price < 10000, f"Maximum price seems unreasonable: {max_price}"
        assert 1 <= avg_price <= 500, f"Average price outside expected range: {avg_price}"
        
        price_coverage = (with_price / total * 100) if total > 0 else 0
        assert price_coverage >= 90, f"Price coverage too low: {price_coverage:.1f}%"
        
        print(f"✅ Price mapping: {price_coverage:.1f}% coverage, avg=${avg_price:.2f}")
    
    def test_item_code_format_validation(self):
        """Test item code format validation after import"""
        # Check item code formats and patterns
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN item_code LIKE '%_XC%' THEN 1 END) as xtrachef_format,
                COUNT(CASE WHEN LENGTH(item_code) >= 4 THEN 1 END) as adequate_length,
                COUNT(CASE WHEN item_code REGEXP '^[A-Za-z0-9_-]+$' THEN 1 END) as valid_chars
            FROM inventory
            WHERE item_code IS NOT NULL AND item_code != ''
        """)
        
        stats = self.cursor.fetchone()
        total, xtrachef_format, adequate_length, valid_chars = stats
        
        if total > 0:
            xtrachef_rate = (xtrachef_format / total * 100)
            length_rate = (adequate_length / total * 100)
            
            print(f"✅ Item code analysis:")
            print(f"   • {xtrachef_rate:.1f}% XtraChef formatted")
            print(f"   • {length_rate:.1f}% adequate length (≥4 chars)")
            
            assert length_rate >= 95, f"Too many short item codes: {length_rate:.1f}%"

class TestProtectedFieldPreservation:
    """Test that protected fields are preserved during any data operations"""
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
    
    def test_sacred_field_data_preservation(self):
        """Test that sacred XtraChef fields contain valid data"""
        sacred_fields = ['item_code', 'item_description', 'vendor_name', 'current_price']
        
        for field in sacred_fields:
            self.cursor.execute(f"""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN {field} IS NOT NULL AND {field} != '' THEN 1 END) as non_null
                FROM inventory
            """)
            
            total, non_null = self.cursor.fetchone()
            coverage = (non_null / total * 100) if total > 0 else 0
            
            # Different coverage expectations for different fields
            if field == 'current_price':
                min_coverage = 95  # Prices are critical
            elif field in ['item_code', 'item_description']:
                min_coverage = 98  # Core identification fields
            else:
                min_coverage = 80  # Other fields can have some gaps
            
            assert coverage >= min_coverage, \
                f"Sacred field '{field}' coverage too low: {coverage:.1f}% (expected ≥{min_coverage}%)"
            
            print(f"✅ {field}: {coverage:.1f}% coverage")
    
    def test_referential_integrity_protection(self):
        """Test referential integrity of XtraChef related data"""
        # Check recipe_ingredients -> inventory relationships
        tables = self.cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='recipe_ingredients'
        """).fetchall()
        
        if tables:
            self.cursor.execute("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN ri.ingredient_id IS NOT NULL THEN 1 END) as linked
                FROM recipe_ingredients ri
            """)
            
            total, linked = self.cursor.fetchone()
            link_rate = (linked / total * 100) if total > 0 else 0
            
            assert link_rate >= 80, \
                f"Recipe-inventory link rate too low: {link_rate:.1f}%"
            
            print(f"✅ Recipe-inventory referential integrity: {link_rate:.1f}%")

@pytest.mark.xtrachef
class TestXtraChefPerformance:
    """Test XtraChef integration performance characteristics"""
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
    
    def test_inventory_query_performance(self):
        """Test that inventory queries perform within acceptable limits"""
        import time
        
        # Test typical inventory lookup query
        start_time = time.time()
        
        self.cursor.execute("""
            SELECT item_code, item_description, vendor_name, current_price
            FROM inventory 
            WHERE current_price > 0
            ORDER BY vendor_name, item_description
            LIMIT 100
        """)
        
        results = self.cursor.fetchall()
        end_time = time.time()
        
        query_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Performance benchmark: inventory queries should complete in < 500ms
        assert query_time < 500, f"Inventory query too slow: {query_time:.2f}ms"
        assert len(results) > 0, "Query should return results"
        
        print(f"✅ Inventory query performance: {query_time:.2f}ms for {len(results)} items")

if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v", "--tb=short"])
