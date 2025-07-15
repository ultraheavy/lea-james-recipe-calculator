#!/usr/bin/env python3
"""
Recipe Cost Calculation Rebuilder
Rebuilds recipe cost calculations from scratch using corrected PDF data and standardized UOMs
Provides complete transparency and audit trails for all calculations
"""

import sqlite3
import logging
import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import decimal
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import csv

# Set up logging with detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import dependencies
from uom_standardizer import UOMStandardizer

# PDF functionality archived - commented out
# try:
#     from pdf_recipe_extractor import PDFRecipeExtractor
#     PDF_SUPPORT = True
# except ImportError:
#     logger.warning("PDF recipe extractor not available - PDF validation disabled")
#     PDF_SUPPORT = False
PDF_SUPPORT = False  # PDF functionality has been archived


class CalculationRebuilder:
    """Rebuild recipe cost calculations with full transparency and validation"""
    
    def __init__(self, db_path: str = 'restaurant_calculator.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.uom_standardizer = UOMStandardizer(db_path)
        self.audit_trail = []
        self.validation_errors = []
        
    def calculate_recipe_cost_from_scratch(self, recipe_id: int, 
                                          include_nested: bool = True) -> Dict[str, Any]:
        """
        Calculate recipe cost from ingredients up with full transparency
        
        Args:
            recipe_id: Recipe ID to calculate
            include_nested: Whether to calculate nested prep recipes
            
        Returns:
            Dict with cost breakdown and calculation details
        """
        cursor = self.conn.cursor()
        
        # Get recipe details - using the actual schema structure
        recipe = cursor.execute("""
            SELECT recipe_id as id, recipe_name, recipe_type, batch_yield, 
                   batch_yield_unit, serving_size, serving_unit,
                   menu_price, food_cost as pdf_stated_cost,
                   portions_per_batch
            FROM recipes_actual
            WHERE recipe_id = ?
        """, (recipe_id,)).fetchone()
        
        if not recipe:
            raise ValueError(f"Recipe {recipe_id} not found")
        
        recipe_name = recipe['recipe_name']
        logger.info(f"Calculating cost for recipe: {recipe_name} (ID: {recipe_id})")
        
        # Initialize calculation result
        calculation = {
            'recipe_id': recipe_id,
            'recipe_name': recipe_name,
            'recipe_type': recipe['recipe_type'],
            'timestamp': datetime.now().isoformat(),
            'ingredients': [],
            'total_cost': Decimal('0'),
            'cost_per_serving': Decimal('0'),
            'pdf_stated_cost': Decimal(str(recipe['pdf_stated_cost'])) if recipe['pdf_stated_cost'] else None,
            'variance_from_pdf': None,
            'calculation_steps': [],
            'warnings': [],
            'errors': []
        }
        
        # Get all ingredients
        ingredients = cursor.execute("""
            SELECT 
                ri.ingredient_id,
                ri.ingredient_name,
                ri.quantity,
                ri.unit as unit_of_measure,
                ri.inventory_id,
                ri.unit_cost,
                ri.total_cost as stated_cost,
                i.current_price,
                i.pack_size,
                i.purchase_unit,
                i.recipe_cost_unit,
                i.yield_percent,
                i.density_g_per_ml,
                i.count_to_weight_g,
                -- Check if this is a nested recipe by looking it up
                (SELECT recipe_id FROM recipes_actual WHERE recipe_name = ri.ingredient_name) as nested_recipe_id,
                CASE 
                    WHEN EXISTS (SELECT 1 FROM recipes_actual WHERE recipe_name = ri.ingredient_name) 
                    THEN 'Prep Recipe' 
                    ELSE 'Product' 
                END as ingredient_type
            FROM recipe_ingredients_actual ri
            LEFT JOIN inventory i ON ri.inventory_id = i.id
            WHERE ri.recipe_id = ?
            ORDER BY ri.ingredient_order, ri.ingredient_id
        """, (recipe_id,)).fetchall()
        
        # Calculate cost for each ingredient
        for ingredient in ingredients:
            ing_calc = self._calculate_ingredient_cost(ingredient, include_nested)
            calculation['ingredients'].append(ing_calc)
            calculation['total_cost'] += ing_calc['total_cost']
            
            # Add calculation steps
            calculation['calculation_steps'].extend(ing_calc['steps'])
            
            # Collect warnings and errors
            if ing_calc['warnings']:
                calculation['warnings'].extend(ing_calc['warnings'])
            if ing_calc['errors']:
                calculation['errors'].extend(ing_calc['errors'])
        
        # Calculate per-serving cost
        serving_size = recipe['serving_size'] or recipe['portions_per_batch']
        if serving_size and serving_size > 0:
            calculation['cost_per_serving'] = (
                calculation['total_cost'] / Decimal(str(serving_size))
            ).quantize(Decimal('0.0001'))
            
            calculation['calculation_steps'].append({
                'step': 'per_serving_calculation',
                'formula': f"${calculation['total_cost']} / {serving_size} servings",
                'result': f"${calculation['cost_per_serving']}"
            })
        
        # Calculate variance from PDF
        if calculation['pdf_stated_cost']:
            calculation['variance_from_pdf'] = (
                calculation['total_cost'] - calculation['pdf_stated_cost']
            ).quantize(Decimal('0.01'))
            
            calculation['variance_percent'] = (
                (calculation['variance_from_pdf'] / calculation['pdf_stated_cost'] * 100)
                if calculation['pdf_stated_cost'] > 0 else Decimal('0')
            ).quantize(Decimal('0.01'))
            
            # Flag significant variances
            if abs(calculation['variance_from_pdf']) > Decimal('0.01'):
                calculation['warnings'].append(
                    f"Cost variance of ${calculation['variance_from_pdf']} "
                    f"({calculation['variance_percent']}%) from PDF stated cost"
                )
        
        # Store audit trail
        self.audit_trail.append(calculation)
        
        return calculation
    
    def _calculate_ingredient_cost(self, ingredient: sqlite3.Row, 
                                  include_nested: bool = True) -> Dict[str, Any]:
        """Calculate cost for a single ingredient with unit conversions"""
        
        try:
            quantity_val = Decimal(str(ingredient['quantity'])) if ingredient['quantity'] is not None else Decimal('0')
        except (ValueError, TypeError, decimal.InvalidOperation) as e:
            logger.error(f"Invalid quantity for {ingredient['ingredient_name']}: {ingredient['quantity']}")
            quantity_val = Decimal('0')
            
        ing_calc = {
            'ingredient_name': ingredient['ingredient_name'],
            'ingredient_type': ingredient['ingredient_type'],
            'quantity': quantity_val,
            'unit': ingredient['unit_of_measure'],
            'unit_cost': Decimal('0'),
            'total_cost': Decimal('0'),
            'steps': [],
            'warnings': [],
            'errors': []
        }
        
        # Handle nested recipes
        if ingredient['ingredient_type'] == 'Prep Recipe' and ingredient['nested_recipe_id']:
            if include_nested:
                nested_calc = self.calculate_recipe_cost_from_scratch(
                    ingredient['nested_recipe_id'], 
                    include_nested=True
                )
                
                # Get yield information for nested recipe
                cursor = self.conn.cursor()
                nested_recipe = cursor.execute("""
                    SELECT batch_yield, batch_yield_unit, portions_per_batch
                    FROM recipes_actual
                    WHERE recipe_id = ?
                """, (ingredient['nested_recipe_id'],)).fetchone()
                
                if nested_recipe and (nested_recipe['batch_yield'] or nested_recipe['portions_per_batch']):
                    yield_qty = Decimal(str(nested_recipe['batch_yield'] or nested_recipe['portions_per_batch']))
                    yield_unit = nested_recipe['batch_yield_unit'] or 'portion'
                    cost_per_yield_unit = nested_calc['total_cost'] / yield_qty
                    
                    ing_calc['unit_cost'] = cost_per_yield_unit
                    ing_calc['total_cost'] = ing_calc['quantity'] * cost_per_yield_unit
                    
                    ing_calc['steps'].append({
                        'step': 'nested_recipe_cost',
                        'description': f"Using nested recipe: {ingredient['ingredient_name']}",
                        'formula': f"${nested_calc['total_cost']} / {yield_qty} {yield_unit}",
                        'unit_cost': f"${cost_per_yield_unit}/unit",
                        'total_cost': f"${ing_calc['total_cost']}"
                    })
                else:
                    ing_calc['errors'].append(
                        f"Nested recipe {ingredient['ingredient_name']} missing yield information"
                    )
            else:
                ing_calc['warnings'].append(
                    f"Skipping nested recipe calculation for {ingredient['ingredient_name']}"
                )
                
        # Handle regular inventory items
        elif ingredient['inventory_id'] and ingredient['current_price']:
            # Parse and standardize units
            quantity, unit = self.uom_standardizer.parse_measurement(
                f"{ingredient['quantity']} {ingredient['unit_of_measure']}"
            )
            
            # Get purchase information
            if ingredient['pack_size'] and ingredient['purchase_unit'] and ingredient['current_price']:
                # Parse pack size - it might already include the unit
                pack_size_str = str(ingredient['pack_size']).strip()
                if any(c.isalpha() for c in pack_size_str):
                    # Pack size includes unit (e.g., "1 lb")
                    pack_qty, pack_unit = self.uom_standardizer.parse_measurement(pack_size_str)
                else:
                    # Pack size is just a number, use purchase_unit
                    pack_qty = Decimal(pack_size_str)
                    pack_unit = self.uom_standardizer.standardize_unit(ingredient['purchase_unit'])
                
                # Calculate unit cost
                unit_cost = (
                    Decimal(str(ingredient['current_price'])) / pack_qty
                ).quantize(Decimal('0.0001'))
                
                # Check if unit conversion is needed
                if unit != pack_unit:
                    # Prepare conversion context
                    context = {
                        'density_g_per_ml': ingredient['density_g_per_ml'],
                        'count_to_weight_g': ingredient['count_to_weight_g']
                    }
                    
                    # Try to convert
                    converted_qty = self.uom_standardizer.convert_units(
                        quantity, unit, pack_unit, context
                    )
                    
                    if converted_qty:
                        ing_calc['total_cost'] = (converted_qty * unit_cost).quantize(Decimal('0.01'))
                        
                        ing_calc['steps'].append({
                            'step': 'unit_conversion',
                            'from': f"{quantity} {unit}",
                            'to': f"{converted_qty} {pack_unit}",
                            'formula': f"{converted_qty} × ${unit_cost}/{pack_unit}",
                            'result': f"${ing_calc['total_cost']}"
                        })
                    else:
                        ing_calc['errors'].append(
                            f"Cannot convert {quantity} {unit} to {pack_unit} for {ingredient['ingredient_name']}"
                        )
                else:
                    # No conversion needed
                    ing_calc['total_cost'] = (quantity * unit_cost).quantize(Decimal('0.01'))
                    
                    ing_calc['steps'].append({
                        'step': 'direct_calculation',
                        'formula': f"{quantity} {unit} × ${unit_cost}/{unit}",
                        'result': f"${ing_calc['total_cost']}"
                    })
                
                ing_calc['unit_cost'] = unit_cost
                
                # Apply yield if applicable
                if ingredient['yield_percent'] and ingredient['yield_percent'] < 100:
                    yield_factor = Decimal(str(ingredient['yield_percent'])) / 100
                    adjusted_cost = ing_calc['total_cost'] / yield_factor
                    
                    ing_calc['steps'].append({
                        'step': 'yield_adjustment',
                        'formula': f"${ing_calc['total_cost']} / {yield_factor} (yield: {ingredient['yield_percent']}%)",
                        'result': f"${adjusted_cost}"
                    })
                    
                    ing_calc['total_cost'] = adjusted_cost.quantize(Decimal('0.01'))
            else:
                ing_calc['errors'].append(
                    f"Missing pack size or purchase unit for {ingredient['ingredient_name']}"
                )
        else:
            ing_calc['errors'].append(
                f"No pricing information for {ingredient['ingredient_name']}"
            )
        
        return ing_calc
    
    def validate_against_pdf_cost(self, recipe_id: int, pdf_cost: Decimal) -> Dict[str, Any]:
        """
        Validate calculated cost against PDF stated cost
        
        Returns validation report with discrepancy analysis
        """
        # Calculate cost
        calculation = self.calculate_recipe_cost_from_scratch(recipe_id)
        
        validation = {
            'recipe_id': recipe_id,
            'recipe_name': calculation['recipe_name'],
            'calculated_cost': calculation['total_cost'],
            'pdf_stated_cost': pdf_cost,
            'variance': calculation['total_cost'] - pdf_cost,
            'variance_percent': (
                ((calculation['total_cost'] - pdf_cost) / pdf_cost * 100)
                if pdf_cost > 0 else Decimal('0')
            ).quantize(Decimal('0.01')),
            'is_valid': abs(calculation['total_cost'] - pdf_cost) <= Decimal('0.01'),
            'validation_notes': []
        }
        
        # Analyze discrepancies
        if not validation['is_valid']:
            validation['validation_notes'].append(
                f"Cost variance exceeds $0.01 threshold: ${validation['variance']}"
            )
            
            # Check for common issues
            if calculation['errors']:
                validation['validation_notes'].append(
                    f"Calculation errors found: {', '.join(calculation['errors'][:3])}"
                )
            
            if calculation['warnings']:
                validation['validation_notes'].append(
                    f"Warnings: {', '.join(calculation['warnings'][:3])}"
                )
            
            # Analyze ingredient-level variances
            validation['ingredient_analysis'] = self._analyze_ingredient_variances(calculation)
        
        return validation
    
    def _analyze_ingredient_variances(self, calculation: Dict) -> List[Dict]:
        """Analyze which ingredients contribute most to cost variance"""
        analysis = []
        
        # Sort ingredients by cost impact
        sorted_ingredients = sorted(
            calculation['ingredients'], 
            key=lambda x: x['total_cost'], 
            reverse=True
        )
        
        for ing in sorted_ingredients[:5]:  # Top 5 cost drivers
            analysis.append({
                'ingredient': ing['ingredient_name'],
                'cost': float(ing['total_cost']),
                'percent_of_total': float(
                    (ing['total_cost'] / calculation['total_cost'] * 100).quantize(Decimal('0.01'))
                ) if calculation['total_cost'] > 0 else 0,
                'has_errors': len(ing['errors']) > 0,
                'errors': ing['errors']
            })
        
        return analysis
    
    def calculate_gross_margin(self, recipe_id: int, menu_price: Optional[Decimal] = None) -> Dict[str, Any]:
        """
        Calculate gross margin for a recipe
        
        Args:
            recipe_id: Recipe ID
            menu_price: Override menu price (uses stored price if not provided)
        """
        cursor = self.conn.cursor()
        
        # Get recipe and menu information
        recipe = cursor.execute("""
            SELECT r.recipe_id as id, r.recipe_name, r.menu_price as recipe_menu_price,
                   mi.menu_price as menu_item_price
            FROM recipes_actual r
            LEFT JOIN menu_items mi ON mi.recipe_id = r.recipe_id
            WHERE r.recipe_id = ?
        """, (recipe_id,)).fetchone()
        
        if not recipe:
            raise ValueError(f"Recipe {recipe_id} not found")
        
        # Determine menu price
        if menu_price is None:
            menu_price = (
                Decimal(str(recipe['menu_item_price'])) if recipe['menu_item_price']
                else Decimal(str(recipe['recipe_menu_price'])) if recipe['recipe_menu_price']
                else Decimal('0')
            )
        
        # Calculate cost
        calculation = self.calculate_recipe_cost_from_scratch(recipe_id)
        
        margin_calc = {
            'recipe_id': recipe_id,
            'recipe_name': recipe['recipe_name'],
            'menu_price': float(menu_price),
            'food_cost': float(calculation['total_cost']),
            'gross_profit': float(menu_price - calculation['total_cost']),
            'gross_margin_percent': 0,
            'food_cost_percent': 0,
            'target_food_cost_percent': 30,  # Industry standard
            'pricing_recommendation': None
        }
        
        if menu_price > 0:
            margin_calc['gross_margin_percent'] = float(
                ((menu_price - calculation['total_cost']) / menu_price * 100).quantize(Decimal('0.01'))
            )
            margin_calc['food_cost_percent'] = float(
                (calculation['total_cost'] / menu_price * 100).quantize(Decimal('0.01'))
            )
            
            # Pricing recommendation
            if margin_calc['food_cost_percent'] > 35:
                margin_calc['pricing_recommendation'] = "Consider increasing price - food cost too high"
            elif margin_calc['food_cost_percent'] < 25:
                margin_calc['pricing_recommendation'] = "Room for price reduction or portion increase"
            else:
                margin_calc['pricing_recommendation'] = "Pricing is well-balanced"
        
        return margin_calc
    
    def create_calculation_audit_trail(self, recipe_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Create detailed audit trail for calculations
        
        Args:
            recipe_id: Specific recipe ID or None for all calculations
        """
        if recipe_id:
            # Filter audit trail for specific recipe
            recipe_audits = [
                audit for audit in self.audit_trail 
                if audit['recipe_id'] == recipe_id
            ]
        else:
            recipe_audits = self.audit_trail
        
        audit_report = {
            'generated_at': datetime.now().isoformat(),
            'total_calculations': len(recipe_audits),
            'calculations': recipe_audits,
            'summary': {
                'total_recipes': len(set(a['recipe_id'] for a in recipe_audits)),
                'calculations_with_errors': sum(1 for a in recipe_audits if a['errors']),
                'calculations_with_warnings': sum(1 for a in recipe_audits if a['warnings']),
                'average_variance_from_pdf': None
            }
        }
        
        # Calculate average variance
        variances = [
            a['variance_from_pdf'] for a in recipe_audits 
            if a['variance_from_pdf'] is not None
        ]
        
        if variances:
            audit_report['summary']['average_variance_from_pdf'] = float(
                sum(variances) / len(variances)
            )
        
        return audit_report
    
    def batch_recalculate_all_recipes(self, recipe_type: Optional[str] = None,
                                     save_report: bool = True) -> Dict[str, Any]:
        """
        Batch recalculate all recipes with comprehensive reporting
        
        Args:
            recipe_type: Filter by recipe type (Main, Prep Recipe, etc.)
            save_report: Save detailed report to file
        """
        cursor = self.conn.cursor()
        
        # Get recipes to calculate
        query = "SELECT recipe_id as id, recipe_name, recipe_type, food_cost FROM recipes_actual"
        params = []
        
        if recipe_type:
            query += " WHERE recipe_type = ?"
            params.append(recipe_type)
        
        recipes = cursor.execute(query, params).fetchall()
        
        logger.info(f"Starting batch calculation for {len(recipes)} recipes")
        
        results = {
            'start_time': datetime.now().isoformat(),
            'total_recipes': len(recipes),
            'successful': 0,
            'failed': 0,
            'recipes': [],
            'summary_stats': {
                'total_calculated_cost': Decimal('0'),
                'total_pdf_stated_cost': Decimal('0'),
                'recipes_matching_pdf': 0,
                'recipes_with_variance': 0,
                'max_variance': Decimal('0'),
                'min_variance': Decimal('999999')
            }
        }
        
        for recipe in recipes:
            try:
                # Calculate cost
                calculation = self.calculate_recipe_cost_from_scratch(recipe['id'])
                
                recipe_result = {
                    'recipe_id': recipe['id'],
                    'recipe_name': recipe['recipe_name'],
                    'recipe_type': recipe['recipe_type'],
                    'calculated_cost': float(calculation['total_cost']),
                    'pdf_stated_cost': float(recipe['food_cost']) if recipe['food_cost'] else None,
                    'variance': float(calculation['variance_from_pdf']) if calculation['variance_from_pdf'] else 0,
                    'has_errors': len(calculation['errors']) > 0,
                    'has_warnings': len(calculation['warnings']) > 0,
                    'status': 'success'
                }
                
                # Update summary stats
                results['summary_stats']['total_calculated_cost'] += calculation['total_cost']
                
                if recipe['food_cost']:
                    results['summary_stats']['total_pdf_stated_cost'] += Decimal(str(recipe['food_cost']))
                    
                    if abs(calculation['variance_from_pdf']) <= Decimal('0.01'):
                        results['summary_stats']['recipes_matching_pdf'] += 1
                    else:
                        results['summary_stats']['recipes_with_variance'] += 1
                        
                        if calculation['variance_from_pdf'] > results['summary_stats']['max_variance']:
                            results['summary_stats']['max_variance'] = calculation['variance_from_pdf']
                        if calculation['variance_from_pdf'] < results['summary_stats']['min_variance']:
                            results['summary_stats']['min_variance'] = calculation['variance_from_pdf']
                
                results['recipes'].append(recipe_result)
                results['successful'] += 1
                
            except Exception as e:
                logger.error(f"Failed to calculate recipe {recipe['id']}: {e}")
                
                results['recipes'].append({
                    'recipe_id': recipe['id'],
                    'recipe_name': recipe['recipe_name'],
                    'status': 'failed',
                    'error': str(e)
                })
                results['failed'] += 1
        
        results['end_time'] = datetime.now().isoformat()
        
        # Convert Decimal to float for JSON serialization
        results['summary_stats']['total_calculated_cost'] = float(results['summary_stats']['total_calculated_cost'])
        results['summary_stats']['total_pdf_stated_cost'] = float(results['summary_stats']['total_pdf_stated_cost'])
        results['summary_stats']['max_variance'] = float(results['summary_stats']['max_variance'])
        results['summary_stats']['min_variance'] = float(results['summary_stats']['min_variance'])
        
        # Save report if requested
        if save_report:
            report_path = Path(f"calculation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(report_path, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Report saved to {report_path}")
            
            # Also create CSV for easy analysis
            csv_path = Path(f"calculation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'recipe_id', 'recipe_name', 'recipe_type', 
                    'calculated_cost', 'pdf_stated_cost', 'variance',
                    'has_errors', 'has_warnings', 'status'
                ])
                writer.writeheader()
                writer.writerows(results['recipes'])
            logger.info(f"CSV report saved to {csv_path}")
        
        return results
    
    def export_calculation_details(self, recipe_id: int, output_path: Optional[Path] = None) -> Path:
        """Export detailed calculation breakdown for a recipe"""
        calculation = self.calculate_recipe_cost_from_scratch(recipe_id)
        
        if not output_path:
            output_path = Path(f"calculation_details_{recipe_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # Convert Decimal to float for JSON serialization
        def decimal_to_float(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: decimal_to_float(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [decimal_to_float(item) for item in obj]
            return obj
        
        calculation_export = decimal_to_float(calculation)
        
        with open(output_path, 'w') as f:
            json.dump(calculation_export, f, indent=2)
        
        logger.info(f"Calculation details exported to {output_path}")
        return output_path
    
    def validate_against_pdf_data(self, pdf_directory: str = None) -> Dict[str, Any]:
        """
        Validate all recipes against PDF extracted data
        
        Args:
            pdf_directory: Path to directory containing PDF files
        
        Returns:
            Comprehensive validation report
        """
        if not PDF_SUPPORT:
            return {
                'error': 'PDF support not available - install PyPDF2',
                'status': 'failed'
            }
        
        if not pdf_directory:
            pdf_directory = "reference/LJ_DATA_Ref/updated_recipes_csv_pdf"
        
        extractor = PDFRecipeExtractor(pdf_directory)
        pdf_data = extractor.extract_all_pdfs()
        
        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'total_pdfs': len(pdf_data),
            'matched_recipes': 0,
            'unmatched_pdfs': [],
            'validation_details': []
        }
        
        cursor = self.conn.cursor()
        
        for pdf_name, pdf_recipe in pdf_data.items():
            # Try to match PDF to database recipe
            recipe_name = pdf_recipe.get('recipe_name', '')
            
            # Try exact match first
            db_recipe = cursor.execute("""
                SELECT recipe_id, recipe_name, food_cost
                FROM recipes_actual
                WHERE LOWER(TRIM(recipe_name)) = LOWER(TRIM(?))
            """, (recipe_name,)).fetchone()
            
            if not db_recipe:
                # Try fuzzy match
                db_recipe = cursor.execute("""
                    SELECT recipe_id, recipe_name, food_cost
                    FROM recipes_actual
                    WHERE LOWER(recipe_name) LIKE LOWER(?)
                    LIMIT 1
                """, (f"%{recipe_name.split()[0]}%",)).fetchone()
            
            if db_recipe:
                validation_results['matched_recipes'] += 1
                
                # Validate cost
                if pdf_recipe.get('food_cost'):
                    validation = self.validate_against_pdf_cost(
                        db_recipe['recipe_id'],
                        Decimal(str(pdf_recipe['food_cost']))
                    )
                    
                    validation_results['validation_details'].append({
                        'pdf_file': pdf_name,
                        'recipe_name': db_recipe['recipe_name'],
                        'recipe_id': db_recipe['recipe_id'],
                        'validation': validation
                    })
            else:
                validation_results['unmatched_pdfs'].append({
                    'pdf_file': pdf_name,
                    'pdf_recipe_name': recipe_name
                })
        
        # Summary statistics
        valid_count = sum(
            1 for v in validation_results['validation_details']
            if v['validation']['is_valid']
        )
        
        validation_results['summary'] = {
            'total_validated': len(validation_results['validation_details']),
            'valid_calculations': valid_count,
            'invalid_calculations': len(validation_results['validation_details']) - valid_count,
            'validation_rate': (
                valid_count / len(validation_results['validation_details']) * 100
                if validation_results['validation_details'] else 0
            )
        }
        
        return validation_results
    
    def generate_comprehensive_report(self, output_dir: str = "reports") -> Path:
        """
        Generate a comprehensive calculation and validation report
        
        Returns:
            Path to the generated report directory
        """
        output_path = Path(output_dir) / f"calculation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Generating comprehensive report in {output_path}")
        
        # 1. Batch calculation report
        logger.info("Running batch calculations...")
        batch_report = self.batch_recalculate_all_recipes(save_report=False)
        
        with open(output_path / "batch_calculations.json", 'w') as f:
            json.dump(batch_report, f, indent=2)
        
        # 2. PDF validation report (if available)
        if PDF_SUPPORT:
            logger.info("Validating against PDF data...")
            pdf_validation = self.validate_against_pdf_data()
            
            with open(output_path / "pdf_validation.json", 'w') as f:
                json.dump(pdf_validation, f, indent=2, default=str)
        
        # 3. Audit trail
        audit_report = self.create_calculation_audit_trail()
        
        with open(output_path / "audit_trail.json", 'w') as f:
            json.dump(audit_report, f, indent=2, default=str)
        
        # 4. Summary report
        summary = {
            'report_generated': datetime.now().isoformat(),
            'total_recipes_calculated': batch_report['total_recipes'],
            'successful_calculations': batch_report['successful'],
            'failed_calculations': batch_report['failed'],
            'average_food_cost': float(
                batch_report['summary_stats']['total_calculated_cost'] / 
                batch_report['successful']
            ) if batch_report['successful'] > 0 else 0,
            'pdf_validation_available': PDF_SUPPORT,
            'calculation_accuracy': None
        }
        
        if PDF_SUPPORT and 'summary' in pdf_validation:
            summary['calculation_accuracy'] = pdf_validation['summary']['validation_rate']
        
        # Generate markdown summary
        with open(output_path / "SUMMARY.md", 'w') as f:
            f.write("# Recipe Cost Calculation Report\n\n")
            f.write(f"Generated: {summary['report_generated']}\n\n")
            
            f.write("## Overview\n\n")
            f.write(f"- Total Recipes: {summary['total_recipes_calculated']}\n")
            f.write(f"- Successful Calculations: {summary['successful_calculations']}\n")
            f.write(f"- Failed Calculations: {summary['failed_calculations']}\n")
            f.write(f"- Average Food Cost: ${summary['average_food_cost']:.2f}\n")
            
            if summary['calculation_accuracy'] is not None:
                f.write(f"- Calculation Accuracy: {summary['calculation_accuracy']:.1f}%\n")
            
            f.write("\n## Key Findings\n\n")
            
            # List recipes with largest variances
            if batch_report['recipes']:
                variances = sorted(
                    [r for r in batch_report['recipes'] if r.get('variance', 0) != 0],
                    key=lambda x: abs(x['variance']),
                    reverse=True
                )[:10]
                
                if variances:
                    f.write("### Top Cost Variances from PDF\n\n")
                    f.write("| Recipe | Calculated | PDF Stated | Variance |\n")
                    f.write("|--------|------------|------------|----------|\n")
                    
                    for r in variances:
                        f.write(
                            f"| {r['recipe_name']} | "
                            f"${r['calculated_cost']:.2f} | "
                            f"${r.get('pdf_stated_cost', 0):.2f} | "
                            f"${r['variance']:.2f} |\n"
                        )
            
            # List recipes with errors
            errors = [r for r in batch_report['recipes'] if r.get('has_errors')]
            if errors:
                f.write(f"\n### Recipes with Calculation Errors ({len(errors)})\n\n")
                for r in errors[:10]:
                    f.write(f"- {r['recipe_name']}\n")
                
                if len(errors) > 10:
                    f.write(f"- ... and {len(errors) - 10} more\n")
        
        logger.info(f"Comprehensive report generated in {output_path}")
        return output_path
    
    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()


def main():
    """Test the calculation rebuilder"""
    rebuilder = CalculationRebuilder()
    
    # Test single recipe calculation
    try:
        # Get a sample recipe
        cursor = rebuilder.conn.cursor()
        sample_recipe = cursor.execute("""
            SELECT recipe_id as id, recipe_name 
            FROM recipes_actual 
            WHERE recipe_type = 'Recipe' 
            LIMIT 1
        """).fetchone()
        
        if sample_recipe:
            recipe_id = sample_recipe['id']
            logger.info(f"\nTesting calculation for: {sample_recipe['recipe_name']}")
            
            # Calculate cost
            calculation = rebuilder.calculate_recipe_cost_from_scratch(recipe_id)
            
            print(f"\nRecipe: {calculation['recipe_name']}")
            print(f"Total Cost: ${calculation['total_cost']}")
            print(f"PDF Stated Cost: ${calculation['pdf_stated_cost']}")
            print(f"Variance: ${calculation['variance_from_pdf']}")
            
            if calculation['warnings']:
                print(f"\nWarnings:")
                for warning in calculation['warnings']:
                    print(f"  - {warning}")
            
            if calculation['errors']:
                print(f"\nErrors:")
                for error in calculation['errors']:
                    print(f"  - {error}")
            
            # Test gross margin calculation
            margin = rebuilder.calculate_gross_margin(recipe_id)
            print(f"\nGross Margin Analysis:")
            print(f"  Menu Price: ${margin['menu_price']}")
            print(f"  Food Cost %: {margin['food_cost_percent']}%")
            print(f"  Gross Margin %: {margin['gross_margin_percent']}%")
            print(f"  Recommendation: {margin['pricing_recommendation']}")
            
            # Export details
            export_path = rebuilder.export_calculation_details(recipe_id)
            print(f"\nDetailed calculation exported to: {export_path}")
        
        # Run batch calculation
        print("\n\nRunning batch calculation for all recipes...")
        batch_results = rebuilder.batch_recalculate_all_recipes(save_report=True)
        
        print(f"\nBatch Calculation Summary:")
        print(f"  Total Recipes: {batch_results['total_recipes']}")
        print(f"  Successful: {batch_results['successful']}")
        print(f"  Failed: {batch_results['failed']}")
        print(f"  Matching PDF Cost: {batch_results['summary_stats']['recipes_matching_pdf']}")
        print(f"  With Variance: {batch_results['summary_stats']['recipes_with_variance']}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Recipe Cost Calculation Rebuilder')
    parser.add_argument('--recipe-id', type=int, help='Calculate specific recipe by ID')
    parser.add_argument('--recipe-name', type=str, help='Calculate specific recipe by name')
    parser.add_argument('--batch', action='store_true', help='Run batch calculation for all recipes')
    parser.add_argument('--validate-pdf', action='store_true', help='Validate against PDF data')
    parser.add_argument('--report', action='store_true', help='Generate comprehensive report')
    parser.add_argument('--db', type=str, default='restaurant_calculator.db', help='Database path')
    
    args = parser.parse_args()
    
    rebuilder = CalculationRebuilder(args.db)
    
    if args.recipe_id:
        # Calculate specific recipe by ID
        try:
            calculation = rebuilder.calculate_recipe_cost_from_scratch(args.recipe_id)
            print(f"\nRecipe: {calculation['recipe_name']}")
            print(f"Total Cost: ${calculation['total_cost']}")
            print(f"PDF Stated Cost: ${calculation['pdf_stated_cost']}")
            print(f"Variance: ${calculation['variance_from_pdf']}")
            
            # Export details
            export_path = rebuilder.export_calculation_details(args.recipe_id)
            print(f"\nDetails exported to: {export_path}")
            
        except Exception as e:
            print(f"Error calculating recipe {args.recipe_id}: {e}")
    
    elif args.recipe_name:
        # Find and calculate recipe by name
        cursor = rebuilder.conn.cursor()
        recipe = cursor.execute("""
            SELECT recipe_id 
            FROM recipes_actual 
            WHERE LOWER(recipe_name) LIKE LOWER(?)
            LIMIT 1
        """, (f"%{args.recipe_name}%",)).fetchone()
        
        if recipe:
            calculation = rebuilder.calculate_recipe_cost_from_scratch(recipe['recipe_id'])
            print(f"\nRecipe: {calculation['recipe_name']}")
            print(f"Total Cost: ${calculation['total_cost']}")
            print(f"PDF Stated Cost: ${calculation['pdf_stated_cost']}")
            print(f"Variance: ${calculation['variance_from_pdf']}")
        else:
            print(f"Recipe '{args.recipe_name}' not found")
    
    elif args.batch:
        # Run batch calculation
        print("Running batch calculation for all recipes...")
        results = rebuilder.batch_recalculate_all_recipes(save_report=True)
        print(f"\nCompleted: {results['successful']} successful, {results['failed']} failed")
        print(f"Reports saved to calculation_report_*.json/csv")
    
    elif args.validate_pdf:
        # Validate against PDF
        if PDF_SUPPORT:
            print("Validating recipes against PDF data...")
            validation = rebuilder.validate_against_pdf_data()
            print(f"\nValidation Results:")
            print(f"Matched Recipes: {validation['matched_recipes']}/{validation['total_pdfs']}")
            if 'summary' in validation:
                print(f"Validation Rate: {validation['summary']['validation_rate']:.1f}%")
        else:
            print("PDF support not available - install PyPDF2")
    
    elif args.report:
        # Generate comprehensive report
        print("Generating comprehensive report...")
        report_path = rebuilder.generate_comprehensive_report()
        print(f"\nReport generated in: {report_path}")
    
    else:
        # Run default test
        main()