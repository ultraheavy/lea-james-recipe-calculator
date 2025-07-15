#!/usr/bin/env python3
"""
Fix UX issues in CSV staging:
1. Fix ingredient names that have categories embedded
2. Normalize units
3. Fix cost formatting
"""

import sqlite3
import re

def fix_ingredient_names(db_path: str = "restaurant_calculator.db"):
    """Clean up ingredient names and extract categories"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    updates = 0
    
    try:
        # Get all ingredients with comma-separated names
        cursor.execute("""
            SELECT staging_id, ingredient_name, category
            FROM stg_csv_recipes
            WHERE ingredient_name LIKE '%,%'
            AND committed = 0
        """)
        
        rows = cursor.fetchall()
        
        for staging_id, ingredient_name, current_category in rows:
            # Parse category and name from format: "Category, Item, Details"
            parts = [p.strip() for p in ingredient_name.split(',')]
            
            if len(parts) >= 2:
                category = parts[0]
                name = ', '.join(parts[1:])  # Keep remaining parts as name
                
                # Update the record
                cursor.execute("""
                    UPDATE stg_csv_recipes
                    SET ingredient_name = ?,
                        category = ?
                    WHERE staging_id = ?
                """, (name, category, staging_id))
                
                updates += 1
        
        conn.commit()
        print(f"Fixed {updates} ingredient names")
        
    except Exception as e:
        conn.rollback()
        print(f"Error fixing ingredient names: {str(e)}")
    finally:
        conn.close()

def normalize_units(db_path: str = "restaurant_calculator.db"):
    """Normalize common unit variations"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    unit_mappings = {
        'qt': 'quart',
        'qts': 'quart',
        'quarts': 'quart',
        'lb': 'pound',
        'lbs': 'pound',
        'pounds': 'pound',
        'oz': 'ounce',
        'ozs': 'ounce',
        'ounces': 'ounce',
        'gal': 'gallon',
        'gallons': 'gallon',
        'tsp': 'teaspoon',
        'tbsp': 'tablespoon',
        'c': 'cup',
        'cups': 'cup',
        'g': 'gram',
        'grams': 'gram',
        'kg': 'kilogram',
        'kilograms': 'kilogram',
        'ml': 'milliliter',
        'milliliters': 'milliliter',
        'l': 'liter',
        'liters': 'liter',
        'ea': 'each',
        'pc': 'piece',
        'pcs': 'piece',
        'pieces': 'piece'
    }
    
    updates = 0
    
    try:
        for old_unit, new_unit in unit_mappings.items():
            cursor.execute("""
                UPDATE stg_csv_recipes
                SET unit = ?
                WHERE LOWER(unit) = ?
                AND committed = 0
            """, (new_unit, old_unit))
            
            updates += cursor.rowcount
        
        conn.commit()
        print(f"Normalized {updates} units")
        
    except Exception as e:
        conn.rollback()
        print(f"Error normalizing units: {str(e)}")
    finally:
        conn.close()

def fix_cost_decimals(db_path: str = "restaurant_calculator.db"):
    """Fix cost values with too many decimal places"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    updates = 0
    
    try:
        # Round costs to 2 decimal places
        cursor.execute("""
            UPDATE stg_csv_recipes
            SET cost = ROUND(CAST(cost AS REAL), 2)
            WHERE cost IS NOT NULL
            AND committed = 0
            AND cost != ROUND(CAST(cost AS REAL), 2)
        """)
        
        updates = cursor.rowcount
        conn.commit()
        print(f"Fixed {updates} cost values")
        
    except Exception as e:
        conn.rollback()
        print(f"Error fixing costs: {str(e)}")
    finally:
        conn.close()

def set_recipe_types(db_path: str = "restaurant_calculator.db"):
    """Set is_prep_recipe flag based on recipe names and patterns"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    prep_patterns = [
        'sauce', 'dressing', 'marinade', 'roux', 'blend', 'mix',
        'seasoning', 'prep', 'base', 'ranch', 'mayo', 'aioli',
        'vinaigrette', 'compound', 'infused', 'pickled'
    ]
    
    updates = 0
    
    try:
        # Build pattern for SQL
        pattern_sql = " OR ".join([f"LOWER(recipe_name) LIKE '%{p}%'" for p in prep_patterns])
        
        cursor.execute(f"""
            UPDATE stg_csv_recipes
            SET is_prep_recipe = 1
            WHERE ({pattern_sql})
            AND is_prep_recipe = 0
            AND committed = 0
        """)
        
        updates = cursor.rowcount
        conn.commit()
        print(f"Set {updates} recipes as prep recipes")
        
    except Exception as e:
        conn.rollback()
        print(f"Error setting recipe types: {str(e)}")
    finally:
        conn.close()

def auto_approve_valid_items(db_path: str = "restaurant_calculator.db"):
    """Auto-approve items without issues"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE stg_csv_recipes
            SET review_status = 'approved',
                needs_review = 0,
                reviewed_at = CURRENT_TIMESTAMP,
                reviewed_by = 'auto_approval'
            WHERE review_status = 'pending'
            AND needs_review = 0
            AND quantity IS NOT NULL
            AND unit IS NOT NULL
            AND cost IS NOT NULL
            AND CAST(cost AS REAL) > 0
            AND is_duplicate = 0
            AND committed = 0
        """)
        
        approved = cursor.rowcount
        conn.commit()
        print(f"Auto-approved {approved} valid items")
        
    except Exception as e:
        conn.rollback()
        print(f"Error auto-approving: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Fixing UX issues in CSV staging...\n")
    
    print("1. Fixing ingredient names...")
    fix_ingredient_names()
    
    print("\n2. Normalizing units...")
    normalize_units()
    
    print("\n3. Fixing cost decimal places...")
    fix_cost_decimals()
    
    print("\n4. Setting prep recipe flags...")
    set_recipe_types()
    
    print("\n5. Auto-approving valid items...")
    auto_approve_valid_items()
    
    print("\nUX fixes complete!")