#!/usr/bin/env python3
"""
Comprehensive recipe import system for Toast POS data
Handles recipe summaries, individual recipe files, and menu connections
"""

import csv
import sqlite3
import os
import glob
from datetime import datetime
import re

DATABASE = 'restaurant_calculator.db'
DATA_DIR = 'data_sources_from_toast'
REFERENCE_DIR = 'reference/LJ_DATA_Ref'
RECIPES_DIR = os.path.join(REFERENCE_DIR, 'recipes')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def parse_quantity(qty_str):
    """Parse various quantity formats from Toast"""
    if not qty_str or qty_str == '':
        return 0.0
    
    # Remove commas and strip
    qty_str = str(qty_str).replace(',', '').strip()
    
    # Handle fractions
    if '/' in qty_str:
        parts = qty_str.split()
        total = 0.0
        for part in parts:
            if '/' in part:
                num, denom = part.split('/')
                total += float(num) / float(denom)
            else:
                total += float(part)
        return total
    
    try:
        return float(qty_str)
    except:
        return 0.0

def parse_price(price_str):
    """Parse price strings, handling $ and other formatting"""
    if not price_str:
        return 0.0
    
    # Remove $, commas, and spaces
    clean_price = str(price_str).replace('$', '').replace(',', '').strip()
    
    try:
        return float(clean_price)
    except:
        return 0.0

