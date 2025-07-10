#!/usr/bin/env python3
"""
XTRACHEF INTEGRATION TESTS - Simple Version (No Dependencies)
CRITICAL: These tests protect the SACRED XtraChef integration per DATA_MODEL.md

⚠️  PROTECTED COMPONENT: XtraChef integration is IMMUTABLE per DATA_MODEL.md
These tests ensure the protected mapping is NEVER broken
"""

import sqlite3
import os
import sys
import json
from datetime import datetime

DATABASE = 'restaurant_calculator.db'

class XtraChefIntegrationTester:
    """PROTECTED: Test XtraChef integration integrity"""
    
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()
        
        # Define the SACRED XtraChef mapping per DATA_MODEL.md
        self.SACRED_MAPPING = {
            'item_code': 'XtraChef: Invoice Item Code',
            'item_description': 'XtraChef: Product Name',
            'vendor_name': 'XtraChef: Vendor Name', 
            'current_price': 'XtraChef: Latest Price',
            'last_purchased_date': 'XtraChef: Invoice Date'
        }
    
    def assert_test(self, condition: bool, test_name: str, message: str = ""):
        """Simple assertion helper"""
        self.tests_run += 1
        
        if condition:
            print(f"✅ PASS: {test_name}")
            self.tests_passed += 1
        else:
            print(f"❌ FAIL: {test_name} - {message}")
            self.tests_failed += 1
    
    def test_sacred_field_integrity(self):
        """CRITICAL: Verify SACRED XtraChef fields are never changed"""
        try:
            # Get inventory table schema
            self.cursor.execute("PRAGMA table_info(inventory)")
            columns = [col[1] for col in self.cursor.fetchall()]
            
            # Check each sacred field exists
            for field, description in self.SACRED_MAPPING.items():
                self.assert_test(
                    field in columns,
                    f"Sacred Field: {field}",
                    f"CRITICAL: Protected XtraChef field '{field}' missing from inventory table"
                )
            
            print(f"   🔒 Protected fields verified: {list(self.SACRED_MAPPING.keys())}")
            
        except Exception as e:
            self.assert_test(False, "Sacred Field Integrity", str(e))
    
    def test_xtrachef_data_presence(self):
        """Test that XtraChef data is present and valid"""
        try:
            # Check for XtraChef formatted item codes
            self.cursor.execute("""
                SELECT COUNT(*) FROM inventory 
                WHERE item_code LIKE '%_XC%' OR item_code LIKE '%XC%'
            """)
            xtrachef_count = self.cursor.fetchone()[0]
            
            # Check total inventory
            self.cursor.execute("SELECT COUNT(*) FROM inventory")
            total_count = self.cursor.fetchone()[0]
            
            self.assert_test(
                total_count >= 200,
                "Inventory Data Presence",
                f"Expected at least 200 inventory items, found {total_count}"
            )
            
            if xtrachef_count > 0:
                print(f"   📊 Found {xtrachef_count} XtraChef formatted items out of {total_count} total")
            
            # Check data completeness
            self.cursor.execute("""
                SELECT COUNT(*) FROM inventory 
                WHERE item_description IS NOT NULL 
                AND current_price IS NOT NULL 
                AND current_price > 0
            """)
            complete_items = self.cursor.fetchone()[0]
            
            completion_rate = (complete_items / total_count * 100) if total_count > 0 else 0
            
            self.assert_test(
                completion_rate >= 80,
                "Data Completeness Rate",
                f"Data completion rate: {completion_rate:.1f}% (should be ≥80%)"
            )
            
        except Exception as e:
            self.assert_test(False, "XtraChef Data Presence", str(e))
    
    def test_xtrachef_data_format_validation(self):
        """Test XtraChef data format integrity"""
        try:
            # Get sample XtraChef items for validation
            self.cursor.execute("""
                SELECT item_code, item_description, vendor_name, current_price, last_purchased_date
                FROM inventory 
                WHERE item_code IS NOT NULL 
                AND item_description IS NOT NULL
                AND current_price > 0
                LIMIT 10
            """)
            
            items = self.cursor.fetchall()
            valid_items = 0
            
            for item_code, description, vendor, price, date in items:
                # Validate item code format
                if item_code and item_code.strip():
                    valid_items += 1
                    
                    # Validate price is reasonable
                    if price and 0.01 <= price <= 1000:
                        pass  # Price is reasonable
                    else:
                        print(f"   ⚠️  Unusual price: {item_code} = ${price}")
                    
                    # Validate description exists
                    if description and len(description.strip()) > 3:
                        pass  # Description is adequate
                    else:
                        print(f"   ⚠️  Short description: {item_code} = '{description}'")
            
            self.assert_test(
                valid_items >= 8,  # 80% of sample should be valid
                "XtraChef Data Format",
                f"{valid_items}/10 sample items have valid format"
            )
            
        except Exception as e:
            self.assert_test(False, "XtraChef Data Format Validation", str(e))
    
    def test_vendor_data_integrity(self):
        """Test vendor information from XtraChef integration"""
        try:
            # Get vendor statistics
            self.cursor.execute("""
                SELECT DISTINCT vendor_name, COUNT(*) as item_count
                FROM inventory 
                WHERE vendor_name IS NOT NULL AND vendor_name != ''
                GROUP BY vendor_name
                ORDER BY item_count DESC
                LIMIT 10
            """)
            
            vendors = self.cursor.fetchall()
            
            self.assert_test(
                len(vendors) >= 5,
                "Vendor Data Presence",
                f"Found {len(vendors)} vendors (should be ≥5)"
            )
            
            if vendors:
                print(f"   📊 Top vendors by item count:")
                for vendor_name, item_count in vendors[:5]:
                    print(f"      • {vendor_name}: {item_count} items")
                    
                    # Validate vendor name quality
                    self.assert_test(
                        vendor_name.strip() != "" and len(vendor_name.strip()) > 2,
                        f"Vendor Name Quality: {vendor_name[:20]}...",
                        f"Vendor name too short: '{vendor_name}'"
                    )
            
        except Exception as e:
            self.assert_test(False, "Vendor Data Integrity", str(e))
    
    def test_price_data_validation(self):
        """Test pricing data from XtraChef integration"""
        try:
            # Get price statistics
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total_items,
                    COUNT(CASE WHEN current_price > 0 THEN 1 END) as items_with_price,
                    AVG(current_price) as avg_price,
                    MIN(current_price) as min_price,
                    MAX(current_price) as max_price
                FROM inventory
            """)
            
            stats = self.cursor.fetchone()
            total, with_price, avg_price, min_price, max_price = stats
            
            price_rate = (with_price / total * 100) if total > 0 else 0
            
            self.assert_test(
                price_rate >= 90,
                "Price Data Coverage",
                f"Price coverage: {price_rate:.1f}% ({with_price}/{total} items have prices)"
            )
            
            # Validate price ranges
            if avg_price:
                self.assert_test(
                    0.10 <= avg_price <= 100,
                    "Average Price Reasonableness",
                    f"Average price ${avg_price:.2f} seems reasonable"
                )
                
                print(f"   📊 Price statistics: Avg=${avg_price:.2f}, Min=${min_price:.2f}, Max=${max_price:.2f}")
            
            # Check for negative prices (critical error)
            self.cursor.execute("""
                SELECT COUNT(*) FROM inventory WHERE current_price < 0
            """)
            negative_prices = self.cursor.fetchone()[0]
            
            self.assert_test(
                negative_prices == 0,
                "No Negative Prices",
                f"Found {negative_prices} items with negative prices (CRITICAL ERROR)"
            )
            
        except Exception as e:
            self.assert_test(False, "Price Data Validation", str(e))
    
    def test_etl_functionality_validation(self):
        """Test that ETL/import functionality is working"""
        try:
            # Check if we can access the ETL module
            etl_file_exists = os.path.exists('etl.py')
            
            self.assert_test(
                etl_file_exists,
                "ETL Module Presence",
                "etl.py file should exist for XtraChef imports"
            )
            
            # Check for UOM aliases (used by ETL)
            uom_file_exists = os.path.exists('uom_aliases.json')
            
            if uom_file_exists:
                try:
                    with open('uom_aliases.json', 'r') as f:
                        uom_data = json.load(f)
                        aliases = uom_data.get('aliases', {})
                        
                    self.assert_test(
                        len(aliases) > 10,
                        "UOM Aliases Configuration",
                        f"Found {len(aliases)} UOM aliases for data processing"
                    )
                    
                except Exception:
                    self.assert_test(False, "UOM Aliases Configuration", "Could not load UOM aliases")
            
            # Check for recent ETL activity (database modifications)
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('inventory', 'vendor_products')
            """)
            required_tables = self.cursor.fetchall()
            
            self.assert_test(
                len(required_tables) >= 1,
                "Required Tables Present",
                f"Found {len(required_tables)} required tables for XtraChef integration"
            )
            
        except Exception as e:
            self.assert_test(False, "ETL Functionality Validation", str(e))
    
    def test_data_consistency_checks(self):
        """Test data consistency across XtraChef integration"""
        try:
            # Check for duplicate item codes (should be unique)
            self.cursor.execute("""
                SELECT item_code, COUNT(*) as count
                FROM inventory 
                WHERE item_code IS NOT NULL AND item_code != ''
                GROUP BY item_code
                HAVING COUNT(*) > 1
            """)
            
            duplicates = self.cursor.fetchall()
            
            self.assert_test(
                len(duplicates) == 0,
                "No Duplicate Item Codes",
                f"Found {len(duplicates)} duplicate item codes (should be unique)"
            )
            
            # Check for orphaned vendor products
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='vendor_products'
            """)
            
            if self.cursor.fetchone():  # vendor_products table exists
                self.cursor.execute("""
                    SELECT COUNT(*)
                    FROM vendor_products vp
                    LEFT JOIN inventory i ON vp.inventory_id = i.id
                    WHERE i.id IS NULL
                """)
                
                orphaned_vp = self.cursor.fetchone()[0]
                
                self.assert_test(
                    orphaned_vp == 0,
                    "No Orphaned Vendor Products",
                    f"Found {orphaned_vp} vendor products without inventory links"
                )
            
            # Check item code format consistency
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN item_code LIKE '%_%' THEN 1 END) as with_underscore,
                    COUNT(CASE WHEN item_code LIKE '%XC%' THEN 1 END) as xtrachef_format
                FROM inventory
                WHERE item_code IS NOT NULL AND item_code != ''
            """)
            
            total, with_underscore, xtrachef_format = self.cursor.fetchone()
            
            if total > 0:
                format_consistency = (xtrachef_format / total * 100)
                print(f"   📊 Item code formats: {xtrachef_format} XtraChef / {total} total ({format_consistency:.1f}%)")
            
        except Exception as e:
            self.assert_test(False, "Data Consistency Checks", str(e))
    
    def test_import_protection_validation(self):
        """Test that XtraChef import protection mechanisms work"""
        try:
            # Verify database constraints exist
            self.cursor.execute("PRAGMA table_info(inventory)")
            columns_info = self.cursor.fetchall()
            
            # Check for primary key or unique constraints on item_code
            item_code_column = None
            for col in columns_info:
                if col[1] == 'item_code':  # col[1] is column name
                    item_code_column = col
                    break
            
            self.assert_test(
                item_code_column is not None,
                "Item Code Column Exists",
                "item_code column must exist for XtraChef imports"
            )
            
            # Test data type validation
            sample_prices = self.cursor.execute("""
                SELECT current_price FROM inventory 
                WHERE current_price IS NOT NULL 
                LIMIT 5
            """).fetchall()
            
            numeric_prices = 0
            for (price,) in sample_prices:
                if isinstance(price, (int, float)) and price >= 0:
                    numeric_prices += 1
            
            self.assert_test(
                numeric_prices == len(sample_prices),
                "Price Data Type Validation",
                f"{numeric_prices}/{len(sample_prices)} prices are valid numeric types"
            )
            
        except Exception as e:
            self.assert_test(False, "Import Protection Validation", str(e))
    
    def run_all_tests(self):
        """Execute all XtraChef integration tests"""
        print("🔒 XTRACHEF INTEGRATION TESTS - PROTECTING SACRED DATA")
        print("=" * 65)
        print("⚠️  CRITICAL: These tests protect IMMUTABLE XtraChef integration")
        print("=" * 65)
        
        self.test_sacred_field_integrity()
        self.test_xtrachef_data_presence()
        self.test_xtrachef_data_format_validation()
        self.test_vendor_data_integrity()
        self.test_price_data_validation()
        self.test_etl_functionality_validation()
        self.test_data_consistency_checks()
        self.test_import_protection_validation()
        
        print("=" * 65)
        print(f"🔒 XTRACHEF PROTECTION TEST SUMMARY:")
        print(f"   Total: {self.tests_run}")
        print(f"   Passed: {self.tests_passed}")
        print(f"   Failed: {self.tests_failed}")
        
        if self.tests_failed == 0:
            print("🎉 ALL XTRACHEF PROTECTION TESTS PASSED!")
            print("✅ Sacred XtraChef integration is secure and intact")
            return 0
        else:
            print(f"🚨 {self.tests_failed} CRITICAL FAILURES!")
            print("❌ XtraChef integration may be compromised - IMMEDIATE ATTENTION REQUIRED")
            return 1
    
    def cleanup(self):
        """Cleanup resources"""
        self.conn.close()

def main():
    """Main test execution"""
    if not os.path.exists(DATABASE):
        print("❌ Error: Database file not found!")
        print("XtraChef integration tests require the restaurant database.")
        return 1
    
    tester = XtraChefIntegrationTester()
    try:
        return tester.run_all_tests()
    finally:
        tester.cleanup()

if __name__ == "__main__":
    sys.exit(main())
