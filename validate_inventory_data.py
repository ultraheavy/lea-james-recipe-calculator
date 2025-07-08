#!/usr/bin/env python3
"""
Comprehensive Inventory Data Validation Script
Validates inventory data integrity, vendor relationships, and recipe linkages
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime
from collections import defaultdict, Counter
import json
import re

class InventoryDataValidator:
    def __init__(self, db_path='restaurant_calculator.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.validation_results = defaultdict(list)
        self.data_quality_metrics = {}
        
    def run_all_validations(self):
        """Run comprehensive data validation suite"""
        print("🔍 Starting Comprehensive Inventory Data Validation")
        print("=" * 80)
        
        # Phase 1: Data Integrity Analysis
        print("\n📊 PHASE 1: DATA INTEGRITY ANALYSIS")
        print("-" * 40)
        self.validate_vendor_product_relationships()
        self.validate_item_codes()
        self.validate_product_descriptions()
        
        # Phase 2: CSV Source Reconciliation
        print("\n📋 PHASE 2: CSV SOURCE RECONCILIATION")
        print("-" * 40)
        self.analyze_mapping_files()
        self.validate_recipe_ingredient_links()
        
        # Phase 3: Data Quality Reporting
        print("\n📈 PHASE 3: DATA QUALITY REPORTING")
        print("-" * 40)
        self.generate_data_quality_report()
        self.generate_vendor_analysis_report()
        
        return self.validation_results, self.data_quality_metrics
    
    def validate_vendor_product_relationships(self):
        """Analyze current vendor-product pairings"""
        print("\n1. Validating Vendor-Product Relationships...")
        
        # Get all inventory items with vendor info
        query = """
        SELECT id, item_code, item_description, vendor_name, current_price
        FROM inventory
        ORDER BY vendor_name, item_description
        """
        items = self.cursor.execute(query).fetchall()
        
        # Group by vendor
        vendor_products = defaultdict(list)
        vendor_issues = []
        
        for item in items:
            vendor = item['vendor_name'] or 'NO_VENDOR'
            vendor_products[vendor].append({
                'id': item['id'],
                'item_code': item['item_code'],
                'description': item['item_description'],
                'price': item['current_price']
            })
        
        # Check for vendor naming inconsistencies
        vendor_names = list(vendor_products.keys())
        for i, vendor1 in enumerate(vendor_names):
            for vendor2 in vendor_names[i+1:]:
                if vendor1.lower().strip() == vendor2.lower().strip() and vendor1 != vendor2:
                    vendor_issues.append({
                        'type': 'vendor_naming_inconsistency',
                        'vendor1': vendor1,
                        'vendor2': vendor2,
                        'message': f"Vendor naming inconsistency: '{vendor1}' vs '{vendor2}'"
                    })
        
        # Check for illogical vendor-product assignments
        for vendor, products in vendor_products.items():
            if vendor == 'NO_VENDOR':
                for product in products:
                    self.validation_results['missing_vendor'].append({
                        'item_id': product['id'],
                        'item_code': product['item_code'],
                        'description': product['description']
                    })
        
        # Look for duplicate products across vendors
        product_vendors = defaultdict(list)
        for vendor, products in vendor_products.items():
            for product in products:
                # Normalize product description for comparison
                normalized = re.sub(r'\s+', ' ', product['description'].lower().strip())
                product_vendors[normalized].append({
                    'vendor': vendor,
                    'id': product['id'],
                    'original_desc': product['description'],
                    'price': product['price']
                })
        
        for product, vendors in product_vendors.items():
            if len(vendors) > 1:
                self.validation_results['duplicate_products'].append({
                    'product': product,
                    'vendors': vendors,
                    'message': f"Product '{product}' found with {len(vendors)} different vendors"
                })
        
        print(f"  ✓ Found {len(vendor_products)} unique vendors")
        print(f"  ⚠ {len(self.validation_results['missing_vendor'])} items missing vendor")
        print(f"  ⚠ {len(vendor_issues)} vendor naming inconsistencies")
        print(f"  ⚠ {len(self.validation_results['duplicate_products'])} potential duplicate products")
    
    def validate_item_codes(self):
        """Validate item_code integrity"""
        print("\n2. Validating Item Codes...")
        
        # Check for duplicate item codes
        query = """
        SELECT item_code, COUNT(*) as count, GROUP_CONCAT(id) as ids,
               GROUP_CONCAT(item_description, ' | ') as descriptions
        FROM inventory
        WHERE item_code IS NOT NULL AND item_code != ''
        GROUP BY item_code
        HAVING count > 1
        """
        duplicates = self.cursor.execute(query).fetchall()
        
        for dup in duplicates:
            self.validation_results['duplicate_item_codes'].append({
                'item_code': dup['item_code'],
                'count': dup['count'],
                'ids': dup['ids'],
                'descriptions': dup['descriptions']
            })
        
        # Check for missing item codes
        query = """
        SELECT id, item_description, vendor_name
        FROM inventory
        WHERE item_code IS NULL OR item_code = ''
        """
        missing = self.cursor.execute(query).fetchall()
        
        for item in missing:
            self.validation_results['missing_item_codes'].append({
                'id': item['id'],
                'description': item['item_description'],
                'vendor': item['vendor_name']
            })
        
        # Analyze item code formats
        query = "SELECT DISTINCT item_code FROM inventory WHERE item_code IS NOT NULL"
        all_codes = [row[0] for row in self.cursor.execute(query).fetchall()]
        
        code_patterns = Counter()
        for code in all_codes:
            if code.startswith('CUSTOM-'):
                code_patterns['CUSTOM'] += 1
            elif re.match(r'^\d+$', code):
                code_patterns['NUMERIC'] += 1
            elif re.match(r'^[A-Z]+-\d+$', code):
                code_patterns['PREFIX-NUMERIC'] += 1
            else:
                code_patterns['OTHER'] += 1
        
        print(f"  ✓ Analyzed {len(all_codes)} item codes")
        print(f"  ⚠ {len(duplicates)} duplicate item codes found")
        print(f"  ⚠ {len(missing)} items missing item codes")
        print(f"  📊 Code patterns: {dict(code_patterns)}")
    
    def validate_product_descriptions(self):
        """Analyze item_description patterns"""
        print("\n3. Validating Product Descriptions...")
        
        query = """
        SELECT id, item_code, item_description, vendor_name
        FROM inventory
        ORDER BY item_description
        """
        items = self.cursor.execute(query).fetchall()
        
        # Check naming convention compliance
        naming_issues = []
        unclear_descriptions = []
        
        for item in items:
            desc = item['item_description']
            
            # Check for very short descriptions
            if len(desc) < 5:
                unclear_descriptions.append({
                    'id': item['id'],
                    'description': desc,
                    'issue': 'Description too short'
                })
            
            # Check for all caps
            elif desc.isupper() and len(desc) > 3:
                naming_issues.append({
                    'id': item['id'],
                    'description': desc,
                    'issue': 'All uppercase'
                })
            
            # Check for vendor codes as descriptions
            elif re.match(r'^[A-Z]{2,4}-\d+$', desc):
                naming_issues.append({
                    'id': item['id'],
                    'description': desc,
                    'issue': 'Vendor code used as description'
                })
        
        # Find potential duplicates using fuzzy matching
        descriptions = [item['item_description'].lower().strip() for item in items]
        potential_duplicates = []
        
        for i, desc1 in enumerate(descriptions):
            for j, desc2 in enumerate(descriptions[i+1:], i+1):
                # Simple similarity check - could be enhanced with fuzzy matching
                if desc1 != desc2 and (desc1 in desc2 or desc2 in desc1):
                    if abs(len(desc1) - len(desc2)) < 10:
                        potential_duplicates.append({
                            'item1': items[i],
                            'item2': items[j],
                            'similarity': 'substring_match'
                        })
        
        self.validation_results['naming_issues'] = naming_issues
        self.validation_results['unclear_descriptions'] = unclear_descriptions
        self.validation_results['potential_duplicate_descriptions'] = potential_duplicates[:20]  # Limit to 20
        
        print(f"  ✓ Analyzed {len(items)} product descriptions")
        print(f"  ⚠ {len(naming_issues)} naming convention issues")
        print(f"  ⚠ {len(unclear_descriptions)} unclear descriptions")
        print(f"  ⚠ {len(potential_duplicates)} potential duplicates found")
    
    def analyze_mapping_files(self):
        """Examine mapping CSV files"""
        print("\n4. Analyzing Mapping Files...")
        
        mapping_results = {}
        
        # Check for approved mappings file
        approved_path = 'data/sources/mapping_approved.csv'
        if os.path.exists(approved_path):
            try:
                approved_df = pd.read_csv(approved_path)
                mapping_results['approved_count'] = len(approved_df)
                
                # Verify approved mappings are applied
                if 'recipe_ingredient' in approved_df.columns and 'inventory_item' in approved_df.columns:
                    for _, row in approved_df.iterrows():
                        # Check if this mapping exists in recipe_ingredients
                        query = """
                        SELECT ri.*, i.item_description
                        FROM recipe_ingredients ri
                        JOIN inventory i ON ri.ingredient_id = i.id
                        WHERE i.item_description = ?
                        """
                        result = self.cursor.execute(query, (row['inventory_item'],)).fetchone()
                        
                        if not result:
                            self.validation_results['unapplied_mappings'].append({
                                'recipe_ingredient': row['recipe_ingredient'],
                                'inventory_item': row['inventory_item'],
                                'status': 'mapping_not_found'
                            })
                
                print(f"  ✓ Found {mapping_results['approved_count']} approved mappings")
            except Exception as e:
                print(f"  ❌ Error reading approved mappings: {e}")
        else:
            print(f"  ⚠ Approved mappings file not found at {approved_path}")
        
        # Check for review files
        review_files = []
        data_sources = 'data/sources'
        if os.path.exists(data_sources):
            for file in os.listdir(data_sources):
                if file.startswith('mapping_review_') and file.endswith('.csv'):
                    review_files.append(os.path.join(data_sources, file))
        
        print(f"  ✓ Found {len(review_files)} review files")
        
        # Analyze unmapped items in recipes
        query = """
        SELECT DISTINCT ri.id, ri.recipe_id, r.recipe_name, ri.ingredient_id
        FROM recipe_ingredients ri
        LEFT JOIN recipes r ON ri.recipe_id = r.id
        WHERE ri.ingredient_id IS NULL OR ri.ingredient_id = 0
        """
        unmapped = self.cursor.execute(query).fetchall()
        
        for item in unmapped:
            self.validation_results['unmapped_recipe_ingredients'].append({
                'recipe_id': item['recipe_id'],
                'recipe_name': item['recipe_name'],
                'ingredient_link_id': item['id']
            })
        
        print(f"  ⚠ {len(unmapped)} unmapped recipe ingredients found")
    
    def validate_recipe_ingredient_links(self):
        """Validate recipe_ingredients table linkages"""
        print("\n5. Validating Recipe-Ingredient Links...")
        
        # Check for invalid ingredient_id references
        query = """
        SELECT ri.*, r.recipe_name
        FROM recipe_ingredients ri
        LEFT JOIN recipes r ON ri.recipe_id = r.id
        LEFT JOIN inventory i ON ri.ingredient_id = i.id
        WHERE ri.ingredient_id IS NOT NULL 
        AND ri.ingredient_id != 0
        AND i.id IS NULL
        """
        orphaned = self.cursor.execute(query).fetchall()
        
        for item in orphaned:
            self.validation_results['orphaned_ingredients'].append({
                'id': item['id'],
                'recipe_name': item['recipe_name'],
                'invalid_ingredient_id': item['ingredient_id']
            })
        
        # Check for illogical quantities or units
        query = """
        SELECT ri.*, r.recipe_name, i.item_description, i.unit_measure
        FROM recipe_ingredients ri
        JOIN recipes r ON ri.recipe_id = r.id
        JOIN inventory i ON ri.ingredient_id = i.id
        WHERE ri.quantity <= 0 OR ri.quantity > 1000
        OR ri.unit_of_measure IS NULL OR ri.unit_of_measure = ''
        """
        illogical = self.cursor.execute(query).fetchall()
        
        for item in illogical:
            issue = []
            if item['quantity'] <= 0:
                issue.append('zero_or_negative_quantity')
            elif item['quantity'] > 1000:
                issue.append('excessive_quantity')
            if not item['unit_of_measure']:
                issue.append('missing_unit')
                
            self.validation_results['illogical_quantities'].append({
                'recipe_name': item['recipe_name'],
                'ingredient': item['item_description'],
                'quantity': item['quantity'],
                'unit': item['unit_of_measure'],
                'issues': issue
            })
        
        # Calculate linkage statistics
        total_links = self.cursor.execute("SELECT COUNT(*) FROM recipe_ingredients").fetchone()[0]
        valid_links = self.cursor.execute("""
            SELECT COUNT(*) FROM recipe_ingredients ri
            JOIN inventory i ON ri.ingredient_id = i.id
            WHERE ri.ingredient_id IS NOT NULL AND ri.ingredient_id != 0
        """).fetchone()[0]
        
        self.data_quality_metrics['recipe_linkage_percentage'] = (valid_links / total_links * 100) if total_links > 0 else 0
        
        print(f"  ✓ Validated {total_links} recipe-ingredient links")
        print(f"  ✅ {valid_links} valid links ({self.data_quality_metrics['recipe_linkage_percentage']:.1f}%)")
        print(f"  ⚠ {len(orphaned)} orphaned ingredient references")
        print(f"  ⚠ {len(illogical)} illogical quantities/units")
    
    def generate_data_quality_report(self):
        """Generate comprehensive data quality metrics"""
        print("\n6. Generating Data Quality Report...")
        
        # Calculate completeness metrics
        total_items = self.cursor.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
        
        metrics = {
            'total_inventory_items': total_items,
            'items_with_vendor': self.cursor.execute(
                "SELECT COUNT(*) FROM inventory WHERE vendor_name IS NOT NULL AND vendor_name != ''"
            ).fetchone()[0],
            'items_with_price': self.cursor.execute(
                "SELECT COUNT(*) FROM inventory WHERE current_price > 0"
            ).fetchone()[0],
            'items_with_item_code': self.cursor.execute(
                "SELECT COUNT(*) FROM inventory WHERE item_code IS NOT NULL AND item_code != ''"
            ).fetchone()[0],
            'items_with_unit': self.cursor.execute(
                "SELECT COUNT(*) FROM inventory WHERE unit_measure IS NOT NULL AND unit_measure != ''"
            ).fetchone()[0],
            'total_recipes': self.cursor.execute("SELECT COUNT(*) FROM recipes").fetchone()[0],
            'recipes_with_ingredients': self.cursor.execute(
                "SELECT COUNT(DISTINCT recipe_id) FROM recipe_ingredients"
            ).fetchone()[0],
            'total_vendors': self.cursor.execute(
                "SELECT COUNT(DISTINCT vendor_name) FROM inventory WHERE vendor_name IS NOT NULL"
            ).fetchone()[0]
        }
        
        # Calculate percentages
        metrics['vendor_completeness'] = (metrics['items_with_vendor'] / total_items * 100) if total_items > 0 else 0
        metrics['price_completeness'] = (metrics['items_with_price'] / total_items * 100) if total_items > 0 else 0
        metrics['item_code_completeness'] = (metrics['items_with_item_code'] / total_items * 100) if total_items > 0 else 0
        metrics['unit_completeness'] = (metrics['items_with_unit'] / total_items * 100) if total_items > 0 else 0
        
        self.data_quality_metrics.update(metrics)
        
        print(f"  📊 Data Completeness Summary:")
        print(f"     - Vendor Information: {metrics['vendor_completeness']:.1f}%")
        print(f"     - Pricing Data: {metrics['price_completeness']:.1f}%")
        print(f"     - Item Codes: {metrics['item_code_completeness']:.1f}%")
        print(f"     - Units: {metrics['unit_completeness']:.1f}%")
    
    def generate_vendor_analysis_report(self):
        """Create vendor-focused analysis"""
        print("\n7. Generating Vendor Analysis...")
        
        # Get vendor statistics
        query = """
        SELECT 
            vendor_name,
            COUNT(*) as product_count,
            COUNT(CASE WHEN current_price > 0 THEN 1 END) as priced_items,
            AVG(current_price) as avg_price,
            MIN(current_price) as min_price,
            MAX(current_price) as max_price
        FROM inventory
        WHERE vendor_name IS NOT NULL AND vendor_name != ''
        GROUP BY vendor_name
        ORDER BY product_count DESC
        """
        
        vendor_stats = self.cursor.execute(query).fetchall()
        
        self.validation_results['vendor_statistics'] = []
        for vendor in vendor_stats:
            self.validation_results['vendor_statistics'].append({
                'vendor': vendor['vendor_name'],
                'product_count': vendor['product_count'],
                'priced_items': vendor['priced_items'],
                'avg_price': round(vendor['avg_price'], 2) if vendor['avg_price'] else 0,
                'price_range': f"${vendor['min_price']:.2f} - ${vendor['max_price']:.2f}" if vendor['min_price'] else "N/A"
            })
        
        print(f"  ✓ Analyzed {len(vendor_stats)} vendors")
        print(f"  📊 Top 5 vendors by product count:")
        for v in vendor_stats[:5]:
            print(f"     - {v['vendor_name']}: {v['product_count']} products")
    
    def save_results(self):
        """Save validation results to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save detailed JSON report
        report_data = {
            'timestamp': timestamp,
            'metrics': self.data_quality_metrics,
            'validation_results': dict(self.validation_results)
        }
        
        with open(f'inventory_validation_{timestamp}.json', 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        # Generate HTML report
        self.generate_html_report(timestamp)
        
        print(f"\n✅ Validation complete! Reports saved:")
        print(f"   - inventory_validation_{timestamp}.json")
        print(f"   - inventory_validation_{timestamp}.html")
    
    def generate_html_report(self, timestamp):
        """Generate HTML report with validation results"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Inventory Data Validation Report - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .metric {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }}
        .warning {{ background: #fff3cd; border-left-color: #ffc107; }}
        .error {{ background: #f8d7da; border-left-color: #dc3545; }}
        .success {{ background: #d4edda; border-left-color: #28a745; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px; text-align: left; border: 1px solid #ddd; }}
        th {{ background: #007bff; color: white; }}
        tr:nth-child(even) {{ background: #f8f9fa; }}
        .issue-list {{ max-height: 300px; overflow-y: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Inventory Data Validation Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>📊 Data Quality Metrics</h2>
        <div class="metric success">
            <h3>Overall Statistics</h3>
            <p>Total Inventory Items: <strong>{self.data_quality_metrics.get('total_inventory_items', 0)}</strong></p>
            <p>Total Recipes: <strong>{self.data_quality_metrics.get('total_recipes', 0)}</strong></p>
            <p>Total Vendors: <strong>{self.data_quality_metrics.get('total_vendors', 0)}</strong></p>
        </div>
        
        <div class="metric">
            <h3>Data Completeness</h3>
            <p>Vendor Information: <strong>{self.data_quality_metrics.get('vendor_completeness', 0):.1f}%</strong></p>
            <p>Pricing Data: <strong>{self.data_quality_metrics.get('price_completeness', 0):.1f}%</strong></p>
            <p>Item Codes: <strong>{self.data_quality_metrics.get('item_code_completeness', 0):.1f}%</strong></p>
            <p>Recipe Linkages: <strong>{self.data_quality_metrics.get('recipe_linkage_percentage', 0):.1f}%</strong></p>
        </div>
        
        <h2>⚠️ Data Quality Issues</h2>
        """
        
        # Add issue summaries
        for issue_type, issues in self.validation_results.items():
            if issues:
                severity = 'warning' if len(issues) < 10 else 'error'
                html += f"""
        <div class="metric {severity}">
            <h3>{issue_type.replace('_', ' ').title()}</h3>
            <p>Found <strong>{len(issues)}</strong> issues</p>
        </div>
                """
        
        # Add vendor statistics table
        if self.validation_results.get('vendor_statistics'):
            html += """
        <h2>📦 Vendor Analysis</h2>
        <table>
            <tr>
                <th>Vendor</th>
                <th>Products</th>
                <th>Priced Items</th>
                <th>Avg Price</th>
                <th>Price Range</th>
            </tr>
            """
            for vendor in self.validation_results['vendor_statistics'][:20]:
                html += f"""
            <tr>
                <td>{vendor['vendor']}</td>
                <td>{vendor['product_count']}</td>
                <td>{vendor['priced_items']}</td>
                <td>${vendor['avg_price']:.2f}</td>
                <td>{vendor['price_range']}</td>
            </tr>
                """
            html += "</table>"
        
        html += """
    </div>
</body>
</html>
        """
        
        with open(f'inventory_validation_{timestamp}.html', 'w') as f:
            f.write(html)

def main():
    validator = InventoryDataValidator()
    validator.run_all_validations()
    validator.save_results()

if __name__ == "__main__":
    main()