def import_recipe_summary():
    """Import or update recipes from the summary file"""
    print("\n📊 Importing recipe summary...")
    
    summary_files = [
        os.path.join(DATA_DIR, 'Recipe_Summary_7_4_2025, 12_07_01 AM.csv'),
        os.path.join(REFERENCE_DIR, 'LEA_JANES_Recipe_List_Summary_7_4_2025, 7_51_55 PM.csv')
    ]
    
    # Use the most recent file that exists
    summary_file = None
    for file in summary_files:
        if os.path.exists(file):
            summary_file = file
            break
    
    if not summary_file:
        print("❌ No recipe summary file found")
        return
    
    print(f"📄 Using summary file: {os.path.basename(summary_file)}")
    
    recipes_imported = 0
    recipes_updated = 0
    
    with open(summary_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        with get_db() as conn:
            for row in reader:
                recipe_name = row.get('RecipeName', '').strip()
                if not recipe_name:
                    continue
                
                # Extract all fields
                recipe_data = {
                    'recipe_name': recipe_name,
                    'status': row.get('Status', 'Draft'),
                    'recipe_group': row.get('RecipeGroup', ''),
                    'recipe_type': row.get('Type', 'Recipe'),
                    'food_cost': parse_price(row.get('FoodCost', 0)),
                    'food_cost_percentage': parse_price(row.get('FoodCostPercentage', 0)),
                    'labor_cost': parse_price(row.get('LaborCost', 0)),
                    'labor_cost_percentage': parse_price(row.get('LaborCostPercentage', 0)),
                    'menu_price': parse_price(row.get('MenuPrice', 0)),
                    'gross_margin': parse_price(row.get('GrossMargin', 0)),
                    'prime_cost': parse_price(row.get('PrimeCost', 0)),
                    'prime_cost_percentage': parse_price(row.get('PrimeCostPercentage', 0)),
                    'shelf_life': row.get('ShelfLife', ''),
                    'shelf_life_uom': row.get('ShelfLifeUom', ''),
                    'prep_recipe_yield': row.get('PrepRecipeYield', ''),
                    'prep_recipe_yield_uom': row.get('PrepRecipeYieldUom', ''),
                    'serving_size': row.get('ServingSize', ''),
                    'serving_size_uom': row.get('ServingSizeUom', ''),
                    'per_serving': parse_price(row.get('PerServing', 0)),
                    'cost_modified': row.get('CostModified', ''),
                }
                
                # Check if recipe exists
                existing = conn.execute(
                    'SELECT id FROM recipes WHERE recipe_name = ?', 
                    (recipe_name,)
                ).fetchone()
                
                if existing:
                    # Update existing recipe
                    conn.execute('''
                        UPDATE recipes 
                        SET status = ?, recipe_group = ?, recipe_type = ?,
                            food_cost = ?, food_cost_percentage = ?,
                            labor_cost = ?, labor_cost_percentage = ?,
                            menu_price = ?, gross_margin = ?,
                            prime_cost = ?, prime_cost_percentage = ?,
                            shelf_life = ?, shelf_life_uom = ?,
                            prep_recipe_yield = ?, prep_recipe_yield_uom = ?,
                            serving_size = ?, serving_size_uom = ?,
                            per_serving = ?, cost_modified = ?,
                            updated_date = CURRENT_TIMESTAMP
                        WHERE recipe_name = ?
                    ''', (
                        recipe_data['status'], recipe_data['recipe_group'],
                        recipe_data['recipe_type'], recipe_data['food_cost'],
                        recipe_data['food_cost_percentage'], recipe_data['labor_cost'],
                        recipe_data['labor_cost_percentage'], recipe_data['menu_price'],
                        recipe_data['gross_margin'], recipe_data['prime_cost'],
                        recipe_data['prime_cost_percentage'], recipe_data['shelf_life'],
                        recipe_data['shelf_life_uom'], recipe_data['prep_recipe_yield'],
                        recipe_data['prep_recipe_yield_uom'], recipe_data['serving_size'],
                        recipe_data['serving_size_uom'], recipe_data['per_serving'],
                        recipe_data['cost_modified'], recipe_name
                    ))
                    recipes_updated += 1
                else:
                    # Insert new recipe
                    conn.execute('''
                        INSERT INTO recipes (
                            recipe_name, status, recipe_group, recipe_type,
                            food_cost, food_cost_percentage, labor_cost, labor_cost_percentage,
                            menu_price, gross_margin, prime_cost, prime_cost_percentage,
                            shelf_life, shelf_life_uom, prep_recipe_yield, prep_recipe_yield_uom,
                            serving_size, serving_size_uom, per_serving, cost_modified
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        recipe_data['recipe_name'], recipe_data['status'],
                        recipe_data['recipe_group'], recipe_data['recipe_type'],
                        recipe_data['food_cost'], recipe_data['food_cost_percentage'],
                        recipe_data['labor_cost'], recipe_data['labor_cost_percentage'],
                        recipe_data['menu_price'], recipe_data['gross_margin'],
                        recipe_data['prime_cost'], recipe_data['prime_cost_percentage'],
                        recipe_data['shelf_life'], recipe_data['shelf_life_uom'],
                        recipe_data['prep_recipe_yield'], recipe_data['prep_recipe_yield_uom'],
                        recipe_data['serving_size'], recipe_data['serving_size_uom'],
                        recipe_data['per_serving'], recipe_data['cost_modified']
                    ))
                    recipes_imported += 1
            
            conn.commit()
    
    print(f"✅ Imported {recipes_imported} new recipes")
    print(f"📝 Updated {recipes_updated} existing recipes")

def import_individual_recipe_files():
    """Import recipe ingredients from individual recipe CSV files"""
    print("\n📁 Importing individual recipe files...")
    
    recipe_files = glob.glob(os.path.join(RECIPES_DIR, '*.csv'))
    print(f"Found {len(recipe_files)} recipe files")
    
    files_processed = 0
    ingredients_added = 0
    
    with get_db() as conn:
        for recipe_file in recipe_files:
            filename = os.path.basename(recipe_file)
            # Extract recipe name from filename (before the restaurant name)
            recipe_name = filename.split('_Lea Jane\'s')[0].strip()
            
            # Get recipe ID
            recipe = conn.execute(
                'SELECT id FROM recipes WHERE recipe_name = ?',
                (recipe_name,)
            ).fetchone()
            
            if not recipe:
                print(f"⚠️  Recipe not found in database: {recipe_name}")
                continue
            
            recipe_id = recipe['id']
            
            # Clear existing ingredients for full refresh
            conn.execute('DELETE FROM recipe_ingredients WHERE recipe_id = ?', (recipe_id,))
            
            # Import ingredients from file - handle Toast format
            with open(recipe_file, 'r', encoding='utf-8-sig') as f:  # Handle BOM
                lines = f.readlines()
                
                # Find the ingredient section
                ingredient_start = -1
                for i, line in enumerate(lines):
                    if line.startswith('Ingredient,Type,Measurement') or line.startswith('Ingredient,Type,Quantity'):
                        ingredient_start = i + 1
                        break
                
                if ingredient_start < 0:
                    continue
                
                # Parse ingredients
                for i in range(ingredient_start, len(lines)):
                    line = lines[i].strip()
                    if not line or line.startswith(',,,'):
                        continue
                    
                    # Parse CSV line manually to handle quoted fields
                    parts = []
                    current = ''
                    in_quotes = False
                    
                    for char in line:
                        if char == '"':
                            in_quotes = not in_quotes
                        elif char == ',' and not in_quotes:
                            parts.append(current.strip())
                            current = ''
                        else:
                            current += char
                    parts.append(current.strip())
                    
                    if len(parts) < 5:
                        continue
                    
                    ingredient_name = parts[0].strip('"')
                    ingredient_type = parts[1]
                    measurement = parts[2]
                    cost_str = parts[4].strip('$')
                    
                    if not ingredient_name or ingredient_name == 'Ingredient':
                        continue
                    
                    # Parse measurement (e.g., "3 each", "2 oz")
                    quantity = 0.0
                    unit = ''
                    if measurement:
                        meas_parts = measurement.split(' ', 1)
                        if meas_parts:
                            quantity = parse_quantity(meas_parts[0])
                            unit = meas_parts[1] if len(meas_parts) > 1 else ''
                    
                    # Parse cost
                    cost = parse_price(cost_str)
                    
                    # Try to match ingredient to inventory
                    ingredient = conn.execute('''
                        SELECT id, current_price, unit_measure 
                        FROM inventory 
                        WHERE LOWER(item_description) = LOWER(?)
                        OR LOWER(item_description) LIKE LOWER(?)
                    ''', (ingredient_name, f'%{ingredient_name}%')).fetchone()
                    
                    ingredient_id = ingredient['id'] if ingredient else None
                    
                    # Insert ingredient
                    conn.execute('''
                        INSERT INTO recipe_ingredients (
                            recipe_id, ingredient_id, ingredient_name,
                            ingredient_type, quantity, unit_of_measure, cost
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (recipe_id, ingredient_id, ingredient_name, 
                          ingredient_type, quantity, unit, cost))
                    
                    ingredients_added += 1
            
            files_processed += 1
            
            # Update recipe total cost from ingredients
            conn.execute('''
                UPDATE recipes 
                SET food_cost = (SELECT COALESCE(SUM(cost), 0) FROM recipe_ingredients WHERE recipe_id = ?),
                    updated_date = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (recipe_id, recipe_id))
        
        conn.commit()
    
    print(f"✅ Processed {files_processed} recipe files")
    print(f"📝 Added {ingredients_added} ingredients")

def create_menu_item_mappings():
    """Create menu items based on recipes and their groups"""
    print("\n🍽️  Creating menu item mappings...")
    
    menu_mapping = {
        # Main dishes
        'FC-01': 'Thicc\'n Tenders',
        'FC-02': 'Leg Quarter', 
        'FC-03': 'Whole Wings',
        'FC-04': 'Fried Chicken Tender',
        'S-01': 'OG Nashville Chicken Sandwich',
        'S-02': 'J-Blaze Chicken Sandwich',
        'S-03': 'Plain Jane Sandwich',
        'S-04': 'Fish Sando',
        'FT-01': 'Chicken Waffle Cone',
        'FT-02': 'Loaded Fries',
        'FT-03': 'Angry Chicken Mac Bowl',
        'SL-01': 'Chicken Caesar Salad',
        
        # Sides
        'SD-01': 'Kale & Cabbage Slaw',
        'SD-02': 'Extra-Crispy Fries',
        'SD-03': 'LJ Mac',
        'SD-04': 'Fried Corn Ribs',
        
        # Sauces/Dips
        'DP-01': 'Charred-Onion Ranch',
        'DP-02': 'Comeback Sauce',
        'DP-03': 'Honey Mustard',
        'DP-04': 'Hot Honey',
        'DP-05': 'Habanero Ranch',
    }
    
    items_created = 0
    items_updated = 0
    
    with get_db() as conn:
        # Get active menu version
        version = conn.execute(
            'SELECT id FROM menu_versions WHERE is_active = 1 LIMIT 1'
        ).fetchone()
        
        version_id = version['id'] if version else 1
        
        for code, display_name in menu_mapping.items():
            # Find recipe by code prefix
            recipe = conn.execute('''
                SELECT id, recipe_name, food_cost, menu_price, recipe_group
                FROM recipes 
                WHERE recipe_name LIKE ?
            ''', (f'{code}%',)).fetchone()
            
            if not recipe:
                continue
            
            # Calculate food cost percent
            food_cost_percent = 0
            if recipe['menu_price'] and recipe['menu_price'] > 0:
                food_cost_percent = (recipe['food_cost'] / recipe['menu_price']) * 100
            
            # Calculate gross profit
            gross_profit = recipe['menu_price'] - recipe['food_cost'] if recipe['menu_price'] else 0
            
            # Check if menu item exists
            existing = conn.execute(
                'SELECT id FROM menu_items WHERE item_name = ? AND version_id = ?',
                (display_name, version_id)
            ).fetchone()
            
            if existing:
                # Update existing
                conn.execute('''
                    UPDATE menu_items
                    SET recipe_id = ?, menu_price = ?, food_cost = ?,
                        food_cost_percent = ?, gross_profit = ?,
                        menu_group = ?, updated_date = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    recipe['id'], recipe['menu_price'], recipe['food_cost'],
                    food_cost_percent, gross_profit, recipe['recipe_group'],
                    existing['id']
                ))
                items_updated += 1
            else:
                # Create new
                conn.execute('''
                    INSERT INTO menu_items (
                        item_name, recipe_id, menu_price, food_cost,
                        food_cost_percent, gross_profit, menu_group,
                        version_id, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    display_name, recipe['id'], recipe['menu_price'],
                    recipe['food_cost'], food_cost_percent, gross_profit,
                    recipe['recipe_group'], version_id, 'Active'
                ))
                items_created += 1
        
        conn.commit()
    
    print(f"✅ Created {items_created} new menu items")
    print(f"📝 Updated {items_updated} existing menu items")

def show_import_summary():
    """Display summary of imported data"""
    print("\n📊 Import Summary:")
    
    with get_db() as conn:
        # Get counts
        recipes = conn.execute('SELECT COUNT(*) as count FROM recipes').fetchone()['count']
        inventory = conn.execute('SELECT COUNT(*) as count FROM inventory').fetchone()['count']
        menu_items = conn.execute('SELECT COUNT(*) as count FROM menu_items').fetchone()['count']
        ingredients = conn.execute('SELECT COUNT(*) as count FROM recipe_ingredients').fetchone()['count']
        
        # Get recipe groups
        groups = conn.execute('''
            SELECT recipe_group, COUNT(*) as count 
            FROM recipes 
            WHERE recipe_group != ''
            GROUP BY recipe_group
        ''').fetchall()
        
        print(f"\n📦 Total Inventory Items: {inventory}")
        print(f"🍳 Total Recipes: {recipes}")
        print(f"🥘 Total Recipe Ingredients: {ingredients}")
        print(f"🍽️  Total Menu Items: {menu_items}")
        
        print("\n📂 Recipe Groups:")
        for group in groups:
            print(f"  - {group['recipe_group']}: {group['count']} recipes")
        
        # Check for missing connections
        missing_ingredients = conn.execute('''
            SELECT COUNT(*) FROM recipe_ingredients WHERE ingredient_id IS NULL
        ''').fetchone()[0]
        
        if missing_ingredients > 0:
            print(f"\n⚠️  {missing_ingredients} ingredients not matched to inventory")

def main():
    """Main import process"""
    print("🚀 Starting comprehensive recipe import...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create backup first
    os.system('python3 backup_database.py')
    
    # Import in order
    import_recipe_summary()
    import_individual_recipe_files()
    create_menu_item_mappings()
    show_import_summary()
    
    print("\n✅ Import complete!")
    print("\n💡 To add new recipes:")
    print("  1. Export recipe from Toast POS")
    print("  2. Place CSV in reference/LJ_DATA_Ref/recipes/")
    print("  3. Run: python3 import_recipe_system.py")

if __name__ == "__main__":
    main()