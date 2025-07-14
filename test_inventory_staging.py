#!/usr/bin/env python3
"""
Test script for inventory staging system
"""

import sqlite3
import os
from inventory_staging_loader import InventoryStagingLoader

def test_staging_system():
    """Test the complete staging system"""
    print("=== Testing Inventory Staging System ===\n")
    
    # 1. First, create the staging table
    print("1. Creating staging table...")
    conn = sqlite3.connect("restaurant_calculator.db")
    
    try:
        with open("migrations/create_staging_inventory_table.sql", 'r') as f:
            sql = f.read()
            conn.executescript(sql)
        conn.commit()
        print("   ✓ Staging table created successfully\n")
    except Exception as e:
        print(f"   ✗ Error creating table: {e}\n")
        return
    finally:
        conn.close()
    
    # 2. Load CSV data
    print("2. Loading CSV data to staging...")
    loader = InventoryStagingLoader()
    
    csv_path = "reference/LJ_DATA_Ref/Lea_Janes_Items_list_latest.csv"
    if not os.path.exists(csv_path):
        print(f"   ✗ CSV file not found: {csv_path}")
        return
    
    stats = loader.load_csv_to_staging(csv_path)
    
    print(f"   ✓ Import Complete!")
    print(f"   - Batch ID: {stats['batch_id']}")
    print(f"   - Total rows: {stats['total_rows']}")
    print(f"   - Loaded: {stats['loaded_rows']}")
    print(f"   - Needs review: {stats['needs_review']}")
    print(f"   - Duplicates: {stats['duplicates']}")
    print(f"   - Errors: {stats['error_rows']}\n")
    
    if stats['errors']:
        print("   Errors encountered:")
        for error in stats['errors'][:3]:
            print(f"     Row {error.get('row', 'N/A')}: {error.get('error', 'Unknown error')}")
        if len(stats['errors']) > 3:
            print(f"     ... and {len(stats['errors']) - 3} more errors")
    
    # 3. Show sample of loaded data
    print("\n3. Sample of loaded data:")
    conn = sqlite3.connect("restaurant_calculator.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get items that need review
    cursor.execute("""
        SELECT 
            staging_id,
            FAM_Product_Name_cleaned as product,
            Vendor_Name_cleaned as vendor,
            Vendor_Item_Code_cleaned as code,
            Last_Purchased_Price_cleaned as price,
            review_notes
        FROM stg_inventory_items 
        WHERE needs_review = 1 
        LIMIT 5
    """)
    
    review_items = cursor.fetchall()
    if review_items:
        print("\n   Items needing review:")
        for item in review_items:
            print(f"   - [{item['staging_id']}] {item['product'] or 'NO PRODUCT'} | {item['vendor']} | ${item['price'] or 0:.2f}")
            if item['review_notes']:
                print(f"     Issues: {item['review_notes'][:100]}...")
    
    # Get items without issues
    cursor.execute("""
        SELECT 
            staging_id,
            FAM_Product_Name_cleaned as product,
            Vendor_Name_cleaned as vendor,
            Last_Purchased_Price_cleaned as price
        FROM stg_inventory_items 
        WHERE needs_review = 0 
        LIMIT 5
    """)
    
    good_items = cursor.fetchall()
    if good_items:
        print("\n   Items without issues:")
        for item in good_items:
            print(f"   - [{item['staging_id']}] {item['product']} | {item['vendor']} | ${item['price']:.2f}")
    
    conn.close()
    
    print("\n4. Admin Review Interface:")
    print("   Visit: http://localhost:8888/admin/inventory-staging/")
    print("   - Review flagged items")
    print("   - Edit data inline")
    print("   - Bulk approve/reject")
    print("   - Process to live inventory")
    
    print("\n=== Testing Complete ===")

if __name__ == "__main__":
    test_staging_system()