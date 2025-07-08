#!/usr/bin/env python3
"""
Analyze vendor_descriptions table to understand the data quality issue
"""

import sqlite3
import pandas as pd

def analyze_vendor_descriptions():
    conn = sqlite3.connect('restaurant_calculator.db')
    
    # Get all vendor descriptions with inventory info
    query = """
    SELECT 
        i.id,
        i.item_code,
        i.item_description,
        i.vendor_name as inventory_vendor,
        vd.vendor_name as vd_vendor,
        vd.vendor_description,
        CASE 
            WHEN i.item_description = vd.vendor_description THEN 'IDENTICAL'
            WHEN vd.vendor_description IS NULL THEN 'NO_DESCRIPTION'
            ELSE 'DIFFERENT'
        END as description_status
    FROM inventory i
    LEFT JOIN vendor_descriptions vd ON i.id = vd.inventory_id
    ORDER BY description_status, i.vendor_name, i.item_description
    """
    
    df = pd.read_sql_query(query, conn)
    
    print("VENDOR DESCRIPTION ANALYSIS")
    print("=" * 60)
    
    # Summary statistics
    total_items = len(df)
    items_with_vd = len(df[df['vendor_description'].notna()])
    identical = len(df[df['description_status'] == 'IDENTICAL'])
    different = len(df[df['description_status'] == 'DIFFERENT'])
    no_desc = len(df[df['description_status'] == 'NO_DESCRIPTION'])
    
    print(f"\nTotal inventory items: {total_items}")
    print(f"Items with vendor descriptions: {items_with_vd}")
    print(f"Identical descriptions: {identical} ({identical/items_with_vd*100:.1f}% of items with descriptions)")
    print(f"Different descriptions: {different} ({different/items_with_vd*100:.1f}% of items with descriptions)")
    print(f"No vendor description: {no_desc}")
    
    # Show examples of DIFFERENT descriptions (these are valuable)
    print("\n" + "="*60)
    print("ITEMS WITH DIFFERENT VENDOR DESCRIPTIONS (These add value):")
    print("="*60)
    
    different_df = df[df['description_status'] == 'DIFFERENT']
    for _, row in different_df.head(10).iterrows():
        print(f"\nItem: {row['item_description']}")
        print(f"Vendor ({row['vd_vendor']}): {row['vendor_description']}")
        print(f"Item Code: {row['item_code']}")
    
    # Check if vendor_descriptions adds any value
    print("\n" + "="*60)
    print("VENDOR DESCRIPTION TABLE VALUE ASSESSMENT:")
    print("="*60)
    
    # Check if vendor names match
    vendor_mismatch = df[(df['inventory_vendor'] != df['vd_vendor']) & df['vd_vendor'].notna()]
    print(f"\nVendor name mismatches: {len(vendor_mismatch)}")
    
    # Recommendation
    print("\n" + "="*60)
    print("RECOMMENDATION:")
    print("="*60)
    print(f"""
The vendor_descriptions table appears to have limited value:
- {identical/items_with_vd*100:.1f}% of entries are identical to item_description
- Only {different} items ({different/items_with_vd*100:.1f}%) have unique vendor descriptions

Options:
1. Hide the "Vendor Description" column if most values are redundant
2. Only show vendor description when it differs from item description
3. Populate vendor descriptions with actual vendor catalog descriptions
4. Remove the vendor_descriptions table if not adding value
    """)
    
    # Save detailed report
    df.to_csv('vendor_descriptions_analysis.csv', index=False)
    print("\nDetailed analysis saved to: vendor_descriptions_analysis.csv")
    
    conn.close()

if __name__ == "__main__":
    analyze_vendor_descriptions()