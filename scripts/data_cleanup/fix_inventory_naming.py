#!/usr/bin/env python3
"""
Fix inventory naming to use standardized names from Product(s) field
This restores the critical connection between inventory and recipes
"""

import csv
import sqlite3
import os
from datetime import datetime

DATABASE = 'restaurant_calculator.db'
DATA_DIR = 'data_sources_from_toast'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def backup_database():
    """Create a backup before making changes"""
    backup_name = f"backups/backup_before_naming_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    os.makedirs('backups', exist_ok=True)
    
    import shutil
    shutil.copy2(DATABASE, backup_name)
    print(f"✅ Database backed up to: {backup_name}")
    return backup_name

def create_vendor_descriptions_table():
    """Create table to store vendor-specific descriptions"""
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS vendor_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER,
                vendor_name TEXT,
                vendor_description TEXT,
                item_code TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (inventory_id) REFERENCES inventory (id),
                UNIQUE(inventory_id, vendor_name)
            )
        ''')
        conn.commit()
        print("✅ Created vendor_descriptions table")

def fix_inventory_names():
    """Update inventory to use standardized names from Product(s) field"""
    print("\n📋 Fixing inventory naming...")
    
    item_file = os.path.join(DATA_DIR, 'Lea_Janes_Hot_Chicken_Item_Detail_Report_20250704_023013.csv')
    
    # Build mapping from vendor description to standardized name
    name_mapping = {}
    vendor_mappings = []  # Store vendor-specific descriptions
    
    with open(item_file, 'r', encoding='utf-8') as f:
        # Skip the first 3 header lines
        for _ in range(3):
            next(f)
        
        reader = csv.DictReader(f)
        for row in reader:
            vendor_desc = row.get('Item Description', '').strip()
            standardized_name = row.get('Product(s)', '').strip()
            vendor_name = row.get('Vendor Name', '').strip()
            item_code = row.get('Item Code', '').strip()
            
            if vendor_desc and standardized_name:
                # Store the mapping
                name_mapping[vendor_desc] = standardized_name
                vendor_mappings.append({
                    'vendor_desc': vendor_desc,
                    'standardized_name': standardized_name,
                    'vendor_name': vendor_name,
                    'item_code': item_code
                })
    
    print(f"Found {len(name_mapping)} name mappings")
    
    # Update inventory with standardized names
    updated_count = 0
    missing_count = 0
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get all current inventory items
        items = cursor.execute('''
            SELECT id, item_description, vendor_name, item_code 
            FROM inventory
        ''').fetchall()
        
        for item in items:
            old_desc = item['item_description']
            
            # Look for standardized name
            if old_desc in name_mapping:
                new_desc = name_mapping[old_desc]
                
                if new_desc:  # Only update if we have a standardized name
                    # Update inventory with standardized name
                    cursor.execute('''
                        UPDATE inventory 
                        SET item_description = ?,
                            product_categories = ?
                        WHERE id = ?
                    ''', (new_desc, new_desc, item['id']))
                    
                    # Store vendor description in new table
                    cursor.execute('''
                        INSERT OR REPLACE INTO vendor_descriptions 
                        (inventory_id, vendor_name, vendor_description, item_code)
                        VALUES (?, ?, ?, ?)
                    ''', (item['id'], item['vendor_name'], old_desc, item['item_code']))
                    
                    updated_count += 1
                    print(f"✓ Updated: {old_desc} → {new_desc}")
                else:
                    missing_count += 1
                    print(f"⚠️  No standardized name for: {old_desc}")
            else:
                # Try to find by item code if description doesn't match exactly
                found = False
                for mapping in vendor_mappings:
                    if mapping['item_code'] == item['item_code'] and mapping['standardized_name']:
                        cursor.execute('''
                            UPDATE inventory 
                            SET item_description = ?,
                                product_categories = ?
                            WHERE id = ?
                        ''', (mapping['standardized_name'], mapping['standardized_name'], item['id']))
                        
                        cursor.execute('''
                            INSERT OR REPLACE INTO vendor_descriptions 
                            (inventory_id, vendor_name, vendor_description, item_code)
                            VALUES (?, ?, ?, ?)
                        ''', (item['id'], item['vendor_name'], old_desc, item['item_code']))
                        
                        updated_count += 1
                        print(f"✓ Updated by code: {old_desc} → {mapping['standardized_name']}")
                        found = True
                        break
                
                if not found:
                    missing_count += 1
                    print(f"❌ No mapping found for: {old_desc}")
        
        conn.commit()
    
    print(f"\n✅ Updated {updated_count} inventory items")
    print(f"⚠️  {missing_count} items without standardized names")
    
    return updated_count, missing_count

def verify_connections():
    """Verify that inventory now connects to recipes properly"""
    print("\n🔍 Verifying inventory-recipe connections...")
    
    with get_db() as conn:
        # Check how many recipe ingredients now match inventory
        matched = conn.execute('''
            SELECT COUNT(DISTINCT ri.id) as count
            FROM recipe_ingredients ri
            JOIN inventory i ON ri.ingredient_name = i.item_description
        ''').fetchone()['count']
        
        total = conn.execute('''
            SELECT COUNT(*) as count FROM recipe_ingredients
        ''').fetchone()['count']
        
        print(f"✅ Recipe ingredients matched: {matched}/{total} ({matched/total*100:.1f}%)")
        
        # Show some examples
        examples = conn.execute('''
            SELECT ri.ingredient_name, i.item_description, i.current_price
            FROM recipe_ingredients ri
            JOIN inventory i ON ri.ingredient_name = i.item_description
            LIMIT 5
        ''').fetchall()
        
        print("\nExample matches:")
        for ex in examples:
            print(f"  ✓ {ex['ingredient_name']} → ${ex['current_price']:.2f}")
        
        # Show unmatched ingredients
        unmatched = conn.execute('''
            SELECT DISTINCT ri.ingredient_name
            FROM recipe_ingredients ri
            LEFT JOIN inventory i ON ri.ingredient_name = i.item_description
            WHERE i.id IS NULL
            LIMIT 10
        ''').fetchall()
        
        if unmatched:
            print(f"\n⚠️  Unmatched recipe ingredients (showing first 10):")
            for item in unmatched:
                print(f"  - {item['ingredient_name']}")

def main():
    print("Inventory Naming Fix")
    print("="*50)
    print("This will update inventory items to use standardized names")
    print("from the Product(s) field, restoring the connection to recipes.\n")
    
    # Backup first
    backup_database()
    
    # Create vendor descriptions table
    create_vendor_descriptions_table()
    
    # Fix the naming
    updated, missing = fix_inventory_names()
    
    # Verify the fix worked
    verify_connections()
    
    print("\n" + "="*50)
    print("Fix complete! The inventory now uses standardized names.")
    print("Vendor-specific descriptions have been preserved in vendor_descriptions table.")

if __name__ == "__main__":
    main()