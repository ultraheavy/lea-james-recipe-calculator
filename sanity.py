#!/usr/bin/env python3
"""
sanity.py - Recipe sanity checks and issue flagging
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RecipeSanityChecker:
    """Check recipes for common issues and flag problems"""
    
    def __init__(self, db_path: str = 'restaurant_calculator.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._ensure_notes_table()
        
    def _ensure_notes_table(self):
        """Ensure recipes_notes table exists"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                note_type TEXT NOT NULL,
                note_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id)
            )
        """)
        self.conn.commit()
        
    def check_high_food_cost(self, threshold: float = 100.0) -> List[Dict]:
        """Find recipes with food cost > threshold%"""
        cursor = self.conn.cursor()
        query = """
            SELECT 
                id,
                recipe_name,
                food_cost,
                menu_price,
                food_cost_percentage
            FROM recipes
            WHERE food_cost_percentage > ?
              AND menu_price > 0
            ORDER BY food_cost_percentage DESC
        """
        
        issues = []
        for row in cursor.execute(query, (threshold,)):
            issues.append({
                'recipe_id': row['id'],
                'recipe_name': row['recipe_name'],
                'food_cost': row['food_cost'],
                'menu_price': row['menu_price'],
                'food_cost_percentage': row['food_cost_percentage']
            })
            
        return issues
    
    def check_no_ingredients(self) -> List[Dict]:
        """Find recipes with no ingredients"""
        cursor = self.conn.cursor()
        query = """
            SELECT 
                r.id,
                r.recipe_name
            FROM recipes r
            LEFT JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            WHERE ri.id IS NULL
            ORDER BY r.recipe_name
        """
        
        issues = []
        for row in cursor.execute(query):
            issues.append({
                'recipe_id': row['id'],
                'recipe_name': row['recipe_name']
            })
            
        return issues
    
    def check_zero_cost_ingredients(self) -> List[Dict]:
        """Find recipes with all zero-cost ingredients"""
        cursor = self.conn.cursor()
        query = """
            SELECT 
                r.id,
                r.recipe_name,
                COUNT(ri.id) as ingredient_count,
                SUM(CASE WHEN ri.cost > 0 THEN 1 ELSE 0 END) as costed_count
            FROM recipes r
            JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            GROUP BY r.id, r.recipe_name
            HAVING costed_count = 0
            ORDER BY r.recipe_name
        """
        
        issues = []
        for row in cursor.execute(query):
            issues.append({
                'recipe_id': row['id'],
                'recipe_name': row['recipe_name'],
                'ingredient_count': row['ingredient_count'],
                'costed_count': row['costed_count']
            })
            
        return issues
    
    def flag_issue(self, recipe_id: int, issue_type: str, issue_text: str):
        """Add a note to flag an issue with a recipe"""
        cursor = self.conn.cursor()
        
        # Check if this issue is already flagged
        cursor.execute("""
            SELECT id FROM recipes_notes
            WHERE recipe_id = ? AND note_type = ?
        """, (recipe_id, issue_type))
        
        if cursor.fetchone():
            # Update existing note
            cursor.execute("""
                UPDATE recipes_notes
                SET note_text = ?, created_at = CURRENT_TIMESTAMP
                WHERE recipe_id = ? AND note_type = ?
            """, (issue_text, recipe_id, issue_type))
        else:
            # Insert new note
            cursor.execute("""
                INSERT INTO recipes_notes (recipe_id, note_type, note_text)
                VALUES (?, ?, ?)
            """, (recipe_id, issue_type, issue_text))
        
        self.conn.commit()
    
    def run_all_checks(self):
        """Run all sanity checks and flag issues"""
        logger.info("Running recipe sanity checks...")
        
        # Check high food cost
        high_cost = self.check_high_food_cost()
        logger.info(f"Found {len(high_cost)} recipes with >100% food cost")
        for recipe in high_cost:
            self.flag_issue(
                recipe['recipe_id'],
                'HIGH_FOOD_COST',
                f"Food cost {recipe['food_cost_percentage']:.1f}% exceeds menu price"
            )
        
        # Check no ingredients
        no_ingredients = self.check_no_ingredients()
        logger.info(f"Found {len(no_ingredients)} recipes with no ingredients")
        for recipe in no_ingredients:
            self.flag_issue(
                recipe['recipe_id'],
                'NO_INGREDIENTS',
                "Recipe has no ingredients defined"
            )
        
        # Check zero cost
        zero_cost = self.check_zero_cost_ingredients()
        logger.info(f"Found {len(zero_cost)} recipes with all zero-cost ingredients")
        for recipe in zero_cost:
            self.flag_issue(
                recipe['recipe_id'],
                'ZERO_COST',
                f"All {recipe['ingredient_count']} ingredients have zero cost"
            )
        
        # Generate summary report
        summary = {
            'timestamp': datetime.now().isoformat(),
            'high_food_cost': len(high_cost),
            'no_ingredients': len(no_ingredients),
            'zero_cost_ingredients': len(zero_cost),
            'total_issues': len(high_cost) + len(no_ingredients) + len(zero_cost)
        }
        
        logger.info(f"Sanity check complete: {summary['total_issues']} total issues found")
        
        return summary
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    """Main entry point"""
    checker = RecipeSanityChecker()
    
    try:
        summary = checker.run_all_checks()
        print(json.dumps(summary, indent=2))
    finally:
        checker.close()

if __name__ == '__main__':
    main()