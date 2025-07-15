#!/usr/bin/env python3
"""
CSV Recipe Loader
Parses CSV recipe exports and loads them into staging table
"""

import os
import csv
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import re
import uuid

class CSVRecipeLoader:
    def __init__(self, db_path: str = "restaurant_calculator.db", csv_dir: str = None):
        self.db_path = db_path
        self.csv_dir = csv_dir or "reference/LJ_DATA_Ref/updated_recipes_csv_pdf/csv"
        self.prep_recipe_keywords = ['sauce', 'roux', 'marinade', 'prep', 'dressing', 'blend', 'mix']
        
    def init_database(self):
        """Initialize the staging table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Read and execute the SQL file
        sql_file = "migrations/create_staging_csv_recipes_table.sql"
        if os.path.exists(sql_file):
            with open(sql_file, 'r') as f:
                sql_script = f.read()
            cursor.executescript(sql_script)
            conn.commit()
        
        conn.close()
    
    def parse_csv_file(self, filepath: str) -> Dict:
        """Parse a single CSV recipe file"""
        recipe_data = {
            'recipe_name': None,
            'ingredients': [],
            'metadata': {},
            'errors': []
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                if len(rows) < 11:
                    recipe_data['errors'].append("File has insufficient rows")
                    return recipe_data
                
                # Extract recipe name from row 2
                # Check both column 0 and column 1 for recipe name
                recipe_name = None
                if len(rows) > 1:
                    if rows[1][0] and rows[1][0].strip() not in ["Prep Recipe Name", "Recipe Name"]:
                        recipe_name = rows[1][0].strip()
                    elif len(rows[1]) > 1 and rows[1][1] and rows[1][1].strip():
                        recipe_name = rows[1][1].strip()
                
                if not recipe_name:
                    recipe_data['errors'].append("Recipe name not found")
                    return recipe_data
                
                recipe_data['recipe_name'] = recipe_name
                
                # Extract metadata
                # Row 5: Type, Portion, Portion Size, etc.
                if len(rows) > 4:
                    recipe_data['metadata']['type'] = rows[4][0] if len(rows[4]) > 0 else None
                    recipe_data['metadata']['portion'] = rows[4][1] if len(rows[4]) > 1 else None
                    recipe_data['metadata']['portion_size'] = rows[4][2] if len(rows[4]) > 2 else None
                    recipe_data['metadata']['batch_size'] = rows[4][3] if len(rows[4]) > 3 else None
                    recipe_data['metadata']['shelf_life'] = rows[4][4] if len(rows[4]) > 4 else None
                
                # Parse ingredients starting from row 11
                for row_num, row in enumerate(rows[10:], start=11):
                    if len(row) < 6:
                        continue
                    
                    ingredient_name = row[0].strip() if row[0] else None
                    if not ingredient_name or ingredient_name == "Ingredient":
                        continue
                    
                    ingredient = {
                        'name': ingredient_name,
                        'type': row[1] if len(row) > 1 else None,
                        'measurement': row[2] if len(row) > 2 else None,
                        'yield': row[3] if len(row) > 3 else None,
                        'usable_yield': row[4] if len(row) > 4 else None,
                        'cost': row[5] if len(row) > 5 else None,
                        'row_number': row_num
                    }
                    
                    # Parse quantity and unit from measurement
                    quantity, unit = self._parse_measurement(ingredient['measurement'])
                    ingredient['quantity'] = quantity
                    ingredient['unit'] = self._normalize_unit(unit)
                    
                    # Determine category from ingredient name
                    ingredient['category'] = self._determine_category(ingredient['name'])
                    
                    # Check if ingredient type is PrepRecipe
                    if ingredient['type'] and ingredient['type'].lower() == 'preprecipe':
                        ingredient['is_prep_ingredient'] = True
                    else:
                        ingredient['is_prep_ingredient'] = False
                    
                    recipe_data['ingredients'].append(ingredient)
                
                # Check if it's a prep recipe
                recipe_data['is_prep_recipe'] = self._is_prep_recipe(recipe_name)
                
        except Exception as e:
            recipe_data['errors'].append(f"Error parsing file: {str(e)}")
        
        return recipe_data
    
    def _parse_measurement(self, measurement: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse measurement string into quantity and unit"""
        if not measurement:
            return None, None
        
        measurement = measurement.strip()
        
        # Handle common patterns
        patterns = [
            (r'^(\d+\.?\d*)\s*(.+)$', lambda m: (m.group(1), m.group(2))),  # "3 gallon"
            (r'^(\d+)\s+(\d+/\d+)\s*(.+)$', lambda m: (f"{m.group(1)} {m.group(2)}", m.group(3))),  # "1 1/2 cup"
            (r'^(\d+/\d+)\s*(.+)$', lambda m: (m.group(1), m.group(2))),  # "1/2 cup"
        ]
        
        for pattern, extractor in patterns:
            match = re.match(pattern, measurement)
            if match:
                return extractor(match)
        
        # If no pattern matches, return the whole thing as quantity
        return measurement, None
    
    def _normalize_unit(self, unit: Optional[str]) -> Optional[str]:
        """Normalize common unit variations"""
        if not unit:
            return unit
        
        unit_lower = unit.lower().strip()
        
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
        
        return unit_mappings.get(unit_lower, unit)
    
    def _determine_category(self, ingredient_name: str) -> Optional[str]:
        """Determine category from ingredient name"""
        if not ingredient_name:
            return None
        
        name_lower = ingredient_name.lower()
        
        # Extract category from comma-separated format
        if ',' in ingredient_name:
            parts = ingredient_name.split(',')
            if parts:
                return parts[0].strip()
        
        # Fallback category detection
        categories = {
            'dairy': ['milk', 'cream', 'cheese', 'butter'],
            'dry goods': ['salt', 'pepper', 'flour', 'sugar'],
            'protein': ['chicken', 'beef', 'pork', 'fish'],
            'produce': ['onion', 'garlic', 'tomato', 'lettuce'],
            'sauce': ['sauce', 'dressing', 'marinade']
        }
        
        for category, keywords in categories.items():
            if any(keyword in name_lower for keyword in keywords):
                return category.title()
        
        return None
    
    def _is_prep_recipe(self, recipe_name: str) -> bool:
        """Determine if recipe is a prep recipe"""
        if not recipe_name:
            return False
        
        name_lower = recipe_name.lower()
        return any(keyword in name_lower for keyword in self.prep_recipe_keywords)
    
    def load_to_staging(self, clear_existing: bool = False) -> Dict[str, Any]:
        """Load all CSV files to staging table"""
        results = {
            'total_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'total_ingredients': 0,
            'errors': [],
            'batch_id': datetime.now().strftime('%Y%m%d_%H%M%S')
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Clear existing data if requested
            if clear_existing:
                cursor.execute("DELETE FROM stg_csv_recipes")
                conn.commit()
            
            # Get all CSV files
            csv_files = [f for f in os.listdir(self.csv_dir) if f.endswith('.csv')]
            results['total_files'] = len(csv_files)
            
            for csv_file in csv_files:
                filepath = os.path.join(self.csv_dir, csv_file)
                
                # Parse the file
                recipe_data = self.parse_csv_file(filepath)
                
                if recipe_data['errors']:
                    results['failed_files'] += 1
                    results['errors'].append({
                        'file': csv_file,
                        'errors': recipe_data['errors']
                    })
                    continue
                
                # Insert ingredients into staging
                for ingredient in recipe_data['ingredients']:
                    validation_errors = self._validate_ingredient(ingredient)
                    needs_review = bool(validation_errors)
                    
                    # Determine if this ingredient is a prep recipe
                    used_as_ingredient = ingredient.get('is_prep_ingredient', False)
                    ingredient_source_type = 'recipe' if used_as_ingredient else 'inventory'
                    ingredient_source_recipe_name = ingredient['name'] if used_as_ingredient else None
                    
                    cursor.execute("""
                        INSERT INTO stg_csv_recipes (
                            recipe_name, ingredient_name, quantity, unit, cost,
                            category, is_prep_recipe, source_filename, row_number,
                            raw_data, needs_review, validation_errors, import_batch_id,
                            used_as_ingredient, ingredient_source_type, ingredient_source_recipe_name
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        recipe_data['recipe_name'],
                        ingredient['name'],
                        ingredient['quantity'],
                        ingredient['unit'],
                        self._clean_cost(ingredient['cost']),
                        ingredient['category'],
                        recipe_data['is_prep_recipe'],
                        csv_file,
                        ingredient['row_number'],
                        str(ingredient),
                        needs_review,
                        ', '.join(validation_errors) if validation_errors else None,
                        results['batch_id'],
                        used_as_ingredient,
                        ingredient_source_type,
                        ingredient_source_recipe_name
                    ))
                    
                    results['total_ingredients'] += 1
                
                results['successful_files'] += 1
                conn.commit()
                
        except Exception as e:
            conn.rollback()
            results['errors'].append({'file': 'general', 'errors': [str(e)]})
        finally:
            conn.close()
        
        return results
    
    def _clean_cost(self, cost: str) -> Optional[str]:
        """Clean cost string to numeric value"""
        if not cost:
            return None
        
        # Remove dollar signs and commas
        cost = cost.replace('$', '').replace(',', '')
        
        # Extract numeric value
        match = re.search(r'(\d+\.?\d*)', cost)
        if match:
            # Round to 2 decimal places
            try:
                return str(round(float(match.group(1)), 2))
            except:
                return match.group(1)
        
        return None
    
    def _validate_ingredient(self, ingredient: Dict) -> List[str]:
        """Validate ingredient data and return list of errors"""
        errors = []
        
        if not ingredient.get('name'):
            errors.append("Missing ingredient name")
        
        if not ingredient.get('quantity'):
            errors.append("Missing quantity")
        
        if not ingredient.get('unit'):
            errors.append("Missing unit")
        
        if not ingredient.get('cost'):
            errors.append("Missing cost")
        
        # Validate cost percentage (if we can calculate it)
        cost_str = self._clean_cost(ingredient.get('cost'))
        if cost_str:
            try:
                cost = float(cost_str)
                # Add any cost validation logic here
            except ValueError:
                errors.append("Invalid cost format")
        
        return errors
    
    def check_duplicates(self):
        """Check for duplicate recipes in staging"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Find recipes that already exist in main recipes table
            cursor.execute("""
                UPDATE stg_csv_recipes
                SET is_duplicate = 1,
                    duplicate_of_recipe = (
                        SELECT recipe_name FROM recipes 
                        WHERE recipes.recipe_name = stg_csv_recipes.recipe_name
                        LIMIT 1
                    )
                WHERE recipe_name IN (
                    SELECT recipe_name FROM recipes
                )
            """)
            
            conn.commit()
        finally:
            conn.close()
    
    def check_prep_dependencies(self):
        """Check for missing prep recipe dependencies"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Find ingredients that are prep recipes but don't exist in system
            cursor.execute("""
                WITH prep_ingredients AS (
                    SELECT DISTINCT ingredient_source_recipe_name
                    FROM stg_csv_recipes
                    WHERE used_as_ingredient = 1 
                    AND ingredient_source_type = 'recipe'
                    AND ingredient_source_recipe_name IS NOT NULL
                ),
                existing_recipes AS (
                    SELECT recipe_name FROM recipes
                    UNION
                    SELECT DISTINCT recipe_name FROM stg_csv_recipes WHERE review_status = 'approved'
                )
                UPDATE stg_csv_recipes
                SET has_prep_dependencies = 1,
                    needs_review = 1,
                    validation_errors = CASE 
                        WHEN validation_errors IS NULL THEN 'Missing prep recipe dependency'
                        ELSE validation_errors || ', Missing prep recipe dependency'
                    END
                WHERE used_as_ingredient = 1
                AND ingredient_source_recipe_name NOT IN (SELECT recipe_name FROM existing_recipes)
            """)
            
            conn.commit()
        finally:
            conn.close()

if __name__ == "__main__":
    # Initialize and run loader
    loader = CSVRecipeLoader()
    loader.init_database()
    
    print("Loading CSV recipes to staging...")
    results = loader.load_to_staging(clear_existing=True)
    
    print(f"\nLoad Results:")
    print(f"Total files: {results['total_files']}")
    print(f"Successful: {results['successful_files']}")
    print(f"Failed: {results['failed_files']}")
    print(f"Total ingredients: {results['total_ingredients']}")
    print(f"Batch ID: {results['batch_id']}")
    
    if results['errors']:
        print("\nErrors:")
        for error in results['errors']:
            print(f"  {error['file']}: {error['errors']}")
    
    # Check for duplicates
    print("\nChecking for duplicates...")
    loader.check_duplicates()
    
    # Check for prep recipe dependencies
    print("Checking for prep recipe dependencies...")
    loader.check_prep_dependencies()
    
    print("Done!")