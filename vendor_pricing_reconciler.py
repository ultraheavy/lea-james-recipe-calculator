#!/usr/bin/env python3
"""
Vendor Pricing Reconciliation Engine
Ensures vendor pricing properly supports recipe calculations through comprehensive
audit, validation, and UOM alignment functions.
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Tuple, Optional, Set
import json
import logging
from collections import defaultdict
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VendorPricingReconciler:
    """Reconcile vendor pricing data with recipe requirements"""
    
    def __init__(self, db_path: str = 'restaurant_calculator.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Load UOM conversion data
        self.uom_conversions = self._load_uom_conversions()
        self.canonical_units = self._load_canonical_units()
        
        # Track issues found during reconciliation
        self.issues = {
            'missing_prices': [],
            'uom_mismatches': [],
            'missing_conversions': [],
            'outdated_prices': [],
            'price_discrepancies': [],
            'pack_size_issues': [],
            'impossible_conversions': []
        }
        
    def _load_uom_conversions(self) -> Dict[str, Dict[str, float]]:
        """Load standard UOM conversions"""
        # Standard conversions between units
        conversions = {
            # Weight conversions
            'kg': {'g': 1000, 'lb': 2.20462, 'oz': 35.274},
            'g': {'kg': 0.001, 'lb': 0.00220462, 'oz': 0.035274},
            'lb': {'kg': 0.453592, 'g': 453.592, 'oz': 16},
            'oz': {'kg': 0.0283495, 'g': 28.3495, 'lb': 0.0625},
            
            # Volume conversions
            'l': {'ml': 1000, 'gal': 0.264172, 'qt': 1.05669, 'pt': 2.11338, 'cup': 4.22675, 'fl oz': 33.814},
            'ml': {'l': 0.001, 'fl oz': 0.033814, 'cup': 0.00422675},
            'gal': {'l': 3.78541, 'qt': 4, 'pt': 8, 'cup': 16, 'fl oz': 128},
            'qt': {'l': 0.946353, 'gal': 0.25, 'pt': 2, 'cup': 4, 'fl oz': 32},
            'fl oz': {'ml': 29.5735, 'l': 0.0295735, 'cup': 0.125, 'gal': 0.0078125},
            
            # Count conversions
            'doz': {'each': 12},
            'case': {'each': 1},  # Default - will be overridden by pack size
            'each': {'doz': 0.0833333}
        }
        
        return conversions
    
    def _load_canonical_units(self) -> Dict[str, str]:
        """Map units to their canonical forms"""
        return {
            # Weight
            'kilogram': 'kg', 'kilograms': 'kg', 'kilo': 'kg', 'kg': 'kg',
            'gram': 'g', 'grams': 'g', 'gm': 'g', 'g': 'g',
            'pound': 'lb', 'pounds': 'lb', 'lbs': 'lb', 'lb': 'lb',
            'ounce': 'oz', 'ounces': 'oz', 'oz': 'oz',
            
            # Volume
            'liter': 'l', 'liters': 'l', 'litre': 'l', 'litres': 'l', 'l': 'l',
            'milliliter': 'ml', 'milliliters': 'ml', 'ml': 'ml',
            'gallon': 'gal', 'gallons': 'gal', 'gal': 'gal',
            'quart': 'qt', 'quarts': 'qt', 'qt': 'qt',
            'fluid ounce': 'fl oz', 'fluid ounces': 'fl oz', 'fl oz': 'fl oz',
            
            # Count
            'each': 'each', 'ea': 'each', 'unit': 'each', 'piece': 'each',
            'dozen': 'doz', 'doz': 'doz',
            'case': 'case', 'cs': 'case', 'box': 'case'
        }
    
    def full_reconciliation(self) -> Dict:
        """Run complete vendor pricing reconciliation"""
        logger.info("Starting vendor pricing reconciliation...")
        
        # Clear previous issues
        self.issues = {key: [] for key in self.issues}
        
        # Run all audit functions
        self.audit_vendor_uom_matches()
        self.identify_missing_conversions()
        self.validate_price_calculations()
        self.check_outdated_prices()
        self.analyze_pack_sizes()
        
        # Generate recommendations
        recommendations = self.generate_recommendations()
        
        # Create comprehensive report
        report = self.generate_report()
        
        return {
            'issues': self.issues,
            'recommendations': recommendations,
            'report': report,
            'summary': self._generate_summary()
        }
    
    def audit_vendor_uom_matches(self):
        """Check if vendor UOM matches recipe usage UOM"""
        query = """
        SELECT DISTINCT
            i.id as inventory_id,
            i.item_code,
            i.item_description,
            i.unit_measure as inventory_uom,
            i.purchase_unit,
            i.recipe_cost_unit,
            vp.vendor_id,
            v.vendor_name,
            vp.unit_measure as vendor_uom,
            vp.pack_size as vendor_pack_size,
            ri.unit_of_measure as recipe_uom,
            r.recipe_name
        FROM inventory i
        LEFT JOIN vendor_products vp ON i.id = vp.inventory_id
        LEFT JOIN vendors v ON vp.vendor_id = v.id
        LEFT JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
        LEFT JOIN recipes r ON ri.recipe_id = r.id
        WHERE vp.is_active = 1
        """
        
        cursor = self.conn.cursor()
        results = cursor.execute(query).fetchall()
        
        for row in results:
            # Normalize units
            vendor_unit = self._normalize_unit(row['vendor_uom'] or row['purchase_unit'])
            recipe_unit = self._normalize_unit(row['recipe_uom'])
            
            if vendor_unit and recipe_unit and vendor_unit != recipe_unit:
                # Check if conversion exists
                if not self._can_convert(vendor_unit, recipe_unit):
                    self.issues['uom_mismatches'].append({
                        'inventory_id': row['inventory_id'],
                        'item': row['item_description'],
                        'vendor': row['vendor_name'],
                        'vendor_uom': vendor_unit,
                        'recipe_uom': recipe_unit,
                        'recipe': row['recipe_name'],
                        'severity': 'HIGH'
                    })
    
    def identify_missing_conversions(self):
        """Identify missing conversion factors between vendor and recipe units"""
        query = """
        SELECT DISTINCT
            i.id as inventory_id,
            i.item_description,
            i.unit_measure,
            i.purchase_unit,
            i.recipe_cost_unit,
            ri.unit_of_measure as recipe_uom,
            COUNT(DISTINCT ri.recipe_id) as recipe_count
        FROM inventory i
        JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
        GROUP BY i.id, ri.unit_of_measure
        """
        
        cursor = self.conn.cursor()
        results = cursor.execute(query).fetchall()
        
        for row in results:
            vendor_unit = self._normalize_unit(row['purchase_unit'] or row['unit_measure'])
            recipe_unit = self._normalize_unit(row['recipe_uom'])
            
            if vendor_unit and recipe_unit and vendor_unit != recipe_unit:
                if not self._can_convert(vendor_unit, recipe_unit):
                    # Check if it's a density-based conversion (volume to weight)
                    if self._needs_density_conversion(vendor_unit, recipe_unit):
                        self.issues['missing_conversions'].append({
                            'inventory_id': row['inventory_id'],
                            'item': row['item_description'],
                            'from_unit': vendor_unit,
                            'to_unit': recipe_unit,
                            'conversion_type': 'density',
                            'affected_recipes': row['recipe_count'],
                            'severity': 'HIGH'
                        })
                    else:
                        self.issues['impossible_conversions'].append({
                            'inventory_id': row['inventory_id'],
                            'item': row['item_description'],
                            'from_unit': vendor_unit,
                            'to_unit': recipe_unit,
                            'reason': 'Incompatible unit dimensions',
                            'affected_recipes': row['recipe_count'],
                            'severity': 'CRITICAL'
                        })
    
    def validate_price_calculations(self):
        """Validate price-per-unit calculations"""
        query = """
        SELECT 
            i.id as inventory_id,
            i.item_code,
            i.item_description,
            i.current_price,
            i.last_purchased_price,
            i.pack_size as inventory_pack_size,
            i.purchase_unit,
            vp.vendor_price,
            vp.pack_size as vendor_pack_size,
            vp.unit_measure as vendor_uom,
            vp.last_purchased_price as vendor_last_price,
            v.vendor_name
        FROM inventory i
        JOIN vendor_products vp ON i.id = vp.inventory_id
        JOIN vendors v ON vp.vendor_id = v.id
        WHERE vp.is_active = 1 AND vp.is_primary = 1
        """
        
        cursor = self.conn.cursor()
        results = cursor.execute(query).fetchall()
        
        for row in results:
            # Check for missing prices
            if not row['vendor_price'] or row['vendor_price'] <= 0:
                self.issues['missing_prices'].append({
                    'inventory_id': row['inventory_id'],
                    'item': row['item_description'],
                    'vendor': row['vendor_name'],
                    'severity': 'HIGH'
                })
                continue
            
            # Compare contract vs last purchased prices
            if row['vendor_last_price'] and row['vendor_price']:
                price_diff_pct = abs(row['vendor_price'] - row['vendor_last_price']) / row['vendor_price'] * 100
                if price_diff_pct > 10:  # More than 10% difference
                    self.issues['price_discrepancies'].append({
                        'inventory_id': row['inventory_id'],
                        'item': row['item_description'],
                        'vendor': row['vendor_name'],
                        'contract_price': row['vendor_price'],
                        'last_purchased': row['vendor_last_price'],
                        'difference_pct': round(price_diff_pct, 2),
                        'severity': 'MEDIUM'
                    })
            
            # Validate pack size calculations
            pack_size = row['vendor_pack_size'] or row['inventory_pack_size']
            if pack_size:
                pack_qty, pack_unit = self._parse_pack_size(pack_size)
                if pack_qty and pack_qty > 1:
                    # Calculate expected unit price
                    expected_unit_price = Decimal(str(row['vendor_price'])) / Decimal(str(pack_qty))
                    # This would need additional logic to compare with actual unit prices
    
    def check_outdated_prices(self, days_threshold: int = 90):
        """Flag items with outdated vendor prices"""
        query = """
        SELECT 
            i.id as inventory_id,
            i.item_description,
            i.last_purchased_date,
            vp.last_purchased_date as vendor_last_date,
            v.vendor_name,
            julianday('now') - julianday(COALESCE(vp.last_purchased_date, i.last_purchased_date)) as days_old
        FROM inventory i
        JOIN vendor_products vp ON i.id = vp.inventory_id
        JOIN vendors v ON vp.vendor_id = v.id
        WHERE vp.is_active = 1
        AND (vp.last_purchased_date IS NOT NULL OR i.last_purchased_date IS NOT NULL)
        """
        
        cursor = self.conn.cursor()
        results = cursor.execute(query).fetchall()
        
        for row in results:
            if row['days_old'] and row['days_old'] > days_threshold:
                self.issues['outdated_prices'].append({
                    'inventory_id': row['inventory_id'],
                    'item': row['item_description'],
                    'vendor': row['vendor_name'],
                    'last_updated': row['vendor_last_date'] or row['last_purchased_date'],
                    'days_old': int(row['days_old']),
                    'severity': 'MEDIUM' if row['days_old'] < 180 else 'HIGH'
                })
    
    def analyze_pack_sizes(self):
        """Analyze complex vendor pack sizes"""
        query = """
        SELECT 
            i.id as inventory_id,
            i.item_description,
            i.pack_size as inventory_pack_size,
            vp.pack_size as vendor_pack_size,
            v.vendor_name
        FROM inventory i
        JOIN vendor_products vp ON i.id = vp.inventory_id
        JOIN vendors v ON vp.vendor_id = v.id
        WHERE vp.is_active = 1
        AND (vp.pack_size IS NOT NULL OR i.pack_size IS NOT NULL)
        """
        
        cursor = self.conn.cursor()
        results = cursor.execute(query).fetchall()
        
        for row in results:
            pack_size = row['vendor_pack_size'] or row['inventory_pack_size']
            if pack_size:
                pack_qty, pack_unit = self._parse_pack_size(pack_size)
                if not pack_qty or not pack_unit:
                    self.issues['pack_size_issues'].append({
                        'inventory_id': row['inventory_id'],
                        'item': row['item_description'],
                        'vendor': row['vendor_name'],
                        'pack_size': pack_size,
                        'issue': 'Unable to parse pack size',
                        'severity': 'HIGH'
                    })
    
    def _normalize_unit(self, unit: Optional[str]) -> Optional[str]:
        """Normalize unit to canonical form"""
        if not unit:
            return None
        unit_lower = unit.lower().strip()
        return self.canonical_units.get(unit_lower, unit_lower)
    
    def _can_convert(self, from_unit: str, to_unit: str) -> bool:
        """Check if conversion is possible between units"""
        if from_unit == to_unit:
            return True
        
        # Check direct conversion
        if from_unit in self.uom_conversions and to_unit in self.uom_conversions[from_unit]:
            return True
        
        # Check reverse conversion
        if to_unit in self.uom_conversions and from_unit in self.uom_conversions[to_unit]:
            return True
        
        # Check if both can convert to a common unit
        for unit in self.uom_conversions:
            if (from_unit in self.uom_conversions.get(unit, {}) and 
                to_unit in self.uom_conversions.get(unit, {})):
                return True
        
        return False
    
    def _needs_density_conversion(self, unit1: str, unit2: str) -> bool:
        """Check if conversion requires density (volume to weight)"""
        volume_units = {'l', 'ml', 'gal', 'qt', 'fl oz', 'cup', 'pt'}
        weight_units = {'kg', 'g', 'lb', 'oz'}
        
        return ((unit1 in volume_units and unit2 in weight_units) or
                (unit1 in weight_units and unit2 in volume_units))
    
    def _parse_pack_size(self, pack_size: str) -> Tuple[Optional[float], Optional[str]]:
        """Parse pack size string to extract quantity and unit"""
        if not pack_size:
            return None, None
        
        # Handle various pack size formats
        # Examples: "24 x 12oz", "case of 24", "1x4l", "128 fl oz"
        
        # Replace multiplication symbols
        pack_size = re.sub(r'[×✕✖⨯]', 'x', pack_size)
        
        # Pattern for "N x N unit" format
        pattern1 = r'^(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*([a-zA-Z\s]+)$'
        match1 = re.match(pattern1, pack_size, re.IGNORECASE)
        if match1:
            packs = float(match1.group(1))
            qty_per_pack = float(match1.group(2))
            unit = match1.group(3).strip()
            return qty_per_pack, self._normalize_unit(unit)
        
        # Pattern for "case of N" format
        pattern2 = r'^case\s+of\s+(\d+)(?:\s+([a-zA-Z\s]+))?$'
        match2 = re.match(pattern2, pack_size, re.IGNORECASE)
        if match2:
            qty = float(match2.group(1))
            unit = match2.group(2) if match2.group(2) else 'each'
            return qty, self._normalize_unit(unit)
        
        # Pattern for "N unit" format
        pattern3 = r'^(\d+(?:\.\d+)?)\s+([a-zA-Z\s]+)$'
        match3 = re.match(pattern3, pack_size, re.IGNORECASE)
        if match3:
            qty = float(match3.group(1))
            unit = match3.group(2).strip()
            return qty, self._normalize_unit(unit)
        
        return None, None
    
    def generate_recommendations(self) -> Dict[str, List[Dict]]:
        """Generate actionable recommendations based on issues found"""
        recommendations = {
            'immediate_actions': [],
            'data_quality': [],
            'process_improvements': [],
            'manual_interventions': []
        }
        
        # Missing prices
        if self.issues['missing_prices']:
            recommendations['immediate_actions'].append({
                'action': 'Update Missing Vendor Prices',
                'priority': 'CRITICAL',
                'items_affected': len(self.issues['missing_prices']),
                'description': 'Items without vendor pricing cannot be accurately costed in recipes',
                'steps': [
                    'Contact vendors for current pricing',
                    'Update vendor_products table with current prices',
                    'Set last_purchased_date to current date'
                ]
            })
        
        # UOM mismatches
        if self.issues['uom_mismatches']:
            unique_conversions = set()
            for issue in self.issues['uom_mismatches']:
                unique_conversions.add((issue['vendor_uom'], issue['recipe_uom']))
            
            recommendations['data_quality'].append({
                'action': 'Create UOM Conversion Mappings',
                'priority': 'HIGH',
                'conversions_needed': len(unique_conversions),
                'description': 'Vendor and recipe units don\'t match - need conversion factors',
                'steps': [
                    'Review each unique conversion requirement',
                    'Add conversion factors to system',
                    'Update affected recipe calculations'
                ]
            })
        
        # Outdated prices
        if self.issues['outdated_prices']:
            old_90_days = len([i for i in self.issues['outdated_prices'] if i['days_old'] > 90])
            old_180_days = len([i for i in self.issues['outdated_prices'] if i['days_old'] > 180])
            
            recommendations['process_improvements'].append({
                'action': 'Implement Regular Price Updates',
                'priority': 'MEDIUM',
                'items_90_days': old_90_days,
                'items_180_days': old_180_days,
                'description': 'Many vendor prices are outdated and may not reflect current costs',
                'steps': [
                    'Set up quarterly price review process',
                    'Automate vendor price import where possible',
                    'Flag items for review after 90 days'
                ]
            })
        
        # Impossible conversions
        if self.issues['impossible_conversions']:
            recommendations['manual_interventions'].append({
                'action': 'Resolve Impossible Unit Conversions',
                'priority': 'HIGH',
                'items_affected': len(self.issues['impossible_conversions']),
                'description': 'Some items have incompatible units that cannot be automatically converted',
                'steps': [
                    'Review each impossible conversion',
                    'Determine if density data is needed (weight to volume)',
                    'Update inventory with missing conversion data',
                    'Consider standardizing units where possible'
                ]
            })
        
        # Pack size issues
        if self.issues['pack_size_issues']:
            recommendations['data_quality'].append({
                'action': 'Standardize Pack Size Formats',
                'priority': 'MEDIUM',
                'items_affected': len(self.issues['pack_size_issues']),
                'description': 'Pack sizes in non-standard formats prevent accurate unit cost calculations',
                'steps': [
                    'Review and correct pack size formats',
                    'Use standard format: "N x N unit" or "N unit"',
                    'Update data entry guidelines'
                ]
            })
        
        return recommendations
    
    def generate_report(self) -> str:
        """Generate comprehensive HTML report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Calculate summary statistics
        total_issues = sum(len(issues) for issues in self.issues.values())
        critical_issues = len(self.issues['missing_prices']) + len(self.issues['impossible_conversions'])
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Vendor Pricing Reconciliation Report - {timestamp}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; background: #f0f2f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; }}
        h1 {{ margin: 0; font-size: 2.5em; }}
        .subtitle {{ opacity: 0.9; margin-top: 10px; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; padding: 30px; background: #f8f9fa; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align: center; }}
        .stat-value {{ font-size: 2.5em; font-weight: bold; margin: 10px 0; }}
        .critical {{ color: #e74c3c; }}
        .warning {{ color: #f39c12; }}
        .info {{ color: #3498db; }}
        .success {{ color: #27ae60; }}
        .issue-section {{ padding: 30px; }}
        .issue-section h2 {{ color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #667eea; color: white; padding: 12px; text-align: left; font-weight: 600; }}
        td {{ padding: 12px; border-bottom: 1px solid #ecf0f1; }}
        tr:hover {{ background: #f8f9fa; }}
        .severity-CRITICAL {{ color: #e74c3c; font-weight: bold; }}
        .severity-HIGH {{ color: #e67e22; font-weight: bold; }}
        .severity-MEDIUM {{ color: #f39c12; }}
        .recommendation {{ background: #e8f4f8; border-left: 4px solid #3498db; padding: 15px; margin: 15px 0; border-radius: 4px; }}
        .recommendation h4 {{ margin: 0 0 10px 0; color: #2980b9; }}
        .steps {{ margin: 10px 0 0 20px; }}
        .footer {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 Vendor Pricing Reconciliation Report</h1>
            <div class="subtitle">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="summary-grid">
            <div class="stat-card">
                <h3>Total Issues</h3>
                <div class="stat-value">{total_issues}</div>
            </div>
            <div class="stat-card">
                <h3>Critical Issues</h3>
                <div class="stat-value critical">{critical_issues}</div>
            </div>
            <div class="stat-card">
                <h3>Missing Prices</h3>
                <div class="stat-value warning">{len(self.issues['missing_prices'])}</div>
            </div>
            <div class="stat-card">
                <h3>UOM Mismatches</h3>
                <div class="stat-value info">{len(self.issues['uom_mismatches'])}</div>
            </div>
        </div>
"""
        
        # Add detailed issue sections
        if self.issues['missing_prices']:
            html += self._generate_issue_section(
                'Missing Vendor Prices',
                self.issues['missing_prices'],
                ['inventory_id', 'item', 'vendor', 'severity']
            )
        
        if self.issues['uom_mismatches']:
            html += self._generate_issue_section(
                'Unit of Measure Mismatches',
                self.issues['uom_mismatches'],
                ['item', 'vendor', 'vendor_uom', 'recipe_uom', 'recipe', 'severity']
            )
        
        if self.issues['impossible_conversions']:
            html += self._generate_issue_section(
                'Impossible Unit Conversions',
                self.issues['impossible_conversions'],
                ['item', 'from_unit', 'to_unit', 'reason', 'affected_recipes', 'severity']
            )
        
        if self.issues['outdated_prices']:
            html += self._generate_issue_section(
                'Outdated Vendor Prices',
                self.issues['outdated_prices'][:20],  # Show top 20
                ['item', 'vendor', 'last_updated', 'days_old', 'severity']
            )
        
        # Add recommendations section
        recommendations = self.generate_recommendations()
        html += '<div class="issue-section"><h2>📋 Recommendations</h2>'
        
        for category, recs in recommendations.items():
            if recs:
                html += f'<h3>{category.replace("_", " ").title()}</h3>'
                for rec in recs:
                    html += f"""
                    <div class="recommendation">
                        <h4>{rec['action']} - Priority: {rec['priority']}</h4>
                        <p>{rec['description']}</p>
                        <div class="steps">
                            <strong>Steps:</strong>
                            <ol>
                    """
                    for step in rec.get('steps', []):
                        html += f'<li>{step}</li>'
                    html += '</ol></div></div>'
        
        html += '</div>'
        
        # Add footer
        html += """
        <div class="footer">
            <p>Vendor Pricing Reconciliation Engine v1.0</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Save report
        filename = f'vendor_pricing_reconciliation_{timestamp}.html'
        with open(filename, 'w') as f:
            f.write(html)
        
        logger.info(f"Report saved: {filename}")
        return filename
    
    def _generate_issue_section(self, title: str, issues: List[Dict], columns: List[str]) -> str:
        """Generate HTML for an issue section"""
        if not issues:
            return ''
        
        html = f'<div class="issue-section"><h2>{title}</h2><table><tr>'
        
        # Add headers
        for col in columns:
            header = col.replace('_', ' ').title()
            html += f'<th>{header}</th>'
        html += '</tr>'
        
        # Add rows
        for issue in issues:
            html += '<tr>'
            for col in columns:
                value = issue.get(col, '')
                if col == 'severity':
                    html += f'<td class="severity-{value}">{value}</td>'
                else:
                    html += f'<td>{value}</td>'
            html += '</tr>'
        
        html += '</table></div>'
        return html
    
    def _generate_summary(self) -> Dict:
        """Generate summary statistics"""
        total_issues = sum(len(issues) for issues in self.issues.values())
        
        return {
            'total_issues': total_issues,
            'critical_issues': len(self.issues['missing_prices']) + len(self.issues['impossible_conversions']),
            'high_priority': len([i for i in self.issues['uom_mismatches'] if i.get('severity') == 'HIGH']),
            'items_needing_prices': len(self.issues['missing_prices']),
            'items_needing_conversions': len(self.issues['missing_conversions']) + len(self.issues['impossible_conversions']),
            'outdated_items': len(self.issues['outdated_prices'])
        }
    
    def export_fix_lists(self):
        """Export actionable fix lists for procurement team"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export missing prices list
        if self.issues['missing_prices']:
            df = pd.DataFrame(self.issues['missing_prices'])
            df.to_csv(f'fix_list_missing_prices_{timestamp}.csv', index=False)
            logger.info(f"Exported {len(df)} items needing prices")
        
        # Export conversion requirements
        conversions_needed = []
        for issue in self.issues['uom_mismatches'] + self.issues['missing_conversions']:
            conversions_needed.append({
                'item': issue['item'],
                'from_unit': issue.get('vendor_uom') or issue.get('from_unit'),
                'to_unit': issue.get('recipe_uom') or issue.get('to_unit'),
                'conversion_type': issue.get('conversion_type', 'standard')
            })
        
        if conversions_needed:
            df = pd.DataFrame(conversions_needed)
            df.to_csv(f'fix_list_conversions_needed_{timestamp}.csv', index=False)
            logger.info(f"Exported {len(df)} conversion requirements")
        
        # Export outdated prices list
        if self.issues['outdated_prices']:
            df = pd.DataFrame(self.issues['outdated_prices'])
            df = df.sort_values('days_old', ascending=False)
            df.to_csv(f'fix_list_outdated_prices_{timestamp}.csv', index=False)
            logger.info(f"Exported {len(df)} items with outdated prices")
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    """Run vendor pricing reconciliation"""
    reconciler = VendorPricingReconciler()
    
    try:
        # Run full reconciliation
        results = reconciler.full_reconciliation()
        
        # Print summary
        summary = results['summary']
        print("\n📊 Vendor Pricing Reconciliation Summary")
        print("=" * 50)
        print(f"Total Issues Found: {summary['total_issues']}")
        print(f"Critical Issues: {summary['critical_issues']}")
        print(f"Items Needing Prices: {summary['items_needing_prices']}")
        print(f"Items Needing Conversions: {summary['items_needing_conversions']}")
        print(f"Outdated Price Items: {summary['outdated_items']}")
        
        # Export fix lists
        reconciler.export_fix_lists()
        
        print(f"\n✅ Report generated: {results['report']}")
        print("📁 Fix lists exported for procurement team")
        
    finally:
        reconciler.close()

if __name__ == "__main__":
    main()