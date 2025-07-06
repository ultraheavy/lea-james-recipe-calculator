#!/usr/bin/env python3
"""
Fix ingredient mapping issues in recipe_ingredients table
"""

import sqlite3

DATABASE = 'restaurant_calculator.db'

def fix_specific_mappings():
    """Fix known incorrect mappings"""
    
    mapping_fixes = [
        # (recipe_name, ingredient_name, correct_item_description)
        ('French Fries - Portion', 'French Fries Recipe', 'Frozen, Potato, French Fries, Frozen'),
        ('French Fries Recipe', 'Frozen, Potato, French Fries, Frozen', 'Frozen, Potato, French Fries, Frozen'),
        
        # Black pepper vs Cayenne pepper mix-ups
        ('Alabama White BBQ', 'Dry Goods, Black Pepper, Ground', 'Dry Goods, Black Pepper, Ground'),
        ('Charred Onion Ranch', 'Dry Goods, Black Pepper, Ground', 'Dry Goods, Black Pepper, Ground'),
        
        # Prep recipes that should link to actual prep recipes
        ('Collard Greens - Side Portion', 'Collard Greens Recipe', None),  # This is a prep recipe reference
        ('Comeback Sauce - Portion', 'Comeback sauce', None),  # This is a prep recipe reference
        
        # Cheese corrections
        ('FT-01 Chicken Waffle Cone', 'Dairy, Cheese, Loaf, Pepper Jack', 'Dairy, Cheese, Loaf, Pepper Jack'),
        
        # BBQ Sauce
        ('BBQ Sauce Chicken Wings', 'Dry Goods, Sauce, BBQ Sweet', 'Dry Goods, Sauce, BBQ Hickory'),
        
        # Water
        ('Collard Greens Recipe', 'Water, Tap', None),  # Remove - water should be free
        
        # Ranch dressing
        ('Chicken Waffle Cone', 'Onion Ranch', None),  # This is a prep recipe
        ('DP-01 Charred-Onion Ranch Dip', 'Charred Onion Ranch', None),  # This is a prep recipe
    ]
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        for recipe_name, ingredient_name, correct_item in mapping_fixes:
            # Get recipe id
            recipe = cursor.execute('SELECT id FROM recipes WHERE recipe_name = ?', (recipe_name,)).fetchone()
            if not recipe:
                print(f"Recipe not found: {recipe_name}")
                continue
                
            recipe_id = recipe[0]
            
            if correct_item is None:
                # This is a prep recipe or should be removed
                print(f"Removing/skipping: {ingredient_name} from {recipe_name}")
                continue
            
            # Find the correct inventory item
            correct_inv = cursor.execute('''
                SELECT id FROM inventory 
                WHERE item_description = ? OR item_description LIKE ?
                LIMIT 1
            ''', (correct_item, f'%{correct_item}%')).fetchone()
            
            if correct_inv:
                # Update the mapping
                cursor.execute('''
                    UPDATE recipe_ingredients 
                    SET ingredient_id = ?,
                        ingredient_name = ?
                    WHERE recipe_id = ? AND ingredient_name = ?
                ''', (correct_inv[0], correct_item, recipe_id, ingredient_name))
                
                if cursor.rowcount > 0:
                    print(f"Fixed: {recipe_name} - {ingredient_name} -> {correct_item}")
            else:
                print(f"Could not find inventory item: {correct_item}")
        
        conn.commit()

