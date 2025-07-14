#!/usr/bin/env python3
"""
CSV Import Diagnostic and Repair Tool

This tool:
1. Identifies systematic CSV import errors
2. Compares CSV data vs PDF ground truth
3. Analyzes import corruption patterns
4. Provides fixed import functions
5. Generates detailed discrepancy reports
"""

import csv
import sqlite3
import json
import re
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from decimal import Decimal
import difflib
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CSVImportDiagnostics:
    """Comprehensive CSV import diagnostic and repair tool"""
    
    def __init__(self, database_path: str = 'restaurant_calculator.db'):
        self.database_path = database_path
        self.diagnostic_results = {
            'field_mapping_errors': [],
            'data_type_errors': [],
            'uom_parsing_errors': [],
            'encoding_errors': [],
            'formula_errors': [],
            'systematic_issues': defaultdict(list)
        }
        self.pdf_extractor = None
        
    def run_full_diagnostics(self):
        """Run complete diagnostic suite"""
        logger.info("Starting CSV Import Diagnostics...")
        
        # 1. Analyze existing CSV files
        self.analyze_csv_files()
        
        # 2. Compare with database data
        self.compare_csv_vs_database()
        
        # 3. If PDF extractor available, compare with PDF ground truth
        if self._check_pdf_extractor():
            self.compare_csv_vs_pdf()
        
        # 4. Identify systematic patterns
        self.identify_systematic_issues()
        
        # 5. Generate report
        self.generate_diagnostic_report()
        
        # 6. Provide fixes
        self.suggest_fixes()
        
    def analyze_csv_files(self):
        """Analyze all CSV files for structural issues"""
        logger.info("Analyzing CSV file structures...")
        
        csv_patterns = [
            'data/sources/data_sources_from_toast/*.csv',
            'data/*.csv',
            'data/sources/*.csv'
        ]
        
        for pattern in csv_patterns:
            for csv_file in Path('.').glob(pattern):
                self._analyze_single_csv(csv_file)
                
    def _analyze_single_csv(self, csv_path: Path):
        """Analyze a single CSV file for issues"""
        try:
            # Check encoding
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            correct_encoding = None
            
            for encoding in encodings:
                try:
                    with open(csv_path, 'r', encoding=encoding) as f:
                        f.read()
                    correct_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue
                    
            if not correct_encoding:
                self.diagnostic_results['encoding_errors'].append({
                    'file': str(csv_path),
                    'error': 'Could not determine encoding'
                })
                return
                
            # Analyze structure
            with open(csv_path, 'r', encoding=correct_encoding) as f:
                lines = f.readlines()
                
            # Check for common CSV issues
            issues = []
            
            # Check for BOM
            if lines and lines[0].startswith('\ufeff'):
                issues.append('File has BOM (Byte Order Mark)')
                
            # Check for irregular headers
            if self._has_toast_header_format(lines):
                issues.append('Toast format with metadata headers')
                
            # Check for inconsistent column counts
            if self._has_inconsistent_columns(csv_path, correct_encoding):
                issues.append('Inconsistent column counts')
                
            # Check for mixed data types
            mixed_types = self._check_mixed_data_types(csv_path, correct_encoding)
            if mixed_types:
                issues.extend(mixed_types)
                
            if issues:
                self.diagnostic_results['systematic_issues']['csv_structure'].append({
                    'file': str(csv_path),
                    'issues': issues,
                    'encoding': correct_encoding
                })
                
        except Exception as e:
            logger.error(f"Error analyzing {csv_path}: {e}")
            
    def _has_toast_header_format(self, lines: List[str]) -> bool:
        """Check if CSV has Toast's special header format"""
        if len(lines) < 3:
            return False
            
        # Toast files often have metadata in first few rows
        return any('Location,' in line and 'Date & Time,' in line for line in lines[:5])
        
    def _has_inconsistent_columns(self, csv_path: Path, encoding: str) -> bool:
        """Check for inconsistent column counts"""
        with open(csv_path, 'r', encoding=encoding) as f:
            reader = csv.reader(f)
            column_counts = set()
            for row in reader:
                if row:  # Skip empty rows
                    column_counts.add(len(row))
                    
        return len(column_counts) > 1
        
    def _check_mixed_data_types(self, csv_path: Path, encoding: str) -> List[str]:
        """Check for mixed data types in columns"""
        issues = []
        
        try:
            with open(csv_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                column_types = defaultdict(set)
                
                for row in reader:
                    for col, value in row.items():
                        if col and value:
                            # Determine type
                            if re.match(r'^-?\d+$', value):
                                column_types[col].add('integer')
                            elif re.match(r'^-?\d+\.?\d*$', value):
                                column_types[col].add('float')
                            elif re.match(r'^\$?[\d,]+\.?\d*$', value):
                                column_types[col].add('currency')
                            elif re.match(r'^\d+\s*[a-zA-Z]+', value):
                                column_types[col].add('quantity_with_unit')
                            else:
                                column_types[col].add('text')
                                
                # Check for mixed types
                for col, types in column_types.items():
                    if len(types) > 1 and 'text' in types:
                        other_types = types - {'text'}
                        if other_types:
                            issues.append(f"Column '{col}' has mixed types: {types}")
                            
        except Exception as e:
            logger.error(f"Error checking data types: {e}")
            
        return issues
        
    def compare_csv_vs_database(self):
        """Compare CSV data with what's in the database"""
        logger.info("Comparing CSV data with database...")
        
        # Focus on recipe ingredients as they're most problematic
        self._compare_recipe_ingredients()
        self._compare_inventory_items()
        
    def _compare_recipe_ingredients(self):
        """Compare recipe ingredients from CSV vs database"""
        csv_dir = Path('data/sources/data_sources_from_toast')
        
        # Get all recipe CSV files
        recipe_files = [f for f in csv_dir.glob('*.csv') 
                       if 'Recipe_Summary' not in f.name and 'Item_Detail' not in f.name]
        
        with sqlite3.connect(self.database_path) as conn:
            conn.row_factory = sqlite3.Row
            
            for csv_file in recipe_files:
                # Extract recipe name from filename
                recipe_name = self._extract_recipe_name_from_filename(csv_file.name)
                
                # Get database version
                db_recipe = conn.execute('''
                    SELECT * FROM recipes WHERE recipe_name = ?
                ''', (recipe_name,)).fetchone()
                
                if not db_recipe:
                    continue
                    
                # Compare ingredients
                csv_ingredients = self._parse_recipe_csv(csv_file)
                db_ingredients = conn.execute('''
                    SELECT * FROM recipe_ingredients_actual 
                    WHERE recipe_id = ?
                ''', (db_recipe['id'],)).fetchall()
                
                # Compare counts
                if len(csv_ingredients) != len(db_ingredients):
                    self.diagnostic_results['systematic_issues']['ingredient_count_mismatch'].append({
                        'recipe': recipe_name,
                        'csv_count': len(csv_ingredients),
                        'db_count': len(db_ingredients)
                    })
                    
                # Compare details
                for csv_ing in csv_ingredients:
                    self._analyze_ingredient_import(csv_ing, db_ingredients, recipe_name)
                    
    def _analyze_ingredient_import(self, csv_ing: Dict, db_ingredients: List, recipe_name: str):
        """Analyze how a single ingredient was imported"""
        # Check for quantity/unit parsing issues
        measurement = csv_ing.get('measurement', '')
        
        # Common patterns that fail
        if ' x ' in measurement:  # e.g., "2 x 4 oz"
            self.diagnostic_results['uom_parsing_errors'].append({
                'recipe': recipe_name,
                'ingredient': csv_ing.get('name', ''),
                'original': measurement,
                'issue': 'Complex unit pattern not parsed correctly'
            })
            
        # Check for missing units
        if measurement and not re.search(r'[a-zA-Z]+', measurement):
            self.diagnostic_results['uom_parsing_errors'].append({
                'recipe': recipe_name,
                'ingredient': csv_ing.get('name', ''),
                'original': measurement,
                'issue': 'No unit found in measurement'
            })
            
        # Check for formula in cost
        cost_str = csv_ing.get('cost', '')
        if '=' in cost_str or any(op in cost_str for op in ['+', '-', '*', '/']):
            self.diagnostic_results['formula_errors'].append({
                'recipe': recipe_name,
                'ingredient': csv_ing.get('name', ''),
                'cost_field': cost_str,
                'issue': 'Formula in cost field instead of calculated value'
            })
            
    def _parse_recipe_csv(self, csv_path: Path) -> List[Dict]:
        """Parse a Toast recipe CSV file"""
        ingredients = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
                
            # Find ingredient section
            ingredient_start = -1
            for i, line in enumerate(lines):
                if 'Ingredient,Type,Measurement' in line:
                    ingredient_start = i + 1
                    break
                    
            if ingredient_start == -1:
                return ingredients
                
            # Parse ingredients
            for line in lines[ingredient_start:]:
                if line.strip():
                    parts = [p.strip('"').strip() for p in line.split(',')]
                    if len(parts) >= 6 and parts[0]:
                        ingredients.append({
                            'name': parts[0],
                            'type': parts[1],
                            'measurement': parts[2],
                            'yield': parts[3] if len(parts) > 3 else '100%',
                            'usable_yield': parts[4] if len(parts) > 4 else '100%',
                            'cost': parts[5] if len(parts) > 5 else ''
                        })
                        
        except Exception as e:
            logger.error(f"Error parsing recipe CSV {csv_path}: {e}")
            
        return ingredients
        
    def _extract_recipe_name_from_filename(self, filename: str) -> str:
        """Extract recipe name from Toast CSV filename"""
        # Pattern: "Recipe Name_Lea Jane's Hot Chicken_date.csv"
        match = re.match(r'^(.+?)_Lea Jane\'s Hot Chicken_\d+', filename)
        if match:
            return match.group(1).strip()
        return filename.replace('.csv', '')
        
    def _compare_inventory_items(self):
        """Compare inventory items from CSV vs database"""
        csv_file = Path('data/sources/data_sources_from_toast/Lea_Janes_Hot_Chicken_Item_Detail_Report_20250704_023013.csv')
        
        if not csv_file.exists():
            return
            
        csv_items = self._parse_inventory_csv(csv_file)
        
        with sqlite3.connect(self.database_path) as conn:
            conn.row_factory = sqlite3.Row
            
            for csv_item in csv_items:
                item_code = csv_item.get('item_code', '')
                if not item_code:
                    continue
                    
                db_item = conn.execute('''
                    SELECT * FROM inventory WHERE item_code = ?
                ''', (item_code,)).fetchone()
                
                if db_item:
                    # Compare pack sizes
                    csv_pack = self._build_pack_size(csv_item)
                    db_pack = db_item['pack_size']
                    
                    if csv_pack != db_pack:
                        self.diagnostic_results['field_mapping_errors'].append({
                            'table': 'inventory',
                            'item_code': item_code,
                            'field': 'pack_size',
                            'csv_value': csv_pack,
                            'db_value': db_pack
                        })
                        
    def _parse_inventory_csv(self, csv_path: Path) -> List[Dict]:
        """Parse Toast inventory CSV"""
        items = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
                
            # Find header line
            header_idx = -1
            for i, line in enumerate(lines):
                if 'Location Name,Vendor Name,Item Code' in line:
                    header_idx = i
                    break
                    
            if header_idx == -1:
                return items
                
            reader = csv.DictReader(lines[header_idx:])
            for row in reader:
                items.append({
                    'item_code': row.get('Item Code', '').strip(),
                    'description': row.get('Item Description', '').strip(),
                    'pack': row.get('Pack', '').strip(),
                    'size': row.get('Size', '').strip(),
                    'uom': row.get('UOM', '').strip(),
                    'price': row.get('Contracted Price ($)', '').strip()
                })
                
        except Exception as e:
            logger.error(f"Error parsing inventory CSV: {e}")
            
        return items
        
    def _build_pack_size(self, item: Dict) -> str:
        """Build pack size string from components"""
        pack = item.get('pack', '')
        size = item.get('size', '')
        uom = item.get('uom', '')
        
        # Normalize units
        if uom == 'fl':
            uom = 'fl oz'
        elif uom == 'ea':
            uom = 'each'
            
        # Build pack size
        if pack and size and uom:
            if pack == '1':
                return f"{size} {uom}"
            else:
                return f"{pack} x {size} {uom}"
        elif size and uom:
            return f"{size} {uom}"
        else:
            return ''
            
    def identify_systematic_issues(self):
        """Identify patterns in import errors"""
        logger.info("Identifying systematic import patterns...")
        
        # Analyze UOM parsing errors
        uom_patterns = defaultdict(int)
        for error in self.diagnostic_results['uom_parsing_errors']:
            pattern = self._extract_uom_pattern(error['original'])
            uom_patterns[pattern] += 1
            
        # Find most common error patterns
        common_patterns = sorted(uom_patterns.items(), key=lambda x: x[1], reverse=True)[:10]
        
        self.diagnostic_results['systematic_issues']['common_uom_patterns'] = [
            {'pattern': pattern, 'count': count} 
            for pattern, count in common_patterns
        ]
        
        # Analyze formula errors
        formula_patterns = defaultdict(int)
        for error in self.diagnostic_results['formula_errors']:
            if '=' in error['cost_field']:
                formula_patterns['excel_formula'] += 1
            elif any(op in error['cost_field'] for op in ['+', '-', '*', '/']):
                formula_patterns['arithmetic_expression'] += 1
                
        self.diagnostic_results['systematic_issues']['formula_patterns'] = dict(formula_patterns)
        
    def _extract_uom_pattern(self, measurement: str) -> str:
        """Extract pattern from measurement string"""
        # Replace numbers with N
        pattern = re.sub(r'\d+\.?\d*', 'N', measurement)
        return pattern.strip()
        
    def _check_pdf_extractor(self) -> bool:
        """Check if PDF extractor is available"""
        try:
            from pdf_recipe_extractor import PDFRecipeExtractor
            self.pdf_extractor = PDFRecipeExtractor('data/sources/pdf_recipes')
            return True
        except ImportError:
            logger.warning("PDF extractor not available for ground truth comparison")
            return False
            
    def compare_csv_vs_pdf(self):
        """Compare CSV data with PDF ground truth"""
        if not self.pdf_extractor:
            return
            
        logger.info("Comparing CSV data with PDF ground truth...")
        
        # Extract PDF data
        pdf_data = self.pdf_extractor.extract_all_pdfs()
        
        # Compare with CSV data
        for pdf_name, pdf_recipe in pdf_data.items():
            recipe_name = pdf_recipe['recipe_name']
            
            # Find corresponding CSV
            csv_path = self._find_matching_csv(recipe_name)
            if not csv_path:
                continue
                
            # Compare data
            csv_data = self._parse_recipe_csv(csv_path)
            self._compare_recipe_data(pdf_recipe, csv_data, recipe_name)
            
    def _find_matching_csv(self, recipe_name: str) -> Optional[Path]:
        """Find CSV file matching recipe name"""
        csv_dir = Path('data/sources/data_sources_from_toast')
        
        # Try exact match first
        for csv_file in csv_dir.glob('*.csv'):
            if recipe_name in csv_file.name:
                return csv_file
                
        # Try fuzzy match
        for csv_file in csv_dir.glob('*.csv'):
            csv_recipe_name = self._extract_recipe_name_from_filename(csv_file.name)
            if difflib.SequenceMatcher(None, recipe_name, csv_recipe_name).ratio() > 0.8:
                return csv_file
                
        return None
        
    def _compare_recipe_data(self, pdf_data: Dict, csv_data: List[Dict], recipe_name: str):
        """Compare recipe data from PDF vs CSV"""
        # Compare costs
        pdf_cost = pdf_data.get('food_cost', 0)
        csv_total_cost = sum(self._parse_cost(ing.get('cost', '0')) for ing in csv_data)
        
        if abs(pdf_cost - csv_total_cost) > 0.01:
            self.diagnostic_results['systematic_issues']['cost_discrepancies'].append({
                'recipe': recipe_name,
                'pdf_cost': pdf_cost,
                'csv_cost': csv_total_cost,
                'difference': abs(pdf_cost - csv_total_cost)
            })
            
        # Compare ingredient counts
        pdf_ing_count = len(pdf_data.get('ingredients', []))
        csv_ing_count = len(csv_data)
        
        if pdf_ing_count != csv_ing_count:
            self.diagnostic_results['systematic_issues']['ingredient_count_discrepancies'].append({
                'recipe': recipe_name,
                'pdf_count': pdf_ing_count,
                'csv_count': csv_ing_count
            })
            
    def _parse_cost(self, cost_str: str) -> float:
        """Parse cost string to float"""
        try:
            # Remove $ and commas
            cost_str = cost_str.replace('$', '').replace(',', '').strip()
            if not cost_str:
                return 0.0
            return float(cost_str)
        except:
            return 0.0
            
    def generate_diagnostic_report(self):
        """Generate comprehensive diagnostic report"""
        logger.info("Generating diagnostic report...")
        
        report_path = f'csv_import_diagnostic_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        # Summarize findings
        summary = {
            'total_issues': sum(len(v) if isinstance(v, list) else 
                              sum(len(issues) for issues in v.values()) 
                              for v in self.diagnostic_results.values()),
            'categories': {
                'field_mapping_errors': len(self.diagnostic_results['field_mapping_errors']),
                'data_type_errors': len(self.diagnostic_results['data_type_errors']),
                'uom_parsing_errors': len(self.diagnostic_results['uom_parsing_errors']),
                'encoding_errors': len(self.diagnostic_results['encoding_errors']),
                'formula_errors': len(self.diagnostic_results['formula_errors']),
                'systematic_issues': len(self.diagnostic_results['systematic_issues'])
            }
        }
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': summary,
            'details': self.diagnostic_results
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Diagnostic report saved to: {report_path}")
        
        # Also generate human-readable report
        self._generate_readable_report()
        
    def _generate_readable_report(self):
        """Generate human-readable diagnostic report"""
        report_path = f'csv_import_diagnostic_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        
        with open(report_path, 'w') as f:
            f.write("CSV IMPORT DIAGNOSTIC REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            # Summary
            f.write("SUMMARY\n")
            f.write("-" * 40 + "\n")
            total_issues = sum(len(v) if isinstance(v, list) else 
                             sum(len(issues) for issues in v.values()) 
                             for v in self.diagnostic_results.values())
            f.write(f"Total Issues Found: {total_issues}\n\n")
            
            # Issue breakdown
            f.write("ISSUE BREAKDOWN\n")
            f.write("-" * 40 + "\n")
            
            # Field mapping errors
            if self.diagnostic_results['field_mapping_errors']:
                f.write(f"\nField Mapping Errors: {len(self.diagnostic_results['field_mapping_errors'])}\n")
                for error in self.diagnostic_results['field_mapping_errors'][:5]:
                    f.write(f"  - {error['table']}.{error['field']}: "
                           f"CSV='{error['csv_value']}' vs DB='{error['db_value']}'\n")
                if len(self.diagnostic_results['field_mapping_errors']) > 5:
                    f.write(f"  ... and {len(self.diagnostic_results['field_mapping_errors']) - 5} more\n")
                    
            # UOM parsing errors
            if self.diagnostic_results['uom_parsing_errors']:
                f.write(f"\nUnit of Measure Parsing Errors: {len(self.diagnostic_results['uom_parsing_errors'])}\n")
                for error in self.diagnostic_results['uom_parsing_errors'][:5]:
                    f.write(f"  - {error['recipe']}: '{error['original']}' - {error['issue']}\n")
                if len(self.diagnostic_results['uom_parsing_errors']) > 5:
                    f.write(f"  ... and {len(self.diagnostic_results['uom_parsing_errors']) - 5} more\n")
                    
            # Formula errors
            if self.diagnostic_results['formula_errors']:
                f.write(f"\nFormula Errors in Cost Fields: {len(self.diagnostic_results['formula_errors'])}\n")
                for error in self.diagnostic_results['formula_errors'][:5]:
                    f.write(f"  - {error['recipe']}: {error['ingredient']} has formula '{error['cost_field']}'\n")
                    
            # Systematic issues
            f.write("\nSYSTEMATIC ISSUES\n")
            f.write("-" * 40 + "\n")
            
            if 'common_uom_patterns' in self.diagnostic_results['systematic_issues']:
                f.write("\nMost Common UOM Patterns Causing Errors:\n")
                for pattern_info in self.diagnostic_results['systematic_issues']['common_uom_patterns'][:5]:
                    f.write(f"  - Pattern '{pattern_info['pattern']}': {pattern_info['count']} occurrences\n")
                    
            # Recommendations
            f.write("\nRECOMMENDATIONS\n")
            f.write("-" * 40 + "\n")
            f.write(self._generate_recommendations())
            
        logger.info(f"Human-readable report saved to: {report_path}")
        
    def _generate_recommendations(self) -> str:
        """Generate recommendations based on findings"""
        recommendations = []
        
        if self.diagnostic_results['uom_parsing_errors']:
            recommendations.append(
                "1. Implement robust UOM parser that handles:\n"
                "   - Complex patterns like '2 x 4 oz'\n"
                "   - Missing units (default to 'each')\n"
                "   - Unit normalization (fl -> fl oz, ea -> each)"
            )
            
        if self.diagnostic_results['formula_errors']:
            recommendations.append(
                "2. Add CSV preprocessing to evaluate formulas:\n"
                "   - Detect Excel formulas (starting with =)\n"
                "   - Evaluate arithmetic expressions\n"
                "   - Convert to numeric values before import"
            )
            
        if self.diagnostic_results['encoding_errors']:
            recommendations.append(
                "3. Implement encoding detection:\n"
                "   - Try multiple encodings (utf-8-sig, latin-1, cp1252)\n"
                "   - Handle BOM markers\n"
                "   - Standardize to UTF-8 for database storage"
            )
            
        if 'csv_structure' in self.diagnostic_results['systematic_issues']:
            recommendations.append(
                "4. Handle Toast CSV format:\n"
                "   - Skip metadata headers\n"
                "   - Find actual data headers dynamically\n"
                "   - Handle inconsistent column counts"
            )
            
        return "\n\n".join(recommendations)
        
    def suggest_fixes(self):
        """Generate fixed import functions"""
        logger.info("Generating fixed import functions...")
        
        # Create fixed import module
        self._generate_fixed_import_module()
        
    def _generate_fixed_import_module(self):
        """Generate a module with fixed import functions"""
        fixed_import_code = '''#!/usr/bin/env python3
"""
Fixed CSV Import Functions
Generated by CSV Import Diagnostics Tool
"""

import csv
import re
from typing import Dict, List, Tuple, Optional
from decimal import Decimal

class FixedCSVImporter:
    """Fixed CSV import functions that handle common issues"""
    
    @staticmethod
    def parse_measurement(measurement: str) -> Tuple[float, str]:
        """Parse measurement string into quantity and unit
        
        Handles patterns like:
        - "10 oz" -> (10.0, "oz")
        - "2 x 4 oz" -> (8.0, "oz")
        - "5" -> (5.0, "each")
        - "1 slice" -> (1.0, "slice")
        """
        if not measurement:
            return (0.0, "each")
            
        measurement = measurement.strip()
        
        # Handle "X x Y unit" pattern
        match = re.match(r'(\d+\.?\d*)\s*x\s*(\d+\.?\d*)\s*(\w+)', measurement)
        if match:
            qty1 = float(match.group(1))
            qty2 = float(match.group(2))
            unit = match.group(3)
            return (qty1 * qty2, unit)
            
        # Handle "X unit" pattern
        match = re.match(r'(\d+\.?\d*)\s*(.+)', measurement)
        if match:
            qty = float(match.group(1))
            unit = match.group(2).strip()
            return (qty, unit if unit else "each")
            
        # Handle just a number
        try:
            return (float(measurement), "each")
        except ValueError:
            # Handle just a unit (assume qty=1)
            return (1.0, measurement)
            
    @staticmethod
    def normalize_unit(unit: str) -> str:
        """Normalize unit abbreviations"""
        unit_map = {
            'fl': 'fl oz',
            'floz': 'fl oz',
            'oz': 'oz',
            'ounce': 'oz',
            'ounces': 'oz',
            'lb': 'lb',
            'lbs': 'lb',
            'pound': 'lb',
            'pounds': 'lb',
            'ea': 'each',
            'pc': 'each',
            'pcs': 'each',
            'piece': 'each',
            'pieces': 'each',
            'slice': 'slice',
            'slices': 'slice',
            'g': 'g',
            'gram': 'g',
            'grams': 'g',
            'kg': 'kg',
            'kilogram': 'kg',
            'kilograms': 'kg',
            'ml': 'ml',
            'milliliter': 'ml',
            'milliliters': 'ml',
            'l': 'L',
            'liter': 'L',
            'liters': 'L',
            'gal': 'gal',
            'gallon': 'gal',
            'gallons': 'gal',
            'qt': 'qt',
            'quart': 'qt',
            'quarts': 'qt',
            'pt': 'pt',
            'pint': 'pt',
            'pints': 'pt',
            'cup': 'cup',
            'cups': 'cup',
            'tbsp': 'tbsp',
            'tablespoon': 'tbsp',
            'tablespoons': 'tbsp',
            'tsp': 'tsp',
            'teaspoon': 'tsp',
            'teaspoons': 'tsp'
        }
        
        unit_lower = unit.lower().strip()
        return unit_map.get(unit_lower, unit)
        
    @staticmethod
    def parse_cost(cost_str: str) -> float:
        """Parse cost string, handling formulas and currency symbols
        
        Handles:
        - "$1.50" -> 1.50
        - "1.50" -> 1.50
        - "=B2*C2" -> 0.0 (with warning)
        - "$1,234.56" -> 1234.56
        """
        if not cost_str:
            return 0.0
            
        cost_str = str(cost_str).strip()
        
        # Check for formulas
        if cost_str.startswith('='):
            print(f"Warning: Formula found in cost field: {cost_str}")
            return 0.0
            
        # Remove currency symbols and commas
        cost_str = cost_str.replace('$', '').replace(',', '').strip()
        
        try:
            return float(cost_str)
        except ValueError:
            print(f"Warning: Could not parse cost: {cost_str}")
            return 0.0
            
    @staticmethod
    def detect_encoding(file_path: str) -> str:
        """Detect file encoding"""
        encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read()
                return encoding
            except UnicodeDecodeError:
                continue
                
        # Default to utf-8
        return 'utf-8'
        
    @classmethod
    def parse_toast_recipe_csv(cls, file_path: str) -> Dict:
        """Parse Toast recipe CSV with all fixes applied"""
        encoding = cls.detect_encoding(file_path)
        
        with open(file_path, 'r', encoding=encoding) as f:
            lines = f.readlines()
            
        # Extract recipe name
        recipe_name = None
        for line in lines[:5]:
            if 'Recipe Name,' in line:
                parts = line.split(',')
                if len(parts) > 1:
                    recipe_name = parts[1].strip()
                break
                
        # Find ingredient section
        ingredients = []
        ingredient_start = -1
        
        for i, line in enumerate(lines):
            if 'Ingredient,Type,Measurement' in line:
                ingredient_start = i + 1
                break
                
        if ingredient_start > -1:
            for line in lines[ingredient_start:]:
                if not line.strip():
                    continue
                    
                parts = [p.strip('"').strip() for p in line.split(',')]
                if len(parts) >= 6 and parts[0]:
                    # Parse measurement
                    quantity, unit = cls.parse_measurement(parts[2])
                    unit = cls.normalize_unit(unit)
                    
                    # Parse cost
                    cost = cls.parse_cost(parts[5] if len(parts) > 5 else '0')
                    
                    ingredients.append({
                        'name': parts[0],
                        'type': parts[1] or 'Product',
                        'quantity': quantity,
                        'unit': unit,
                        'yield_percent': parts[3] if len(parts) > 3 else '100%',
                        'usable_yield': parts[4] if len(parts) > 4 else '100%',
                        'cost': cost
                    })
                    
        return {
            'recipe_name': recipe_name,
            'ingredients': ingredients
        }
        
    @classmethod
    def parse_toast_inventory_csv(cls, file_path: str) -> List[Dict]:
        """Parse Toast inventory CSV with all fixes applied"""
        encoding = cls.detect_encoding(file_path)
        items = []
        
        with open(file_path, 'r', encoding=encoding) as f:
            lines = f.readlines()
            
        # Find header line
        header_idx = -1
        for i, line in enumerate(lines):
            if 'Location Name,Vendor Name,Item Code' in line:
                header_idx = i
                break
                
        if header_idx == -1:
            return items
            
        reader = csv.DictReader(lines[header_idx:])
        for row in reader:
            # Build pack size
            pack = row.get('Pack', '').strip()
            size = row.get('Size', '').strip()
            uom = row.get('UOM', '').strip()
            
            # Normalize units
            uom = cls.normalize_unit(uom)
            
            # Build pack size string
            if pack and size and uom:
                if pack == '1':
                    pack_size = f"{size} {uom}"
                else:
                    pack_size = f"{pack} x {size} {uom}"
            elif size and uom:
                pack_size = f"{size} {uom}"
            else:
                pack_size = ''
                
            # Parse prices
            current_price = cls.parse_cost(row.get('Contracted Price ($)', '0'))
            last_price = cls.parse_cost(row.get('Last Purchased Price ($)', '0'))
            
            items.append({
                'item_code': row.get('Item Code', '').strip(),
                'description': row.get('Item Description', '').strip(),
                'vendor_name': row.get('Vendor Name', '').strip(),
                'pack_size': pack_size,
                'current_price': current_price,
                'last_purchased_price': last_price,
                'last_purchased_date': row.get('Last Purchased Date', '').strip(),
                'unit_measure': uom,
                'product_categories': row.get('Product(s)', '').strip()
            })
            
        return items

# Example usage:
if __name__ == '__main__':
    importer = FixedCSVImporter()
    
    # Parse a recipe CSV
    recipe_data = importer.parse_toast_recipe_csv('path/to/recipe.csv')
    print(f"Recipe: {recipe_data['recipe_name']}")
    for ing in recipe_data['ingredients']:
        print(f"  - {ing['name']}: {ing['quantity']} {ing['unit']} @ ${ing['cost']:.2f}")
'''
        
        with open('fixed_csv_importer.py', 'w') as f:
            f.write(fixed_import_code)
            
        logger.info("Fixed import module saved to: fixed_csv_importer.py")


def main():
    """Run the diagnostic tool"""
    diagnostics = CSVImportDiagnostics()
    diagnostics.run_full_diagnostics()
    
    print("\n" + "="*80)
    print("CSV IMPORT DIAGNOSTICS COMPLETE")
    print("="*80)
    print("\nReports generated:")
    print("- csv_import_diagnostic_report_[timestamp].json (detailed JSON)")
    print("- csv_import_diagnostic_summary_[timestamp].txt (human-readable)")
    print("- fixed_csv_importer.py (fixed import functions)")
    print("\nReview the reports for detailed findings and recommendations.")


if __name__ == '__main__':
    main()