#!/usr/bin/env python3
"""
ingredient_matcher.py - Fuzzy matching for ingredient names to inventory items
"""

import sqlite3
import csv
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import logging

try:
    from rapidfuzz import process, fuzz
except ImportError:
    print("ERROR: rapidfuzz not installed. Run: pip install rapidfuzz")
    exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IngredientMatcher:
    """Fuzzy match recipe ingredients to inventory items"""
    
    def __init__(self, db_path: str = 'restaurant_calculator.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
    def get_mismatched_ingredients(self) -> List[Dict]:
        """Get all recipe ingredients that don't match inventory"""
        cursor = self.conn.cursor()
        query = """
            SELECT DISTINCT
                ri.recipe_id,
                ri.id as ri_id,
                ri.ingredient_name,
                r.recipe_name,
                ri.ingredient_id
            FROM recipe_ingredients ri
            JOIN recipes r ON ri.recipe_id = r.id
            WHERE ri.ingredient_id IS NULL
               OR ri.ingredient_id NOT IN (SELECT id FROM inventory)
            ORDER BY ri.recipe_id, ri.ingredient_name
        """
        
        results = []
        for row in cursor.execute(query):
            results.append({
                'recipe_id': row['recipe_id'],
                'ingredient_id': row['ri_id'],
                'ingredient_name': row['ingredient_name'],
                'recipe_name': row['recipe_name'],
                'current_inventory_id': row['ingredient_id']
            })
        
        return results
    
    def get_inventory_items(self) -> Dict[int, str]:
        """Get all inventory items for matching"""
        cursor = self.conn.cursor()
        query = """
            SELECT id, item_description
            FROM inventory
            WHERE item_description IS NOT NULL
              AND item_description != ''
        """
        
        items = {}
        for row in cursor.execute(query):
            items[row['id']] = row['item_description']
        
        return items
    
    def normalize_name(self, name: str) -> str:
        """Normalize ingredient/item names for better matching"""
        if not name:
            return ""
        
        # Convert to lowercase
        name = name.lower().strip()
        
        # Remove common prefixes
        prefixes = ['dry goods,', 'produce,', 'protein,', 'dairy,', 'frozen,', 'n/a bev,', 'non con,']
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):].strip()
        
        # Normalize common terms
        replacements = {
            ' - ': ' ',
            '  ': ' ',
            'chesse': 'cheese',
            'mayonaise': 'mayonnaise',
            'sambal': 'sambal chili',
            'chickn': 'chicken',
            'pd ': '',
            'wt': '',
            '-v': '',
        }
        
        for old, new in replacements.items():
            name = name.replace(old, new)
        
        return name.strip()
    
    def find_matches(self, ingredient_name: str, inventory_items: Dict[int, str], 
                    limit: int = 3) -> List[Tuple[int, str, float]]:
        """Find best matching inventory items for an ingredient"""
        if not ingredient_name:
            return []
        
        # Normalize the search term
        search_term = self.normalize_name(ingredient_name)
        
        # Create normalized inventory mapping
        normalized_inventory = {
            item_id: (self.normalize_name(desc), desc) 
            for item_id, desc in inventory_items.items()
        }
        
        # Prepare choices for fuzzy matching
        choices = {
            item_id: norm_desc 
            for item_id, (norm_desc, _) in normalized_inventory.items()
        }
        
        # Perform fuzzy matching
        matches = process.extract(
            search_term,
            choices,
            scorer=fuzz.token_sort_ratio,
            limit=limit
        )
        
        # Format results
        results = []
        for match, score, item_id in matches:
            _, original_desc = normalized_inventory[item_id]
            results.append((item_id, original_desc, score))
        
        return results
    
    def generate_mapping_review(self, output_file: str = None) -> str:
        """Generate CSV file for manual review of matches"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'mapping_review_{timestamp}.csv'
        
        mismatched = self.get_mismatched_ingredients()
        inventory_items = self.get_inventory_items()
        
        logger.info(f"Found {len(mismatched)} mismatched ingredients")
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'recipe_id', 'ingredient_id', 'recipe_name', 'bad_name',
                'suggestion_1', 'score_1', 'id_1',
                'suggestion_2', 'score_2', 'id_2',
                'suggestion_3', 'score_3', 'id_3',
                'selected_id', 'action'
            ])
            
            for item in mismatched:
                matches = self.find_matches(item['ingredient_name'], inventory_items)
                
                row = [
                    item['recipe_id'],
                    item['ingredient_id'],
                    item['recipe_name'],
                    item['ingredient_name']
                ]
                
                # Add up to 3 suggestions
                for i in range(3):
                    if i < len(matches):
                        item_id, desc, score = matches[i]
                        row.extend([desc, f"{score:.1f}", item_id])
                    else:
                        row.extend(['', '', ''])
                
                # Add columns for manual selection
                row.extend(['', ''])  # selected_id, action
                
                writer.writerow(row)
        
        logger.info(f"Mapping review saved to {output_file}")
        return output_file
    
    def apply_mappings(self, mapping_file: str) -> int:
        """Apply reviewed mappings from CSV file"""
        if not Path(mapping_file).exists():
            logger.error(f"Mapping file not found: {mapping_file}")
            return 0
        
        updates = []
        
        with open(mapping_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                selected_id = row.get('selected_id', '').strip()
                action = row.get('action', '').strip().lower()
                
                if selected_id and selected_id.isdigit() and action == 'apply':
                    updates.append({
                        'ingredient_id': int(row['ingredient_id']),
                        'inventory_id': int(selected_id)
                    })
        
        if not updates:
            logger.warning("No mappings to apply")
            return 0
        
        # Apply updates
        cursor = self.conn.cursor()
        
        for update in updates:
            cursor.execute("""
                UPDATE recipe_ingredients 
                SET ingredient_id = ?
                WHERE id = ?
            """, (update['inventory_id'], update['ingredient_id']))
        
        self.conn.commit()
        logger.info(f"Applied {len(updates)} ingredient mappings")
        
        return len(updates)
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Fuzzy match recipe ingredients to inventory')
    parser.add_argument('--generate', action='store_true',
                       help='Generate mapping review CSV')
    parser.add_argument('--apply-mappings', type=str,
                       help='Apply mappings from reviewed CSV file')
    parser.add_argument('--output', type=str,
                       help='Output filename for mapping review')
    
    args = parser.parse_args()
    
    matcher = IngredientMatcher()
    
    try:
        if args.generate:
            output_file = matcher.generate_mapping_review(args.output)
            print(f"Mapping review generated: {output_file}")
            
        elif args.apply_mappings:
            count = matcher.apply_mappings(args.apply_mappings)
            print(f"Applied {count} mappings")
            
        else:
            parser.print_help()
            
    finally:
        matcher.close()

if __name__ == '__main__':
    main()