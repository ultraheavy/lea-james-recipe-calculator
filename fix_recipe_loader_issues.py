#!/usr/bin/env python3
"""
Fix Recipe Loader Issues
- Fixes comma-separated ingredient names
- Removes duplicates
- Reloads data with corrected parser
"""

import sqlite3
import os
from csv_recipe_loader import CSVRecipeLoaderV2

def analyze_current_issues(db_path):
    """Analyze current staging data issues"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== Current Data Analysis ===")
    
    # Check total records
    total = cursor.execute("SELECT COUNT(*) FROM stg_csv_recipes").fetchone()[0]
    print(f"Total staging records: {total}")
    
    # Check recipes with comma issues
    comma_issues = cursor.execute("""
        SELECT COUNT(DISTINCT recipe_name) 
        FROM stg_csv_recipes 
        WHERE ingredient_name LIKE '%,%'
    """).fetchone()[0]
    print(f"Recipes with comma-separated ingredients: {comma_issues}")
    
    # Check duplicate analysis
    duplicates = cursor.execute("""
        SELECT recipe_name, COUNT(*) as cnt, COUNT(DISTINCT ingredient_name) as unique_ingredients
        FROM stg_csv_recipes
        GROUP BY recipe_name
        HAVING COUNT(*) > 20
        ORDER BY cnt DESC
        LIMIT 5
    """).fetchall()
    
    if duplicates:
        print("\nRecipes with many entries:")
        for recipe, count, unique_count in duplicates:
            print(f"  {recipe}: {count} rows, {unique_count} unique ingredients")
    
    # Check category extraction issues
    category_issues = cursor.execute("""
        SELECT ingredient_name, category, COUNT(*) as cnt
        FROM stg_csv_recipes
        WHERE category IS NOT NULL
        GROUP BY ingredient_name, category
        ORDER BY cnt DESC
        LIMIT 5
    """).fetchall()
    
    if category_issues:
        print("\nIngredients with extracted categories:")
        for ing, cat, cnt in category_issues:
            print(f"  {ing} | Category: {cat} | Count: {cnt}")
    
    conn.close()

def fix_and_reload(db_path):
    """Clear staging and reload with fixed parser"""
    print("\n=== Fixing and Reloading Data ===")
    
    # Initialize loader with fixed parser
    loader = CSVRecipeLoaderV2(db_path)
    
    # Initialize database (ensure tables exist)
    loader.init_database()
    
    # Clear existing staging data
    print("Clearing existing staging data...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM stg_csv_recipes")
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    print(f"Deleted {deleted} existing records")
    
    # Reload with fixed parser
    print("\nReloading CSV files with fixed parser...")
    results = loader.load_to_staging(clear_existing=False)  # Already cleared above
    
    print(f"\nReload Results:")
    print(f"  Total unique recipes: {results['total_files']}")
    print(f"  Duplicate files skipped: {results['skipped_files']}")
    print(f"  Successfully loaded: {results['successful_files']}")
    print(f"  Failed: {results['failed_files']}")
    print(f"  Total ingredients: {results['total_ingredients']}")
    print(f"  Batch ID: {results['batch_id']}")
    
    if results['errors']:
        print("\nErrors encountered:")
        for error in results['errors'][:5]:
            print(f"  {error['file']}: {error['errors']}")
    
    # Check for duplicates and dependencies
    print("\nChecking for duplicates in main database...")
    loader.check_duplicates()
    
    print("Checking for prep recipe dependencies...")
    loader.check_prep_dependencies()
    
    return results

def verify_fixes(db_path):
    """Verify the fixes were applied correctly"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n=== Verification ===")
    
    # Check if comma issues are resolved
    comma_issues = cursor.execute("""
        SELECT COUNT(*) 
        FROM stg_csv_recipes 
        WHERE category IS NOT NULL
    """).fetchone()[0]
    print(f"Records with extracted categories: {comma_issues}")
    
    # Sample corrected ingredients
    samples = cursor.execute("""
        SELECT recipe_name, ingredient_name, category
        FROM stg_csv_recipes
        WHERE ingredient_name LIKE '%,%'
        LIMIT 5
    """).fetchall()
    
    if samples:
        print("\nSample ingredients with commas (should show full name, no category):")
        for recipe, ing, cat in samples:
            print(f"  Recipe: {recipe}")
            print(f"    Ingredient: {ing}")
            print(f"    Category: {cat}")
    
    # Check ingredient counts per recipe
    recipe_counts = cursor.execute("""
        SELECT recipe_name, COUNT(*) as ingredient_count
        FROM stg_csv_recipes
        WHERE is_latest_version = 1
        GROUP BY recipe_name
        ORDER BY ingredient_count DESC
        LIMIT 5
    """).fetchall()
    
    print("\nTop recipes by ingredient count:")
    for recipe, count in recipe_counts:
        print(f"  {recipe}: {count} ingredients")
    
    conn.close()

def main():
    db_path = "restaurant_calculator.db"
    
    print("Recipe Loader Issue Fixer")
    print("=" * 50)
    
    # Analyze current issues
    analyze_current_issues(db_path)
    
    # Ask for confirmation
    response = input("\nProceed with fixing and reloading? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return
    
    # Fix and reload
    results = fix_and_reload(db_path)
    
    # Verify fixes
    verify_fixes(db_path)
    
    print("\nDone! You can now review the data in the staging admin interface.")

if __name__ == "__main__":
    main()