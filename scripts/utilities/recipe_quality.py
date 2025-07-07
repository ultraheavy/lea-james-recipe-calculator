#!/usr/bin/env python3
"""
Recipe quality sweep - flag issues and generate reports
"""

import sqlite3
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RecipeQualityChecker:
    """Check recipes for quality issues"""
    
    def __init__(self, db_path: str = 'restaurant_calculator.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._ensure_notes_table()
        
    def _ensure_notes_table(self):
        """Ensure recipe_notes table exists"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipe_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                note_type TEXT NOT NULL,
                note_text TEXT NOT NULL,
                severity TEXT DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id),
                UNIQUE(recipe_id, note_type)
            )
        """)
        self.conn.commit()
        
    def check_high_food_cost(self, threshold: float = 100.0) -> List[Dict]:
        """Find recipes with food cost > threshold%"""
        cursor = self.conn.cursor()
        query = """
            SELECT 
                r.id,
                r.recipe_name,
                r.food_cost,
                r.menu_price,
                r.food_cost_percentage,
                COUNT(ri.id) as ingredient_count,
                SUM(ri.cost) as total_ingredient_cost
            FROM recipes r
            LEFT JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            WHERE r.food_cost_percentage > ?
              AND r.menu_price > 0
            GROUP BY r.id
            ORDER BY r.food_cost_percentage DESC
        """
        
        issues = []
        for row in cursor.execute(query, (threshold,)):
            issues.append({
                'recipe_id': row['id'],
                'recipe_name': row['recipe_name'],
                'food_cost': row['food_cost'],
                'menu_price': row['menu_price'],
                'food_cost_percentage': row['food_cost_percentage'],
                'ingredient_count': row['ingredient_count'],
                'total_ingredient_cost': row['total_ingredient_cost'],
                'issue_type': 'high_food_cost',
                'severity': 'high'
            })
            
        return issues
    
    def check_no_ingredients(self) -> List[Dict]:
        """Find recipes with no ingredients"""
        cursor = self.conn.cursor()
        query = """
            SELECT 
                r.id,
                r.recipe_name,
                r.menu_price,
                r.recipe_group
            FROM recipes r
            LEFT JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            LEFT JOIN recipe_components rc ON r.id = rc.parent_recipe_id
            WHERE ri.id IS NULL AND rc.id IS NULL
            ORDER BY r.recipe_name
        """
        
        issues = []
        for row in cursor.execute(query):
            issues.append({
                'recipe_id': row['id'],
                'recipe_name': row['recipe_name'],
                'menu_price': row['menu_price'],
                'recipe_group': row['recipe_group'],
                'issue_type': 'no_ingredients',
                'severity': 'critical'
            })
            
        return issues
    
    def check_zero_cost_ingredients(self) -> List[Dict]:
        """Find recipes where all ingredients have zero cost"""
        cursor = self.conn.cursor()
        query = """
            SELECT 
                r.id,
                r.recipe_name,
                r.menu_price,
                COUNT(ri.id) as ingredient_count,
                SUM(CASE WHEN ri.cost > 0 THEN 1 ELSE 0 END) as costed_count,
                GROUP_CONCAT(ri.ingredient_name) as ingredients
            FROM recipes r
            JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            GROUP BY r.id
            HAVING costed_count = 0
            ORDER BY r.recipe_name
        """
        
        issues = []
        for row in cursor.execute(query):
            issues.append({
                'recipe_id': row['id'],
                'recipe_name': row['recipe_name'],
                'menu_price': row['menu_price'],
                'ingredient_count': row['ingredient_count'],
                'ingredients': row['ingredients'],
                'issue_type': 'zero_cost',
                'severity': 'high'
            })
            
        return issues
    
    def check_missing_costs(self) -> List[Dict]:
        """Find recipes with some missing ingredient costs"""
        cursor = self.conn.cursor()
        query = """
            SELECT 
                r.id,
                r.recipe_name,
                COUNT(ri.id) as total_ingredients,
                SUM(CASE WHEN i.current_price IS NULL OR i.current_price = 0 
                    THEN 1 ELSE 0 END) as missing_costs,
                GROUP_CONCAT(CASE WHEN i.current_price IS NULL OR i.current_price = 0 
                    THEN ri.ingredient_name ELSE NULL END) as missing_items
            FROM recipes r
            JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            LEFT JOIN inventory i ON ri.ingredient_id = i.id
            GROUP BY r.id
            HAVING missing_costs > 0
            ORDER BY missing_costs DESC, r.recipe_name
        """
        
        issues = []
        for row in cursor.execute(query):
            issues.append({
                'recipe_id': row['id'],
                'recipe_name': row['recipe_name'],
                'total_ingredients': row['total_ingredients'],
                'missing_costs': row['missing_costs'],
                'missing_items': row['missing_items'],
                'issue_type': 'missing_costs',
                'severity': 'medium'
            })
            
        return issues
    
    def save_issue_to_notes(self, recipe_id: int, issue_type: str, 
                           note_text: str, severity: str = 'medium'):
        """Save issue to recipe_notes table"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO recipe_notes 
            (recipe_id, note_type, note_text, severity)
            VALUES (?, ?, ?, ?)
        """, (recipe_id, issue_type, note_text, severity))
        
        self.conn.commit()
    
    def generate_quality_report(self, output_file: str = None) -> str:
        """Generate comprehensive quality report"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'recipe_quality_{timestamp}.csv'
        
        # Run all checks
        all_issues = []
        
        # High food cost
        high_cost = self.check_high_food_cost()
        for issue in high_cost:
            note = f"Food cost {issue['food_cost_percentage']:.1f}% exceeds menu price"
            self.save_issue_to_notes(issue['recipe_id'], 'high_food_cost', 
                                   note, issue['severity'])
        all_issues.extend(high_cost)
        
        # No ingredients
        no_ingredients = self.check_no_ingredients()
        for issue in no_ingredients:
            note = "Recipe has no ingredients or components defined"
            self.save_issue_to_notes(issue['recipe_id'], 'no_ingredients', 
                                   note, issue['severity'])
        all_issues.extend(no_ingredients)
        
        # Zero cost
        zero_cost = self.check_zero_cost_ingredients()
        for issue in zero_cost:
            note = f"All {issue['ingredient_count']} ingredients have zero cost"
            self.save_issue_to_notes(issue['recipe_id'], 'zero_cost', 
                                   note, issue['severity'])
        all_issues.extend(zero_cost)
        
        # Missing costs
        missing_costs = self.check_missing_costs()
        for issue in missing_costs:
            note = f"{issue['missing_costs']} of {issue['total_ingredients']} ingredients missing costs"
            self.save_issue_to_notes(issue['recipe_id'], 'missing_costs', 
                                   note, issue['severity'])
        all_issues.extend(missing_costs)
        
        # Write CSV report
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if all_issues:
                # Get all unique fieldnames from all issues
                fieldnames = set()
                for issue in all_issues:
                    fieldnames.update(issue.keys())
                fieldnames = sorted(list(fieldnames))
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_issues)
        
        # Log summary
        logger.info(f"Recipe quality check complete:")
        logger.info(f"  High food cost (>100%): {len(high_cost)}")
        logger.info(f"  No ingredients: {len(no_ingredients)}")
        logger.info(f"  All zero cost: {len(zero_cost)}")
        logger.info(f"  Some missing costs: {len(missing_costs)}")
        logger.info(f"  Total issues: {len(all_issues)}")
        logger.info(f"Report saved to: {output_file}")
        
        return output_file
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    """Main entry point"""
    checker = RecipeQualityChecker()
    
    try:
        report_file = checker.generate_quality_report()
        print(f"Quality report generated: {report_file}")
        
        # Also output summary to stdout
        cursor = checker.conn.cursor()
        summary = cursor.execute("""
            SELECT 
                note_type,
                severity,
                COUNT(*) as count
            FROM recipe_notes
            GROUP BY note_type, severity
            ORDER BY severity DESC, count DESC
        """).fetchall()
        
        print("\nRecipe Quality Summary:")
        print("-" * 50)
        for row in summary:
            print(f"{row[0]:20} {row[1]:8} {row[2]:5} recipes")
        
    finally:
        checker.close()

if __name__ == '__main__':
    main()