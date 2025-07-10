#!/usr/bin/env python3
"""
Phase 3: Data Migration & Validation
Migrates data from old schema to new schema with proper validation
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Tuple

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('restaurant_calculator.db')

def migrate_recipes(conn: sqlite3.Connection) -> int:
    """Migrate recipes with proper type classification and cost fixes"""
    cursor = conn.cursor()
    
    # Get all old recipes
    old_recipes = cursor.execute("""
        SELECT id, recipe_name, status, recipe_group, recipe_type,
               food_cost, menu_price, prep_recipe_yield, prep_recipe_yield_uom,
               serving_size, serving_size_uom, station, shelf_life, procedure
        FROM recipes
    """).fetchall()
    
    migrated_count = 0
    
    for old_recipe in old_recipes:
        (old_id, recipe_name, status, recipe_group, recipe_type,
         food_cost, menu_price, prep_yield, prep_yield_unit,
         serving_size, serving_unit, station, shelf_life, procedure) = old_recipe
        
        # Determine recipe type based on data
        if recipe_type == 'PrepRecipe' or prep_yield:
            final_recipe_type = 'PrepRecipe'
        else:
            final_recipe_type = 'Recipe'
        
        # Clean up recipe group
        if not recipe_group:
            recipe_group = 'Main'
        
        # Handle prep recipes vs final recipes differently
        if final_recipe_type == 'PrepRecipe':
            # Prep recipes don't have menu prices
            final_menu_price = None
            batch_yield = prep_yield
            batch_yield_unit = prep_yield_unit
        else:
            # Final recipes need menu prices
            final_menu_price = menu_price
            batch_yield = None
            batch_yield_unit = None
        
        # Insert into new table
        try:
            cursor.execute("""
                INSERT INTO recipes_new (
                    recipe_name, recipe_type, recipe_group, status,
                    serving_size, serving_unit, station,
                    batch_yield, batch_yield_unit,
                    food_cost, menu_price,
                    instructions, shelf_life_hours,
                    migrated_from_old_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recipe_name, final_recipe_type, recipe_group, status or 'Draft',
                serving_size, serving_unit, station,
                batch_yield, batch_yield_unit,
                food_cost or 0, final_menu_price,
                procedure, int(shelf_life) if shelf_life and shelf_life.isdigit() else None,
                old_id
            ))
            
            migrated_count += 1
            print(f"✓ Migrated: {recipe_name} ({final_recipe_type})")
            
        except sqlite3.IntegrityError as e:
            print(f"✗ Failed to migrate {recipe_name}: {e}")
    
    conn.commit()
    return migrated_count

