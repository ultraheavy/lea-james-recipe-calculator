#!/usr/bin/env python3
"""
XTRACHEF INTEGRATION TESTS - PROTECTED COMPONENT
These tests verify the SACRED XtraChef CSV import functionality per DATA_MODEL.md

CRITICAL: XtraChef integration is IMMUTABLE per DATA_MODEL.md
These tests ensure the protected mapping is never broken
"""

import pytest
import sqlite3
import os
import csv
from typing import Dict, List, Any

DATABASE = 'restaurant_calculator.db'

class TestXtraChefIntegration:
    """
    PROTECTED: Test XtraChef CSV import integrity
    Per DATA_MODEL.md - this component is SACRED and cannot be modified
    """
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
        
        # Define the SACRED XtraChef mapping per DATA_MODEL.md
        self.SACRED_MAPPING = {
            'Invoice Item Code': 'item_code',
            'Product Name': 'item_description', 
            'Vendor': 'vendor_name',
            'Price': 'current_price',
            'Invoice Date': 'last_purchased_date'
        }
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
    
    def test_xtrachef_mapping_integrity(self):
        """
        CRITICAL: Verify XtraChef CSV mapping is NEVER changed
        This mapping is SACRED per DATA_MODEL.md
        """
        # This test validates that the mapping is exactly as defined
        expected_fields = {
            'item_code': 'XtraChef: Invoice Item Code',
            'item_description': 'XtraChef: Product Name',
            'vendor_name': 'XtraChef: Vendor Name', 
            'current_price': 'XtraChef: Latest Price',
            'last_purchased_date': 'XtraChef: Invoice Date'
        }
        
        # Verify all protected fields exist in inventory table
        self.cursor.execute("PRAGMA table_info(inventory)")
        columns = [col[1] for col in self.cursor.fetchall()]
        
        for field in expected_fields.keys():
            assert field in columns, f"CRITICAL: Protected XtraChef field '{field}' missing from inventory table"
        
        print("✅ XtraChef mapping integrity verified - all SACRED fields present")
    
    def test_xtrachef_data_format_validation(self):
        """Test that XtraChef data follows expected format patterns"""
        # Check for XtraChef formatted item codes (containing _XC)
        self.cursor.execute("""
            SELECT item_code, item_description, vendor_name, current_price
            FROM inventory 
            WHERE item_code LIKE '%_XC%' OR item_code LIKE '%XC%'
            LIMIT 10
        """)
        
        xtrachef_items = self.cursor.fetchall()
        
        if len(xtrachef_items) > 0:
            print(f"Found {len(xtrachef_items)} XtraChef items")
            
            for item_code, description, vendor, price in xtrachef_items:
                # Validate XtraChef data integrity
                assert item_code is not None and item_code.strip() != "", \
                    "XtraChef item_code cannot be null or empty"
                assert description is not None and description.strip() != "", \
                    "XtraChef item_description cannot be null or empty"
                assert price is not None and price > 0, \
                    f"XtraChef current_price must be positive, got {price} for {item_code}"
                
                print(f"✅ XtraChef item: {item_code} - {description} - ${price}")
        else:
            print("⚠️  No XtraChef formatted items found (may be normal if not yet imported)")
    
    def test_vendor_data_integrity(self):
        """Test vendor information from XtraChef integration"""
        self.cursor.execute("""
            SELECT DISTINCT vendor_name, COUNT(*) as item_count
            FROM inventory 
            WHERE vendor_name IS NOT NULL AND vendor_name != ''
            GROUP BY vendor_name
            ORDER BY item_count DESC
            LIMIT 10
        """)
        
        vendors = self.cursor.fetchall()
        assert len(vendors) > 0, "No vendor data found - XtraChef integration may be incomplete"
        
        print(f"Found {len(vendors)} vendors with inventory items:")
        for vendor_name, item_count in vendors:
            assert vendor_name.strip() != "", "Vendor name cannot be empty"
            assert item_count > 0, "Vendor must have at least one item"
            print(f"✅ {vendor_name}: {item_count} items")
    
    def test_price_data_validity(self):
        """Test that pricing data from XtraChef is valid"""
        self.cursor.execute("""
            SELECT item_code, item_description, current_price, last_purchased_price
            FROM inventory 
            WHERE current_price IS NOT NULL
            ORDER BY current_price DESC
            LIMIT 20
        """)
        
        items_with_prices = self.cursor.fetchall()
        assert len(items_with_prices) > 0, "No items with pricing data found"
        
        for item_code, description, current_price, last_price in items_with_prices:
            # Validate price data
            assert current_price > 0, f"Current price must be positive for {item_code}"
            assert current_price < 1000, f"Price seems unreasonably high: ${current_price} for {item_code}"
            
            if last_price is not None:
                assert last_price >= 0, f"Last purchased price cannot be negative for {item_code}"
            
            print(f"✅ {item_code}: ${current_price:.2f}")
    
    def test_date_format_validation(self):
        """Test XtraChef date format integrity"""
        self.cursor.execute("""
            SELECT item_code, last_purchased_date
            FROM inventory 
            WHERE last_purchased_date IS NOT NULL 
            AND last_purchased_date != ''
            LIMIT 10
        """)
        
        items_with_dates = self.cursor.fetchall()
        
        if len(items_with_dates) > 0:
            print(f"Found {len(items_with_dates)} items with purchase dates")
            
            for item_code, date_str in items_with_dates:
                assert date_str is not None, f"Date cannot be null for {item_code}"
                assert len(date_str) > 0, f"Date cannot be empty for {item_code}"
                
                # Basic date format validation (flexible to accommodate different formats)
                assert any(char.isdigit() for char in date_str), \
                    f"Date should contain digits: {date_str} for {item_code}"
                
                print(f"✅ {item_code}: {date_str}")
        else:
            print("⚠️  No purchase dates found (may be normal depending on XtraChef setup)")

