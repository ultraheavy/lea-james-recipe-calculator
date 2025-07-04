#!/usr/bin/env python3
"""
Fix the Toast data import issues:
1. Use Last Purchased Price instead of Contracted Price
2. Fix duplicate recipes
3. Better data validation
"""

import sqlite3
import csv
import os
from datetime import datetime

DATABASE = 'restaurant_calculator.db'
DATA_DIR = 'data_sources_from_toast'

def fix_inventory_costs():
    """Fix inventory costs by using Last Purchased Price"""
    print("🔧 Fixing inventory costs...")
    
    item_file = os.path.join(DATA_DIR, 'Lea_Janes_Hot_Chicken_Item_Detail_Report_20250704_023013.csv')
    
    with open(item_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
        # Find the actual header line
        header_line_index = -1
        for i, line in enumerate(lines):
            if 'Location Name,Vendor Name,Item Code' in line:
                header_line_index = i
                break
        
        if header_line_index == -1:
            print("❌ Could not find header in CSV file")
            return
        
        # Read from the header line onwards
        reader = csv.DictReader(lines[header_line_index:])
        
        updated = 0
        with sqlite3.connect(DATABASE) as conn:
            for row in reader:
                try:
                    item_code = row.get('Item Code', '').strip()
                    if not item_code:
                        continue
                    
                    # Use Last Purchased Price as the primary cost
                    last_price = row.get('Last Purchased Price ($)', '').strip()
                    contracted_price = row.get('Contracted Price ($)', '').strip()
                    
                    # Parse prices safely
                    def safe_float(value):
                        try:
                            return float(value) if value and str(value).strip() not in ['', '0', 'None'] else 0
                        except:
                            return 0
                    
                    last_price_val = safe_float(last_price)
                    contracted_price_val = safe_float(contracted_price)
                    
                    # Use last purchased price if available, otherwise contracted price
                    primary_cost = last_price_val if last_price_val > 0 else contracted_price_val
                    
                    if primary_cost > 0:
                        conn.execute('''
                            UPDATE inventory 
                            SET current_price = ?, last_purchased_price = ?, updated_date = ?
                            WHERE item_code = ?
                        ''', (primary_cost, last_price_val, datetime.now().isoformat(), item_code))
                        updated += 1
                        
                except Exception as e:
                    print(f"Error updating item {item_code}: {e}")
            
            conn.commit()
    
    print(f"✅ Updated {updated} inventory items with correct costs")

def remove_duplicate_recipes():
    """Remove duplicate recipes, keeping the most recent one"""
    print("🔧 Removing duplicate recipes...")
    
    with sqlite3.connect(DATABASE) as conn:
        # Find duplicates
        duplicates = conn.execute('''
            SELECT recipe_name, COUNT(*) as count, GROUP_CONCAT(id) as ids
            FROM recipes 
            GROUP BY recipe_name 
            HAVING COUNT(*) > 1
        ''').fetchall()
        
        removed = 0
        for dup in duplicates:
            recipe_name = dup[0]
            ids = dup[2].split(',')
            
            # Keep the last one (highest ID), remove others
            ids_to_remove = ids[:-1]
            
            for recipe_id in ids_to_remove:
                # Remove recipe ingredients first
                conn.execute('DELETE FROM recipe_ingredients WHERE recipe_id = ?', (recipe_id,))
                # Remove menu items that reference this recipe
                conn.execute('UPDATE menu_items SET recipe_id = NULL WHERE recipe_id = ?', (recipe_id,))
                # Remove the recipe
                conn.execute('DELETE FROM recipes WHERE id = ?', (recipe_id,))
                removed += 1
        
        conn.commit()
    
    print(f"✅ Removed {removed} duplicate recipes")

def validate_data():
    """Validate the corrected data"""
    print("🔍 Validating corrected data...")
    
    with sqlite3.connect(DATABASE) as conn:
        # Check inventory costs
        with_cost = conn.execute('''
            SELECT COUNT(*) as count 
            FROM inventory 
            WHERE current_price > 0
        ''').fetchone()['count']
        
        no_cost = conn.execute('''
            SELECT COUNT(*) as count 
            FROM inventory 
            WHERE current_price = 0 OR current_price IS NULL
        ''').fetchone()['count']
        
        # Check for duplicates
        duplicates = conn.execute('''
            SELECT COUNT(*) as count
            FROM (
                SELECT recipe_name, COUNT(*) as cnt
                FROM recipes 
                GROUP BY recipe_name 
                HAVING COUNT(*) > 1
            )
        ''').fetchone()['count']
        
        # Sample high-cost items
        expensive_items = conn.execute('''
            SELECT item_description, current_price, vendor_name
            FROM inventory 
            WHERE current_price > 0
            ORDER BY current_price DESC 
            LIMIT 5
        ''').fetchall()
        
        print(f"📊 VALIDATION RESULTS:")
        print(f"  - Items WITH cost: {with_cost}")
        print(f"  - Items WITHOUT cost: {no_cost}")
        print(f"  - Recipe duplicates: {duplicates}")
        print(f"  - Cost percentage: {(with_cost/(with_cost+no_cost)*100):.1f}%")
        
        print(f"\n💰 TOP 5 EXPENSIVE ITEMS:")
        for item in expensive_items:
            print(f"  - {item[0]}: ${item[1]:.2f} ({item[2]})")

def fix_all_issues():
    """Fix all identified issues"""
    print("🚀 Starting data fix process...")
    print("=" * 50)
    
    fix_inventory_costs()
    remove_duplicate_recipes()
    validate_data()
    
    print("=" * 50)
    print("✅ Data fix process completed!")

if __name__ == '__main__':
    fix_all_issues()
