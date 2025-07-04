#!/usr/bin/env python3
"""
Import recipe ingredients from individual recipe CSV files
and link them to inventory items for cost calculations
"""

import sqlite3
import csv
import os
import glob
from datetime import datetime

DATABASE = 'restaurant_calculator.db'
DATA_DIR = 'data_sources_from_toast'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def find_recipe_csv_files():
    """Find all individual recipe CSV files"""
    pattern = os.path.join(DATA_DIR, '*_Lea James Hot Chicken_*.csv')
    recipe_files = glob.glob(pattern)
    
    # Filter out the main reports
    recipe_files = [f for f in recipe_files if 'Item_Detail_Report' not in f and 'Recipe_Summary' not in f]
    
    print(f"🔍 Found {len(recipe_files)} recipe CSV files")
    return recipe_files

def parse_recipe_csv(file_path):
    """Parse individual recipe CSV file"""
    recipe_name = None
    ingredients = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            # Find recipe name (usually in line 2)
            for line in lines[:5]:
                if 'Recipe Name,' in line:
                    recipe_name = line.split(',')[1].strip()
                    break
            
            # Find ingredients section
            ingredient_section = False
            for line in lines:
                if 'Ingredient,Type,Measurement' in line:
                    ingredient_section = True
                    continue
                
                if ingredient_section and line.strip():
                    parts = [p.strip('"').strip() for p in line.split(',')]
                    if len(parts) >= 6 and parts[0] and parts[2]:
                        ingredient = {
                            'description': parts[0],
                            'type': parts[1] if len(parts) > 1 else 'Product',
                            'measurement': parts[2],
                            'yield_percent': parts[3] if len(parts) > 3 else '100%',
                            'cost': parts[5] if len(parts) > 5 else '0'
                        }
                        ingredients.append(ingredient)
    
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    
    return recipe_name, ingredients

def find_matching_inventory_item(ingredient_desc):
    """Find inventory item that matches ingredient description"""
    with get_db() as conn:
        # Try exact match on product categories first
        exact_match = conn.execute('''
            SELECT id, item_description, product_categories 
            FROM inventory 
            WHERE UPPER(product_categories) = UPPER(?)
        ''', (ingredient_desc,)).fetchone()
        
        if exact_match:
            return exact_match
        
        # Try partial matches on key words
        keywords = ingredient_desc.replace(',', ' ').split()
        for keyword in keywords:
            if len(keyword) > 3:  # Skip short words
                partial_match = conn.execute('''
                    SELECT id, item_description, product_categories 
                    FROM inventory 
                    WHERE UPPER(item_description) LIKE ? 
                       OR UPPER(product_categories) LIKE ?
                    LIMIT 1
                ''', (f'%{keyword.upper()}%', f'%{keyword.upper()}%')).fetchone()
                
                if partial_match:
                    return partial_match
        
        return None

def import_recipe_ingredients():
    """Import ingredients for all recipes"""
    print("🍳 Importing recipe ingredients...")
    
    recipe_files = find_recipe_csv_files()
    total_ingredients = 0
    matched_ingredients = 0
    unmatched_ingredients = []
    
    with get_db() as conn:
        for file_path in recipe_files:
            recipe_name, ingredients = parse_recipe_csv(file_path)
            
            if not recipe_name or not ingredients:
                continue
            
            # Find the recipe in database
            recipe = conn.execute('''
                SELECT id FROM recipes WHERE recipe_name = ?
            ''', (recipe_name,)).fetchone()
            
            if not recipe:
                print(f"⚠️  Recipe '{recipe_name}' not found in database")
                continue
            
            recipe_id = recipe['id']
            
            # Clear existing ingredients for this recipe
            conn.execute('DELETE FROM recipe_ingredients WHERE recipe_id = ?', (recipe_id,))
            
            print(f"\n📝 Processing recipe: {recipe_name}")
            
            for ingredient in ingredients:
                total_ingredients += 1
                
                # Find matching inventory item
                inventory_item = find_matching_inventory_item(ingredient['description'])
                
                if inventory_item:
                    matched_ingredients += 1
                    
                    # Parse measurement (e.g., "10 oz" -> quantity=10, unit="oz")
                    measurement = ingredient['measurement'].strip()
                    quantity = 0
                    unit = 'each'
                    
                    try:
                        parts = measurement.split()
                        if len(parts) >= 2:
                            quantity = float(parts[0])
                            unit = ' '.join(parts[1:])
                        elif len(parts) == 1:
                            try:
                                quantity = float(parts[0])
                            except:
                                unit = parts[0]
                    except:
                        pass
                    
                    # Parse cost
                    cost = 0
                    try:
                        cost_str = ingredient['cost'].replace('$', '').replace(',', '')
                        if cost_str:
                            cost = float(cost_str)
                    except:
                        pass
                    
                    # Insert ingredient
                    conn.execute('''
                        INSERT INTO recipe_ingredients 
                        (recipe_id, ingredient_id, ingredient_name, ingredient_type, 
                         quantity, unit_of_measure, cost)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        recipe_id,
                        inventory_item['id'],
                        ingredient['description'],
                        ingredient['type'],
                        quantity,
                        unit,
                        cost
                    ))
                    
                    print(f"  ✅ {ingredient['description']} → {inventory_item['item_description']} ({quantity} {unit})")
                
                else:
                    unmatched_ingredients.append({
                        'recipe': recipe_name,
                        'ingredient': ingredient['description']
                    })
                    print(f"  ❌ No match found for: {ingredient['description']}")
        
        conn.commit()
    
    print(f"\n📊 INGREDIENT IMPORT SUMMARY:")
    print(f"  - Total ingredients processed: {total_ingredients}")
    print(f"  - Successfully matched: {matched_ingredients}")
    print(f"  - Unmatched: {len(unmatched_ingredients)}")
    print(f"  - Match rate: {(matched_ingredients/total_ingredients*100):.1f}%")
    
    if unmatched_ingredients:
        print(f"\n❌ UNMATCHED INGREDIENTS:")
        for item in unmatched_ingredients[:10]:  # Show first 10
            print(f"  - {item['recipe']}: {item['ingredient']}")
        if len(unmatched_ingredients) > 10:
            print(f"  ... and {len(unmatched_ingredients) - 10} more")

def update_recipe_costs():
    """Update recipe costs based on linked ingredients"""
    print("\n💰 Updating recipe costs from ingredient data...")
    
    with get_db() as conn:
        recipes = conn.execute('SELECT id, recipe_name FROM recipes').fetchall()
        updated = 0
        
        for recipe in recipes:
            # Calculate total cost from ingredients
            total_cost = conn.execute('''
                SELECT COALESCE(SUM(cost), 0) as total
                FROM recipe_ingredients 
                WHERE recipe_id = ?
            ''', (recipe['id'],)).fetchone()['total']
            
            if total_cost > 0:
                # Update recipe cost
                conn.execute('''
                    UPDATE recipes 
                    SET food_cost = ?, updated_date = ?
                    WHERE id = ?
                ''', (total_cost, datetime.now().isoformat(), recipe['id']))
                updated += 1
        
        conn.commit()
    
    print(f"✅ Updated costs for {updated} recipes")

def main():
    """Main import process"""
    print("🚀 Starting recipe ingredient import process...")
    print("=" * 60)
    
    import_recipe_ingredients()
    update_recipe_costs()
    
    print("=" * 60)
    print("✅ Recipe ingredient import completed!")

if __name__ == '__main__':
    main()