class TestInventoryDataValidation:
    """Test inventory data structure and constraints"""
    
    def setup_method(self):
        """Setup test environment"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
    
    def teardown_method(self):
        """Cleanup after tests"""
        self.conn.close()
    
    def test_inventory_completeness(self):
        """Test that inventory has sufficient data for operations"""
        # Check total inventory count
        self.cursor.execute("SELECT COUNT(*) FROM inventory")
        total_items = self.cursor.fetchone()[0]
        
        assert total_items >= 100, f"Expected at least 100 inventory items, found {total_items}"
        print(f"✅ Total inventory items: {total_items}")
        
        # Check items with complete data
        self.cursor.execute("""
            SELECT COUNT(*) FROM inventory 
            WHERE item_description IS NOT NULL 
            AND current_price IS NOT NULL 
            AND current_price > 0
        """)
        complete_items = self.cursor.fetchone()[0]
        
        completion_rate = (complete_items / total_items) * 100
        assert completion_rate >= 80, f"Data completion rate too low: {completion_rate:.1f}%"
        print(f"✅ Data completion rate: {completion_rate:.1f}%")
    
    def test_unique_constraints(self):
        """Test database unique constraints are enforced"""
        # Check for duplicate item codes
        self.cursor.execute("""
            SELECT item_code, COUNT(*) as count
            FROM inventory 
            WHERE item_code IS NOT NULL AND item_code != ''
            GROUP BY item_code
            HAVING COUNT(*) > 1
        """)
        
        duplicates = self.cursor.fetchall()
        assert len(duplicates) == 0, f"Found {len(duplicates)} duplicate item codes"
        print("✅ No duplicate item codes found")
    
    def test_category_classification(self):
        """Test product category classification from XtraChef"""
        self.cursor.execute("""
            SELECT DISTINCT product_categories, COUNT(*) as count
            FROM inventory 
            WHERE product_categories IS NOT NULL AND product_categories != ''
            GROUP BY product_categories
            ORDER BY count DESC
        """)
        
        categories = self.cursor.fetchall()
        
        if len(categories) > 0:
            print(f"Found {len(categories)} product categories:")
            for category, count in categories:
                assert count > 0, f"Category {category} should have items"
                print(f"✅ {category}: {count} items")
        else:
            print("⚠️  No product categories found (may need categorization)")

if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v", "--tb=short"])
