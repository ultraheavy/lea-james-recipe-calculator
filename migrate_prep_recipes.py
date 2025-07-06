#!/usr/bin/env python3
"""
Migrate prep recipes from recipe_ingredients to recipe_components
"""

import sqlite3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_prep_recipes():
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    # Map of prep recipe names to their recipe IDs
    prep_recipes = {
        'Charred Onion Ranch': 104,
        'Collard Greens Recipe': 123,  
        'French Fries Recipe': 82,
        'Fried Chicken Tender': 91,
        'Kale Kimchi Recipe': 84,
        'Onion Ranch': 127,
        'Pickled Shallot': 131,
        'Roux recipe': 78,
        'Hot Honey Sauce': 107,
        'Ritz Crumble': 68
    }
    
    # Find all recipe_ingredients that reference prep recipes
    placeholders = ','.join(['?' for _ in prep_recipes])
    query = f"""
        SELECT 
            ri.id,
            ri.recipe_id,
            ri.ingredient_name,
            ri.quantity,
            ri.unit_of_measure,
            ri.cost,
            r.recipe_name
        FROM recipe_ingredients ri
        JOIN recipes r ON ri.recipe_id = r.id
        WHERE ri.ingredient_name IN ({placeholders})
    """
    
    cursor.execute(query, list(prep_recipes.keys()))
    prep_recipe_ingredients = cursor.fetchall()
    
    logger.info(f"Found {len(prep_recipe_ingredients)} prep recipe references to migrate")
    
    # Create recipe_components table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipe_components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_recipe_id INTEGER NOT NULL,
            component_recipe_id INTEGER NOT NULL,
            quantity DECIMAL(10,4) NOT NULL,
            unit_of_measure TEXT NOT NULL,
            cost DECIMAL(10,2) DEFAULT 0,
            FOREIGN KEY (parent_recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
            FOREIGN KEY (component_recipe_id) REFERENCES recipes(id) ON DELETE RESTRICT,
            UNIQUE(parent_recipe_id, component_recipe_id)
        )
    """)
    
    migrated = 0
    failed = 0
    
    for ri_id, recipe_id, ingredient_name, quantity, uom, cost, recipe_name in prep_recipe_ingredients:
        if ingredient_name in prep_recipes:
            component_recipe_id = prep_recipes[ingredient_name]
            
            # Check if this component already exists
            cursor.execute("""
                SELECT id FROM recipe_components 
                WHERE parent_recipe_id = ? AND component_recipe_id = ?
            """, (recipe_id, component_recipe_id))
            
            if cursor.fetchone():
                logger.info(f"Component already exists: {recipe_name} -> {ingredient_name}")
                continue
            
            try:
                # Insert into recipe_components
                cursor.execute("""
                    INSERT INTO recipe_components 
                    (parent_recipe_id, component_recipe_id, quantity, unit_of_measure, cost)
                    VALUES (?, ?, ?, ?, ?)
                """, (recipe_id, component_recipe_id, quantity or 1, uom or 'each', cost or 0))
                
                # Delete from recipe_ingredients
                cursor.execute("DELETE FROM recipe_ingredients WHERE id = ?", (ri_id,))
                
                migrated += 1
                logger.info(f"Migrated: {recipe_name} -> {ingredient_name}")
                
            except Exception as e:
                logger.error(f"Failed to migrate {recipe_name} -> {ingredient_name}: {e}")
                failed += 1
    
    conn.commit()
    
    logger.info(f"\nMigration complete:")
    logger.info(f"  Migrated: {migrated}")
    logger.info(f"  Failed: {failed}")
    logger.info(f"  Already existed: {len(prep_recipe_ingredients) - migrated - failed}")
    
    # Show remaining prep recipe references
    cursor.execute("""
        SELECT COUNT(*) FROM recipe_ingredients 
        WHERE ingredient_name LIKE '%Recipe%' 
           OR ingredient_name IN ('Charred Onion Ranch', 'Onion Ranch', 'Fried Chicken Tender', 
                                 'Pickled Shallot', 'Hot Honey Sauce', 'Ritz Crumble')
    """)
    remaining = cursor.fetchone()[0]
    logger.info(f"  Remaining prep recipe references: {remaining}")
    
    conn.close()

if __name__ == '__main__':
    migrate_prep_recipes()