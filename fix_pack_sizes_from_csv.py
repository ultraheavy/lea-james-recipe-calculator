#!/usr/bin/env python3
"""
Fix pack sizes by reading from the original CSV data
"""

import sqlite3
import csv

DATABASE = 'restaurant_calculator.db'
CSV_FILE = 'data_sources_from_toast/Lea_Janes_Hot_Chicken_Item_Detail_Report_20250704_023013.csv'

def fix_pack_sizes_from_csv():
    """Read the original CSV and fix pack sizes properly"""
    
    # Read CSV data
    csv_data = {}
    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        # Skip the first two header rows
        next(f)
        next(f)
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('Item Code'):
                continue
                
            item_code = row['Item Code']
            
            # Build pack size string properly from Pack, Size, Unit columns
            pack = row.get('Pack', '').strip()
            size = row.get('Size', '').strip()
            unit = row.get('Unit', '').strip()
            
            # Build the pack size string
            if pack and size and unit:
                # Handle special cases
                if unit == 'fl':
                    unit = 'fl oz'
                elif unit == 'ea':
                    unit = 'each'
                
                if pack == '1':
                    full_pack_size = f"{size} {unit}"
                else:
                    full_pack_size = f"{pack} x {size} {unit}"
            elif size:
                # Just size, no pack/unit
                full_pack_size = str(size)
            else:
                # Default
                full_pack_size = '1 each'
            
            csv_data[item_code] = {
                'pack_size': full_pack_size,
                'vendor': row.get('Vendor Name', ''),
                'price': row.get('Last Purchased Price ($)', '0'),
                'description': row.get('Item Description', '')
            }
    
    # Update database
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        updated = 0
        for item_code, data in csv_data.items():
            cursor.execute('''
                UPDATE inventory 
                SET pack_size = ?
                WHERE item_code = ?
            ''', (data['pack_size'], item_code))
            
            if cursor.rowcount > 0:
                updated += 1
                print(f"Updated {item_code}: {data['pack_size']}")
        
        conn.commit()
        print(f"\nTotal items updated: {updated}")

def recalculate_all_costs():
    """Recalculate all recipe costs after pack size fixes"""
    from unit_converter import UnitConverter
    
    converter = UnitConverter(DATABASE)
    
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all recipes
        recipes = cursor.execute('SELECT id, recipe_name FROM recipes').fetchall()
        
        print(f"\nRecalculating costs for {len(recipes)} recipes...")
        
        for recipe in recipes:
            recipe_id = recipe['id']
            
            # Get all ingredients
            ingredients = cursor.execute('''
                SELECT ri.*, i.* 
                FROM recipe_ingredients ri
                JOIN inventory i ON ri.ingredient_id = i.id
                WHERE ri.recipe_id = ?
            ''', (recipe_id,)).fetchall()
            
            total_cost = 0
            
            for ingredient in ingredients:
                quantity = ingredient['quantity']
                unit = ingredient['unit_of_measure']
                inventory_item = dict(ingredient)
                
                try:
                    cost = converter.calculate_ingredient_cost(
                        inventory_item,
                        quantity,
                        unit
                    )
                    
                    # Update ingredient cost
                    cursor.execute('''
                        UPDATE recipe_ingredients 
                        SET cost = ?
                        WHERE recipe_id = ? AND ingredient_id = ?
                    ''', (cost, recipe_id, ingredient['ingredient_id']))
                    
                    total_cost += cost
                    
                except Exception as e:
                    print(f"  ERROR with {ingredient['item_description']}: {e}")
            
            # Update recipe total
            cursor.execute('''
                UPDATE recipes 
                SET food_cost = ?,
                    prime_cost = ? + COALESCE(labor_cost, 0)
                WHERE id = ?
            ''', (total_cost, total_cost, recipe_id))
            
            if recipe['recipe_name'] in ['CHilli Oil - Hot Fat', 'Mac Sauce', 'Hot Honey Sauce']:
                print(f"{recipe['recipe_name']}: ${total_cost:.2f}")
        
        conn.commit()
        print("\nRecalculation complete!")

if __name__ == '__main__':
    print("Fixing pack sizes from CSV...")
    fix_pack_sizes_from_csv()
    
    print("\nRecalculating all recipe costs...")
    recalculate_all_costs()