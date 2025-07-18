#!/usr/bin/env python3
"""
Comprehensive fix for recipe loader issues:
1. Fix ingredient name parsing (comma issues)  
2. Fix duplicate detection logic
3. Properly handle prep recipes
4. Clean and reload data
"""

import sqlite3
import os
import sys
from datetime import datetime
from csv_recipe_loader import CSVRecipeLoaderV2

class RecipeLoaderFixer:
    def __init__(self, db_path="restaurant_calculator.db"):
        self.db_path = db_path
        
    def analyze_issues(self):
        """Analyze current data issues"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        print("=== Current Data Analysis ===\n")
        
        # 1. Total records
        total = cursor.execute("SELECT COUNT(*) FROM stg_csv_recipes").fetchone()[0]
        print(f"Total staging records: {total}")
        
        # 2. Recipes marked as duplicates
        dup_recipes = cursor.execute("""
            SELECT recipe_name, COUNT(*) as cnt
            FROM stg_csv_recipes
            WHERE is_duplicate = 1
            GROUP BY recipe_name
            ORDER BY cnt DESC
            LIMIT 5
        """).fetchall()
        
        if dup_recipes:
            print("\nRecipes incorrectly marked as duplicates:")
            for recipe, count in dup_recipes:
                print(f"  {recipe}: {count} ingredients marked as duplicate")
        
        # 3. Category extraction issues
        category_counts = cursor.execute("""
            SELECT 
                CASE 
                    WHEN category IS NULL THEN 'No Category'
                    WHEN category = ingredient_name THEN 'Same as Ingredient'
                    ELSE 'Has Category'
                END as category_status,
                COUNT(*) as count
            FROM stg_csv_recipes
            GROUP BY category_status
        """).fetchall()
        
        print("\nCategory extraction status:")
        for status, count in category_counts:
            print(f"  {status}: {count}")
        
        # 4. Sample ingredient parsing issues
        samples = cursor.execute("""
            SELECT ingredient_name, category
            FROM stg_csv_recipes
            WHERE ingredient_name LIKE '%,%'
            LIMIT 5
        """).fetchall()
        
        if samples:
            print("\nSample ingredients with commas:")
            for ing, cat in samples:
                print(f"  Ingredient: {ing}")
                print(f"  Category: {cat}\n")
        
        conn.close()
    
    def fix_duplicate_flags(self):
        """Fix the incorrect duplicate flagging"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        print("\n=== Fixing Duplicate Flags ===")
        
        # First, reset all duplicate flags
        cursor.execute("""
            UPDATE stg_csv_recipes
            SET is_duplicate = 0,
                duplicate_of_recipe = NULL
        """)
        reset_count = cursor.rowcount
        print(f"Reset {reset_count} duplicate flags")
        
        # Now properly identify duplicates within the staging table
        # (same recipe imported multiple times in different batches)
        cursor.execute("""
            WITH recipe_first_import AS (
                SELECT recipe_name, MIN(imported_at) as first_import
                FROM stg_csv_recipes
                GROUP BY recipe_name
            )
            UPDATE stg_csv_recipes
            SET is_duplicate = 1
            WHERE EXISTS (
                SELECT 1 
                FROM recipe_first_import rfi
                WHERE rfi.recipe_name = stg_csv_recipes.recipe_name
                AND stg_csv_recipes.imported_at > rfi.first_import
            )
        """)
        
        dup_count = cursor.rowcount
        print(f"Properly marked {dup_count} records as duplicates")
        
        conn.commit()
        conn.close()
    
    def create_improved_loader(self):
        """Create a custom loader with all fixes"""
        # The CSVRecipeLoaderV2 already has our parsing fixes
        # We just need to ensure check_duplicates doesn't mess things up
        loader = CSVRecipeLoaderV2(self.db_path)
        
        # Override the problematic check_duplicates method
        def fixed_check_duplicates(self):
            """Fixed version that doesn't mark all ingredients as duplicates"""
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                # Only update a flag to indicate the recipe exists in main table
                # Don't mark as duplicate - that's for staging duplicates
                cursor.execute("""
                    UPDATE stg_csv_recipes
                    SET review_notes = 'Recipe already exists in main database'
                    WHERE recipe_name IN (
                        SELECT DISTINCT recipe_name FROM recipes
                    )
                    AND review_notes IS NULL
                """)
                
                updated = cursor.rowcount
                if updated > 0:
                    print(f"Flagged {updated} records for recipes that already exist")
                
                conn.commit()
            finally:
                conn.close()
        
        # Replace the method
        loader.check_duplicates = lambda: fixed_check_duplicates(loader)
        
        return loader
    
    def reload_clean(self):
        """Clean reload with all fixes"""
        print("\n=== Clean Reload with Fixes ===")
        
        # Create backup first
        backup_name = f"backup_before_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        print(f"Creating backup: {backup_name}")
        os.system(f"cp {self.db_path} {backup_name}")
        
        # Get improved loader
        loader = self.create_improved_loader()
        
        # Clear staging
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM stg_csv_recipes")
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        print(f"Cleared {deleted} existing staging records")
        
        # Reload
        print("\nReloading CSV files...")
        results = loader.load_to_staging(clear_existing=False)
        
        print(f"\nReload Results:")
        print(f"  Total files: {results['total_files']}")
        print(f"  Successful: {results['successful_files']}")
        print(f"  Failed: {results['failed_files']}")
        print(f"  Total ingredients: {results['total_ingredients']}")
        
        # Run the fixed duplicate check
        loader.check_duplicates()
        
        # Check prep dependencies
        loader.check_prep_dependencies()
        
        return results
    
    def verify_fixes(self):
        """Verify all fixes were applied"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        print("\n=== Verification ===")
        
        # 1. Check category extraction
        category_sample = cursor.execute("""
            SELECT ingredient_name, category, COUNT(*) as count
            FROM stg_csv_recipes
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
            LIMIT 5
        """).fetchall()
        
        if category_sample:
            print("\nTop categories extracted:")
            for ing, cat, count in category_sample:
                print(f"  {cat}: {count} ingredients")
        
        # 2. Check duplicate status
        dup_summary = cursor.execute("""
            SELECT 
                is_duplicate,
                COUNT(DISTINCT recipe_name) as recipes,
                COUNT(*) as total_rows
            FROM stg_csv_recipes
            GROUP BY is_duplicate
        """).fetchall()
        
        print("\nDuplicate flag summary:")
        for is_dup, recipes, rows in dup_summary:
            status = "Duplicate" if is_dup else "Not Duplicate"
            print(f"  {status}: {recipes} recipes, {rows} total rows")
        
        # 3. Check specific recipe
        alabama_check = cursor.execute("""
            SELECT ingredient_name, category, is_duplicate
            FROM stg_csv_recipes
            WHERE recipe_name = 'Alabama White BBQ'
            ORDER BY row_number
        """).fetchall()
        
        if alabama_check:
            print("\nAlabama White BBQ ingredients (should NOT be marked as duplicates):")
            for ing, cat, is_dup in alabama_check:
                dup_flag = "DUP" if is_dup else "OK"
                print(f"  [{dup_flag}] {ing} (Category: {cat})")
        
        conn.close()

def main():
    fixer = RecipeLoaderFixer()
    
    print("Recipe Loader Comprehensive Fix")
    print("=" * 50)
    
    # Analyze current state
    fixer.analyze_issues()
    
    # Ask for confirmation
    response = input("\nProceed with fixes? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return
    
    # Apply fixes
    fixer.fix_duplicate_flags()
    
    # Ask about full reload
    response = input("\nPerform full reload with fixed parser? (yes/no): ")
    if response.lower() == 'yes':
        fixer.reload_clean()
    
    # Verify
    fixer.verify_fixes()
    
    print("\nDone! Review the data in the staging admin interface.")
    print("URL: http://localhost:8888/admin/recipe-csv-staging/")

if __name__ == "__main__":
    main()