def fix_prep_recipe_references():
    """Fix references to prep recipes in recipe_ingredients"""
    
    print("\nFixing prep recipe references...")
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        # Find all recipe ingredients that reference prep recipes
        prep_refs = cursor.execute('''
            SELECT ri.id, ri.recipe_id, ri.ingredient_name, r.recipe_name
            FROM recipe_ingredients ri
            JOIN recipes r ON ri.recipe_id = r.id
            WHERE ri.ingredient_name IN (
                SELECT recipe_name FROM recipes WHERE recipe_type = 'PrepRecipe'
            )
            AND ri.ingredient_id IS NULL
        ''').fetchall()
        
        for ri_id, recipe_id, prep_recipe_name, recipe_name in prep_refs:
            # Get the prep recipe
            prep_recipe = cursor.execute('''
                SELECT id, food_cost, prep_recipe_yield, prep_recipe_yield_uom
                FROM recipes 
                WHERE recipe_name = ? AND recipe_type = 'PrepRecipe'
            ''', (prep_recipe_name,)).fetchone()
            
            if prep_recipe:
                # For prep recipes, we need to calculate the cost based on yield
                # This is a simplified calculation - may need refinement
                prep_id, prep_cost, prep_yield, prep_yield_uom = prep_recipe
                
                # Get the quantity used in the recipe
                quantity_used = cursor.execute('''
                    SELECT quantity, unit_of_measure 
                    FROM recipe_ingredients 
                    WHERE id = ?
                ''', (ri_id,)).fetchone()
                
                if quantity_used and prep_cost:
                    qty, unit = quantity_used
                    # Simple cost calculation - may need unit conversion
                    prep_yield_num = float(prep_yield) if prep_yield else 1
                    cost_per_unit = prep_cost / prep_yield_num if prep_yield_num > 0 else 0
                    ingredient_cost = cost_per_unit * qty
                    
                    # Update the cost
                    cursor.execute('''
                        UPDATE recipe_ingredients 
                        SET cost = ?
                        WHERE id = ?
                    ''', (ingredient_cost, ri_id))
                    
                    print(f"Updated prep recipe cost: {recipe_name} uses {qty} {unit} of {prep_recipe_name} = ${ingredient_cost:.2f}")
        
        conn.commit()

def find_better_matches():
    """Try to find better matches for mismatched ingredients"""
    
    print("\nFinding better matches for ingredients...")
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        # Get all mismatched ingredients
        mismatches = cursor.execute('''
            SELECT ri.id, ri.recipe_id, ri.ingredient_name, ri.ingredient_id, 
                   i.item_description, r.recipe_name
            FROM recipe_ingredients ri
            LEFT JOIN inventory i ON ri.ingredient_id = i.id
            JOIN recipes r ON ri.recipe_id = r.id
            WHERE (ri.ingredient_name != i.item_description OR i.item_description IS NULL)
            AND ri.ingredient_id IS NOT NULL
        ''').fetchall()
        
        for ri_id, recipe_id, ingredient_name, current_inv_id, current_desc, recipe_name in mismatches:
            # Try to find a better match
            better_match = cursor.execute('''
                SELECT id, item_description 
                FROM inventory 
                WHERE item_description = ? 
                   OR item_description LIKE ?
                   OR item_description LIKE ?
                ORDER BY 
                    CASE WHEN item_description = ? THEN 1
                         WHEN item_description LIKE ? THEN 2
                         ELSE 3 END
                LIMIT 1
            ''', (ingredient_name, f'{ingredient_name}%', f'%{ingredient_name}%',
                  ingredient_name, f'{ingredient_name}%')).fetchone()
            
            if better_match and better_match[0] != current_inv_id:
                new_inv_id, new_desc = better_match
                cursor.execute('''
                    UPDATE recipe_ingredients 
                    SET ingredient_id = ?
                    WHERE id = ?
                ''', (new_inv_id, ri_id))
                
                print(f"Better match: {recipe_name} - {ingredient_name} -> {new_desc}")
        
        conn.commit()

def fix_non_con_items():
    """Handle non-consumable items (cups, lids) that shouldn't have ingredient costs"""
    
    print("\nHandling non-consumable items...")
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        # Find non-con items
        non_cons = cursor.execute('''
            SELECT DISTINCT ingredient_name 
            FROM recipe_ingredients 
            WHERE ingredient_name LIKE 'Non Con%'
        ''').fetchall()
        
        for (item_name,) in non_cons:
            # Check if this exists in inventory
            inv_item = cursor.execute('''
                SELECT id FROM inventory 
                WHERE item_description = ? OR item_description LIKE ?
            ''', (item_name, f'%{item_name.replace("Non Con, ", "")}%')).fetchone()
            
            if inv_item:
                # Update all references
                cursor.execute('''
                    UPDATE recipe_ingredients 
                    SET ingredient_id = ?
                    WHERE ingredient_name = ?
                ''', (inv_item[0], item_name))
                
                print(f"Linked non-con item: {item_name}")
            else:
                print(f"Non-con item not in inventory: {item_name}")
        
        conn.commit()

if __name__ == '__main__':
    print("Fixing ingredient mappings...")
    fix_specific_mappings()
    fix_prep_recipe_references()
    find_better_matches()
    fix_non_con_items()
    print("\nIngredient mapping fixes complete!")