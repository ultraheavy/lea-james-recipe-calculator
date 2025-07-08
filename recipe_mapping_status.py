#!/usr/bin/env python3
"""
Recipe Mapping Status Report
Verifies all recipe-ingredient mappings and identifies issues
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

class RecipeMappingVerifier:
    def __init__(self, db_path='restaurant_calculator.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
    def verify_mappings(self):
        """Comprehensive recipe-ingredient mapping verification"""
        print("🔗 Recipe Mapping Status Verification")
        print("=" * 60)
        
        # Get all recipe ingredients with mapping status
        mapping_status = self.get_mapping_status()
        
        # Analyze approved mappings
        approved_status = self.check_approved_mappings()
        
        # Find unmapped ingredients
        unmapped = self.find_unmapped_ingredients()
        
        # Check for custom vs vendor items
        custom_analysis = self.analyze_custom_items()
        
        # Generate report
        self.generate_html_report(mapping_status, approved_status, unmapped, custom_analysis)
        
        return mapping_status, unmapped
    
    def get_mapping_status(self):
        """Get comprehensive mapping status for all recipe ingredients"""
        query = """
        SELECT 
            r.id as recipe_id,
            r.recipe_name,
            r.status as recipe_status,
            ri.id as link_id,
            ri.ingredient_name,
            ri.ingredient_id,
            ri.quantity,
            ri.unit_of_measure,
            ri.cost,
            i.item_description as mapped_item,
            i.vendor_name,
            i.current_price,
            i.item_code,
            CASE 
                WHEN ri.ingredient_id IS NULL OR ri.ingredient_id = 0 THEN 'UNMAPPED'
                WHEN i.id IS NULL THEN 'INVALID_MAPPING'
                WHEN i.item_code LIKE 'CUSTOM-%' THEN 'CUSTOM_ITEM'
                ELSE 'VENDOR_ITEM'
            END as mapping_status
        FROM recipes r
        LEFT JOIN recipe_ingredients ri ON r.id = ri.recipe_id
        LEFT JOIN inventory i ON ri.ingredient_id = i.id
        ORDER BY r.recipe_name, ri.ingredient_name
        """
        
        return pd.read_sql_query(query, self.conn)
    
    def check_approved_mappings(self):
        """Verify approved mappings from CSV files"""
        approved_mappings = []
        issues = []
        
        # Check approved mappings file
        approved_path = 'data/sources/mapping_approved.csv'
        if os.path.exists(approved_path):
            try:
                approved_df = pd.read_csv(approved_path)
                print(f"  ✓ Found {len(approved_df)} approved mappings")
                
                # Verify each approved mapping
                for _, mapping in approved_df.iterrows():
                    # Check if mapping is implemented
                    query = """
                    SELECT ri.*, i.item_description
                    FROM recipe_ingredients ri
                    LEFT JOIN inventory i ON ri.ingredient_id = i.id
                    WHERE ri.ingredient_name LIKE ?
                    """
                    
                    results = pd.read_sql_query(query, self.conn, params=[f"%{mapping.get('recipe_ingredient', '')}%"])
                    
                    if results.empty:
                        issues.append({
                            'type': 'mapping_not_found',
                            'recipe_ingredient': mapping.get('recipe_ingredient', 'Unknown'),
                            'approved_item': mapping.get('inventory_item', 'Unknown')
                        })
                    else:
                        for _, result in results.iterrows():
                            if result['item_description'] != mapping.get('inventory_item'):
                                issues.append({
                                    'type': 'incorrect_mapping',
                                    'recipe_ingredient': mapping.get('recipe_ingredient'),
                                    'expected': mapping.get('inventory_item'),
                                    'actual': result['item_description']
                                })
                
            except Exception as e:
                print(f"  ❌ Error reading approved mappings: {e}")
        
        return {'approved_count': len(approved_mappings), 'issues': issues}
    
    def find_unmapped_ingredients(self):
        """Find all unmapped recipe ingredients"""
        query = """
        SELECT 
            r.recipe_name,
            r.status as recipe_status,
            ri.id as link_id,
            ri.ingredient_name,
            ri.quantity,
            ri.unit_of_measure,
            COUNT(*) OVER (PARTITION BY r.id) as recipe_ingredient_count,
            COUNT(CASE WHEN ri.ingredient_id IS NOT NULL AND ri.ingredient_id != 0 
                      THEN 1 END) OVER (PARTITION BY r.id) as mapped_count
        FROM recipes r
        JOIN recipe_ingredients ri ON r.id = ri.recipe_id
        WHERE ri.ingredient_id IS NULL OR ri.ingredient_id = 0
        ORDER BY r.recipe_name, ri.ingredient_name
        """
        
        unmapped = pd.read_sql_query(query, self.conn)
        
        # Group by recipe
        recipe_summary = unmapped.groupby(['recipe_name', 'recipe_status']).agg({
            'link_id': 'count',
            'recipe_ingredient_count': 'first',
            'mapped_count': 'first'
        }).reset_index()
        
        recipe_summary.columns = ['recipe_name', 'recipe_status', 'unmapped_count', 
                                  'total_ingredients', 'mapped_count']
        
        return {
            'unmapped_details': unmapped,
            'recipe_summary': recipe_summary
        }
    
    def analyze_custom_items(self):
        """Analyze custom vs vendor items in recipes"""
        query = """
        SELECT 
            CASE 
                WHEN i.item_code LIKE 'CUSTOM-%' THEN 'Custom Item'
                WHEN i.vendor_name IS NULL THEN 'No Vendor'
                ELSE 'Vendor Item'
            END as item_type,
            COUNT(DISTINCT ri.id) as usage_count,
            COUNT(DISTINCT ri.recipe_id) as recipe_count,
            COUNT(DISTINCT i.id) as unique_items,
            AVG(ri.cost) as avg_cost
        FROM recipe_ingredients ri
        JOIN inventory i ON ri.ingredient_id = i.id
        WHERE ri.ingredient_id IS NOT NULL AND ri.ingredient_id != 0
        GROUP BY item_type
        """
        
        return pd.read_sql_query(query, self.conn)
    
    def generate_html_report(self, mapping_status, approved_status, unmapped, custom_analysis):
        """Generate comprehensive HTML mapping report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Calculate statistics
        total_links = len(mapping_status)
        mapped_links = len(mapping_status[mapping_status['mapping_status'] != 'UNMAPPED'])
        unmapped_count = len(mapping_status[mapping_status['mapping_status'] == 'UNMAPPED'])
        invalid_count = len(mapping_status[mapping_status['mapping_status'] == 'INVALID_MAPPING'])
        
        mapping_percentage = (mapped_links / total_links * 100) if total_links > 0 else 0
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Recipe Mapping Status Report - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #e74c3c; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; background: #ecf0f1; padding: 10px; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-card.success {{ border-left: 4px solid #27ae60; }}
        .stat-card.warning {{ border-left: 4px solid #f39c12; }}
        .stat-card.error {{ border-left: 4px solid #e74c3c; }}
        .stat-value {{ font-size: 2.5em; font-weight: bold; margin: 10px 0; }}
        .stat-label {{ color: #7f8c8d; font-size: 0.9em; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px; text-align: left; border: 1px solid #ddd; }}
        th {{ background: #34495e; color: white; }}
        tr:nth-child(even) {{ background: #f8f9fa; }}
        .unmapped {{ background: #ffebee; }}
        .custom {{ background: #e3f2fd; }}
        .progress-bar {{ width: 100%; height: 20px; background: #ecf0f1; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: #27ae60; transition: width 0.3s; }}
        .recipe-status {{ padding: 5px 10px; border-radius: 4px; font-size: 0.85em; }}
        .status-active {{ background: #27ae60; color: white; }}
        .status-draft {{ background: #f39c12; color: white; }}
        .status-inactive {{ background: #95a5a6; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 Recipe Mapping Status Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="summary-grid">
            <div class="stat-card success">
                <div class="stat-label">Total Recipe-Ingredient Links</div>
                <div class="stat-value">{total_links}</div>
            </div>
            <div class="stat-card {'success' if mapping_percentage >= 95 else 'warning' if mapping_percentage >= 80 else 'error'}">
                <div class="stat-label">Mapping Completeness</div>
                <div class="stat-value">{mapping_percentage:.1f}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {mapping_percentage}%"></div>
                </div>
            </div>
            <div class="stat-card {'error' if unmapped_count > 0 else 'success'}">
                <div class="stat-label">Unmapped Ingredients</div>
                <div class="stat-value">{unmapped_count}</div>
            </div>
            <div class="stat-card {'error' if invalid_count > 0 else 'success'}">
                <div class="stat-label">Invalid Mappings</div>
                <div class="stat-value">{invalid_count}</div>
            </div>
        </div>
        """
        
        # Recipes with unmapped ingredients
        if not unmapped['recipe_summary'].empty:
            html += """
        <h2>⚠️ Recipes with Unmapped Ingredients</h2>
        <table>
            <tr>
                <th>Recipe Name</th>
                <th>Status</th>
                <th>Unmapped</th>
                <th>Total Ingredients</th>
                <th>Mapping %</th>
            </tr>
            """
            
            for _, recipe in unmapped['recipe_summary'].iterrows():
                mapping_pct = (recipe['mapped_count'] / recipe['total_ingredients'] * 100) if recipe['total_ingredients'] > 0 else 0
                status_class = f"status-{recipe['recipe_status'].lower()}"
                
                html += f"""
            <tr class="unmapped">
                <td><strong>{recipe['recipe_name']}</strong></td>
                <td><span class="recipe-status {status_class}">{recipe['recipe_status']}</span></td>
                <td>{recipe['unmapped_count']}</td>
                <td>{recipe['total_ingredients']}</td>
                <td>{mapping_pct:.1f}%</td>
            </tr>
                """
            
            html += "</table>"
            
            # Detailed unmapped ingredients
            html += """
        <h3>Unmapped Ingredient Details</h3>
        <table>
            <tr>
                <th>Recipe</th>
                <th>Ingredient Name</th>
                <th>Quantity</th>
                <th>Unit</th>
                <th>Action Required</th>
            </tr>
            """
            
            for _, item in unmapped['unmapped_details'].head(50).iterrows():
                html += f"""
            <tr>
                <td>{item['recipe_name']}</td>
                <td><strong>{item['ingredient_name'] or 'UNNAMED'}</strong></td>
                <td>{item['quantity']}</td>
                <td>{item['unit_of_measure'] or 'NO UNIT'}</td>
                <td>Map to inventory item</td>
            </tr>
                """
            
            if len(unmapped['unmapped_details']) > 50:
                html += f"""
            <tr>
                <td colspan="5" style="text-align: center; font-style: italic;">
                    ... and {len(unmapped['unmapped_details']) - 50} more unmapped ingredients
                </td>
            </tr>
                """
            
            html += "</table>"
        
        # Custom vs Vendor items analysis
        if not custom_analysis.empty:
            html += """
        <h2>📊 Custom vs Vendor Items Analysis</h2>
        <table>
            <tr>
                <th>Item Type</th>
                <th>Usage Count</th>
                <th>Recipe Count</th>
                <th>Unique Items</th>
                <th>Avg Cost</th>
            </tr>
            """
            
            for _, row in custom_analysis.iterrows():
                row_class = 'custom' if row['item_type'] == 'Custom Item' else ''
                html += f"""
            <tr class="{row_class}">
                <td><strong>{row['item_type']}</strong></td>
                <td>{row['usage_count']}</td>
                <td>{row['recipe_count']}</td>
                <td>{row['unique_items']}</td>
                <td>${row['avg_cost']:.2f}</td>
            </tr>
                """
            
            html += "</table>"
        
        # Approved mapping issues
        if approved_status['issues']:
            html += f"""
        <h2>❌ Approved Mapping Issues</h2>
        <p>Found {len(approved_status['issues'])} issues with approved mappings:</p>
        <table>
            <tr>
                <th>Issue Type</th>
                <th>Recipe Ingredient</th>
                <th>Expected</th>
                <th>Actual</th>
            </tr>
            """
            
            for issue in approved_status['issues'][:20]:
                html += f"""
            <tr>
                <td>{issue['type'].replace('_', ' ').title()}</td>
                <td>{issue.get('recipe_ingredient', 'N/A')}</td>
                <td>{issue.get('expected', issue.get('approved_item', 'N/A'))}</td>
                <td>{issue.get('actual', 'Not Found')}</td>
            </tr>
                """
            
            html += "</table>"
        
        html += """
        <h2>📋 Next Steps</h2>
        <ol>
            <li><strong>Map Unmapped Ingredients:</strong> Review and map all unmapped ingredients to appropriate inventory items</li>
            <li><strong>Verify Invalid Mappings:</strong> Check and fix any invalid ingredient mappings</li>
            <li><strong>Review Custom Items:</strong> Ensure custom items have accurate pricing</li>
            <li><strong>Update Recipe Status:</strong> Activate recipes once all ingredients are mapped</li>
        </ol>
    </div>
</body>
</html>
        """
        
        filename = f'recipe_mapping_status_{timestamp}.html'
        with open(filename, 'w') as f:
            f.write(html)
        
        print(f"✅ Recipe mapping status report saved: {filename}")
        
        # Save detailed data
        mapping_status.to_csv(f'recipe_mapping_details_{timestamp}.csv', index=False)

def main():
    verifier = RecipeMappingVerifier()
    mapping_status, unmapped = verifier.verify_mappings()
    
    print(f"\n📊 Summary:")
    print(f"  - Total recipe-ingredient links: {len(mapping_status)}")
    print(f"  - Unmapped ingredients: {len(unmapped['unmapped_details'])}")
    print(f"  - Affected recipes: {len(unmapped['recipe_summary'])}")

if __name__ == "__main__":
    main()