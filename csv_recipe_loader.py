#!/usr/bin/env python3
"""
CSV Recipe Loader V2 - with duplicate file handling
Pre-checks for duplicate files and only loads the most recent version
"""

import os
import csv
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import re
import uuid

class CSVRecipeLoaderV2:
    def __init__(self, db_path: str = "restaurant_calculator.db", csv_dir: str = None):
        self.db_path = db_path
        self.csv_dir = csv_dir or "reference/LJ_DATA_Ref/updated_recipes_csv_pdf/csv"
        self.prep_recipe_keywords = ['sauce', 'roux', 'marinade', 'prep', 'dressing', 'blend', 'mix']
        
    def analyze_csv_files(self) -> Dict[str, List[Dict]]:
        """Analyze CSV files and group by recipe name"""
        recipe_files = {}
        
        # Get all CSV files
        csv_files = [f for f in os.listdir(self.csv_dir) if f.endswith('.csv')]
        
        for csv_file in csv_files:
            # Parse filename to extract recipe name and timestamp
            # Format: "Recipe Name_Restaurant_YYYYMMDD_HHMMSS.csv"
            match = re.match(r'^(.+?)_[^_]+_(\d{8})_(\d{6})\.csv$', csv_file)
            
            if match:
                recipe_name = match.group(1).strip()
                date_str = match.group(2)
                time_str = match.group(3)
                timestamp = f"{date_str}_{time_str}"
                
                # Normalize recipe name (remove extra spaces, standardize case)
                recipe_key = re.sub(r'\s+', ' ', recipe_name.lower().strip())
                
                file_info = {
                    'filename': csv_file,
                    'recipe_name': recipe_name,
                    'timestamp': timestamp,
                    'filepath': os.path.join(self.csv_dir, csv_file)
                }
                
                if recipe_key not in recipe_files:
                    recipe_files[recipe_key] = []
                recipe_files[recipe_key].append(file_info)
            else:
                print(f"Warning: Could not parse filename: {csv_file}")
        
        # Sort each group by timestamp (most recent first)
        for recipe_key in recipe_files:
            recipe_files[recipe_key].sort(key=lambda x: x['timestamp'], reverse=True)
        
        return recipe_files
    
    def select_files_to_load(self, recipe_files: Dict[str, List[Dict]]) -> List[Dict]:
        """Select which files to load (most recent version of each recipe)"""
        files_to_load = []
        duplicate_report = []
        
        for recipe_key, versions in recipe_files.items():
            if len(versions) > 1:
                # We have duplicates
                selected = versions[0]  # Most recent
                skipped = versions[1:]  # Older versions
                
                duplicate_report.append({
                    'recipe': selected['recipe_name'],
                    'selected': selected['filename'],
                    'skipped': [v['filename'] for v in skipped]
                })
            else:
                selected = versions[0]
            
            files_to_load.append(selected)
        
        # Print duplicate report
        if duplicate_report:
            print("\n=== Duplicate Files Found ===")
            print(f"Found {len(duplicate_report)} recipes with multiple versions")
            for dup in duplicate_report[:5]:  # Show first 5
                print(f"\nRecipe: {dup['recipe']}")
                print(f"  Selected: {dup['selected']}")
                print(f"  Skipped: {', '.join(dup['skipped'])}")
            if len(duplicate_report) > 5:
                print(f"\n... and {len(duplicate_report) - 5} more")
            print("="*40 + "\n")
        
        return files_to_load
    
    def init_database(self):
        """Initialize the staging table with new fields"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Add new fields if they don't exist
        try:
            cursor.execute("ALTER TABLE stg_csv_recipes ADD COLUMN source_timestamp TEXT")
        except:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE stg_csv_recipes ADD COLUMN is_latest_version BOOLEAN DEFAULT TRUE")
        except:
            pass  # Column already exists
        
        try:
            cursor.execute("ALTER TABLE stg_csv_recipes ADD COLUMN replaced_by_batch TEXT")
        except:
            pass  # Column already exists
        
        conn.commit()
        conn.close()
    
    def mark_old_versions(self, recipe_name: str, current_batch: str):
        """Mark older versions of a recipe as not latest"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Mark all previous versions as not latest
            cursor.execute("""
                UPDATE stg_csv_recipes
                SET is_latest_version = 0,
                    replaced_by_batch = ?
                WHERE recipe_name = ?
                AND import_batch_id != ?
                AND is_latest_version = 1
            """, (current_batch, recipe_name, current_batch))
            
            conn.commit()
        finally:
            conn.close()
    
    def parse_csv_file(self, file_info: Dict) -> Dict:
        """Parse a single CSV recipe file with metadata"""
        recipe_data = {
            'recipe_name': None,
            'ingredients': [],
            'metadata': {
                'source_timestamp': file_info['timestamp'],
                'source_filename': file_info['filename']
            },
            'errors': []
        }
        
        try:
            with open(file_info['filepath'], 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                if len(rows) < 11:
                    recipe_data['errors'].append("File has insufficient rows")
                    return recipe_data
                
                # Extract recipe name from row 2
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
                if len(rows) > 4:
                    recipe_data['metadata']['type'] = rows[4][0] if len(rows[4]) > 0 else None
                    recipe_data['metadata']['portion'] = rows[4][1] if len(rows[4]) > 1 else None
                    recipe_data['metadata']['portion_size'] = rows[4][2] if len(rows[4]) > 2 else None
                    recipe_data['metadata']['batch_size'] = rows[4][3] if len(rows[4]) > 3 else None
                    recipe_data['metadata']['shelf_life'] = rows[4][4] if len(rows[4]) > 4 else None
                
                # Parse ingredients
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
                    
                    # Parse quantity and unit
                    quantity, unit = self._parse_measurement(ingredient['measurement'])
                    ingredient['quantity'] = quantity
                    ingredient['unit'] = self._normalize_unit(unit)
                    
                    # Clean ingredient name and extract category
                    ingredient['name'], ingredient['category'] = self._parse_ingredient_name(ingredient['name'])
                    
                    # Check if ingredient is a prep recipe
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
    
    def _parse_ingredient_name(self, ingredient_name: str) -> Tuple[str, Optional[str]]:
        """Parse ingredient name and extract category if present"""
        if not ingredient_name:
            return ingredient_name, None
        
        # Check for comma-separated format: "Category, Item, Details"
        if ',' in ingredient_name:
            parts = [p.strip() for p in ingredient_name.split(',')]
            if len(parts) >= 2:
                category = parts[0]
                name = ', '.join(parts[1:])
                return name, category
        
        return ingredient_name, None
    
    def _parse_measurement(self, measurement: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse measurement string into quantity and unit"""
        if not measurement:
            return None, None
        
        measurement = measurement.strip()
        
        # Handle common patterns
        patterns = [
            (r'^(\d+\.?\d*)\s*(.+)$', lambda m: (m.group(1), m.group(2))),
            (r'^(\d+)\s+(\d+/\d+)\s*(.+)$', lambda m: (f"{m.group(1)} {m.group(2)}", m.group(3))),
            (r'^(\d+/\d+)\s*(.+)$', lambda m: (m.group(1), m.group(2))),
        ]
        
        for pattern, extractor in patterns:
            match = re.match(pattern, measurement)
            if match:
                return extractor(match)
        
        return measurement, None
    
    def _normalize_unit(self, unit: Optional[str]) -> Optional[str]:
        """Normalize common unit variations"""
        if not unit:
            return unit
        
        unit_lower = unit.lower().strip()
        
        unit_mappings = {
            'qt': 'quart', 'qts': 'quart', 'quarts': 'quart',
            'lb': 'pound', 'lbs': 'pound', 'pounds': 'pound',
            'oz': 'ounce', 'ozs': 'ounce', 'ounces': 'ounce',
            'gal': 'gallon', 'gallons': 'gallon',
            'tsp': 'teaspoon', 'tbsp': 'tablespoon',
            'c': 'cup', 'cups': 'cup',
            'g': 'gram', 'grams': 'gram',
            'kg': 'kilogram', 'kilograms': 'kilogram',
            'ml': 'milliliter', 'milliliters': 'milliliter',
            'l': 'liter', 'liters': 'liter',
            'ea': 'each', 'pc': 'piece', 'pcs': 'piece', 'pieces': 'piece'
        }
        
        return unit_mappings.get(unit_lower, unit)
    
    def _clean_cost(self, cost: str) -> Optional[str]:
        """Clean cost string to numeric value"""
        if not cost:
            return None
        
        cost = cost.replace('$', '').replace(',', '')
        
        match = re.search(r'(\d+\.?\d*)', cost)
        if match:
            try:
                return str(round(float(match.group(1)), 2))
            except:
                return match.group(1)
        
        return None
    
    def _is_prep_recipe(self, recipe_name: str) -> bool:
        """Determine if recipe is a prep recipe"""
        if not recipe_name:
            return False
        
        name_lower = recipe_name.lower()
        return any(keyword in name_lower for keyword in self.prep_recipe_keywords)
    
    def _validate_ingredient(self, ingredient: Dict) -> List[str]:
        """Validate ingredient data"""
        errors = []
        
        if not ingredient.get('name'):
            errors.append("Missing ingredient name")
        
        if not ingredient.get('quantity'):
            errors.append("Missing quantity")
        
        if not ingredient.get('unit'):
            errors.append("Missing unit")
        
        if not ingredient.get('cost'):
            errors.append("Missing cost")
        
        return errors
    
    def load_to_staging(self, clear_existing: bool = False) -> Dict[str, Any]:
        """Load CSV files to staging with duplicate handling"""
        results = {
            'total_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'skipped_files': 0,
            'total_ingredients': 0,
            'errors': [],
            'batch_id': datetime.now().strftime('%Y%m%d_%H%M%S')
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Clear existing data if requested
            if clear_existing:
                print("Clearing existing staging data...")
                cursor.execute("DELETE FROM stg_csv_recipes")
                deleted_count = cursor.rowcount
                conn.commit()
                print(f"Cleared {deleted_count} existing records")
            
            # Analyze files and select which to load
            print("Analyzing CSV files for duplicates...")
            recipe_files = self.analyze_csv_files()
            files_to_load = self.select_files_to_load(recipe_files)
            
            results['total_files'] = len(files_to_load)
            results['skipped_files'] = sum(len(versions) - 1 for versions in recipe_files.values() if len(versions) > 1)
            
            print(f"Loading {len(files_to_load)} unique recipes...")
            
            for file_info in files_to_load:
                # Parse the file
                recipe_data = self.parse_csv_file(file_info)
                
                if recipe_data['errors']:
                    results['failed_files'] += 1
                    results['errors'].append({
                        'file': file_info['filename'],
                        'errors': recipe_data['errors']
                    })
                    continue
                
                # Mark old versions as not latest
                self.mark_old_versions(recipe_data['recipe_name'], results['batch_id'])
                
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
                            category, is_prep_recipe, source_filename, source_timestamp,
                            row_number, raw_data, needs_review, validation_errors, 
                            import_batch_id, used_as_ingredient, ingredient_source_type, 
                            ingredient_source_recipe_name, is_latest_version
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        recipe_data['recipe_name'],
                        ingredient['name'],
                        ingredient['quantity'],
                        ingredient['unit'],
                        self._clean_cost(ingredient['cost']),
                        ingredient['category'],
                        recipe_data['is_prep_recipe'],
                        file_info['filename'],
                        file_info['timestamp'],
                        ingredient['row_number'],
                        str(ingredient),
                        needs_review,
                        ', '.join(validation_errors) if validation_errors else None,
                        results['batch_id'],
                        used_as_ingredient,
                        ingredient_source_type,
                        ingredient_source_recipe_name,
                        True  # is_latest_version
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
    
    def check_duplicates(self):
        """Check for duplicate recipes in main recipes table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
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
                AND is_latest_version = 1
            """)
            
            conn.commit()
        finally:
            conn.close()
    
    def check_prep_dependencies(self):
        """Check for missing prep recipe dependencies"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                WITH prep_ingredients AS (
                    SELECT DISTINCT ingredient_source_recipe_name
                    FROM stg_csv_recipes
                    WHERE used_as_ingredient = 1 
                    AND ingredient_source_type = 'recipe'
                    AND ingredient_source_recipe_name IS NOT NULL
                    AND is_latest_version = 1
                ),
                existing_recipes AS (
                    SELECT recipe_name FROM recipes
                    UNION
                    SELECT DISTINCT recipe_name FROM stg_csv_recipes 
                    WHERE review_status = 'approved' AND is_latest_version = 1
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
                AND is_latest_version = 1
            """)
            
            conn.commit()
        finally:
            conn.close()

if __name__ == "__main__":
    # Initialize and run loader
    loader = CSVRecipeLoaderV2()
    loader.init_database()
    
    print("CSV Recipe Loader V2 - with duplicate file handling")
    print("="*50)
    
    # ALWAYS clear existing data to prevent duplicates
    results = loader.load_to_staging(clear_existing=True)
    
    print(f"\nLoad Results:")
    print(f"Total unique recipes: {results['total_files']}")
    print(f"Duplicate files skipped: {results['skipped_files']}")
    print(f"Successfully loaded: {results['successful_files']}")
    print(f"Failed: {results['failed_files']}")
    print(f"Total ingredients: {results['total_ingredients']}")
    print(f"Batch ID: {results['batch_id']}")
    
    if results['errors']:
        print("\nErrors:")
        for error in results['errors']:
            print(f"  {error['file']}: {error['errors']}")
    
    # Check for duplicates in main database
    print("\nChecking for duplicates in main database...")
    loader.check_duplicates()
    
    # Check for prep recipe dependencies
    print("Checking for prep recipe dependencies...")
    loader.check_prep_dependencies()
    
    print("\nDone!")