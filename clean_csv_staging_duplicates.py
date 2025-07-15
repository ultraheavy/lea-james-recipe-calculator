#!/usr/bin/env python3
"""
Clean duplicate recipes from CSV staging table
Keeps the most recent/complete version of each recipe
"""

import sqlite3
from datetime import datetime

def clean_duplicates(db_path: str = "restaurant_calculator.db"):
    """Remove duplicate recipes, keeping the best version"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    results = {
        'duplicates_found': 0,
        'records_removed': 0,
        'recipes_cleaned': []
    }
    
    try:
        # Find all duplicate recipe names
        cursor.execute("""
            SELECT recipe_name, COUNT(*) as count 
            FROM stg_csv_recipes 
            GROUP BY recipe_name 
            HAVING COUNT(*) > 1
        """)
        
        duplicate_recipes = cursor.fetchall()
        results['duplicates_found'] = len(duplicate_recipes)
        
        for recipe_name, count in duplicate_recipes:
            print(f"\nProcessing {recipe_name} ({count} versions)...")
            
            # Get all versions of this recipe
            cursor.execute("""
                SELECT staging_id, source_filename, imported_at, 
                       COUNT(*) OVER (PARTITION BY source_filename) as ingredients_count
                FROM stg_csv_recipes
                WHERE recipe_name = ?
                ORDER BY imported_at DESC, ingredients_count DESC
            """, (recipe_name,))
            
            versions = cursor.fetchall()
            
            # Keep the first (most recent with most ingredients)
            keep_file = versions[0][1]
            keep_ids = []
            
            # Get all staging_ids for the version we're keeping
            cursor.execute("""
                SELECT staging_id 
                FROM stg_csv_recipes 
                WHERE recipe_name = ? AND source_filename = ?
            """, (recipe_name, keep_file))
            
            keep_ids = [row[0] for row in cursor.fetchall()]
            
            # Delete all other versions
            placeholders = ','.join('?' * len(keep_ids))
            cursor.execute(f"""
                DELETE FROM stg_csv_recipes 
                WHERE recipe_name = ? 
                AND staging_id NOT IN ({placeholders})
            """, [recipe_name] + keep_ids)
            
            removed = cursor.rowcount
            results['records_removed'] += removed
            results['recipes_cleaned'].append({
                'recipe': recipe_name,
                'kept': keep_file,
                'removed': removed
            })
            
            print(f"  Kept: {keep_file}")
            print(f"  Removed: {removed} records")
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {str(e)}")
    finally:
        conn.close()
    
    return results

def add_unique_constraint():
    """Add a unique constraint to prevent future duplicates within a batch"""
    conn = sqlite3.connect("restaurant_calculator.db")
    cursor = conn.cursor()
    
    try:
        # Create unique index on recipe_name + ingredient_name + import_batch_id
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_recipe_ingredient_batch 
            ON stg_csv_recipes(recipe_name, ingredient_name, import_batch_id)
        """)
        conn.commit()
        print("Added unique constraint to prevent future duplicates")
    except Exception as e:
        print(f"Error adding constraint: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Cleaning duplicate recipes from staging table...")
    
    # Clean duplicates
    results = clean_duplicates()
    
    print(f"\n=== Cleaning Summary ===")
    print(f"Duplicate recipes found: {results['duplicates_found']}")
    print(f"Total records removed: {results['records_removed']}")
    
    if results['recipes_cleaned']:
        print("\nRecipes cleaned:")
        for item in results['recipes_cleaned'][:10]:  # Show first 10
            print(f"  - {item['recipe']}: removed {item['removed']} duplicates")
        if len(results['recipes_cleaned']) > 10:
            print(f"  ... and {len(results['recipes_cleaned']) - 10} more")
    
    # Add constraint for future imports
    print("\nAdding unique constraint...")
    add_unique_constraint()
    
    print("\nDone!")