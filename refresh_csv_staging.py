#!/usr/bin/env python3
"""
Refresh CSV Recipe Staging Data
Clears existing staging data and reloads from CSV files
"""

import sqlite3
from csv_recipe_loader import CSVRecipeLoaderV2
from datetime import datetime

def refresh_staging():
    """Clear and reload staging data"""
    print("="*60)
    print("CSV Recipe Staging Refresh")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Check current state
    conn = sqlite3.connect("restaurant_calculator.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) as total, 
               COUNT(DISTINCT recipe_name) as recipes,
               COUNT(DISTINCT import_batch_id) as batches
        FROM stg_csv_recipes
    """)
    current = cursor.fetchone()
    
    if current[0] > 0:
        print(f"\nCurrent staging data:")
        print(f"  - {current[0]} total records")
        print(f"  - {current[1]} unique recipes")
        print(f"  - {current[2]} import batches")
    else:
        print("\nStaging table is currently empty")
    
    conn.close()
    
    # Initialize and run loader
    print("\nStarting fresh import...")
    print("-"*40)
    
    loader = CSVRecipeLoaderV2()
    loader.init_database()
    
    # Always clear existing data
    results = loader.load_to_staging(clear_existing=True)
    
    print("\n" + "="*60)
    print("REFRESH COMPLETE")
    print("="*60)
    
    print(f"\nSummary:")
    print(f"  - Loaded {results['successful_files']} recipes successfully")
    print(f"  - Skipped {results['skipped_files']} duplicate files")
    print(f"  - Failed to load {results['failed_files']} files")
    print(f"  - Total ingredients: {results['total_ingredients']}")
    print(f"  - New batch ID: {results['batch_id']}")
    
    if results['errors']:
        print("\nErrors encountered:")
        for error in results['errors']:
            print(f"  - {error['file']}: {error['errors']}")
    
    # Check for issues
    print("\nChecking for duplicates in main database...")
    loader.check_duplicates()
    
    print("Checking for prep recipe dependencies...")
    loader.check_prep_dependencies()
    
    # Final statistics
    conn = sqlite3.connect("restaurant_calculator.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN needs_review = 1 THEN 1 END) as needs_review,
            COUNT(CASE WHEN is_duplicate = 1 THEN 1 END) as duplicates,
            COUNT(CASE WHEN has_prep_dependencies = 1 THEN 1 END) as missing_deps
        FROM stg_csv_recipes
        WHERE is_latest_version = 1
    """)
    
    issues = cursor.fetchone()
    
    if any(issues):
        print("\nItems requiring attention:")
        if issues[0]:
            print(f"  - {issues[0]} items need review")
        if issues[1]:
            print(f"  - {issues[1]} recipes already exist in main database")
        if issues[2]:
            print(f"  - {issues[2]} items have missing prep recipe dependencies")
    else:
        print("\n✅ All items loaded successfully with no issues!")
    
    conn.close()
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nAccess the admin interface at: http://localhost:8888/admin/recipe-csv-staging/")

if __name__ == "__main__":
    refresh_staging()