#!/usr/bin/env python3
"""
Vendor Analysis and Standardization Report Generator
Analyzes vendor data quality and generates recommendations
"""

import sqlite3
import pandas as pd
from datetime import datetime
import json
from collections import Counter, defaultdict

class VendorAnalyzer:
    def __init__(self, db_path='restaurant_calculator.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
    def analyze_vendors(self):
        """Comprehensive vendor analysis"""
        print("📦 Vendor Analysis Report Generation")
        print("=" * 60)
        
        # Get all vendor data
        query = """
        SELECT 
            vendor_name,
            COUNT(*) as product_count,
            COUNT(DISTINCT item_code) as unique_codes,
            COUNT(CASE WHEN current_price > 0 THEN 1 END) as priced_items,
            AVG(current_price) as avg_price,
            MIN(current_price) as min_price,
            MAX(current_price) as max_price,
            COUNT(DISTINCT product_categories) as category_count,
            GROUP_CONCAT(DISTINCT product_categories) as categories
        FROM inventory
        WHERE vendor_name IS NOT NULL AND vendor_name != ''
        GROUP BY vendor_name
        ORDER BY product_count DESC
        """
        
        vendors = pd.read_sql_query(query, self.conn)
        
        # Analyze vendor naming patterns
        vendor_issues = self.find_vendor_naming_issues(vendors)
        
        # Analyze product distribution
        product_analysis = self.analyze_product_distribution()
        
        # Generate recommendations
        recommendations = self.generate_vendor_recommendations(vendors, vendor_issues)
        
        # Create HTML report
        self.generate_html_report(vendors, vendor_issues, product_analysis, recommendations)
        
        return vendors, vendor_issues, recommendations
    
    def find_vendor_naming_issues(self, vendors):
        """Find potential vendor naming inconsistencies"""
        issues = []
        vendor_names = vendors['vendor_name'].tolist()
        
        # Check for similar vendor names
        for i, v1 in enumerate(vendor_names):
            for v2 in vendor_names[i+1:]:
                # Check for case variations
                if v1.lower() == v2.lower() and v1 != v2:
                    issues.append({
                        'type': 'case_variation',
                        'vendor1': v1,
                        'vendor2': v2,
                        'recommendation': f"Standardize to: {v1.upper()}"
                    })
                
                # Check for punctuation variations
                v1_clean = v1.replace(',', '').replace('.', '').replace("'", '')
                v2_clean = v2.replace(',', '').replace('.', '').replace("'", '')
                if v1_clean.lower() == v2_clean.lower() and v1 != v2:
                    issues.append({
                        'type': 'punctuation_variation',
                        'vendor1': v1,
                        'vendor2': v2,
                        'recommendation': f"Standardize punctuation"
                    })
                
                # Check for Inc/INC variations
                if 'inc' in v1.lower() and 'inc' in v2.lower():
                    if v1.replace('INC.', 'INC').replace('Inc.', 'INC') == v2.replace('INC.', 'INC').replace('Inc.', 'INC'):
                        issues.append({
                            'type': 'inc_variation',
                            'vendor1': v1,
                            'vendor2': v2,
                            'recommendation': "Standardize to 'INC.'"
                        })
        
        return issues
    
    def analyze_product_distribution(self):
        """Analyze how products are distributed across vendors"""
        query = """
        SELECT 
            item_description,
            COUNT(DISTINCT vendor_name) as vendor_count,
            GROUP_CONCAT(DISTINCT vendor_name) as vendors,
            MIN(current_price) as min_price,
            MAX(current_price) as max_price,
            AVG(current_price) as avg_price
        FROM inventory
        WHERE vendor_name IS NOT NULL
        GROUP BY item_description
        HAVING vendor_count > 1
        ORDER BY vendor_count DESC, item_description
        """
        
        multi_vendor_products = pd.read_sql_query(query, self.conn)
        
        # Find products with significant price variations
        multi_vendor_products['price_variation'] = (
            (multi_vendor_products['max_price'] - multi_vendor_products['min_price']) / 
            multi_vendor_products['avg_price'] * 100
        )
        
        return multi_vendor_products
    
    def generate_vendor_recommendations(self, vendors, issues):
        """Generate specific recommendations for vendor data"""
        recommendations = {
            'standardization': [],
            'consolidation': [],
            'data_quality': [],
            'pricing': []
        }
        
        # Vendor naming standardization
        if issues:
            recommendations['standardization'].append({
                'priority': 'HIGH',
                'action': 'Standardize vendor naming conventions',
                'details': f"Found {len(issues)} vendor naming inconsistencies",
                'examples': issues[:3]
            })
        
        # Identify vendors needing consolidation
        vendor_groups = defaultdict(list)
        for _, vendor in vendors.iterrows():
            base_name = vendor['vendor_name'].upper().replace('INC.', '').replace(',', '').strip()
            vendor_groups[base_name].append(vendor['vendor_name'])
        
        for base, names in vendor_groups.items():
            if len(names) > 1:
                recommendations['consolidation'].append({
                    'priority': 'MEDIUM',
                    'action': f"Consolidate vendor variations",
                    'vendors': names,
                    'suggested_name': names[0]  # Use the most common format
                })
        
        # Data quality recommendations
        for _, vendor in vendors.iterrows():
            completion_rate = vendor['priced_items'] / vendor['product_count']
            if completion_rate < 0.9:
                recommendations['data_quality'].append({
                    'priority': 'HIGH',
                    'vendor': vendor['vendor_name'],
                    'action': 'Update missing price data',
                    'missing_prices': vendor['product_count'] - vendor['priced_items']
                })
        
        return recommendations
    
    def generate_html_report(self, vendors, issues, product_analysis, recommendations):
        """Generate comprehensive HTML vendor report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Vendor Analysis Report - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; background: #ecf0f1; padding: 10px; }}
        h3 {{ color: #7f8c8d; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #3498db; }}
        .stat-card h4 {{ margin: 0 0 10px 0; color: #2c3e50; }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: #3498db; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border: 1px solid #ddd; }}
        th {{ background: #3498db; color: white; font-weight: bold; }}
        tr:nth-child(even) {{ background: #f8f9fa; }}
        .warning {{ background: #fff3cd; color: #856404; padding: 10px; border-radius: 4px; margin: 10px 0; }}
        .recommendation {{ background: #d1ecf1; color: #0c5460; padding: 15px; border-radius: 4px; margin: 10px 0; }}
        .high-priority {{ border-left: 4px solid #e74c3c; }}
        .medium-priority {{ border-left: 4px solid #f39c12; }}
        .low-priority {{ border-left: 4px solid #27ae60; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📦 Vendor Analysis & Standardization Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="summary-grid">
            <div class="stat-card">
                <h4>Total Vendors</h4>
                <div class="stat-value">{len(vendors)}</div>
            </div>
            <div class="stat-card">
                <h4>Total Products</h4>
                <div class="stat-value">{vendors['product_count'].sum()}</div>
            </div>
            <div class="stat-card">
                <h4>Naming Issues Found</h4>
                <div class="stat-value">{len(issues)}</div>
            </div>
            <div class="stat-card">
                <h4>Average Products/Vendor</h4>
                <div class="stat-value">{vendors['product_count'].mean():.1f}</div>
            </div>
        </div>
        
        <h2>🏢 Vendor Overview</h2>
        <table>
            <tr>
                <th>Vendor Name</th>
                <th>Products</th>
                <th>Priced Items</th>
                <th>Avg Price</th>
                <th>Price Range</th>
                <th>Categories</th>
                <th>Data Quality</th>
            </tr>
        """
        
        for _, vendor in vendors.iterrows():
            completion = vendor['priced_items'] / vendor['product_count'] * 100
            quality_color = '#27ae60' if completion >= 95 else '#f39c12' if completion >= 80 else '#e74c3c'
            
            html += f"""
            <tr>
                <td><strong>{vendor['vendor_name']}</strong></td>
                <td>{vendor['product_count']}</td>
                <td>{vendor['priced_items']}</td>
                <td>${vendor['avg_price']:.2f}</td>
                <td>${vendor['min_price']:.2f} - ${vendor['max_price']:.2f}</td>
                <td>{vendor['category_count']} categories</td>
                <td><span style="color: {quality_color}; font-weight: bold;">{completion:.1f}%</span></td>
            </tr>
            """
        
        html += "</table>"
        
        # Vendor naming issues
        if issues:
            html += """
        <h2>⚠️ Vendor Naming Issues</h2>
        <div class="warning">
            <p><strong>Found vendor naming inconsistencies that should be standardized:</strong></p>
        </div>
        <table>
            <tr>
                <th>Issue Type</th>
                <th>Vendor 1</th>
                <th>Vendor 2</th>
                <th>Recommendation</th>
            </tr>
            """
            for issue in issues[:10]:  # Show first 10
                html += f"""
            <tr>
                <td>{issue['type'].replace('_', ' ').title()}</td>
                <td>{issue['vendor1']}</td>
                <td>{issue['vendor2']}</td>
                <td>{issue['recommendation']}</td>
            </tr>
                """
            html += "</table>"
        
        # Recommendations
        html += "<h2>📋 Recommendations</h2>"
        
        for category, recs in recommendations.items():
            if recs:
                html += f"<h3>{category.replace('_', ' ').title()}</h3>"
                for rec in recs[:5]:  # Show first 5
                    priority_class = rec.get('priority', 'MEDIUM').lower() + '-priority'
                    html += f"""
                <div class="recommendation {priority_class}">
                    <strong>Priority: {rec.get('priority', 'MEDIUM')}</strong><br>
                    Action: {rec.get('action', 'N/A')}<br>
                    """
                    if 'details' in rec:
                        html += f"Details: {rec['details']}<br>"
                    if 'vendors' in rec:
                        html += f"Vendors: {', '.join(rec['vendors'])}<br>"
                    html += "</div>"
        
        # Multi-vendor products
        if not product_analysis.empty:
            high_variation = product_analysis[product_analysis['price_variation'] > 20]
            if not high_variation.empty:
                html += """
        <h2>💰 Products with Price Variations</h2>
        <p>Products sold by multiple vendors with significant price differences:</p>
        <table>
            <tr>
                <th>Product</th>
                <th>Vendors</th>
                <th>Min Price</th>
                <th>Max Price</th>
                <th>Variation</th>
            </tr>
                """
                for _, prod in high_variation.head(15).iterrows():
                    html += f"""
            <tr>
                <td>{prod['item_description']}</td>
                <td>{prod['vendor_count']} vendors</td>
                <td>${prod['min_price']:.2f}</td>
                <td>${prod['max_price']:.2f}</td>
                <td>{prod['price_variation']:.1f}%</td>
            </tr>
                    """
                html += "</table>"
        
        html += """
    </div>
</body>
</html>
        """
        
        filename = f'vendor_analysis_report_{timestamp}.html'
        with open(filename, 'w') as f:
            f.write(html)
        
        print(f"✅ Vendor analysis report saved: {filename}")
        
        # Also save raw data
        vendors.to_csv(f'vendor_data_{timestamp}.csv', index=False)
        
        with open(f'vendor_recommendations_{timestamp}.json', 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'issues': issues,
                'recommendations': recommendations
            }, f, indent=2)

def main():
    analyzer = VendorAnalyzer()
    vendors, issues, recommendations = analyzer.analyze_vendors()
    
    print(f"\n📊 Summary:")
    print(f"  - Total vendors: {len(vendors)}")
    print(f"  - Naming issues: {len(issues)}")
    print(f"  - Recommendations: {sum(len(v) for v in recommendations.values())}")

if __name__ == "__main__":
    main()