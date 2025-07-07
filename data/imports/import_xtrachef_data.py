#!/usr/bin/env python3
"""
Import correct pack sizes and validate recipe costs from XtraChef data
"""

import sqlite3
import csv

DATABASE = 'restaurant_calculator.db'
ITEM_FILE = 'reference/LJ_DATA_Ref/Lea_Janes__Item_LIST_READY_FOR_IMPORT_latest.csv'
RECIPE_FILE = 'reference/LJ_DATA_Ref/LEA_JANES_Recipe_List_Summary_7_4_2025, 7_51_55 PM.csv'

def import_pack_sizes():
    """Import correct pack sizes from XtraChef item list"""
    
    updates = 0
    
    with open(ITEM_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            
            for row in reader:
                item_code = row.get('Item Code', '').strip()
                if not item_code:
                    continue
                
                # Build pack size from Pack, Size, Unit
                pack = row.get('Pack', '').strip()
                size = row.get('Size', '').strip()
                unit = row.get('Unit', '').strip()
                
                # Build pack size string
                if pack and size and unit:
                    if unit == 'fl':
                        unit = 'fl oz'
                    elif unit == 'ea':
                        unit = 'each'
                    
                    if pack == '1':
                        pack_size = f"{size} {unit}"
                    else:
                        pack_size = f"{pack} x {size} {unit}"
                elif size and unit:
                    pack_size = f"{size} {unit}"
                else:
                    continue  # Skip if no valid pack size
                
                # Update in database
                cursor.execute('''
                    UPDATE inventory 
                    SET pack_size = ?
                    WHERE item_code = ?
                ''', (pack_size, item_code))
                
                if cursor.rowcount > 0:
                    updates += 1
                    if updates <= 10:  # Show first 10
                        print(f"Updated {item_code}: {pack_size}")
            
            conn.commit()
    
    print(f"\nTotal pack sizes updated: {updates}")
    return updates

def validate_recipe_costs():
    """Compare our calculated costs with XtraChef expected costs"""
    
    print("\nValidating recipe costs against XtraChef data...")
    
    # Read expected costs
    expected_costs = {}
    with open(RECIPE_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            recipe_name = row['RecipeName']
            food_cost = float(row['FoodCost']) if row['FoodCost'] else 0
            expected_costs[recipe_name] = food_cost
    
    # Compare with our database
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        discrepancies = []
        
        for recipe_name, expected_cost in expected_costs.items():
            result = cursor.execute('''
                SELECT food_cost FROM recipes WHERE recipe_name = ?
            ''', (recipe_name,)).fetchone()
            
            if result:
                actual_cost = result[0] or 0
                diff = abs(actual_cost - expected_cost)
                pct_diff = (diff / expected_cost * 100) if expected_cost > 0 else 0
                
                if pct_diff > 10:  # More than 10% difference
                    discrepancies.append({
                        'recipe': recipe_name,
                        'expected': expected_cost,
                        'actual': actual_cost,
                        'diff': diff,
                        'pct': pct_diff
                    })
        
        # Show discrepancies
        if discrepancies:
            print("\nRecipes with significant cost differences:")
            print("-" * 80)
            print(f"{'Recipe':<40} {'Expected':>10} {'Actual':>10} {'Diff %':>8}")
            print("-" * 80)
            
            for d in sorted(discrepancies, key=lambda x: x['pct'], reverse=True)[:20]:
                print(f"{d['recipe']:<40} ${d['expected']:>9.2f} ${d['actual']:>9.2f} {d['pct']:>7.1f}%")
        else:
            print("\nAll recipe costs are within acceptable range!")

def recalculate_all_costs():
    """Recalculate all recipe costs after pack size fixes"""
    from unit_converter import UnitConverter
    
    converter = UnitConverter(DATABASE)
    
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        recipes = cursor.execute('SELECT id, recipe_name FROM recipes').fetchall()
        
        print(f"\nRecalculating costs for {len(recipes)} recipes...")
        
        for recipe in recipes:
            recipe_id = recipe['id']
            
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
                    
                    cursor.execute('''
                        UPDATE recipe_ingredients 
                        SET cost = ?
                        WHERE recipe_id = ? AND ingredient_id = ?
                    ''', (cost, recipe_id, ingredient['ingredient_id']))
                    
                    total_cost += cost
                    
                except Exception as e:
                    pass  # Skip errors silently
            
            cursor.execute('''
                UPDATE recipes 
                SET food_cost = ?,
                    prime_cost = ? + COALESCE(labor_cost, 0)
                WHERE id = ?
            ''', (total_cost, total_cost, recipe_id))
        
        conn.commit()
        print("Recalculation complete!")

if __name__ == '__main__':
    # Import correct pack sizes
    if import_pack_sizes() > 0:
        # Recalculate costs
        recalculate_all_costs()
    
    # Validate against expected costs
    validate_recipe_costs()