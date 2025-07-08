#!/usr/bin/env python3
"""
Update vendor_descriptions table with actual vendor descriptions from original CSV
"""

import sqlite3
import pandas as pd
import csv

def update_vendor_descriptions():
    """Update vendor descriptions with data from original Toast CSV"""
    
    # Read the Toast item detail report
    csv_path = 'data/sources/data_sources_from_toast/Lea_Janes_Hot_Chicken_Item_Detail_Report_20250704_023013.csv'
    
    print("Reading Toast Item Detail Report...")
    
    # Skip the header rows (first 3 rows are headers)
    df = pd.read_csv(csv_path, skiprows=3)
    
    # Display column names to verify
    print(f"CSV Columns: {df.columns.tolist()}")
    
    # Connect to database
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    # First, let's see what we're working with
    print("\nAnalyzing data mapping...")
    
    # Sample the data
    print("\nSample CSV data:")
    for idx, row in df.head(5).iterrows():
        print(f"Item Code: {row['Item Code']}")
        print(f"Vendor: {row['Vendor Name']}")
        print(f"Vendor Description: {row['Item Description']}")
        print("-" * 40)
    
    # Check how many matches we can find
    matched = 0
    updated = 0
    
    for idx, row in df.iterrows():
        item_code = str(row['Item Code']).strip()
        vendor_name = str(row['Vendor Name']).strip()
        vendor_desc = str(row['Item Description']).strip()
        
        # Find the inventory item
        cursor.execute("""
            SELECT id, item_description 
            FROM inventory 
            WHERE item_code = ? AND vendor_name = ?
        """, (item_code, vendor_name))
        
        result = cursor.fetchone()
        
        if result:
            inv_id, our_desc = result
            matched += 1
            
            # Check if vendor description is different from our description
            if vendor_desc != our_desc:
                # Update vendor_descriptions table
                cursor.execute("""
                    INSERT OR REPLACE INTO vendor_descriptions 
                    (inventory_id, vendor_name, vendor_description)
                    VALUES (?, ?, ?)
                """, (inv_id, vendor_name, vendor_desc))
                updated += 1
                
                if updated <= 10:  # Show first 10 updates
                    print(f"\nUpdating ID {inv_id}:")
                    print(f"  Our description: {our_desc}")
                    print(f"  Vendor description: {vendor_desc}")
    
    # Commit changes
    conn.commit()
    
    print(f"\n" + "="*60)
    print(f"SUMMARY:")
    print(f"Total CSV rows: {len(df)}")
    print(f"Matched inventory items: {matched}")
    print(f"Updated vendor descriptions: {updated}")
    
    # Verify the updates
    cursor.execute("""
        SELECT COUNT(*) 
        FROM inventory i 
        JOIN vendor_descriptions vd ON i.id = vd.inventory_id 
        WHERE i.item_description != vd.vendor_description
    """)
    different_count = cursor.fetchone()[0]
    
    print(f"Items with different vendor descriptions: {different_count}")
    
    conn.close()
    
    print("\n✅ Vendor descriptions updated successfully!")

if __name__ == "__main__":
    # Backup first
    import shutil
    import datetime
    
    backup_name = f"restaurant_calculator_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy('restaurant_calculator.db', backup_name)
    print(f"Database backed up to: {backup_name}")
    
    update_vendor_descriptions()