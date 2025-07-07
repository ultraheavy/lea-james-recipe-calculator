#!/usr/bin/env python3
"""
Recalculate all recipe and menu item costs
Run this after database migrations to fix cost calculations
"""
import sqlite3
from decimal import Decimal

def get_unit_conversion(conn, from_unit, to_unit, unit_type):
    """Get conversion factor between units"""
    if from_unit == to_unit:
        return 1.0
    
    cursor = conn.cursor()
    
    # Get conversion factors
    cursor.execute('''
        SELECT u1.to_base_factor, u2.to_base_factor
        FROM units u1, units u2
        WHERE u1.unit_name = ? AND u2.unit_name = ?
        AND u1.unit_type = u2.unit_type
    ''', (from_unit, to_unit))
    
    result = cursor.fetchone()
    if result:
        return float(result[0]) / float(result[1])
    
    # If no direct conversion, return 1.0 as fallback
    return 1.0

def parse_pack_size(pack_size_str):
    """Parse pack size string to extract quantity and unit"""
    if not pack_size_str:
        return 1.0, 'each'
    
    pack_size_str = str(pack_size_str).strip().lower()
    
    # Handle special cases
    if pack_size_str in ['', 'each', '1']:
        return 1.0, 'each'
    
    # Try to parse "number unit" format
    parts = pack_size_str.split()
    if len(parts) >= 2:
        try:
            qty = float(parts[0])
            unit = parts[1]
            return qty, unit
        except ValueError:
            pass
    
    # Try to extract just a number
    try:
        return float(pack_size_str), 'each'
    except ValueError:
        return 1.0, 'each'

def calculate_recipe_cost(conn, recipe_id):
    """Calculate the total cost of a recipe"""
    cursor = conn.cursor()
    
    # Get all ingredients for this recipe
    cursor.execute('''
        SELECT 
            ri.quantity,
            ri.unit_measure,
            i.current_price,
            i.pack_size,
            i.purchase_unit,
            i.yield_percent
        FROM recipe_ingredients ri
        JOIN inventory i ON ri.ingredient_id = i.id
        WHERE ri.recipe_id = ?
    ''', (recipe_id,))
    
    total_cost = Decimal('0')
    
    for row in cursor.fetchall():
        quantity = Decimal(str(row[0] or 0))
        recipe_unit = row[1] or 'each'
        price_per_pack = Decimal(str(row[2] or 0))
        pack_size_str = row[3] or '1'
        purchase_unit = row[4] or 'each'
        yield_percent = Decimal(str(row[5] or 100)) / 100
        
        if quantity <= 0 or price_per_pack <= 0:
            continue
        
        # Parse pack size
        pack_qty, pack_unit = parse_pack_size(pack_size_str)
        
        # Calculate price per unit
        if pack_qty > 0:
            price_per_unit = price_per_pack / Decimal(str(pack_qty))
        else:
            price_per_unit = price_per_pack
        
        # Get unit conversion
        conversion = get_unit_conversion(conn, recipe_unit, pack_unit, 'weight')
        
        # Calculate ingredient cost
        ingredient_cost = quantity * price_per_unit * Decimal(str(conversion))
        
        # Apply yield
        if yield_percent > 0:
            ingredient_cost = ingredient_cost / yield_percent
        
        total_cost += ingredient_cost
    
    # Update recipe with new cost
    cursor.execute('''
        UPDATE recipes 
        SET food_cost = ?
        WHERE id = ?
    ''', (float(total_cost), recipe_id))
    
    return float(total_cost)

def recalculate_all_costs():
    """Recalculate costs for all recipes and menu items"""
    conn = sqlite3.connect('restaurant_calculator.db')
    
    try:
        print("Recalculating all recipe costs...")
        
        # Get all recipes
        cursor = conn.cursor()
        cursor.execute('SELECT id, recipe_name FROM recipes')
        recipes = cursor.fetchall()
        
        updated_count = 0
        for recipe_id, recipe_name in recipes:
            old_cost = cursor.execute('SELECT food_cost FROM recipes WHERE id = ?', (recipe_id,)).fetchone()[0]
            new_cost = calculate_recipe_cost(conn, recipe_id)
            
            if abs(old_cost - new_cost) > 0.01:
                print(f"Updated {recipe_name}: ${old_cost:.2f} -> ${new_cost:.2f}")
                updated_count += 1
        
        print(f"\nUpdated {updated_count} recipes")
        
        # Update menu items with recipe costs
        print("\nUpdating menu items...")
        cursor.execute('''
            UPDATE menu_items 
            SET food_cost = (
                SELECT food_cost 
                FROM recipes 
                WHERE recipes.id = menu_items.recipe_id
            )
            WHERE recipe_id IS NOT NULL
        ''')
        
        menu_updated = cursor.rowcount
        print(f"Updated {menu_updated} menu items")
        
        conn.commit()
        print("\nCost recalculation complete!")
        
        # Show summary statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_items,
                AVG(CASE WHEN menu_price > 0 THEN (food_cost / menu_price * 100) ELSE 0 END) as avg_food_cost_pct,
                COUNT(CASE WHEN menu_price > 0 AND food_cost / menu_price > 0.35 THEN 1 END) as high_cost_items
            FROM menu_items 
            WHERE menu_price > 0 AND food_cost > 0
        ''')
        
        stats = cursor.fetchone()
        print(f"\nSummary:")
        print(f"Total menu items: {stats[0]}")
        print(f"Average food cost %: {stats[1]:.1f}%")
        print(f"Items over 35% food cost: {stats[2]}")
        
    except Exception as e:
        conn.rollback()
        print(f"Error recalculating costs: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    recalculate_all_costs()