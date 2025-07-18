#!/usr/bin/env python3
"""
Analyze Recipe Duplicate Issues
"""

import sqlite3
import os
from collections import defaultdict

def analyze_duplicates(db_path):
    """Analyze duplicate patterns in CSV files"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== Recipe Duplicate Analysis ===\n")
    
    # 1. Check file duplicates in CSV directory
    csv_dir = "reference/LJ_DATA_Ref/updated_recipes_csv_pdf/csv"
    if os.path.exists(csv_dir):
        print("1. Analyzing CSV Files:")
        recipe_files = defaultdict(list)
        
        for filename in os.listdir(csv_dir):
            if filename.endswith('.csv'):
                # Extract recipe name from filename
                parts = filename.split('_')
                if parts:
                    recipe_name = parts[0]
                    recipe_files[recipe_name].append(filename)
        
        # Show duplicates
        duplicate_count = 0
        for recipe, files in recipe_files.items():
            if len(files) > 1:
                duplicate_count += 1
                if duplicate_count <= 5:  # Show first 5
                    print(f"\n  Recipe: {recipe}")
                    for f in sorted(files):
                        print(f"    - {f}")
        
        if duplicate_count > 5:
            print(f"\n  ... and {duplicate_count - 5} more recipes with multiple files")
        
        print(f"\n  Total recipes with multiple CSV files: {duplicate_count}")
    
    # 2. Check staging table for duplicates
    print("\n2. Staging Table Analysis:")
    
    # Get recipe counts
    recipe_stats = cursor.execute("""
        SELECT 
            recipe_name,
            COUNT(*) as total_rows,
            COUNT(DISTINCT ingredient_name) as unique_ingredients,
            COUNT(DISTINCT import_batch_id) as batches,
            SUM(CASE WHEN is_duplicate = 1 THEN 1 ELSE 0 END) as marked_duplicates,
            SUM(CASE WHEN is_latest_version = 1 THEN 1 ELSE 0 END) as latest_version_count
        FROM stg_csv_recipes
        GROUP BY recipe_name
        HAVING COUNT(*) > 5
        ORDER BY total_rows DESC
    """).fetchall()
    
    if recipe_stats:
        print("\n  Recipes with multiple entries in staging:")
        print("  Recipe Name | Total Rows | Unique Ingredients | Batches | Marked Dupes | Latest Version")
        print("  " + "-" * 85)
        for stat in recipe_stats[:10]:
            print(f"  {stat[0][:30]:30} | {stat[1]:10} | {stat[2]:18} | {stat[3]:7} | {stat[4]:12} | {stat[5]:14}")
    
    # 3. Check for split recipe issues
    print("\n3. Potential Split Recipe Issues:")
    
    # Look for ingredients marked as prep recipes used in other recipes
    prep_usage = cursor.execute("""
        SELECT 
            ingredient_source_recipe_name,
            COUNT(DISTINCT recipe_name) as used_in_recipes,
            COUNT(*) as total_uses
        FROM stg_csv_recipes
        WHERE used_as_ingredient = 1
        AND ingredient_source_recipe_name IS NOT NULL
        GROUP BY ingredient_source_recipe_name
        ORDER BY total_uses DESC
        LIMIT 10
    """).fetchall()
    
    if prep_usage:
        print("\n  Prep recipes and their usage:")
        print("  Prep Recipe | Used in # Recipes | Total Uses")
        print("  " + "-" * 50)
        for prep in prep_usage:
            print(f"  {prep[0][:30]:30} | {prep[1]:17} | {prep[2]:10}")
    
    # 4. Check batch information
    print("\n4. Import Batch Information:")
    
    batches = cursor.execute("""
        SELECT 
            import_batch_id,
            COUNT(*) as total_records,
            COUNT(DISTINCT recipe_name) as unique_recipes,
            MIN(imported_at) as import_time
        FROM stg_csv_recipes
        GROUP BY import_batch_id
        ORDER BY import_time DESC
        LIMIT 5
    """).fetchall()
    
    if batches:
        print("\n  Recent import batches:")
        print("  Batch ID | Total Records | Unique Recipes | Import Time")
        print("  " + "-" * 65)
        for batch in batches:
            print(f"  {batch[0]} | {batch[1]:13} | {batch[2]:14} | {batch[3]}")
    
    # 5. Check for comma parsing issues
    print("\n5. Ingredient Name Parsing Issues:")
    
    comma_patterns = cursor.execute("""
        SELECT 
            SUBSTR(ingredient_name, 1, INSTR(ingredient_name || ',', ',') - 1) as first_part,
            COUNT(*) as count
        FROM stg_csv_recipes
        WHERE ingredient_name LIKE '%,%'
        GROUP BY first_part
        ORDER BY count DESC
        LIMIT 10
    """).fetchall()
    
    if comma_patterns:
        print("\n  Common patterns before first comma:")
        for pattern, count in comma_patterns:
            print(f"    '{pattern}': {count} occurrences")
    
    conn.close()

def main():
    db_path = "restaurant_calculator.db"
    analyze_duplicates(db_path)

if __name__ == "__main__":
    main()