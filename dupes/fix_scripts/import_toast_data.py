#!/usr/bin/env python3
"""
Import Toast POS data into restaurant calculator database
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

def import_vendors():
    """Import unique vendors from item detail report"""
    print("📦 Importing vendors...")
    
    vendors = set()
    item_file = os.path.join(DATA_DIR, 'Lea_Janes_Hot_Chicken_Item_Detail_Report_20250704_023013.csv')
    
    with open(item_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            vendor_name = row.get('Vendor Name', '').strip()
            if vendor_name and vendor_name != 'Vendor Name':
                vendors.add(vendor_name)
    
    with get_db() as conn:
        for vendor in vendors:
            try:
                conn.execute('''
                    INSERT OR IGNORE INTO vendors (vendor_name, active)
                    VALUES (?, ?)
                ''', (vendor, True))
            except Exception as e:
                print(f"Error inserting vendor {vendor}: {e}")
        conn.commit()
    
    print(f"✅ Imported {len(vendors)} vendors")

def import_inventory():
    """Import inventory items from Toast item detail report"""
    print("📋 Importing inventory items...")
    
    item_file = os.path.join(DATA_DIR, 'Lea_Janes_Hot_Chicken_Item_Detail_Report_20250704_023013.csv')
    imported = 0
    
    with open(item_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        with get_db() as conn:
            for row in reader:
                try:
                    # Skip header rows
                    if row.get('Item Code') == 'Item Code' or not row.get('Item Description'):
                        continue
                    
                    # Clean and parse data
                    item_code = row.get('Item Code', '').strip()
                    item_description = row.get('Item Description', '').strip()
                    vendor_name = row.get('Vendor Name', '').strip()
                    current_price = float(row.get('Contracted Price ($)', 0) or 0)
                    last_price = float(row.get('Last Purchased Price ($)', 0) or 0)
                    last_date = row.get('Last Purchased Date', '').strip()
                    unit_measure = row.get('UOM', '').strip()
                    pack_size = f"{row.get('Pack', '')} x {row.get('Size', '')}"
                    product_categories = row.get('Product(s)', '').strip()
                    
                    if item_description:  # Only import if we have a description
                        conn.execute('''
                            INSERT OR REPLACE INTO inventory 
                            (item_code, item_description, vendor_name, current_price, 
                             last_purchased_price, last_purchased_date, unit_measure, 
                             pack_size, product_categories, updated_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            item_code,
                            item_description,
                            vendor_name,
                            current_price,
                            last_price,
                            last_date,
                            unit_measure,
                            pack_size.strip(' x '),
                            product_categories,
                            datetime.now().isoformat()
                        ))
                        imported += 1
                        
                except Exception as e:
                    print(f"Error importing item {row.get('Item Description', 'Unknown')}: {e}")
            
            conn.commit()
    
    print(f"✅ Imported {imported} inventory items")

def import_recipes():
    """Import recipes from Toast recipe summary"""
    print("🍳 Importing recipes...")
    
    recipe_file = os.path.join(DATA_DIR, 'Recipe_Summary_7_4_2025, 12_07_01 AM.csv')
    imported = 0
    
    with open(recipe_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        with get_db() as conn:
            for row in reader:
                try:
                    recipe_name = row.get('RecipeName', '').strip()
                    if not recipe_name:
                        continue
                    
                    # Parse numeric values safely
                    def safe_float(value, default=0):
                        try:
                            return float(value) if value and value.strip() else default
                        except:
                            return default
                    
                    food_cost = safe_float(row.get('FoodCost', 0))
                    food_cost_percentage = safe_float(row.get('FoodCostPercentage', 0))
                    labor_cost = safe_float(row.get('LaborCost', 0))
                    menu_price = safe_float(row.get('MenuPrice', 0))
                    gross_margin = safe_float(row.get('GrossMargin', 0))
                    per_serving = safe_float(row.get('PerServing', 0))
                    
                    conn.execute('''
                        INSERT OR REPLACE INTO recipes 
                        (recipe_name, status, recipe_group, recipe_type, food_cost, 
                         food_cost_percentage, labor_cost, labor_cost_percentage, 
                         menu_price, gross_margin, shelf_life, shelf_life_uom,
                         prep_recipe_yield, prep_recipe_yield_uom, serving_size, 
                         serving_size_uom, per_serving, cost_modified, updated_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        recipe_name,
                        row.get('Status', 'Draft').strip(),
                        row.get('RecipeGroup', '').strip(),
                        row.get('Type', 'Recipe').strip(),
                        food_cost,
                        food_cost_percentage,
                        labor_cost,
                        safe_float(row.get('LaborCostPercentage', 0)),
                        menu_price,
                        gross_margin,
                        row.get('ShelfLife', '').strip(),
                        row.get('ShelfLifeUom', '').strip(),
                        row.get('PrepRecipeYield', '').strip(),
                        row.get('PrepRecipeYieldUom', '').strip(),
                        row.get('ServingSize', '').strip(),
                        row.get('ServingSizeUom', '').strip(),
                        per_serving,
                        row.get('CostModified', '').strip(),
                        datetime.now().isoformat()
                    ))
                    imported += 1
                    
                except Exception as e:
                    print(f"Error importing recipe {row.get('RecipeName', 'Unknown')}: {e}")
            
            conn.commit()
    
    print(f"✅ Imported {imported} recipes")

def create_menu_items_from_recipes():
    """Create menu items from recipes that have menu prices"""
    print("🍽️ Creating menu items from recipes...")
    
    with get_db() as conn:
        # Get recipes with menu prices > 0
        recipes = conn.execute('''
            SELECT * FROM recipes 
            WHERE menu_price > 0 AND recipe_type = 'Recipe'
        ''').fetchall()
        
        imported = 0
        for recipe in recipes:
            try:
                # Calculate food cost percentage
                food_cost_percent = 0
                if recipe['menu_price'] > 0:
                    food_cost_percent = (recipe['food_cost'] / recipe['menu_price']) * 100
                
                gross_profit = recipe['menu_price'] - recipe['food_cost']
                
                conn.execute('''
                    INSERT OR REPLACE INTO menu_items 
                    (item_name, menu_group, recipe_id, menu_price, food_cost, 
                     food_cost_percent, gross_profit, status, serving_size, updated_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    recipe['recipe_name'],
                    recipe['recipe_group'] or 'Main',
                    recipe['id'],
                    recipe['menu_price'],
                    recipe['food_cost'],
                    food_cost_percent,
                    gross_profit,
                    'Active',
                    f"{recipe['serving_size']} {recipe['serving_size_uom']}".strip(),
                    datetime.now().isoformat()
                ))
                imported += 1
                
            except Exception as e:
                print(f"Error creating menu item for {recipe['recipe_name']}: {e}")
        
        conn.commit()
    
    print(f"✅ Created {imported} menu items from recipes")

def import_all_data():
    """Import all Toast POS data"""
    print("🚀 Starting Toast POS data import...")
    print("=" * 50)
    
    try:
        import_vendors()
        import_inventory()
        import_recipes()
        create_menu_items_from_recipes()
        
        print("=" * 50)
        print("✅ Toast POS data import completed successfully!")
        
        # Show summary
        with get_db() as conn:
            vendor_count = conn.execute('SELECT COUNT(*) as count FROM vendors').fetchone()['count']
            inventory_count = conn.execute('SELECT COUNT(*) as count FROM inventory').fetchone()['count']
            recipe_count = conn.execute('SELECT COUNT(*) as count FROM recipes').fetchone()['count']
            menu_count = conn.execute('SELECT COUNT(*) as count FROM menu_items').fetchone()['count']
        
        print(f"""
📊 IMPORT SUMMARY:
- Vendors: {vendor_count}
- Inventory Items: {inventory_count}
- Recipes: {recipe_count}
- Menu Items: {menu_count}
        """)
        
    except Exception as e:
        print(f"❌ Error during import: {e}")

if __name__ == '__main__':
    import_all_data()
