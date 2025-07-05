#!/usr/bin/env python3
"""
Sync Toast POS data - monitors for new files and imports them automatically
Can be run as a scheduled task or manually
"""

import os
import glob
import sqlite3
import csv
import hashlib
import json
from datetime import datetime
from import_recipe_system import (
    parse_quantity, parse_price, get_db,
    import_recipe_summary, import_individual_recipe_files,
    create_menu_item_mappings
)

SYNC_STATE_FILE = '.toast_sync_state.json'
WATCH_DIRECTORIES = [
    'data_sources_from_toast',
    'reference/LJ_DATA_Ref',
    'reference/LJ_DATA_Ref/recipes'
]

def get_file_hash(filepath):
    """Get hash of file contents"""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def load_sync_state():
    """Load the last sync state"""
    if os.path.exists(SYNC_STATE_FILE):
        with open(SYNC_STATE_FILE, 'r') as f:
            return json.load(f)
    return {'files': {}, 'last_sync': None}

def save_sync_state(state):
    """Save the current sync state"""
    state['last_sync'] = datetime.now().isoformat()
    with open(SYNC_STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def find_new_or_modified_files(state):
    """Find files that are new or have been modified"""
    new_files = []
    modified_files = []
    current_files = {}
    
    for directory in WATCH_DIRECTORIES:
        if not os.path.exists(directory):
            continue
            
        # Find all CSV files
        pattern = os.path.join(directory, '*.csv')
        for filepath in glob.glob(pattern):
            file_hash = get_file_hash(filepath)
            current_files[filepath] = file_hash
            
            if filepath not in state['files']:
                new_files.append(filepath)
            elif state['files'][filepath] != file_hash:
                modified_files.append(filepath)
    
    return new_files, modified_files, current_files

def import_inventory_file(filepath):
    """Import inventory from item detail report"""
    print(f"  📦 Importing inventory from {os.path.basename(filepath)}")
    
    items_imported = 0
    items_updated = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        with get_db() as conn:
            for row in reader:
                # Skip header rows
                if row.get('Item Description') == 'Item Description':
                    continue
                
                item_code = row.get('Item Code', '').strip()
                item_desc = row.get('Item Description', '').strip()
                vendor = row.get('Vendor Name', '').strip()
                
                if not item_desc:
                    continue
                
                # Parse data
                item_data = {
                    'item_code': item_code,
                    'item_description': item_desc,
                    'vendor_name': vendor,
                    'current_price': parse_price(row.get('Contracted Price ($)', 0)),
                    'last_purchased_price': parse_price(row.get('Last Purchased Price ($)', 0)),
                    'last_purchased_date': row.get('Last Purchased Date', ''),
                    'unit_measure': row.get('UOM', ''),
                    'purchase_unit': row.get('Item UOM', ''),
                    'pack_size': row.get('Pack', ''),
                    'product_categories': row.get('Product(s)', ''),
                }
                
                # Check if exists
                existing = conn.execute(
                    'SELECT id FROM inventory WHERE item_code = ?',
                    (item_code,)
                ).fetchone()
                
                if existing:
                    # Update
                    conn.execute('''
                        UPDATE inventory
                        SET item_description = ?, vendor_name = ?,
                            current_price = ?, last_purchased_price = ?,
                            last_purchased_date = ?, unit_measure = ?,
                            purchase_unit = ?, pack_size = ?,
                            product_categories = ?, updated_date = CURRENT_TIMESTAMP
                        WHERE item_code = ?
                    ''', (
                        item_data['item_description'], item_data['vendor_name'],
                        item_data['current_price'], item_data['last_purchased_price'],
                        item_data['last_purchased_date'], item_data['unit_measure'],
                        item_data['purchase_unit'], item_data['pack_size'],
                        item_data['product_categories'], item_code
                    ))
                    items_updated += 1
                else:
                    # Insert
                    conn.execute('''
                        INSERT INTO inventory (
                            item_code, item_description, vendor_name,
                            current_price, last_purchased_price, last_purchased_date,
                            unit_measure, purchase_unit, pack_size,
                            product_categories, yield_percent
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item_data['item_code'], item_data['item_description'],
                        item_data['vendor_name'], item_data['current_price'],
                        item_data['last_purchased_price'], item_data['last_purchased_date'],
                        item_data['unit_measure'], item_data['purchase_unit'],
                        item_data['pack_size'], item_data['product_categories'], 100
                    ))
                    items_imported += 1
            
            conn.commit()
    
    print(f"    ✅ Imported {items_imported} new items, updated {items_updated}")

def process_file(filepath):
    """Process a single file based on its type"""
    filename = os.path.basename(filepath)
    
    # Determine file type
    if 'Item_Detail_Report' in filename or 'Item_LIST_READY' in filename:
        import_inventory_file(filepath)
    elif 'Recipe_Summary' in filename or 'Recipe_List_Summary' in filename:
        print(f"  🍳 Processing recipe summary: {filename}")
        import_recipe_summary()
    elif '/recipes/' in filepath:
        print(f"  📄 Individual recipe file: {filename}")
        # Individual files are processed in batch by import_individual_recipe_files
    else:
        print(f"  ❓ Unknown file type: {filename}")

def sync_toast_data():
    """Main sync function"""
    print("🔄 Toast POS Data Sync")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # Load previous state
    state = load_sync_state()
    
    if state['last_sync']:
        print(f"📌 Last sync: {state['last_sync']}")
    
    # Find changes
    new_files, modified_files, current_files = find_new_or_modified_files(state)
    
    if not new_files and not modified_files:
        print("✅ No changes detected - everything is up to date!")
        return
    
    # Create backup
    print("\n📦 Creating database backup...")
    os.system('python3 backup_database.py')
    
    # Process new files
    if new_files:
        print(f"\n🆕 Found {len(new_files)} new files:")
        for filepath in new_files:
            print(f"  - {os.path.basename(filepath)}")
            process_file(filepath)
    
    # Process modified files
    if modified_files:
        print(f"\n📝 Found {len(modified_files)} modified files:")
        for filepath in modified_files:
            print(f"  - {os.path.basename(filepath)}")
            process_file(filepath)
    
    # Always reprocess all individual recipe files together
    if any('/recipes/' in f for f in new_files + modified_files):
        print("\n🔄 Reprocessing all recipe ingredients...")
        import_individual_recipe_files()
    
    # Update menu mappings
    print("\n🍽️  Updating menu mappings...")
    create_menu_item_mappings()
    
    # Show summary
    print("\n📊 Current Database Status:")
    with get_db() as conn:
        recipes = conn.execute('SELECT COUNT(*) FROM recipes').fetchone()[0]
        inventory = conn.execute('SELECT COUNT(*) FROM inventory').fetchone()[0]
        menu_items = conn.execute('SELECT COUNT(*) FROM menu_items').fetchone()[0]
        
        print(f"  - Recipes: {recipes}")
        print(f"  - Inventory Items: {inventory}")
        print(f"  - Menu Items: {menu_items}")
    
    # Save new state
    state['files'] = current_files
    save_sync_state(state)
    
    print("\n✅ Sync complete!")

def show_sync_status():
    """Show the current sync status"""
    state = load_sync_state()
    
    print("📊 Toast Data Sync Status")
    print("-" * 50)
    
    if state['last_sync']:
        print(f"Last sync: {state['last_sync']}")
        print(f"Tracking {len(state['files'])} files")
        
        print("\n📁 Monitored directories:")
        for directory in WATCH_DIRECTORIES:
            if os.path.exists(directory):
                csv_count = len(glob.glob(os.path.join(directory, '*.csv')))
                print(f"  - {directory}: {csv_count} CSV files")
    else:
        print("No previous sync found - run sync to start tracking")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        show_sync_status()
    else:
        sync_toast_data()