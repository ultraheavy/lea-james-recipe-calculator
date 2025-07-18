#!/usr/bin/env python3
"""
CSV Recipe Loader FIXED - Properly handles the actual CSV format
"""

import os
import csv
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import re
import uuid

class CSVRecipeLoaderFixed:
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
        
        return recipe_files
    
    def select_files_to_load(self, recipe_files: Dict[str, List[Dict]]) -> List[Dict]:
        """Select which files to load (most recent version of each recipe)"""
        files_to_load = []
        
        for recipe_key, versions in recipe_files.items():
            # Sort by timestamp (newest first)
            sorted_versions = sorted(versions, key=lambda x: x['timestamp'], reverse=True)
            
            # Take the most recent version
            files_to_load.append(sorted_versions[0])
            
            # Mark older versions for info
            if len(sorted_versions) > 1:
                print(f"Recipe '{sorted_versions[0]['recipe_name']}' has {len(sorted_versions)} versions, using most recent: {sorted_versions[0]['timestamp']}")
        
        return files_to_load
    
    def parse_csv_file(self, file_info: Dict) -> Dict:
        """Parse a single CSV recipe file - FIXED for actual format"""
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
                
                # Extract recipe name from row 2 (index 1)
                # Row format: "Prep Recipe Name,Alabama White BBQ ,,,,,,"
                recipe_name = None
                if len(rows) > 1 and len(rows[1]) > 1:
                    recipe_name = rows[1][1].strip() if rows[1][1] else None
                
                if not recipe_name:
                    recipe_data['errors'].append("Recipe name not found")
                    return recipe_data
                
                recipe_data['recipe_name'] = recipe_name
                
                # Parse ingredients starting from row 11 (index 10)
                for row_num, row in enumerate(rows[10:], start=11):
                    if not row or not row[0] or row[0].strip() == '':
                        continue
                    
                    # Parse the quoted ingredient field
                    raw_ingredient = row[0] if len(row) > 0 else None
                    if not raw_ingredient:
                        continue
                    
                    # Clean and parse ingredient name
                    ingredient_name, category = self._parse_ingredient_field(raw_ingredient)
                    
                    ingredient = {
                        'name': ingredient_name,
                        'type': row[1] if len(row) > 1 else None,
                        'measurement': row[2] if len(row) > 2 else None,
                        'yield': row[3] if len(row) > 3 else None,
                        'usable_yield': row[4] if len(row) > 4 else None,
                        'cost': row[5] if len(row) > 5 else None,
                        'category': category,
                        'row_number': row_num
                    }
                    
                    # Parse quantity and unit from measurement
                    quantity, unit = self._parse_measurement(ingredient['measurement'])
                    ingredient['quantity'] = quantity
                    ingredient['unit'] = self._normalize_unit(unit)
                    
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
    
    def _parse_ingredient_field(self, ingredient_field: str) -> Tuple[str, Optional[str]]:
        """Parse the ingredient field - KEEP ORIGINAL FORMAT for matching"""
        if not ingredient_field:
            return ingredient_field, None
        
        # Remove outer quotes but preserve the content format
        ingredient_name = ingredient_field.strip('"').strip()
        
        # Try to extract category for metadata, but keep the full name
        category = None
        
        # Common category keywords
        category_keywords = ['Produce', 'Dairy', 'Dry Goods', 'Dry Good', 'Meat', 'Poultry', 
                           'Protein', 'Seafood', 'Frozen', 'Beverages', 'Supplies', 
                           'Paper Goods', 'Chemicals', 'Spices', 'Recipe', 'PrepRecipe']
        
        # Look for category in the string but don't modify the name
        if ',' in ingredient_name:
            parts = [p.strip() for p in ingredient_name.split(',')]
            
            # Check if first part is a category
            for part in parts:
                for cat in category_keywords:
                    if cat.lower() == part.lower() or cat.lower() in part.lower():
                        category = part
                        break
                if category:
                    break
        
        # Return the FULL original name, with category extracted separately
        return ingredient_name, category
    
    def _parse_measurement(self, measurement: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse measurement string into quantity and unit"""
        if not measurement:
            return None, None
        
        measurement = measurement.strip()
        
        # Handle common patterns
        patterns = [
            # "10 oz", "1.5 cup", etc
            (r'^(\d+\.?\d*)\s+(.+)$', lambda m: (m.group(1), m.group(2))),
            # "1 1/2 cup"
            (r'^(\d+)\s+(\d+/\d+)\s+(.+)$', lambda m: (f"{m.group(1)} {m.group(2)}", m.group(3))),
            # "1/2 cup"
            (r'^(\d+/\d+)\s+(.+)$', lambda m: (m.group(1), m.group(2))),
            # Just a number (assume each)
            (r'^(\d+\.?\d*)$', lambda m: (m.group(1), 'each')),
        ]
        
        for pattern, extractor in patterns:
            match = re.match(pattern, measurement)
            if match:
                return extractor(match)
        
        # If no pattern matches, try to split on first space
        parts = measurement.split(' ', 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        
        return measurement, None
    
    def _normalize_unit(self, unit: Optional[str]) -> Optional[str]:
        """Normalize common unit variations"""
        if not unit:
            return unit
        
        unit_lower = unit.lower().strip()
        
        # Handle fluid ounces
        if 'fl oz' in unit_lower or 'fl. oz' in unit_lower:
            return 'fl oz'
        
        unit_mappings = {
            'qt': 'quart', 'qts': 'quart', 'quarts': 'quart',
            'lb': 'pound', 'lbs': 'pound', 'pounds': 'pound',
            'oz': 'ounce', 'ozs': 'ounce', 'ounces': 'ounce',
            'gal': 'gallon', 'gallons': 'gallon',
            'tsp': 'teaspoon', 'teaspoons': 'teaspoon',
            'tbsp': 'tablespoon', 'tablespoons': 'tablespoon',
            'c': 'cup', 'cups': 'cup',
            'g': 'gram', 'grams': 'gram',
            'kg': 'kilogram', 'kilograms': 'kilogram',
            'ml': 'milliliter', 'milliliters': 'milliliter',
            'l': 'liter', 'liters': 'liter',
            'ea': 'each', 'pc': 'piece', 'pcs': 'piece', 'pieces': 'piece',
            'slice': 'slice', 'slices': 'slice'
        }
        
        return unit_mappings.get(unit_lower, unit)
    
    def _clean_cost(self, cost: str) -> Optional[str]:
        """Clean cost string to numeric value"""
        if not cost:
            return None
        
        # Remove dollar signs and commas
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
    
    def clear_staging_table(self):
        """Clear all records from staging table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM stg_csv_recipes")
            deleted_count = cursor.rowcount
            conn.commit()
            print(f"Cleared {deleted_count} existing records from staging table")
        finally:
            conn.close()
    
    def load_to_staging(self) -> Dict[str, Any]:
        """Load CSV files to staging - ALWAYS clears existing data first"""
        results = {
            'total_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'skipped_files': 0,
            'total_ingredients': 0,
            'errors': [],
            'batch_id': datetime.now().strftime('%Y%m%d_%H%M%S')
        }
        
        # ALWAYS clear staging first
        print("Clearing existing staging data...")
        self.clear_staging_table()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
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

if __name__ == "__main__":
    loader = CSVRecipeLoaderFixed()
    
    print("CSV Recipe Loader FIXED - Properly handles actual CSV format")
    print("=" * 60)
    
    results = loader.load_to_staging()
    
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
    
    print("\nDone!")