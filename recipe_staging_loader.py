#!/usr/bin/env python3
"""
Recipe List CSV Staging Loader
Loads original xtraCHEF export CSV and transforms headers to new structure
"""

import csv
import sqlite3
import json
from datetime import datetime
import hashlib
from typing import Dict, List, Tuple, Any, Optional
import re
import os

class RecipeStagingLoader:
    def __init__(self, db_path: str = "restaurant_calculator.db"):
        self.db_path = db_path
        self.header_mapping = {
            # Original xtraCHEF headers -> New headers
            "LocationName": "FAM_Location_Name",
            "RecipeName": "Recipe_Name", 
            "Status": "Status",
            "RecipeGroup": "Recipe_Group",
            "Type": "Recipe_Type",
            "FoodCost": "Recipe_Food_Cost",
            "FoodCostPercentage": "Food_Cost_Percentage",
            "LaborCost": "Labor_Cost",
            "LaborCostPercentage": "Labor_Cost_Percentage",
            "MenuPrice": "Menu_Price",
            "PrepRecipeYieldPercentage": "Prep_Recipe_Yield_Percentage",
            "GrossMargin": "Gross_Margin",
            "PrimeCost": "Prime_Cost",
            "PrimeCostPercentage": "Prime_Cost_Percentage",
            "CostModified": "Date_Cost_Modified",
            "ShelfLife": "Shelf_Life",
            "ShelfLifeUom": "Shelf_Life_Uom",
            "PrepRecipeYield": "Prep_Recipe_Yield",
            "PrepRecipeYieldUom": "Prep_Recipe_Yield_Uom",
            "Serving": "Serving",
            "ServingSize": "Serving_Size",
            "ServingSizeUom": "Serving_Size_Uom",
            "PerServing": "Per_Serving"
        }
        
    def init_staging_table(self):
        """Create staging table if it doesn't exist"""
        with open(os.path.join(os.path.dirname(__file__), 'migrations', 'create_staging_recipes_table.sql'), 'r') as f:
            schema_sql = f.read()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Execute each statement separately
        for statement in schema_sql.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        conn.commit()
        conn.close()
        print("Staging table initialized successfully")
    
    def parse_numeric(self, value: str, field_name: str = None) -> Tuple[Optional[float], str, Optional[str]]:
        """Parse numeric value and return (cleaned_value, raw_value, flag)"""
        if not value or value.strip() == "":
            return None, value, "empty"
        
        # Remove quotes if present
        value = value.strip('"').strip()
        
        # Check for percentage values that are way too high
        try:
            num_val = float(value)
            
            # Auto-correct extremely high percentages only for percentage fields
            if field_name and "percentage" in field_name.lower():
                if num_val > 1000:
                    # Likely a formatting issue - auto-divide by 100
                    return num_val / 100, value, "percentage_auto_corrected"
                elif num_val > 100 and num_val < 1000:
                    # Flag for review but don't auto-correct
                    return num_val, value, "high_percentage_flagged"
            
            return num_val, value, None
        except ValueError:
            return None, value, "parse_error"
    
    def parse_date(self, value: str) -> Tuple[Optional[str], str]:
        """Parse date value and return (cleaned_value, flag)"""
        if not value or value.strip() == "":
            return None, "empty"
        
        # Remove quotes
        value = value.strip('"').strip()
        
        # Try different date formats
        date_formats = [
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%Y %H:%M",
            "%m/%d/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d"
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(value, fmt)
                return parsed_date.strftime("%Y-%m-%d %H:%M:%S"), None
            except ValueError:
                continue
        
        return value, "parse_error"
    
    def validate_row(self, row: Dict) -> Tuple[bool, List[str]]:
        """Validate a row and return (needs_review, errors)"""
        needs_review = False
        errors = []
        
        # Required fields check
        if not row.get('recipe_name'):
            needs_review = True
            errors.append("Missing recipe name")
        
        # Check for zero or missing food cost - ALWAYS flag
        food_cost = row.get('food_cost')
        if food_cost is None or food_cost == 0:
            needs_review = True
            if row.get('recipe_type') == 'Recipe':
                errors.append("Zero or missing food cost for Recipe type")
            else:
                errors.append("Zero or missing food cost - needs validation")
        
        # Check food cost percentage thresholds
        food_cost_pct = row.get('food_cost_percentage')
        if food_cost_pct is not None:
            if food_cost_pct < 10:
                needs_review = True
                errors.append(f"Food cost percentage {food_cost_pct}% below 10% - may indicate missing data")
            elif food_cost_pct > 40:
                needs_review = True
                errors.append(f"Food cost percentage {food_cost_pct}% above 40% - requires profitability review")
            
            # Check for extremely high percentages (potential formatting issue)
            if food_cost_pct > 100:
                needs_review = True
                errors.append(f"Food cost percentage {food_cost_pct}% exceeds 100% - possible formatting error")
        
        # Check status - flag draft, hold test/non-standard
        status = row.get('status', '').lower()
        if status == 'draft':
            needs_review = True
            errors.append("Draft recipe - requires review before publishing")
        elif status not in ['published', 'approved', 'active', 'complete']:
            needs_review = True
            errors.append(f"Non-standard status '{row.get('status')}' - requires manual approval")
            row['review_status'] = 'hold'  # Mark for holding
        
        # Check menu price for recipes (flag don't reject)
        if row.get('recipe_type') == 'Recipe' and not row.get('menu_price'):
            needs_review = True
            errors.append("Recipe missing menu price - needs assignment")
        
        # Check gross margin threshold
        gross_margin = row.get('gross_margin')
        if gross_margin is not None and gross_margin < 60:
            needs_review = True
            errors.append(f"Gross margin {gross_margin:.1f}% below 60% threshold")
        
        # Validate margin calculations
        if row.get('menu_price') and row.get('food_cost') and row['menu_price'] > 0:
            calculated_margin = ((row['menu_price'] - row['food_cost']) / row['menu_price']) * 100
            calculated_food_cost_pct = (row['food_cost'] / row['menu_price']) * 100
            
            row['calculated_margin'] = calculated_margin
            row['calculated_food_cost_percent'] = calculated_food_cost_pct
            
            # Check for negative margins
            if calculated_margin < 0:
                needs_review = True
                errors.append(f"Negative margin calculated: {calculated_margin:.1f}%")
            
            # Check margin variance
            if row.get('gross_margin'):
                variance = abs(calculated_margin - row['gross_margin'])
                if variance > 5:  # 5% tolerance
                    needs_review = True
                    errors.append(f"Margin calculation variance: {variance:.2f}%")
        
        # Check prep recipe requirements
        if row.get('recipe_type') == 'PrepRecipe':
            if not row.get('yield_quantity'):
                needs_review = True
                errors.append("Prep recipe missing yield quantity")
            if not row.get('yield_unit'):
                needs_review = True
                errors.append("Prep recipe missing yield unit")
        
        # Check per serving cost
        if row.get('recipe_type') == 'Recipe' and row.get('per_serving') == 0:
            needs_review = True
            errors.append("Zero per serving cost")
        
        return needs_review, errors
    
    def generate_hash(self, row: Dict) -> str:
        """Generate hash for duplicate detection"""
        key_fields = [
            row.get('location_name', ''),
            row.get('recipe_name', ''),
            row.get('recipe_type', '')
        ]
        return hashlib.md5('|'.join(key_fields).encode()).hexdigest()
    
    def load_csv(self, csv_path: str, batch_id: str = None) -> Dict[str, Any]:
        """Load CSV file into staging table"""
        if not batch_id:
            batch_id = datetime.now().strftime("RECIPE_%Y%m%d_%H%M%S")
        
        # Extract filename from path for tracking
        source_filename = os.path.basename(csv_path)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {
            'batch_id': batch_id,
            'source_file': source_filename,
            'total_rows': 0,
            'loaded': 0,
            'errors': 0,
            'needs_review': 0,
            'duplicates': 0
        }
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                # Read the file to detect the delimiter
                sample = f.read(1024)
                f.seek(0)
                
                # Detect delimiter
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(f, delimiter=delimiter)
                
                for row_num, raw_row in enumerate(reader, 1):
                    stats['total_rows'] += 1
                    
                    try:
                        # Transform row using header mapping
                        staged_row = {
                            'original_row_number': row_num,
                            'import_batch_id': batch_id,
                            'source_filename': source_filename,
                            'source_row_json': json.dumps(raw_row)
                        }
                        
                        # Map basic text fields
                        staged_row['location_name'] = raw_row.get('LocationName', '').strip('"')
                        staged_row['recipe_name'] = raw_row.get('RecipeName', '').strip('"')
                        staged_row['status'] = raw_row.get('Status', '').strip('"')
                        staged_row['recipe_group'] = raw_row.get('RecipeGroup', '').strip('"')
                        staged_row['recipe_type'] = raw_row.get('Type', '').strip('"')
                        
                        # Parse numeric fields
                        food_cost, food_cost_raw, food_cost_flag = self.parse_numeric(raw_row.get('FoodCost', ''), 'FoodCost')
                        staged_row['food_cost'] = food_cost
                        staged_row['food_cost_raw'] = food_cost_raw
                        staged_row['food_cost_flag'] = food_cost_flag
                        
                        food_cost_pct, food_cost_pct_raw, food_cost_pct_flag = self.parse_numeric(raw_row.get('FoodCostPercentage', ''), 'FoodCostPercentage')
                        staged_row['food_cost_percentage'] = food_cost_pct
                        staged_row['food_cost_percentage_raw'] = food_cost_pct_raw
                        staged_row['food_cost_percentage_flag'] = food_cost_pct_flag
                        
                        labor_cost, labor_cost_raw, _ = self.parse_numeric(raw_row.get('LaborCost', ''), 'LaborCost')
                        staged_row['labor_cost'] = labor_cost or 0
                        staged_row['labor_cost_raw'] = labor_cost_raw
                        
                        labor_cost_pct, labor_cost_pct_raw, _ = self.parse_numeric(raw_row.get('LaborCostPercentage', ''), 'LaborCostPercentage')
                        staged_row['labor_cost_percentage'] = labor_cost_pct or 0
                        staged_row['labor_cost_percentage_raw'] = labor_cost_pct_raw
                        
                        menu_price, menu_price_raw, menu_price_flag = self.parse_numeric(raw_row.get('MenuPrice', ''), 'MenuPrice')
                        staged_row['menu_price'] = menu_price
                        staged_row['menu_price_raw'] = menu_price_raw
                        staged_row['menu_price_flag'] = menu_price_flag
                        
                        gross_margin, gross_margin_raw, gross_margin_flag = self.parse_numeric(raw_row.get('GrossMargin', ''), 'GrossMargin')
                        staged_row['gross_margin'] = gross_margin
                        staged_row['gross_margin_raw'] = gross_margin_raw
                        staged_row['gross_margin_flag'] = gross_margin_flag
                        
                        prime_cost, prime_cost_raw, _ = self.parse_numeric(raw_row.get('PrimeCost', ''), 'PrimeCost')
                        staged_row['prime_cost'] = prime_cost
                        staged_row['prime_cost_raw'] = prime_cost_raw
                        
                        prime_cost_pct, prime_cost_pct_raw, _ = self.parse_numeric(raw_row.get('PrimeCostPercentage', ''), 'PrimeCostPercentage')
                        staged_row['prime_cost_percentage'] = prime_cost_pct
                        staged_row['prime_cost_percentage_raw'] = prime_cost_pct_raw
                        
                        prep_yield_pct, prep_yield_pct_raw, _ = self.parse_numeric(raw_row.get('PrepRecipeYieldPercentage', ''), 'PrepRecipeYieldPercentage')
                        staged_row['prep_recipe_yield_percentage'] = prep_yield_pct or 100
                        staged_row['prep_recipe_yield_percentage_raw'] = prep_yield_pct_raw
                        
                        # Parse date
                        cost_date, cost_date_flag = self.parse_date(raw_row.get('CostModified', ''))
                        staged_row['cost_modified_date'] = cost_date
                        staged_row['cost_modified_date_raw'] = raw_row.get('CostModified', '')
                        staged_row['cost_modified_date_flag'] = cost_date_flag
                        
                        # Shelf life
                        staged_row['shelf_life'] = raw_row.get('ShelfLife', '').strip('"')
                        staged_row['shelf_life_uom'] = raw_row.get('ShelfLifeUom', '').strip('"')
                        
                        # Yield
                        staged_row['yield_quantity'] = raw_row.get('PrepRecipeYield', '').strip('"')
                        staged_row['yield_unit'] = raw_row.get('PrepRecipeYieldUom', '').strip('"')
                        
                        # Serving info
                        staged_row['serving'] = raw_row.get('Serving', '').strip('"')
                        staged_row['serving_size'] = raw_row.get('ServingSize', '').strip('"')
                        staged_row['serving_size_uom'] = raw_row.get('ServingSizeUom', '').strip('"')
                        
                        per_serving, per_serving_raw, per_serving_flag = self.parse_numeric(raw_row.get('PerServing', ''), 'PerServing')
                        staged_row['per_serving'] = per_serving
                        staged_row['per_serving_raw'] = per_serving_raw
                        staged_row['per_serving_flag'] = per_serving_flag
                        
                        # Validate and calculate
                        needs_review, errors = self.validate_row(staged_row)
                        staged_row['needs_review'] = needs_review
                        staged_row['validation_errors'] = json.dumps(errors) if errors else None
                        
                        if needs_review:
                            stats['needs_review'] += 1
                        
                        # Calculate margin variance
                        if staged_row.get('calculated_margin') and staged_row.get('gross_margin'):
                            staged_row['margin_variance'] = staged_row['calculated_margin'] - staged_row['gross_margin']
                        
                        # Generate duplicate hash
                        staged_row['duplicate_check_hash'] = self.generate_hash(staged_row)
                        
                        # Check for existing recipe match
                        cursor.execute("""
                            SELECT id FROM recipes 
                            WHERE recipe_name = ? 
                            LIMIT 1
                        """, (staged_row['recipe_name'],))
                        match = cursor.fetchone()
                        if match:
                            staged_row['matched_recipe_id'] = match[0]
                        
                        # Insert into staging table
                        columns = list(staged_row.keys())
                        placeholders = ','.join(['?' for _ in columns])
                        insert_sql = f"""
                            INSERT INTO stg_recipes ({','.join(columns)})
                            VALUES ({placeholders})
                        """
                        
                        cursor.execute(insert_sql, list(staged_row.values()))
                        stats['loaded'] += 1
                        
                    except Exception as e:
                        print(f"Error processing row {row_num}: {e}")
                        stats['errors'] += 1
                
                # Check for duplicates within batch
                cursor.execute("""
                    UPDATE stg_recipes
                    SET is_duplicate = 1,
                        duplicate_of_staging_id = (
                            SELECT MIN(staging_id) 
                            FROM stg_recipes s2 
                            WHERE s2.duplicate_check_hash = stg_recipes.duplicate_check_hash
                            AND s2.import_batch_id = stg_recipes.import_batch_id
                            AND s2.staging_id < stg_recipes.staging_id
                        )
                    WHERE import_batch_id = ?
                    AND EXISTS (
                        SELECT 1 FROM stg_recipes s2
                        WHERE s2.duplicate_check_hash = stg_recipes.duplicate_check_hash
                        AND s2.import_batch_id = stg_recipes.import_batch_id
                        AND s2.staging_id < stg_recipes.staging_id
                    )
                """, (batch_id,))
                
                stats['duplicates'] = cursor.rowcount
                
                conn.commit()
                
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
        
        return stats

def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Load recipe CSV into staging table')
    parser.add_argument('csv_file', help='Path to CSV file')
    parser.add_argument('--db', default='restaurant_calculator.db', help='Database path')
    parser.add_argument('--batch-id', help='Batch ID (auto-generated if not provided)')
    parser.add_argument('--init', action='store_true', help='Initialize staging table')
    
    args = parser.parse_args()
    
    loader = RecipeStagingLoader(args.db)
    
    if args.init:
        loader.init_staging_table()
        print("Staging table initialized")
        return
    
    if not os.path.exists(args.csv_file):
        print(f"Error: CSV file not found: {args.csv_file}")
        return
    
    print(f"Loading CSV: {args.csv_file}")
    stats = loader.load_csv(args.csv_file, args.batch_id)
    
    print("\nLoad Statistics:")
    print(f"  Batch ID: {stats['batch_id']}")
    print(f"  Total rows: {stats['total_rows']}")
    print(f"  Loaded: {stats['loaded']}")
    print(f"  Errors: {stats['errors']}")
    print(f"  Needs review: {stats['needs_review']}")
    print(f"  Duplicates: {stats['duplicates']}")

if __name__ == "__main__":
    main()