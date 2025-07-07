#!/usr/bin/env python3
"""
Import purchase_unit and recipe_cost_unit from XtraChef data
"""

import sqlite3
import csv

DATABASE = 'restaurant_calculator.db'
ITEM_FILE = 'reference/LJ_DATA_Ref/Lea_Janes__Item_LIST_READY_FOR_IMPORT_latest.csv'

def import_units():
    """Import purchase and recipe units from XtraChef data"""
    
    updates = 0
    examples = []
    
    with open(ITEM_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            
            for row in reader:
                item_code = row.get('Item Code', '').strip()
                if not item_code:
                    continue
                
                # Get units
                purchase_unit = row.get('UOM', '').strip()  # How it's purchased
                recipe_unit = row.get('Item UOM', '').strip()  # How it's used in recipes
                
                # Clean up common abbreviations
                if purchase_unit == 'cs':
                    purchase_unit = 'case'
                if recipe_unit == 'ea':
                    recipe_unit = 'each'
                elif recipe_unit == 'fl':
                    recipe_unit = 'fl oz'
                
                # Update in database
                cursor.execute('''
                    UPDATE inventory 
                    SET purchase_unit = ?,
                        recipe_cost_unit = ?
                    WHERE item_code = ?
                ''', (purchase_unit, recipe_unit, item_code))
                
                if cursor.rowcount > 0:
                    updates += 1
                    if updates <= 10:  # Show first 10 examples
                        examples.append({
                            'item_code': item_code,
                            'description': row.get('Item Description', ''),
                            'purchase_unit': purchase_unit,
                            'recipe_unit': recipe_unit,
                            'pack_size': f"{row.get('Pack', '')} x {row.get('Size', '')} {row.get('Unit', '')}"
                        })
            
            conn.commit()
    
    print(f"Updated {updates} items with purchase and recipe units\n")
    
    if examples:
        print("Examples of updates:")
        print("-" * 100)
        for ex in examples:
            print(f"Item: {ex['description'][:40]:<40}")
            print(f"  Purchase Unit: {ex['purchase_unit']:<15} Recipe Unit: {ex['recipe_unit']:<15}")
            print(f"  Pack Size: {ex['pack_size']}")
            print()
    
    return updates

def check_missing_units():
    """Check how many items still have missing units"""
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        # Count items with missing units
        missing = cursor.execute('''
            SELECT COUNT(*) FROM inventory 
            WHERE (purchase_unit IS NULL OR recipe_cost_unit IS NULL)
        ''').fetchone()[0]
        
        total = cursor.execute('SELECT COUNT(*) FROM inventory').fetchone()[0]
        
        print(f"\nItems with missing units: {missing} out of {total} ({missing/total*100:.1f}%)")
        
        # Show some examples of items with missing units
        examples = cursor.execute('''
            SELECT item_code, item_description, vendor_name, pack_size 
            FROM inventory 
            WHERE (purchase_unit IS NULL OR recipe_cost_unit IS NULL)
            LIMIT 5
        ''').fetchall()
        
        if examples:
            print("\nExamples of items still missing units:")
            print("-" * 80)
            for item in examples:
                print(f"{item[0]:<15} {item[1]:<40} {item[3] or 'No pack size'}")

if __name__ == '__main__':
    print("Importing purchase and recipe units from XtraChef data...")
    import_units()
    check_missing_units()