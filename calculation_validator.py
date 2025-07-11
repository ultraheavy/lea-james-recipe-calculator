#!/usr/bin/env python3
"""
End-to-End Calculation Validation System
Tests the entire calculation chain from vendor prices to menu margins
Validates against PDF stated values and provides comprehensive accuracy reporting
"""

import sqlite3
import logging
import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import csv
from collections import defaultdict

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import dependencies
try:
    from calculation_rebuilder import CalculationRebuilder
    from uom_standardizer import UOMStandardizer
    from vendor_pricing_reconciler import VendorPricingReconciler
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Some dependencies not available: {e}")
    DEPENDENCIES_AVAILABLE = False


class CalculationValidator:
    """Comprehensive calculation validation system"""
    
    def __init__(self, db_path: str = 'restaurant_calculator.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Initialize supporting modules if available
        if DEPENDENCIES_AVAILABLE:
            self.calculation_rebuilder = CalculationRebuilder(db_path)
            self.uom_standardizer = UOMStandardizer(db_path)
            self.vendor_reconciler = VendorPricingReconciler(db_path)
        
        # Validation results storage
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'calculation_chain_tests': [],
            'accuracy_metrics': {},
            'systematic_errors': [],
            'recommendations': []
        }
        
        # Accuracy thresholds
        self.TOLERANCE_CENTS = Decimal('0.01')  # $0.01 tolerance
        self.TOLERANCE_PERCENT = Decimal('0.1')  # 0.1% tolerance
        
    def run_full_system_validation(self) -> Dict[str, Any]:
        """
        Run complete end-to-end validation of the calculation system
        
        Returns:
            Comprehensive validation report
        """
        logger.info("Starting full system calculation validation...")
        
        # 1. Validate vendor pricing foundation
        logger.info("Step 1: Validating vendor pricing data...")
        vendor_validation = self._validate_vendor_pricing()
        
        # 2. Validate UOM conversions
        logger.info("Step 2: Validating UOM conversions...")
        uom_validation = self._validate_uom_conversions()
        
        # 3. Test recipe calculation chains
        logger.info("Step 3: Testing recipe calculation chains...")
        calculation_validation = self._test_calculation_chains()
        
        # 4. Validate menu margins
        logger.info("Step 4: Validating menu margin calculations...")
        margin_validation = self._validate_menu_margins()
        
        # 5. Compare against PDF values
        logger.info("Step 5: Comparing against PDF stated values...")
        pdf_validation = self._validate_against_pdf_values()
        
        # 6. Calculate accuracy metrics
        logger.info("Step 6: Calculating accuracy metrics...")
        self._calculate_accuracy_metrics()
        
        # 7. Identify systematic errors
        logger.info("Step 7: Identifying systematic errors...")
        self._identify_systematic_errors()
        
        # 8. Generate recommendations
        logger.info("Step 8: Generating recommendations...")
        self._generate_recommendations()
        
        # Compile final report
        self.validation_results['vendor_validation'] = vendor_validation
        self.validation_results['uom_validation'] = uom_validation
        self.validation_results['calculation_validation'] = calculation_validation
        self.validation_results['margin_validation'] = margin_validation
        self.validation_results['pdf_validation'] = pdf_validation
        
        return self.validation_results
    
    def _validate_vendor_pricing(self) -> Dict[str, Any]:
        """Validate vendor pricing data integrity"""
        cursor = self.conn.cursor()
        
        validation = {
            'total_inventory_items': 0,
            'items_with_pricing': 0,
            'items_missing_pricing': [],
            'items_with_outdated_pricing': [],
            'items_with_pack_size_issues': [],
            'validation_status': 'passed'
        }
        
        # Get all inventory items
        items = cursor.execute("""
            SELECT id, item_description, current_price, pack_size, 
                   purchase_unit, last_purchased_date
            FROM inventory
        """).fetchall()
        
        validation['total_inventory_items'] = len(items)
        
        for item in items:
            # Check for pricing
            if not item['current_price'] or item['current_price'] <= 0:
                validation['items_missing_pricing'].append({
                    'id': item['id'],
                    'description': item['item_description']
                })
            else:
                validation['items_with_pricing'] += 1
            
            # Check for outdated pricing (over 90 days old)
            if item['last_purchased_date']:
                try:
                    last_date = datetime.strptime(item['last_purchased_date'], '%Y-%m-%d')
                    if (datetime.now() - last_date).days > 90:
                        validation['items_with_outdated_pricing'].append({
                            'id': item['id'],
                            'description': item['item_description'],
                            'last_updated': item['last_purchased_date']
                        })
                except ValueError:
                    pass
            
            # Check pack size format
            if not item['pack_size'] or not item['purchase_unit']:
                validation['items_with_pack_size_issues'].append({
                    'id': item['id'],
                    'description': item['item_description'],
                    'pack_size': item['pack_size'],
                    'purchase_unit': item['purchase_unit']
                })
        
        # Determine validation status
        if validation['items_missing_pricing'] or validation['items_with_pack_size_issues']:
            validation['validation_status'] = 'failed'
        elif validation['items_with_outdated_pricing']:
            validation['validation_status'] = 'warning'
        
        return validation
    
    def _validate_uom_conversions(self) -> Dict[str, Any]:
        """Test UOM conversion accuracy"""
        validation = {
            'conversion_tests': [],
            'failed_conversions': [],
            'missing_conversions': [],
            'validation_status': 'passed'
        }
        
        # Test common conversions used in recipes
        test_conversions = [
            ('1 lb', 'oz', Decimal('16')),
            ('1 kg', 'g', Decimal('1000')),
            ('1 gal', 'fl oz', Decimal('128')),
            ('1 cup', 'tbsp', Decimal('16')),
            ('1 dozen', 'each', Decimal('12'))
        ]
        
        for input_str, target_unit, expected in test_conversions:
            try:
                # Parse and convert
                quantity, unit = self.uom_standardizer.parse_measurement(input_str)
                
                # Try conversion
                context = {}  # Basic context
                result = self.uom_standardizer.convert_units(
                    quantity, unit, target_unit, context
                )
                
                if result:
                    # Check accuracy
                    if abs(result - expected) <= Decimal('0.001'):
                        validation['conversion_tests'].append({
                            'input': input_str,
                            'target': target_unit,
                            'expected': float(expected),
                            'actual': float(result),
                            'status': 'passed'
                        })
                    else:
                        validation['failed_conversions'].append({
                            'input': input_str,
                            'target': target_unit,
                            'expected': float(expected),
                            'actual': float(result),
                            'variance': float(result - expected)
                        })
                        validation['validation_status'] = 'failed'
                else:
                    validation['missing_conversions'].append({
                        'from': unit,
                        'to': target_unit
                    })
                    validation['validation_status'] = 'warning'
                    
            except Exception as e:
                validation['failed_conversions'].append({
                    'input': input_str,
                    'error': str(e)
                })
                validation['validation_status'] = 'failed'
        
        return validation
    
    def _test_calculation_chains(self) -> Dict[str, Any]:
        """Test complete calculation chains for representative recipes"""
        cursor = self.conn.cursor()
        
        validation = {
            'recipes_tested': 0,
            'calculation_chains': [],
            'chain_failures': [],
            'validation_status': 'passed'
        }
        
        # Select representative recipes from each category
        categories = ['Mains', 'Sides', 'Sauces', 'Prep Recipe']
        
        for category in categories:
            # Get sample recipes
            recipes = cursor.execute("""
                SELECT r.recipe_id, r.recipe_name, r.recipe_type, r.food_cost as pdf_cost
                FROM recipes_actual r
                WHERE r.recipe_type = ? OR r.recipe_group = ?
                LIMIT 3
            """, (category, category)).fetchall()
            
            for recipe in recipes:
                try:
                    # Test calculation chain
                    chain_result = self._test_single_calculation_chain(recipe)
                    validation['calculation_chains'].append(chain_result)
                    validation['recipes_tested'] += 1
                    
                    if chain_result['status'] != 'passed':
                        validation['chain_failures'].append({
                            'recipe_id': recipe['recipe_id'],
                            'recipe_name': recipe['recipe_name'],
                            'failure_reason': chain_result.get('error', 'Unknown error')
                        })
                        validation['validation_status'] = 'warning'
                        
                except Exception as e:
                    logger.error(f"Chain test failed for recipe {recipe['recipe_id']}: {e}")
                    validation['chain_failures'].append({
                        'recipe_id': recipe['recipe_id'],
                        'recipe_name': recipe['recipe_name'],
                        'failure_reason': str(e)
                    })
                    validation['validation_status'] = 'failed'
        
        return validation
    
    def _test_single_calculation_chain(self, recipe: sqlite3.Row) -> Dict[str, Any]:
        """Test calculation chain for a single recipe"""
        chain_test = {
            'recipe_id': recipe['recipe_id'],
            'recipe_name': recipe['recipe_name'],
            'checkpoints': [],
            'status': 'passed',
            'total_variance': Decimal('0')
        }
        
        # Calculate from scratch
        calculation = self.calculation_rebuilder.calculate_recipe_cost_from_scratch(
            recipe['recipe_id']
        )
        
        # Checkpoint 1: Vendor price to ingredient cost
        for ingredient in calculation['ingredients']:
            checkpoint = {
                'name': f"Ingredient: {ingredient['ingredient_name']}",
                'type': 'vendor_to_ingredient',
                'calculated_cost': float(ingredient['total_cost']),
                'has_errors': len(ingredient['errors']) > 0,
                'errors': ingredient['errors']
            }
            
            if checkpoint['has_errors']:
                chain_test['status'] = 'warning'
            
            chain_test['checkpoints'].append(checkpoint)
        
        # Checkpoint 2: Recipe total cost
        recipe_checkpoint = {
            'name': 'Recipe Total Cost',
            'type': 'recipe_total',
            'calculated_cost': float(calculation['total_cost']),
            'pdf_stated_cost': float(recipe['pdf_cost']) if recipe['pdf_cost'] else None,
            'variance': None,
            'variance_percent': None
        }
        
        if recipe_checkpoint['pdf_stated_cost']:
            variance = Decimal(str(calculation['total_cost'])) - Decimal(str(recipe['pdf_cost']))
            recipe_checkpoint['variance'] = float(variance)
            recipe_checkpoint['variance_percent'] = float(
                (variance / Decimal(str(recipe['pdf_cost'])) * 100) 
                if recipe['pdf_cost'] > 0 else 0
            )
            
            # Check if within tolerance
            if abs(variance) > self.TOLERANCE_CENTS:
                chain_test['status'] = 'failed' if abs(variance) > Decimal('0.10') else 'warning'
                chain_test['total_variance'] = variance
        
        chain_test['checkpoints'].append(recipe_checkpoint)
        
        # Checkpoint 3: Menu margin (if applicable)
        cursor = self.conn.cursor()
        menu_item = cursor.execute("""
            SELECT mi.menu_price, mi.id
            FROM menu_items mi
            WHERE mi.recipe_id = ?
            LIMIT 1
        """, (recipe['recipe_id'],)).fetchone()
        
        if menu_item and menu_item['menu_price']:
            margin = self.calculation_rebuilder.calculate_gross_margin(
                recipe['recipe_id'], 
                Decimal(str(menu_item['menu_price']))
            )
            
            margin_checkpoint = {
                'name': 'Menu Margin',
                'type': 'menu_margin',
                'menu_price': margin['menu_price'],
                'food_cost': margin['food_cost'],
                'food_cost_percent': margin['food_cost_percent'],
                'gross_margin_percent': margin['gross_margin_percent'],
                'within_target': 25 <= margin['food_cost_percent'] <= 35
            }
            
            if not margin_checkpoint['within_target']:
                chain_test['status'] = 'warning' if chain_test['status'] == 'passed' else chain_test['status']
            
            chain_test['checkpoints'].append(margin_checkpoint)
        
        return chain_test
    
    def _validate_menu_margins(self) -> Dict[str, Any]:
        """Validate menu margin calculations"""
        cursor = self.conn.cursor()
        
        validation = {
            'total_menu_items': 0,
            'items_validated': 0,
            'margin_distribution': {
                'excellent': 0,  # < 25% food cost
                'good': 0,       # 25-30% food cost
                'acceptable': 0,  # 30-35% food cost
                'poor': 0,       # > 35% food cost
                'no_cost': 0     # Missing cost data
            },
            'items_needing_attention': [],
            'validation_status': 'passed'
        }
        
        # Get all menu items with recipes
        menu_items = cursor.execute("""
            SELECT mi.id, mi.item_name, mi.menu_price, mi.recipe_id,
                   r.food_cost, r.recipe_name
            FROM menu_items mi
            LEFT JOIN recipes_actual r ON mi.recipe_id = r.recipe_id
            WHERE mi.menu_price > 0
        """).fetchall()
        
        validation['total_menu_items'] = len(menu_items)
        
        for item in menu_items:
            if item['recipe_id'] and item['food_cost']:
                try:
                    # Calculate margin
                    margin = self.calculation_rebuilder.calculate_gross_margin(
                        item['recipe_id'],
                        Decimal(str(item['menu_price']))
                    )
                    
                    validation['items_validated'] += 1
                    
                    # Categorize margin
                    fc_percent = margin['food_cost_percent']
                    if fc_percent < 25:
                        validation['margin_distribution']['excellent'] += 1
                    elif fc_percent <= 30:
                        validation['margin_distribution']['good'] += 1
                    elif fc_percent <= 35:
                        validation['margin_distribution']['acceptable'] += 1
                    else:
                        validation['margin_distribution']['poor'] += 1
                        validation['items_needing_attention'].append({
                            'item_name': item['item_name'],
                            'menu_price': float(item['menu_price']),
                            'food_cost': margin['food_cost'],
                            'food_cost_percent': fc_percent,
                            'recommendation': margin['pricing_recommendation']
                        })
                        
                except Exception as e:
                    logger.error(f"Margin calculation failed for {item['item_name']}: {e}")
                    validation['margin_distribution']['no_cost'] += 1
            else:
                validation['margin_distribution']['no_cost'] += 1
        
        # Set validation status
        if validation['margin_distribution']['no_cost'] > validation['total_menu_items'] * 0.1:
            validation['validation_status'] = 'failed'
        elif validation['margin_distribution']['poor'] > validation['total_menu_items'] * 0.2:
            validation['validation_status'] = 'warning'
        
        return validation
    
    def _validate_against_pdf_values(self) -> Dict[str, Any]:
        """Validate calculations against PDF stated values"""
        cursor = self.conn.cursor()
        
        validation = {
            'recipes_with_pdf_values': 0,
            'exact_matches': 0,
            'within_tolerance': 0,
            'significant_variances': [],
            'variance_distribution': defaultdict(int),
            'validation_status': 'passed'
        }
        
        # Get all recipes with PDF values
        recipes = cursor.execute("""
            SELECT recipe_id, recipe_name, food_cost as pdf_cost
            FROM recipes_actual
            WHERE food_cost IS NOT NULL AND food_cost > 0
        """).fetchall()
        
        validation['recipes_with_pdf_values'] = len(recipes)
        
        for recipe in recipes:
            try:
                # Calculate cost
                calculation = self.calculation_rebuilder.calculate_recipe_cost_from_scratch(
                    recipe['recipe_id']
                )
                
                pdf_cost = Decimal(str(recipe['pdf_cost']))
                calc_cost = calculation['total_cost']
                variance = calc_cost - pdf_cost
                variance_percent = (variance / pdf_cost * 100) if pdf_cost > 0 else 0
                
                # Categorize variance
                if abs(variance) <= self.TOLERANCE_CENTS:
                    validation['exact_matches'] += 1
                    validation['variance_distribution']['exact'] += 1
                elif abs(variance) <= Decimal('0.10'):  # Within $0.10
                    validation['within_tolerance'] += 1
                    validation['variance_distribution']['small'] += 1
                else:
                    validation['variance_distribution']['significant'] += 1
                    validation['significant_variances'].append({
                        'recipe_id': recipe['recipe_id'],
                        'recipe_name': recipe['recipe_name'],
                        'calculated_cost': float(calc_cost),
                        'pdf_cost': float(pdf_cost),
                        'variance': float(variance),
                        'variance_percent': float(variance_percent),
                        'calculation_errors': calculation.get('errors', []),
                        'calculation_warnings': calculation.get('warnings', [])
                    })
                    
            except Exception as e:
                logger.error(f"PDF validation failed for recipe {recipe['recipe_id']}: {e}")
                validation['variance_distribution']['error'] += 1
        
        # Calculate validation rate
        if validation['recipes_with_pdf_values'] > 0:
            validation['accuracy_rate'] = (
                (validation['exact_matches'] + validation['within_tolerance']) / 
                validation['recipes_with_pdf_values'] * 100
            )
            
            if validation['accuracy_rate'] < 80:
                validation['validation_status'] = 'failed'
            elif validation['accuracy_rate'] < 90:
                validation['validation_status'] = 'warning'
        
        return validation
    
    def _calculate_accuracy_metrics(self):
        """Calculate overall system accuracy metrics"""
        metrics = {
            'overall_accuracy': 0,
            'calculation_success_rate': 0,
            'average_variance': 0,
            'variance_std_dev': 0,
            'confidence_level': 'low'
        }
        
        # Aggregate results from all validations
        total_tests = self.validation_results['total_validations']
        successful_tests = self.validation_results['successful_validations']
        
        if total_tests > 0:
            metrics['calculation_success_rate'] = (successful_tests / total_tests) * 100
        
        # Calculate variance statistics from PDF validation
        if 'pdf_validation' in self.validation_results:
            pdf_val = self.validation_results['pdf_validation']
            if pdf_val.get('recipes_with_pdf_values', 0) > 0:
                metrics['overall_accuracy'] = pdf_val.get('accuracy_rate', 0)
                
                # Calculate average variance
                if pdf_val.get('significant_variances'):
                    variances = [v['variance'] for v in pdf_val['significant_variances']]
                    metrics['average_variance'] = sum(variances) / len(variances)
                    
                    # Calculate standard deviation
                    if len(variances) > 1:
                        mean = metrics['average_variance']
                        variance = sum((x - mean) ** 2 for x in variances) / len(variances)
                        metrics['variance_std_dev'] = variance ** 0.5
        
        # Determine confidence level
        if metrics['overall_accuracy'] >= 95 and metrics['calculation_success_rate'] >= 95:
            metrics['confidence_level'] = 'high'
        elif metrics['overall_accuracy'] >= 85 and metrics['calculation_success_rate'] >= 85:
            metrics['confidence_level'] = 'medium'
        else:
            metrics['confidence_level'] = 'low'
        
        self.validation_results['accuracy_metrics'] = metrics
    
    def _identify_systematic_errors(self):
        """Identify patterns in calculation errors"""
        systematic_errors = []
        
        # Analyze calculation chain failures
        if 'calculation_validation' in self.validation_results:
            calc_val = self.validation_results['calculation_validation']
            
            # Group failures by type
            error_patterns = defaultdict(list)
            
            for chain in calc_val.get('calculation_chains', []):
                if chain['status'] != 'passed':
                    for checkpoint in chain['checkpoints']:
                        if checkpoint.get('has_errors'):
                            for error in checkpoint.get('errors', []):
                                error_patterns[error].append(chain['recipe_name'])
            
            # Identify systematic patterns
            for error_msg, affected_recipes in error_patterns.items():
                if len(affected_recipes) >= 3:  # Pattern threshold
                    systematic_errors.append({
                        'error_type': 'calculation_error',
                        'pattern': error_msg,
                        'frequency': len(affected_recipes),
                        'affected_recipes': affected_recipes[:5],  # Sample
                        'impact': 'high' if len(affected_recipes) > 10 else 'medium'
                    })
        
        # Analyze UOM conversion failures
        if 'uom_validation' in self.validation_results:
            uom_val = self.validation_results['uom_validation']
            
            if uom_val.get('missing_conversions'):
                systematic_errors.append({
                    'error_type': 'missing_conversions',
                    'pattern': 'Missing unit conversions',
                    'frequency': len(uom_val['missing_conversions']),
                    'details': uom_val['missing_conversions'],
                    'impact': 'high'
                })
        
        # Analyze vendor pricing issues
        if 'vendor_validation' in self.validation_results:
            vendor_val = self.validation_results['vendor_validation']
            
            if len(vendor_val.get('items_missing_pricing', [])) > 5:
                systematic_errors.append({
                    'error_type': 'missing_vendor_pricing',
                    'pattern': 'Inventory items without pricing',
                    'frequency': len(vendor_val['items_missing_pricing']),
                    'impact': 'critical'
                })
        
        self.validation_results['systematic_errors'] = systematic_errors
    
    def _generate_recommendations(self):
        """Generate actionable recommendations based on validation results"""
        recommendations = []
        
        # Based on systematic errors
        for error in self.validation_results.get('systematic_errors', []):
            if error['error_type'] == 'missing_vendor_pricing':
                recommendations.append({
                    'priority': 'critical',
                    'category': 'data_quality',
                    'recommendation': f"Update pricing for {error['frequency']} inventory items",
                    'action': 'Review and update vendor pricing data',
                    'impact': 'Will improve calculation accuracy significantly'
                })
            
            elif error['error_type'] == 'missing_conversions':
                recommendations.append({
                    'priority': 'high',
                    'category': 'system_configuration',
                    'recommendation': 'Add missing unit conversions to the system',
                    'action': 'Configure conversion factors for missing unit pairs',
                    'impact': 'Will enable accurate cost calculations for affected ingredients'
                })
        
        # Based on accuracy metrics
        metrics = self.validation_results.get('accuracy_metrics', {})
        if metrics.get('confidence_level') == 'low':
            recommendations.append({
                'priority': 'critical',
                'category': 'system_review',
                'recommendation': 'Conduct comprehensive system review',
                'action': 'Review calculation logic and data quality issues',
                'impact': 'System accuracy below acceptable threshold'
            })
        
        # Based on margin validation
        if 'margin_validation' in self.validation_results:
            margin_val = self.validation_results['margin_validation']
            if margin_val.get('items_needing_attention'):
                recommendations.append({
                    'priority': 'high',
                    'category': 'pricing_strategy',
                    'recommendation': f"Review pricing for {len(margin_val['items_needing_attention'])} menu items",
                    'action': 'Adjust menu prices or reduce costs for items with poor margins',
                    'impact': 'Will improve overall profitability'
                })
        
        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 999))
        
        self.validation_results['recommendations'] = recommendations
    
    def generate_validation_report(self, output_dir: str = "validation_reports") -> Path:
        """Generate comprehensive validation report"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_dir = output_path / f"validation_report_{timestamp}"
        report_dir.mkdir(exist_ok=True)
        
        logger.info(f"Generating validation report in {report_dir}")
        
        # 1. Save raw validation results
        with open(report_dir / "validation_results.json", 'w') as f:
            json.dump(self.validation_results, f, indent=2, default=str)
        
        # 2. Generate accuracy scorecard
        self._generate_accuracy_scorecard(report_dir)
        
        # 3. Generate error analysis report
        self._generate_error_analysis(report_dir)
        
        # 4. Generate management summary
        self._generate_management_summary(report_dir)
        
        # 5. Export validation details for drill-down
        self._export_validation_details(report_dir)
        
        logger.info(f"Validation report generated in {report_dir}")
        return report_dir
    
    def _generate_accuracy_scorecard(self, output_dir: Path):
        """Generate accuracy scorecard"""
        metrics = self.validation_results.get('accuracy_metrics', {})
        
        with open(output_dir / "accuracy_scorecard.md", 'w') as f:
            f.write("# Calculation Accuracy Scorecard\n\n")
            f.write(f"Generated: {self.validation_results['timestamp']}\n\n")
            
            f.write("## Overall Metrics\n\n")
            f.write(f"- **Overall Accuracy**: {metrics.get('overall_accuracy', 0):.1f}%\n")
            f.write(f"- **Calculation Success Rate**: {metrics.get('calculation_success_rate', 0):.1f}%\n")
            f.write(f"- **Confidence Level**: {metrics.get('confidence_level', 'unknown').upper()}\n")
            f.write(f"- **Average Variance**: ${abs(metrics.get('average_variance', 0)):.2f}\n\n")
            
            # Component scores
            f.write("## Component Validation\n\n")
            
            components = [
                ('Vendor Pricing', self.validation_results.get('vendor_validation', {})),
                ('UOM Conversions', self.validation_results.get('uom_validation', {})),
                ('Recipe Calculations', self.validation_results.get('calculation_validation', {})),
                ('Menu Margins', self.validation_results.get('margin_validation', {})),
                ('PDF Accuracy', self.validation_results.get('pdf_validation', {}))
            ]
            
            f.write("| Component | Status | Details |\n")
            f.write("|-----------|--------|--------|\n")
            
            for name, validation in components:
                status = validation.get('validation_status', 'unknown')
                status_icon = '✅' if status == 'passed' else '⚠️' if status == 'warning' else '❌'
                
                details = self._get_component_details(name, validation)
                f.write(f"| {name} | {status_icon} {status.upper()} | {details} |\n")
    
    def _get_component_details(self, component_name: str, validation: Dict) -> str:
        """Get summary details for a component"""
        if component_name == 'Vendor Pricing':
            total = validation.get('total_inventory_items', 0)
            with_pricing = validation.get('items_with_pricing', 0)
            return f"{with_pricing}/{total} items priced"
        
        elif component_name == 'UOM Conversions':
            tests = len(validation.get('conversion_tests', []))
            failed = len(validation.get('failed_conversions', []))
            return f"{tests - failed}/{tests} conversions passed"
        
        elif component_name == 'Recipe Calculations':
            tested = validation.get('recipes_tested', 0)
            failures = len(validation.get('chain_failures', []))
            return f"{tested - failures}/{tested} chains validated"
        
        elif component_name == 'Menu Margins':
            total = validation.get('total_menu_items', 0)
            validated = validation.get('items_validated', 0)
            return f"{validated}/{total} items validated"
        
        elif component_name == 'PDF Accuracy':
            rate = validation.get('accuracy_rate', 0)
            return f"{rate:.1f}% accuracy rate"
        
        return "No data"
    
    def _generate_error_analysis(self, output_dir: Path):
        """Generate detailed error analysis"""
        with open(output_dir / "error_analysis.md", 'w') as f:
            f.write("# Error Analysis Report\n\n")
            
            # Systematic errors
            f.write("## Systematic Errors Identified\n\n")
            
            if self.validation_results.get('systematic_errors'):
                for error in self.validation_results['systematic_errors']:
                    f.write(f"### {error['pattern']}\n\n")
                    f.write(f"- **Type**: {error['error_type']}\n")
                    f.write(f"- **Frequency**: {error['frequency']} occurrences\n")
                    f.write(f"- **Impact**: {error['impact'].upper()}\n")
                    
                    if error.get('affected_recipes'):
                        f.write(f"- **Sample affected items**: {', '.join(error['affected_recipes'][:3])}\n")
                    
                    f.write("\n")
            else:
                f.write("No systematic errors identified.\n\n")
            
            # Significant variances
            f.write("## Significant Cost Variances\n\n")
            
            pdf_val = self.validation_results.get('pdf_validation', {})
            variances = pdf_val.get('significant_variances', [])
            
            if variances:
                # Sort by variance amount
                variances.sort(key=lambda x: abs(x['variance']), reverse=True)
                
                f.write("| Recipe | Calculated | PDF Stated | Variance | % Variance |\n")
                f.write("|--------|------------|------------|----------|------------|\n")
                
                for v in variances[:20]:  # Top 20
                    f.write(
                        f"| {v['recipe_name'][:30]} | "
                        f"${v['calculated_cost']:.2f} | "
                        f"${v['pdf_cost']:.2f} | "
                        f"${v['variance']:.2f} | "
                        f"{v['variance_percent']:.1f}% |\n"
                    )
            else:
                f.write("No significant variances found.\n")
    
    def _generate_management_summary(self, output_dir: Path):
        """Generate executive summary for management"""
        with open(output_dir / "management_summary.md", 'w') as f:
            f.write("# Calculation System Validation - Management Summary\n\n")
            f.write(f"Report Date: {datetime.now().strftime('%B %d, %Y')}\n\n")
            
            # Overall health
            metrics = self.validation_results.get('accuracy_metrics', {})
            confidence = metrics.get('confidence_level', 'low')
            
            f.write("## System Health\n\n")
            
            if confidence == 'high':
                f.write("✅ **EXCELLENT** - The calculation system is performing accurately and reliably.\n\n")
            elif confidence == 'medium':
                f.write("⚠️ **GOOD** - The calculation system is generally accurate but has some issues.\n\n")
            else:
                f.write("❌ **NEEDS ATTENTION** - The calculation system has significant accuracy issues.\n\n")
            
            # Key metrics
            f.write("## Key Metrics\n\n")
            f.write(f"- Recipe calculation accuracy: **{metrics.get('overall_accuracy', 0):.1f}%**\n")
            f.write(f"- System reliability: **{metrics.get('calculation_success_rate', 0):.1f}%**\n")
            
            # Financial impact
            margin_val = self.validation_results.get('margin_validation', {})
            poor_margins = margin_val.get('margin_distribution', {}).get('poor', 0)
            total_items = margin_val.get('total_menu_items', 0)
            
            if total_items > 0:
                poor_margin_pct = (poor_margins / total_items) * 100
                f.write(f"- Menu items with poor margins: **{poor_margins}** ({poor_margin_pct:.1f}%)\n\n")
            
            # Top recommendations
            f.write("## Priority Actions\n\n")
            
            recommendations = self.validation_results.get('recommendations', [])
            critical_recs = [r for r in recommendations if r['priority'] == 'critical']
            high_recs = [r for r in recommendations if r['priority'] == 'high']
            
            if critical_recs:
                f.write("### Critical (Immediate Action Required)\n\n")
                for rec in critical_recs:
                    f.write(f"- {rec['recommendation']}\n")
                f.write("\n")
            
            if high_recs:
                f.write("### High Priority\n\n")
                for rec in high_recs[:3]:  # Top 3
                    f.write(f"- {rec['recommendation']}\n")
                f.write("\n")
            
            # Risk assessment
            f.write("## Risk Assessment\n\n")
            
            systematic_errors = self.validation_results.get('systematic_errors', [])
            if systematic_errors:
                f.write(f"- **{len(systematic_errors)}** systematic issues identified\n")
                f.write("- Potential revenue impact from pricing errors\n")
                f.write("- Risk of incorrect cost reporting\n")
            else:
                f.write("- No major systematic issues identified\n")
                f.write("- Low risk of calculation errors\n")
    
    def _export_validation_details(self, output_dir: Path):
        """Export detailed validation data for drill-down analysis"""
        # Export calculation chains to CSV
        calc_val = self.validation_results.get('calculation_validation', {})
        chains = calc_val.get('calculation_chains', [])
        
        if chains:
            csv_path = output_dir / "calculation_chains.csv"
            with open(csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Recipe ID', 'Recipe Name', 'Status', 'Total Variance',
                    'Vendor to Ingredient Errors', 'Recipe Total Variance',
                    'Food Cost %', 'Within Target'
                ])
                
                for chain in chains:
                    # Extract checkpoint data
                    vendor_errors = sum(
                        1 for c in chain['checkpoints'] 
                        if c['type'] == 'vendor_to_ingredient' and c.get('has_errors')
                    )
                    
                    recipe_variance = next(
                        (c['variance'] for c in chain['checkpoints'] if c['type'] == 'recipe_total'),
                        None
                    )
                    
                    margin_data = next(
                        (c for c in chain['checkpoints'] if c['type'] == 'menu_margin'),
                        {}
                    )
                    
                    writer.writerow([
                        chain['recipe_id'],
                        chain['recipe_name'],
                        chain['status'],
                        float(chain['total_variance']),
                        vendor_errors,
                        recipe_variance,
                        margin_data.get('food_cost_percent', ''),
                        margin_data.get('within_target', '')
                    ])
        
        # Export items needing manual review
        review_items = []
        
        # Add items with poor margins
        margin_val = self.validation_results.get('margin_validation', {})
        for item in margin_val.get('items_needing_attention', []):
            review_items.append({
                'type': 'poor_margin',
                'item_name': item['item_name'],
                'issue': f"Food cost {item['food_cost_percent']:.1f}%",
                'recommendation': item['recommendation']
            })
        
        # Add items with missing pricing
        vendor_val = self.validation_results.get('vendor_validation', {})
        for item in vendor_val.get('items_missing_pricing', [])[:10]:  # Limit to 10
            review_items.append({
                'type': 'missing_price',
                'item_name': item['description'],
                'issue': 'No vendor pricing',
                'recommendation': 'Update vendor pricing data'
            })
        
        if review_items:
            review_path = output_dir / "items_for_review.csv"
            with open(review_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['type', 'item_name', 'issue', 'recommendation'])
                writer.writeheader()
                writer.writerows(review_items)
    
    def run_quick_validation(self, recipe_ids: List[int] = None) -> Dict[str, Any]:
        """Run quick validation on specific recipes"""
        if not recipe_ids:
            # Get a sample of recipes
            cursor = self.conn.cursor()
            recipe_ids = [r['recipe_id'] for r in cursor.execute("""
                SELECT recipe_id FROM recipes_actual 
                WHERE food_cost IS NOT NULL 
                ORDER BY RANDOM() 
                LIMIT 10
            """).fetchall()]
        
        quick_results = {
            'timestamp': datetime.now().isoformat(),
            'recipes_tested': len(recipe_ids),
            'results': []
        }
        
        for recipe_id in recipe_ids:
            try:
                # Test calculation chain
                cursor = self.conn.cursor()
                recipe = cursor.execute("""
                    SELECT recipe_id, recipe_name, food_cost as pdf_cost
                    FROM recipes_actual
                    WHERE recipe_id = ?
                """, (recipe_id,)).fetchone()
                
                if recipe:
                    chain_result = self._test_single_calculation_chain(recipe)
                    quick_results['results'].append({
                        'recipe_id': recipe_id,
                        'recipe_name': recipe['recipe_name'],
                        'status': chain_result['status'],
                        'variance': float(chain_result['total_variance'])
                    })
            except Exception as e:
                logger.error(f"Quick validation failed for recipe {recipe_id}: {e}")
                quick_results['results'].append({
                    'recipe_id': recipe_id,
                    'status': 'error',
                    'error': str(e)
                })
        
        return quick_results
    
    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()


def main():
    """Run the calculation validator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='End-to-End Calculation Validation System')
    parser.add_argument('--full', action='store_true', help='Run full system validation')
    parser.add_argument('--quick', action='store_true', help='Run quick validation on sample recipes')
    parser.add_argument('--recipe-ids', nargs='+', type=int, help='Specific recipe IDs to validate')
    parser.add_argument('--report', action='store_true', help='Generate validation report')
    parser.add_argument('--db', type=str, default='restaurant_calculator.db', help='Database path')
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = CalculationValidator(args.db)
    
    if args.full:
        print("Running full system validation...")
        results = validator.run_full_system_validation()
        
        print(f"\n=== VALIDATION SUMMARY ===")
        print(f"Overall Accuracy: {results['accuracy_metrics']['overall_accuracy']:.1f}%")
        print(f"Confidence Level: {results['accuracy_metrics']['confidence_level'].upper()}")
        
        if results['systematic_errors']:
            print(f"\nSystematic Errors Found: {len(results['systematic_errors'])}")
            for error in results['systematic_errors'][:3]:
                print(f"  - {error['pattern']} ({error['frequency']} occurrences)")
        
        if results['recommendations']:
            print(f"\nTop Recommendations:")
            for rec in results['recommendations'][:3]:
                print(f"  [{rec['priority'].upper()}] {rec['recommendation']}")
        
        if args.report:
            report_dir = validator.generate_validation_report()
            print(f"\nDetailed report generated in: {report_dir}")
    
    elif args.quick or args.recipe_ids:
        print("Running quick validation...")
        results = validator.run_quick_validation(args.recipe_ids)
        
        print(f"\nTested {results['recipes_tested']} recipes:")
        for result in results['results']:
            status_icon = '✅' if result['status'] == 'passed' else '⚠️' if result['status'] == 'warning' else '❌'
            print(f"{status_icon} {result.get('recipe_name', f'Recipe {result['recipe_id']}')} - {result['status']}")
            if result.get('variance'):
                print(f"   Variance: ${result['variance']:.2f}")
    
    else:
        # Default: Run quick validation
        print("Running quick validation (use --full for comprehensive validation)...")
        results = validator.run_quick_validation()
        
        passed = sum(1 for r in results['results'] if r['status'] == 'passed')
        print(f"\nQuick validation: {passed}/{results['recipes_tested']} passed")
        print("\nRun with --full flag for comprehensive system validation")


if __name__ == "__main__":
    main()