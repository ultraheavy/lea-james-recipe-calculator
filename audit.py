#!/usr/bin/env python3
"""
Data Quality Audit Script for Recipe Cost Database
Scans all tables and validates against business rules
"""
import sqlite3
import csv
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any
from decimal import Decimal, InvalidOperation

# Validation Rules
VALID_UOMS = {
    'weight': ['lb', 'oz', 'g', 'kg', 'gram', 'pound', 'ounce', 'kilogram'],
    'volume': ['gal', 'qt', 'pt', 'cup', 'fl oz', 'l', 'ml', 'gallon', 'quart', 
               'pint', 'fluid ounce', 'liter', 'milliliter'],
    'count': ['each', 'ea', 'dozen', 'doz', 'case', 'cs', 'pack', 'can', 'jar',
              'bag', 'box', 'carton', 'container']
}

ALL_VALID_UOMS = set()
for uom_list in VALID_UOMS.values():
    ALL_VALID_UOMS.update(uom_list)

class DataAuditor:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.failures: List[Dict[str, Any]] = []
        
    def add_failure(self, table: str, pk: Any, error_message: str, 
                   column: str = None, value: Any = None):
        """Record a validation failure"""
        self.failures.append({
            'table': table,
            'pk': str(pk),
            'column': column or '',
            'value': str(value) if value is not None else '',
            'error_message': error_message,
            'timestamp': datetime.now().isoformat()
        })
    
    def validate_numeric(self, value: Any, field_name: str, 
                        min_val: float = None, max_val: float = None) -> bool:
        """Validate numeric fields"""
        if value is None:
            return True  # NULLs handled separately
        
        try:
            num_val = float(value)
            if min_val is not None and num_val < min_val:
                return False
            if max_val is not None and num_val > max_val:
                return False
            return True
        except (ValueError, TypeError):
            return False
    
    def validate_uom(self, uom: str) -> bool:
        """Validate unit of measure"""
        if not uom:
            return False
        
        uom_lower = uom.lower().strip()
        return uom_lower in ALL_VALID_UOMS
    
    def parse_pack_size(self, pack_size: str) -> Tuple[bool, str]:
        """Validate and parse pack size format"""
        if not pack_size:
            return False, "Pack size is empty"
        
        # Pattern: "number x number unit" or "number unit"
        pattern1 = r'^\d+(\.\d+)?\s*x\s*\d+(\.\d+)?\s*\w+$'
        pattern2 = r'^\d+(\.\d+)?\s*\w+$'
        
        if re.match(pattern1, pack_size, re.IGNORECASE):
            # Extract unit from "N x N unit"
            parts = pack_size.split()
            if len(parts) >= 4:
                unit = ' '.join(parts[3:])
                if not self.validate_uom(unit):
                    return False, f"Invalid unit in pack size: {unit}"
            return True, ""
        elif re.match(pattern2, pack_size, re.IGNORECASE):
            # Extract unit from "N unit"
            match = re.match(r'^\d+(\.\d+)?\s*(.+)$', pack_size)
            if match:
                unit = match.group(2)
                if not self.validate_uom(unit):
                    return False, f"Invalid unit in pack size: {unit}"
            return True, ""
        else:
            return False, f"Invalid pack size format: {pack_size}"
    
    def audit_inventory(self):
        """Audit inventory/items table"""
        print("Auditing inventory table...")
        cursor = self.conn.cursor()
        
        rows = cursor.execute("""
            SELECT id, item_code, item_description, current_price, 
                   pack_size, purchase_unit, recipe_cost_unit, yield_percent
            FROM inventory
        """).fetchall()
        
        for row in rows:
            # Required fields
            if not row['item_code']:
                self.add_failure('inventory', row['id'], 
                               'Missing required item_code', 'item_code')
            
            if not row['item_description']:
                self.add_failure('inventory', row['id'], 
                               'Missing required item_description', 'item_description')
            
            # Price validation
            if row['current_price'] is not None:
                if not self.validate_numeric(row['current_price'], 'current_price', min_val=0):
                    self.add_failure('inventory', row['id'], 
                                   f'Invalid price: {row["current_price"]}', 
                                   'current_price', row['current_price'])
            
            # Pack size validation
            if row['pack_size']:
                valid, error = self.parse_pack_size(row['pack_size'])
                if not valid:
                    self.add_failure('inventory', row['id'], error, 
                                   'pack_size', row['pack_size'])
            
            # UOM validation
            if row['purchase_unit'] and not self.validate_uom(row['purchase_unit']):
                self.add_failure('inventory', row['id'], 
                               f'Invalid purchase unit: {row["purchase_unit"]}',
                               'purchase_unit', row['purchase_unit'])
            
            if row['recipe_cost_unit'] and not self.validate_uom(row['recipe_cost_unit']):
                self.add_failure('inventory', row['id'], 
                               f'Invalid recipe cost unit: {row["recipe_cost_unit"]}',
                               'recipe_cost_unit', row['recipe_cost_unit'])
            
            # Yield percent validation
            if row['yield_percent'] is not None:
                if not self.validate_numeric(row['yield_percent'], 'yield_percent', 
                                           min_val=0, max_val=100):
                    self.add_failure('inventory', row['id'], 
                                   f'Invalid yield percent: {row["yield_percent"]}',
                                   'yield_percent', row['yield_percent'])
    
    def audit_recipes(self):
        """Audit recipes table"""
        print("Auditing recipes table...")
        cursor = self.conn.cursor()
        
        rows = cursor.execute("""
            SELECT r.id, r.recipe_name, r.food_cost, r.menu_price, 
                   r.prep_recipe_yield, r.prep_recipe_yield_uom,
                   COUNT(ri.id) as ingredient_count,
                   SUM(CASE WHEN ri.cost > 0 THEN 1 ELSE 0 END) as costed_count
            FROM recipes r
            LEFT JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            GROUP BY r.id
        """).fetchall()
        
        for row in rows:
            # Required fields
            if not row['recipe_name']:
                self.add_failure('recipes', row['id'], 
                               'Missing required recipe_name', 'recipe_name')
            
            # Food cost validation
            if row['food_cost'] is not None:
                if not self.validate_numeric(row['food_cost'], 'food_cost', min_val=0):
                    self.add_failure('recipes', row['id'], 
                                   f'Invalid food cost: {row["food_cost"]}',
                                   'food_cost', row['food_cost'])
            
            # Menu price validation
            if row['menu_price'] is not None and row['menu_price'] > 0:
                if not self.validate_numeric(row['menu_price'], 'menu_price', min_val=0):
                    self.add_failure('recipes', row['id'], 
                                   f'Invalid menu price: {row["menu_price"]}',
                                   'menu_price', row['menu_price'])
                
                # Check for reasonable food cost percentage
                if row['food_cost'] and row['food_cost'] > 0:
                    food_cost_pct = (row['food_cost'] / row['menu_price']) * 100
                    if food_cost_pct > 50:
                        self.add_failure('recipes', row['id'], 
                                       f'High food cost percentage: {food_cost_pct:.1f}%',
                                       'food_cost_percentage', food_cost_pct)
            
            # Recipe with no ingredients
            if row['ingredient_count'] == 0:
                self.add_failure('recipes', row['id'], 
                               'Recipe has no ingredients')
            
            # Recipe with no costed ingredients
            elif row['costed_count'] == 0:
                self.add_failure('recipes', row['id'], 
                               'Recipe has no costed ingredients')
            
            # Prep recipe yield validation
            if row['prep_recipe_yield_uom'] and not self.validate_uom(row['prep_recipe_yield_uom']):
                self.add_failure('recipes', row['id'], 
                               f'Invalid prep recipe yield UOM: {row["prep_recipe_yield_uom"]}',
                               'prep_recipe_yield_uom', row['prep_recipe_yield_uom'])
    
    def audit_recipe_ingredients(self):
        """Audit recipe_ingredients table"""
        print("Auditing recipe_ingredients table...")
        cursor = self.conn.cursor()
        
        rows = cursor.execute("""
            SELECT ri.id, ri.recipe_id, ri.ingredient_id, ri.ingredient_name,
                   ri.quantity, ri.unit_of_measure, ri.cost,
                   r.recipe_name, i.item_description
            FROM recipe_ingredients ri
            LEFT JOIN recipes r ON ri.recipe_id = r.id
            LEFT JOIN inventory i ON ri.ingredient_id = i.id
        """).fetchall()
        
        for row in rows:
            # Missing recipe reference
            if not row['recipe_name']:
                self.add_failure('recipe_ingredients', row['id'], 
                               'Invalid recipe_id reference', 'recipe_id', row['recipe_id'])
            
            # Missing ingredient reference
            if row['ingredient_id'] and not row['item_description']:
                self.add_failure('recipe_ingredients', row['id'], 
                               'Invalid ingredient_id reference', 
                               'ingredient_id', row['ingredient_id'])
            
            # No ingredient link at all
            if not row['ingredient_id'] and not row['ingredient_name']:
                self.add_failure('recipe_ingredients', row['id'], 
                               'No ingredient specified')
            
            # Quantity validation
            if row['quantity'] is None:
                self.add_failure('recipe_ingredients', row['id'], 
                               'Missing quantity', 'quantity')
            elif not self.validate_numeric(row['quantity'], 'quantity', min_val=0):
                self.add_failure('recipe_ingredients', row['id'], 
                               f'Invalid quantity: {row["quantity"]}',
                               'quantity', row['quantity'])
            
            # UOM validation
            if not row['unit_of_measure']:
                self.add_failure('recipe_ingredients', row['id'], 
                               'Missing unit_of_measure', 'unit_of_measure')
            elif not self.validate_uom(row['unit_of_measure']):
                self.add_failure('recipe_ingredients', row['id'], 
                               f'Invalid UOM: {row["unit_of_measure"]}',
                               'unit_of_measure', row['unit_of_measure'])
            
            # Cost validation
            if row['cost'] is not None:
                if not self.validate_numeric(row['cost'], 'cost', min_val=0):
                    self.add_failure('recipe_ingredients', row['id'], 
                                   f'Invalid cost: {row["cost"]}',
                                   'cost', row['cost'])
            
            # Ingredient name mismatch
            if (row['ingredient_id'] and row['ingredient_name'] and 
                row['item_description'] and 
                row['ingredient_name'] != row['item_description']):
                self.add_failure('recipe_ingredients', row['id'], 
                               f'Ingredient name mismatch: "{row["ingredient_name"]}" vs "{row["item_description"]}"',
                               'ingredient_name', row['ingredient_name'])
    
    def audit_vendor_products(self):
        """Audit vendor_products table"""
        print("Auditing vendor_products table...")
        cursor = self.conn.cursor()
        
        rows = cursor.execute("""
            SELECT vp.id, vp.inventory_id, vp.vendor_id, vp.vendor_price,
                   vp.pack_size, vp.unit_measure, vp.is_primary,
                   i.item_description, v.vendor_name
            FROM vendor_products vp
            LEFT JOIN inventory i ON vp.inventory_id = i.id
            LEFT JOIN vendors v ON vp.vendor_id = v.id
        """).fetchall()
        
        # Track primary vendors per item
        primary_by_item = {}
        
        for row in rows:
            # Invalid references
            if not row['item_description']:
                self.add_failure('vendor_products', row['id'], 
                               'Invalid inventory_id reference',
                               'inventory_id', row['inventory_id'])
            
            if not row['vendor_name']:
                self.add_failure('vendor_products', row['id'], 
                               'Invalid vendor_id reference',
                               'vendor_id', row['vendor_id'])
            
            # Price validation
            if row['vendor_price'] is not None:
                if not self.validate_numeric(row['vendor_price'], 'vendor_price', min_val=0):
                    self.add_failure('vendor_products', row['id'], 
                                   f'Invalid vendor price: {row["vendor_price"]}',
                                   'vendor_price', row['vendor_price'])
            
            # Pack size validation
            if row['pack_size']:
                valid, error = self.parse_pack_size(row['pack_size'])
                if not valid:
                    self.add_failure('vendor_products', row['id'], error,
                                   'pack_size', row['pack_size'])
            
            # Multiple primary vendors
            if row['is_primary']:
                item_id = row['inventory_id']
                if item_id in primary_by_item:
                    self.add_failure('vendor_products', row['id'], 
                                   f'Multiple primary vendors for item {row["item_description"]}')
                else:
                    primary_by_item[item_id] = row['id']
    
    def audit_data_consistency(self):
        """Cross-table consistency checks"""
        print("Auditing data consistency...")
        cursor = self.conn.cursor()
        
        # Check for recipes using items not in inventory
        orphan_ingredients = cursor.execute("""
            SELECT ri.id, ri.recipe_id, ri.ingredient_name, r.recipe_name
            FROM recipe_ingredients ri
            JOIN recipes r ON ri.recipe_id = r.id
            WHERE ri.ingredient_id IS NULL 
            AND ri.ingredient_name NOT IN (SELECT recipe_name FROM recipes WHERE recipe_type = 'PrepRecipe')
        """).fetchall()
        
        for row in orphan_ingredients:
            self.add_failure('recipe_ingredients', row['id'],
                           f'Ingredient "{row["ingredient_name"]}" not found in inventory for recipe "{row["recipe_name"]}"')
        
        # Check for inconsistent pricing
        price_issues = cursor.execute("""
            SELECT i.id, i.item_description, i.current_price,
                   vp.vendor_price, v.vendor_name
            FROM inventory i
            JOIN vendor_products vp ON i.id = vp.inventory_id
            JOIN vendors v ON vp.vendor_id = v.id
            WHERE vp.is_primary = 1
            AND ABS(i.current_price - vp.vendor_price) > 0.01
        """).fetchall()
        
        for row in price_issues:
            self.add_failure('inventory', row['id'],
                           f'Price mismatch: inventory ${row["current_price"]} vs primary vendor ${row["vendor_price"]}')
    
    def save_results(self, output_dir: str = 'audit_reports'):
        """Save audit results to CSV"""
        Path(output_dir).mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{output_dir}/audit_failures_{timestamp}.csv"
        
        with open(filename, 'w', newline='') as f:
            if self.failures:
                fieldnames = ['timestamp', 'table', 'pk', 'column', 'value', 'error_message']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.failures)
        
        print(f"\nAudit complete. Found {len(self.failures)} issues.")
        print(f"Results saved to: {filename}")
        
        # Summary by table
        table_counts = {}
        for failure in self.failures:
            table = failure['table']
            table_counts[table] = table_counts.get(table, 0) + 1
        
        print("\nSummary by table:")
        for table, count in sorted(table_counts.items()):
            print(f"  {table}: {count} issues")
    
    def run_full_audit(self):
        """Run all audit checks"""
        print("Starting comprehensive data audit...")
        print("=" * 60)
        
        self.audit_inventory()
        self.audit_recipes()
        self.audit_recipe_ingredients()
        self.audit_vendor_products()
        self.audit_data_consistency()
        
        self.save_results()
        self.conn.close()

if __name__ == "__main__":
    auditor = DataAuditor('restaurant_calculator.db')
    auditor.run_full_audit()