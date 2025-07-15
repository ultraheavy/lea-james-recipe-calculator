#!/usr/bin/env python3
"""
Load parsed PDF recipes into staging table for review.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PDFRecipeLoader:
    """Load parsed PDF recipes into staging table."""
    
    def __init__(self, db_path='recipe_cost_app.db'):
        self.db_path = db_path
        
    def load_recipes(self, json_path: str) -> int:
        """Load recipes from JSON file into staging table."""
        # Read parsed recipes
        with open(json_path, 'r', encoding='utf-8') as f:
            recipes = json.load(f)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing staging data (optional - comment out to append)
        cursor.execute("DELETE FROM stg_pdf_recipes")
        logger.info("Cleared existing staging data")
        
        total_rows = 0
        recipes_with_issues = []
        
        try:
            for recipe_data in recipes:
                recipe_name = recipe_data['metadata'].get('recipe_name', 'Unknown')
                recipe_prefix = recipe_data['metadata'].get('prefix')
                is_prep_recipe = recipe_data['metadata'].get('is_prep_recipe', False)
                source_file = recipe_data['source_file']
                
                # Process each ingredient
                ingredients = recipe_data.get('ingredients', [])
                
                if not ingredients:
                    logger.warning(f"No ingredients found for recipe: {recipe_name}")
                    recipes_with_issues.append(recipe_name)
                
                for ingredient in ingredients:
                    # Determine if needs review
                    needs_review = self._needs_review(ingredient)
                    
                    # Insert row
                    cursor.execute("""
                        INSERT INTO stg_pdf_recipes (
                            recipe_name, recipe_prefix, ingredient_name,
                            quantity, unit, cost, is_prep_recipe,
                            source_file, source_text, needs_review
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        recipe_name,
                        recipe_prefix,
                        ingredient.get('ingredient_name', ''),
                        ingredient.get('quantity'),
                        ingredient.get('unit'),
                        ingredient.get('cost'),
                        is_prep_recipe,
                        source_file,
                        ingredient.get('raw_line', ''),
                        needs_review
                    ))
                    
                    total_rows += 1
            
            conn.commit()
            logger.info(f"Successfully loaded {total_rows} ingredient rows")
            
            if recipes_with_issues:
                logger.warning(f"Recipes with no ingredients: {', '.join(recipes_with_issues)}")
            
            # Summary statistics
            self._print_summary(cursor)
            
        except Exception as e:
            logger.error(f"Error loading recipes: {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()
        
        return total_rows
    
    def _needs_review(self, ingredient: dict) -> bool:
        """Determine if an ingredient needs review."""
        # Check for missing or zero cost
        cost = ingredient.get('cost')
        if not cost or cost == '0' or cost == '0.00':
            return True
        
        # Check for missing quantity or unit
        if not ingredient.get('quantity') or not ingredient.get('unit'):
            return True
        
        # Check for suspicious ingredient names
        name = ingredient.get('ingredient_name', '')
        if not name or len(name) < 3:
            return True
        
        # Check if name looks like a cost or quantity
        if name.startswith('$') or name.replace('.', '').isdigit():
            return True
        
        return False
    
    def _print_summary(self, cursor):
        """Print summary statistics."""
        # Total recipes
        cursor.execute("SELECT COUNT(DISTINCT recipe_name) FROM stg_pdf_recipes")
        total_recipes = cursor.fetchone()[0]
        
        # Total ingredients
        cursor.execute("SELECT COUNT(*) FROM stg_pdf_recipes")
        total_ingredients = cursor.fetchone()[0]
        
        # Needs review
        cursor.execute("SELECT COUNT(*) FROM stg_pdf_recipes WHERE needs_review = 1")
        needs_review = cursor.fetchone()[0]
        
        # Prep recipes
        cursor.execute("SELECT COUNT(DISTINCT recipe_name) FROM stg_pdf_recipes WHERE is_prep_recipe = 1")
        prep_recipes = cursor.fetchone()[0]
        
        # Missing costs
        cursor.execute("SELECT COUNT(*) FROM stg_pdf_recipes WHERE cost IS NULL OR cost = '' OR cost = '0' OR cost = '0.00'")
        missing_costs = cursor.fetchone()[0]
        
        print("\n" + "=" * 60)
        print("STAGING TABLE SUMMARY")
        print("=" * 60)
        print(f"Total recipes loaded: {total_recipes}")
        print(f"Total ingredient rows: {total_ingredients}")
        print(f"Rows needing review: {needs_review} ({needs_review/total_ingredients*100:.1f}%)")
        print(f"Prep recipes: {prep_recipes}")
        print(f"Missing/zero costs: {missing_costs}")
        print("=" * 60)


def main():
    """Main entry point."""
    # Path to parsed recipes JSON
    json_path = "/Users/ndrfn/Dropbox/001-Projects/Claude_projects/python_we4b_recipe_app/LJ_Test_Doca/reference/LJ_DATA_Ref/updated_recipes_csv_pdf/parsed_recipes.json"
    
    if not Path(json_path).exists():
        logger.error(f"JSON file not found: {json_path}")
        return
    
    loader = PDFRecipeLoader()
    
    try:
        rows_loaded = loader.load_recipes(json_path)
        print(f"\n✅ Successfully loaded {rows_loaded} ingredient rows into staging table")
    except Exception as e:
        print(f"\n❌ Error loading recipes: {str(e)}")
        raise


if __name__ == "__main__":
    main()