def migrate_menu_items(conn: sqlite3.Connection) -> Tuple[int, List[Dict]]:
    """Migrate menu items with strict 1:1 recipe enforcement"""
    cursor = conn.cursor()
    
    # Find menu items with proper 1:1 recipe relationships
    clean_items = cursor.execute("""
        SELECT mi.id, mi.item_name, mi.menu_group, mi.item_description,
               mi.recipe_id, mi.menu_price, rn.recipe_id as new_recipe_id
        FROM menu_items mi
        JOIN recipes r ON mi.recipe_id = r.id
        JOIN recipes_new rn ON r.id = rn.migrated_from_old_id
        WHERE mi.recipe_id IS NOT NULL
        AND mi.recipe_id NOT IN (
            -- Exclude recipes with multiple menu items
            SELECT recipe_id FROM menu_items 
            GROUP BY recipe_id 
            HAVING COUNT(*) > 1
        )
    """).fetchall()
    
    migrated_count = 0
    
    for item in clean_items:
        (old_id, item_name, menu_group, description,
         old_recipe_id, menu_price, new_recipe_id) = item
        
        try:
            cursor.execute("""
                INSERT INTO menu_items_new (
                    item_name, recipe_id, menu_category,
                    description, current_price,
                    migrated_from_old_id
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                item_name, new_recipe_id, menu_group or 'Main',
                description, menu_price, old_id
            ))
            
            migrated_count += 1
            print(f"✓ Migrated menu item: {item_name}")
            
        except sqlite3.IntegrityError as e:
            print(f"✗ Failed to migrate menu item {item_name}: {e}")
    
    # Log problematic relationships
    problems = cursor.execute("""
        SELECT r.recipe_name, COUNT(mi.id) as item_count,
               GROUP_CONCAT(mi.item_name, ', ') as items
        FROM menu_items mi
        JOIN recipes r ON mi.recipe_id = r.id
        WHERE mi.recipe_id IS NOT NULL
        GROUP BY mi.recipe_id
        HAVING COUNT(mi.id) > 1
    """).fetchall()
    
    problem_list = []
    for recipe_name, item_count, items in problems:
        problem_list.append({
            'recipe_name': recipe_name,
            'item_count': item_count,
            'items': items
        })
        print(f"⚠️  Multiple items for recipe '{recipe_name}': {items}")
    
    conn.commit()
    return migrated_count, problem_list

def migrate_menus(conn: sqlite3.Connection) -> int:
    """Migrate and consolidate menu system"""
    cursor = conn.cursor()
    
    # Migrate existing menus
    old_menus = cursor.execute("""
        SELECT id, menu_name, description, is_active
        FROM menus
    """).fetchall()
    
    for old_id, menu_name, description, is_active in old_menus:
        # Determine menu version/status
        if 'V3' in menu_name or 'v3' in menu_name:
            menu_version = 'V3 Planning'
            status = 'Draft'
        elif is_active:
            menu_version = 'Current'
            status = 'Active'
        else:
            menu_version = 'Master'
            status = 'Active'
        
        cursor.execute("""
            INSERT INTO menus_new (
                menu_name, menu_version, status, description
            ) VALUES (?, ?, ?, ?)
        """, (menu_name, menu_version, status, description))
        
        print(f"✓ Migrated menu: {menu_name} ({menu_version})")
    
    conn.commit()
    return len(old_menus)

def migrate_menu_assignments(conn: sqlite3.Connection) -> int:
    """Migrate menu item assignments"""
    cursor = conn.cursor()
    
    # Get menu assignments for migrated items only
    assignments = cursor.execute("""
        SELECT DISTINCT
            mn.menu_id,
            min.menu_item_id,
            mmi.category,
            mmi.sort_order,
            mmi.override_price
        FROM menu_menu_items mmi
        JOIN menu_items mi ON mmi.menu_item_id = mi.id
        JOIN menu_items_new min ON mi.id = min.migrated_from_old_id
        JOIN menus m ON mmi.menu_id = m.id
        JOIN menus_new mn ON m.menu_name = mn.menu_name
    """).fetchall()
    
    migrated_count = 0
    
    for menu_id, menu_item_id, category, sort_order, override_price in assignments:
        try:
            cursor.execute("""
                INSERT INTO menu_assignments_new (
                    menu_id, menu_item_id, category_section,
                    sort_order, price_override
                ) VALUES (?, ?, ?, ?, ?)
            """, (menu_id, menu_item_id, category, sort_order, override_price))
            
            migrated_count += 1
            
        except sqlite3.IntegrityError:
            pass  # Skip duplicates
    
    print(f"✓ Migrated {migrated_count} menu assignments")
    conn.commit()
    return migrated_count

def migrate_recipe_ingredients(conn: sqlite3.Connection) -> int:
    """Migrate recipe ingredients"""
    cursor = conn.cursor()
    
    # Get all recipe ingredients
    ingredients = cursor.execute("""
        SELECT ri.id, ri.recipe_id, ri.ingredient_id, ri.ingredient_name,
               ri.quantity, ri.unit_of_measure, ri.cost,
               rn.recipe_id as new_recipe_id
        FROM recipe_ingredients ri
        JOIN recipes r ON ri.recipe_id = r.id
        JOIN recipes_new rn ON r.id = rn.migrated_from_old_id
    """).fetchall()
    
    migrated_count = 0
    
    for (old_id, old_recipe_id, inventory_id, ingredient_name,
         quantity, unit, cost, new_recipe_id) in ingredients:
        
        cursor.execute("""
            INSERT INTO recipe_ingredients_new (
                recipe_id, inventory_id, ingredient_name,
                quantity, unit, total_cost,
                ingredient_order, migrated_from_old_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            new_recipe_id, inventory_id, ingredient_name,
            quantity or 0, unit or 'each', cost or 0,
            migrated_count, old_id
        ))
        
        migrated_count += 1
    
    print(f"✓ Migrated {migrated_count} recipe ingredients")
    conn.commit()
    return migrated_count

def create_migration_report(conn: sqlite3.Connection, problems: List[Dict]):
    """Create a detailed migration report"""
    cursor = conn.cursor()
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'recipes_migrated': cursor.execute("SELECT COUNT(*) FROM recipes_new").fetchone()[0],
        'menu_items_migrated': cursor.execute("SELECT COUNT(*) FROM menu_items_new").fetchone()[0],
        'menus_migrated': cursor.execute("SELECT COUNT(*) FROM menus_new").fetchone()[0],
        'ingredients_migrated': cursor.execute("SELECT COUNT(*) FROM recipe_ingredients_new").fetchone()[0],
        'problems': problems
    }
    
    with open('migrations/migration_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n📊 Migration Summary:")
    print(f"   Recipes: {report['recipes_migrated']}")
    print(f"   Menu Items: {report['menu_items_migrated']}")
    print(f"   Menus: {report['menus_migrated']}")
    print(f"   Ingredients: {report['ingredients_migrated']}")
    print(f"   Problems requiring manual review: {len(problems)}")

def main():
    """Run the complete migration"""
    print("🚀 Starting data migration...")
    
    conn = get_db_connection()
    
    try:
        # Phase 1: Migrate recipes
        print("\n📦 Migrating recipes...")
        recipes_count = migrate_recipes(conn)
        
        # Phase 2: Migrate menu items (with 1:1 enforcement)
        print("\n🍽️  Migrating menu items...")
        items_count, problems = migrate_menu_items(conn)
        
        # Phase 3: Migrate menus
        print("\n📋 Migrating menus...")
        menus_count = migrate_menus(conn)
        
        # Phase 4: Migrate menu assignments
        print("\n🔗 Migrating menu assignments...")
        assignments_count = migrate_menu_assignments(conn)
        
        # Phase 5: Migrate recipe ingredients
        print("\n🥕 Migrating recipe ingredients...")
        ingredients_count = migrate_recipe_ingredients(conn)
        
        # Create migration report
        create_migration_report(conn, problems)
        
        print("\n✅ Migration complete!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()