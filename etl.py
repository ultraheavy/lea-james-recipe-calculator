#!/usr/bin/env python3
"""
ETL pipeline with P1 fixes for pack size parsing and UOM normalization
"""

import re
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional, Dict, List
import pandas as pd
from decimal import Decimal
import subprocess
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ETLPipeline:
    """ETL pipeline with robust pack size parsing and UOM normalization"""
    
    def __init__(self, db_path: str = 'restaurant_calculator.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.uom_aliases = self._load_uom_aliases()
        self.error_log = []
        
    def _load_uom_aliases(self) -> Dict[str, str]:
        """Load UOM aliases from JSON file"""
        aliases_path = Path(__file__).parent / 'uom_aliases.json'
        if aliases_path.exists():
            with open(aliases_path, 'r') as f:
                data = json.load(f)
                return data.get('aliases', {})
        return {}
    
    def map_uom_alias(self, uom: str) -> str:
        """Map UOM alias to canonical form"""
        if not uom:
            return ''
        
        # Normalize to lowercase and strip whitespace
        uom_lower = uom.lower().strip()
        
        # Check aliases
        if uom_lower in self.uom_aliases:
            return self.uom_aliases[uom_lower]
        
        # Return as-is if not an alias
        return uom_lower
    
    def parse_pack_size(self, pack_size: str) -> Tuple[float, str]:
        """
        Parse pack size string with robust grammar support
        
        Examples:
        - "1x4l" → (4.0, "l")
        - "24 × 1 ea" → (1.0, "each")  # Assuming 24-pack
        - "12x2.5kg" → (2.5, "kg")
        - "128 fl oz" → (128.0, "ml")
        - "5 fl oz" → (5.0, "ml")
        
        Returns (quantity, unit) or logs error and returns (1.0, "each")
        """
        if not pack_size:
            return 1.0, "each"
        
        # Normalize the string
        pack_size = pack_size.strip()
        
        # Replace various multiplication symbols with 'x'
        pack_size = re.sub(r'[×✕✖⨯]', 'x', pack_size)
        
        # Main pattern to match both formats:
        # Group 1-3: "N x N unit" format
        # Group 4-5: "N unit" format (single token)
        pattern = r'^(?:(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s+([a-zA-Z\s-]+)|(\d+(?:\.\d+)?)\s+([a-zA-Z\s-]+))$'
        match = re.match(pattern, pack_size, re.IGNORECASE)
        
        if match:
            if match.group(1) is not None:
                # "N x N unit" format
                packs = float(match.group(1))
                qty_per_pack = float(match.group(2))
                unit = match.group(3).strip()
            else:
                # "N unit" format - treat as 1 x N unit
                qty_per_pack = float(match.group(4))
                unit = match.group(5).strip()
            
            # Map unit alias
            canonical_unit = self.map_uom_alias(unit)
            
            # Check if we have a valid unit
            if self._is_valid_unit(canonical_unit):
                return qty_per_pack, canonical_unit
            else:
                self._log_error('pack_size', pack_size, f"Unknown unit after aliasing: {unit} → {canonical_unit}")
                return 1.0, "each"
        
        # Alternative pattern for compact format "NxNunit" (no spaces)
        pattern2 = r'^(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)([a-zA-Z]+)$'
        match2 = re.match(pattern2, pack_size, re.IGNORECASE)
        if match2:
            packs = float(match2.group(1))
            qty_per_pack = float(match2.group(2))
            unit = match2.group(3).strip()
            
            # Map unit alias
            canonical_unit = self.map_uom_alias(unit)
            
            if self._is_valid_unit(canonical_unit):
                return qty_per_pack, canonical_unit
            else:
                self._log_error('pack_size', pack_size, f"Unknown unit after aliasing: {unit} → {canonical_unit}")
                return 1.0, "each"
        
        # Reject "N x N" without unit
        if re.match(r'^\d+(?:\.\d+)?\s*x\s*\d+(?:\.\d+)?$', pack_size, re.IGNORECASE):
            self._log_error('pack_size', pack_size, "Pack size missing unit")
            return 1.0, "each"
        
        # Fallback
        self._log_error('pack_size', pack_size, "Unparseable pack size format")
        return 1.0, "each"
    
    def canonical_uom(self, uom_str: str) -> Tuple[str, float]:
        """
        Get canonical UOM and conversion factor
        
        Returns (canonical_code, factor) where factor converts to canonical unit
        E.g., "tbsp" → ("ml", 14.786)
        """
        if not uom_str:
            return "each", 1.0
        
        # First map aliases
        canonical = self.map_uom_alias(uom_str)
        
        # Load conversions
        aliases_path = Path(__file__).parent / 'uom_aliases.json'
        if aliases_path.exists():
            with open(aliases_path, 'r') as f:
                data = json.load(f)
                conversions = data.get('conversions', {})
                
                # Check for specific conversion factors
                if uom_str.lower() in ['tbsp', 'tablespoon', 'tblsp']:
                    return canonical, conversions.get('tbsp_to_ml', 14.786)
                elif uom_str.lower() in ['tsp', 'teaspoon']:
                    return canonical, conversions.get('tsp_to_ml', 4.929)
                elif uom_str.lower() in ['fl oz', 'floz', 'fl_oz', 'fl-oz', 'fl']:
                    return canonical, conversions.get('floz_to_ml', 29.573)
                elif uom_str.lower() == 'cup':
                    return canonical, conversions.get('cup_to_ml', 236.588)
                elif uom_str.lower() in ['pt', 'pint']:
                    return canonical, conversions.get('pt_to_ml', 473.176)
                elif uom_str.lower() in ['qt', 'quart']:
                    return canonical, conversions.get('qt_to_ml', 946.353)
                elif uom_str.lower() in ['gal', 'gallon', 'gal.']:
                    return canonical, conversions.get('gal_to_ml', 3785.412)
                elif uom_str.lower() in ['lb', 'pound']:
                    return canonical, conversions.get('lb_to_g', 453.592)
                elif uom_str.lower() in ['oz', 'ounce']:
                    return canonical, conversions.get('oz_to_g', 28.350)
        
        return canonical, 1.0
    
    def _is_valid_unit(self, unit: str) -> bool:
        """Check if unit is valid after aliasing"""
        # Load canonical units from aliases file
        aliases_path = Path(__file__).parent / 'uom_aliases.json'
        if aliases_path.exists():
            with open(aliases_path, 'r') as f:
                data = json.load(f)
                canonical = data.get('canonical_units', {})
                all_valid = []
                for unit_list in canonical.values():
                    all_valid.extend(unit_list)
                return unit in all_valid
        return True  # Permissive if no validation data
    
    def _log_error(self, field: str, value: str, message: str):
        """Log ETL error"""
        self.error_log.append({
            'timestamp': datetime.now().isoformat(),
            'field': field,
            'value': value,
            'error': message
        })
        logger.warning(f"{field}: {value} - {message}")
    
    def process_inventory_csv(self, csv_path: str):
        """Process inventory CSV with pack size and UOM fixes"""
        logger.info(f"Processing inventory CSV: {csv_path}")
        
        # Read CSV
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        cursor = self.conn.cursor()
        processed = 0
        
        for _, row in df.iterrows():
            # Parse pack size if present
            pack_size = row.get('Pack Size', '')
            if pack_size and pd.notna(pack_size):
                qty, unit = self.parse_pack_size(str(pack_size))
                # Update pack size to canonical format
                if unit != "each":
                    pack_size = f"{qty} {unit}"
                else:
                    pack_size = str(qty)
            
            # Map UOM aliases
            purchase_unit = self.map_uom_alias(str(row.get('UOM', '')))
            recipe_unit = self.map_uom_alias(str(row.get('Item UOM', '')))
            
            # Update or insert
            cursor.execute("""
                INSERT INTO inventory (
                    item_code, item_description, vendor_name,
                    current_price, pack_size, purchase_unit, 
                    recipe_cost_unit, yield_percent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(item_code) DO UPDATE SET
                    item_description = excluded.item_description,
                    vendor_name = excluded.vendor_name,
                    current_price = excluded.current_price,
                    pack_size = excluded.pack_size,
                    purchase_unit = excluded.purchase_unit,
                    recipe_cost_unit = excluded.recipe_cost_unit,
                    yield_percent = excluded.yield_percent,
                    updated_date = CURRENT_TIMESTAMP
            """, (
                row.get('Item Code', ''),
                row.get('Item Description', ''),
                row.get('Vendor', ''),
                float(row.get('Price', 0)) if pd.notna(row.get('Price')) else 0,
                pack_size,
                purchase_unit,
                recipe_unit,
                float(row.get('Yield %', 100)) if pd.notna(row.get('Yield %')) else 100
            ))
            
            processed += 1
        
        self.conn.commit()
        logger.info(f"Processed {processed} inventory items")
    
    def process_vendor_products_csv(self, csv_path: str):
        """Process vendor products CSV with pack size fixes"""
        logger.info(f"Processing vendor products CSV: {csv_path}")
        
        # This would process vendor product data
        # Implementation depends on actual CSV structure
        pass
    
    def fix_existing_data(self):
        """Fix pack sizes and UOMs in existing database"""
        logger.info("Fixing existing database entries...")
        
        cursor = self.conn.cursor()
        
        # Fix inventory pack sizes
        inventory_items = cursor.execute("""
            SELECT id, pack_size FROM inventory 
            WHERE pack_size IS NOT NULL AND pack_size != ''
        """).fetchall()
        
        fixed_count = 0
        for item_id, pack_size in inventory_items:
            qty, unit = self.parse_pack_size(pack_size)
            # Always include unit in pack size for consistency
            qty_str = str(int(qty)) if qty == int(qty) else str(qty)
            new_pack_size = f"{qty_str} {unit}"
            
            if new_pack_size != pack_size:
                cursor.execute("""
                    UPDATE inventory SET pack_size = ? WHERE id = ?
                """, (new_pack_size, item_id))
                fixed_count += 1
        
        logger.info(f"Fixed {fixed_count} inventory pack sizes")
        
        # Fix inventory UOMs using aliases
        uom_fixes = [
            ('purchase_unit', 'ct', 'each'),
            ('purchase_unit', 'count', 'each'),
            ('purchase_unit', 'piece', 'each'),
            ('purchase_unit', 'bg', 'bag'),
            ('purchase_unit', 'jug', 'each'),
            ('purchase_unit', 'bottle', 'each'),
            ('purchase_unit', 'unit', 'each'),
            ('recipe_cost_unit', 'slice', 'each'),
            ('recipe_cost_unit', 'btl', 'each'),
            ('recipe_cost_unit', 'bottle', 'each'),
            ('recipe_cost_unit', 'jug', 'each'),
            ('recipe_cost_unit', 'fl', 'ml'),
        ]
        
        for column, old_val, new_val in uom_fixes:
            cursor.execute(f"""
                UPDATE inventory 
                SET {column} = ?
                WHERE LOWER({column}) = ?
            """, (new_val, old_val))
        
        # Fix vendor_products pack sizes
        vendor_products = cursor.execute("""
            SELECT id, pack_size FROM vendor_products
            WHERE pack_size IS NOT NULL AND pack_size != ''
        """).fetchall()
        
        vp_fixed = 0
        for vp_id, pack_size in vendor_products:
            qty, unit = self.parse_pack_size(pack_size)
            # Always include unit in pack size for consistency
            qty_str = str(int(qty)) if qty == int(qty) else str(qty)
            new_pack_size = f"{qty_str} {unit}"
            
            if new_pack_size != pack_size:
                cursor.execute("""
                    UPDATE vendor_products SET pack_size = ? WHERE id = ?
                """, (new_pack_size, vp_id))
                vp_fixed += 1
        
        logger.info(f"Fixed {vp_fixed} vendor_products pack sizes")
        
        # Fix recipe_ingredients UOMs if table exists
        tables = cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='recipe_ingredients'
        """).fetchall()
        
        if tables:
            ri_uom_fixes = [
                ('slice', 'each'),
                ('fl ounce', 'fl oz'),
                ('tablespoon', 'tbsp'),
                ('portions', 'each'),
            ]
            
            for old_val, new_val in ri_uom_fixes:
                cursor.execute("""
                    UPDATE recipe_ingredients 
                    SET unit_of_measure = ?
                    WHERE LOWER(unit_of_measure) = ?
                """, (new_val, old_val))
        
        self.conn.commit()
        logger.info("Database fixes completed")
    
    def write_error_log(self):
        """Write ETL errors to log file"""
        if self.error_log:
            log_dir = Path('etl_logs')
            log_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = log_dir / f'etl_error_log_{timestamp}.json'
            
            with open(log_file, 'w') as f:
                json.dump(self.error_log, f, indent=2)
            
            logger.info(f"Wrote {len(self.error_log)} errors to {log_file}")
    
    def run_audit(self):
        """Run audit.py and capture results"""
        logger.info("Running data audit...")
        
        # Run audit script
        result = subprocess.run([
            sys.executable, 'audit.py'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Audit failed: {result.stderr}")
        else:
            logger.info("Audit completed successfully")
    
    def generate_delta_report(self):
        """Generate delta audit report comparing before/after P1 fixes"""
        # Find the latest audit file
        audit_dir = Path('audit_reports')
        audit_files = sorted(audit_dir.glob('audit_failures_*.csv'))
        
        if len(audit_files) < 2:
            logger.warning("Need at least 2 audit files for delta report")
            return
        
        # Read original and new audit results
        original_file = audit_files[-2]  # Second most recent
        new_file = audit_files[-1]       # Most recent
        
        original_df = pd.read_csv(original_file)
        new_df = pd.read_csv(new_file)
        
        # Generate summary
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_file = f'audit_reports/audit_summary_P1_{timestamp}.md'
        
        with open(summary_file, 'w') as f:
            f.write("# P1 Fixes - Audit Delta Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Original errors: {len(original_df)}\n")
            f.write(f"- Remaining errors: {len(new_df)}\n")
            f.write(f"- Fixed: {len(original_df) - len(new_df)}\n")
            f.write(f"- Reduction: {((len(original_df) - len(new_df)) / len(original_df) * 100):.1f}%\n\n")
            
            # Error breakdown by type
            f.write("## Remaining Errors by Type\n\n")
            error_types = new_df.groupby('error_message').size().sort_values(ascending=False)
            
            for error, count in error_types.items():
                f.write(f"- {error}: {count}\n")
            
            f.write("\n## Remaining Errors by Table\n\n")
            table_errors = new_df.groupby('table').size().sort_values(ascending=False)
            
            for table, count in table_errors.items():
                f.write(f"- {table}: {count}\n")
        
        # Print summary to stdout
        with open(summary_file, 'r') as f:
            print(f.read())
        
        logger.info(f"Delta report saved to {summary_file}")
    
    def run_full_etl(self):
        """Run complete ETL pipeline with P1 fixes"""
        logger.info("Starting full ETL pipeline with P1 fixes...")
        
        # Fix existing data
        self.fix_existing_data()
        
        # Process CSV files if they exist
        csv_dir = Path('data_sources_from_toast')
        if csv_dir.exists():
            for csv_file in csv_dir.glob('*.csv'):
                if 'item' in csv_file.name.lower():
                    self.process_inventory_csv(csv_file)
        
        # Write error log
        self.write_error_log()
        
        # Run audit
        self.run_audit()
        
        # Generate delta report
        self.generate_delta_report()
        
        logger.info("ETL pipeline completed")
    
    def backfill_prices(self):
        """P2: Backfill missing prices from vendor_products"""
        logger.info("Backfilling missing prices...")
        
        cursor = self.conn.cursor()
        
        # Find items with null prices
        null_price_items = cursor.execute("""
            SELECT id, item_code, item_description
            FROM inventory
            WHERE current_price IS NULL OR current_price = 0
        """).fetchall()
        
        logger.info(f"Found {len(null_price_items)} items with missing prices")
        
        backfilled = 0
        still_null = []
        
        for item_id, item_code, item_description in null_price_items:
            # Try to find most recent price from vendor_products
            recent_price = cursor.execute("""
                SELECT vp.vendor_price
                FROM vendor_products vp
                WHERE vp.inventory_id = ?
                  AND vp.vendor_price IS NOT NULL
                  AND vp.vendor_price > 0
                ORDER BY vp.id DESC
                LIMIT 1
            """, (item_id,)).fetchone()
            
            if recent_price and recent_price[0]:
                cursor.execute("""
                    UPDATE inventory
                    SET current_price = ?,
                        updated_date = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (recent_price[0], item_id))
                backfilled += 1
                logger.debug(f"Backfilled price for {item_code}: ${recent_price[0]}")
            else:
                still_null.append({
                    'id': item_id,
                    'item_code': item_code,
                    'item_description': item_description
                })
        
        self.conn.commit()
        
        logger.info(f"Backfilled {backfilled} prices")
        
        if still_null:
            logger.warning(f"{len(still_null)} items still have null prices:")
            for item in still_null[:10]:  # Show first 10
                logger.warning(f"  - {item['item_code']}: {item['item_description']}")
        
        return backfilled, still_null
    
    def fix_recipe_sanity(self):
        """P2: Flag and fix recipes with issues"""
        logger.info("Running recipe sanity checks...")
        
        cursor = self.conn.cursor()
        
        # Create recipes_notes table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                note_type TEXT NOT NULL,
                note_text TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            )
        """)
        
        # Find recipes with >100% food cost
        high_cost_recipes = cursor.execute("""
            SELECT id, recipe_name, food_cost, menu_price,
                   ROUND((food_cost / NULLIF(menu_price, 0)) * 100, 1) as food_cost_pct
            FROM recipes
            WHERE menu_price > 0 
              AND food_cost > menu_price
        """).fetchall()
        
        for recipe in high_cost_recipes:
            cursor.execute("""
                INSERT INTO recipes_notes (recipe_id, note_type, note_text)
                VALUES (?, 'high_food_cost', ?)
            """, (
                recipe[0],
                f"Food cost ${recipe[2]:.2f} exceeds menu price ${recipe[3]:.2f} ({recipe[4]}%)"
            ))
        
        logger.info(f"Flagged {len(high_cost_recipes)} recipes with >100% food cost")
        
        # Find recipes with no ingredients
        empty_recipes = cursor.execute("""
            SELECT r.id, r.recipe_name
            FROM recipes r
            LEFT JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            WHERE ri.id IS NULL
        """).fetchall()
        
        for recipe_id, recipe_name in empty_recipes:
            cursor.execute("""
                INSERT INTO recipes_notes (recipe_id, note_type, note_text)
                VALUES (?, 'no_ingredients', 'Recipe has no ingredients defined')
            """, (recipe_id,))
        
        logger.info(f"Flagged {len(empty_recipes)} recipes with no ingredients")
        
        # Find recipes with zero-cost ingredients
        zero_cost_recipes = cursor.execute("""
            SELECT DISTINCT r.id, r.recipe_name
            FROM recipes r
            JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            LEFT JOIN inventory i ON ri.ingredient_id = i.id
            WHERE r.food_cost = 0
               OR (i.current_price IS NULL OR i.current_price = 0)
        """).fetchall()
        
        for recipe_id, recipe_name in zero_cost_recipes:
            cursor.execute("""
                INSERT INTO recipes_notes (recipe_id, note_type, note_text)
                VALUES (?, 'zero_cost', 'Recipe has zero or null cost ingredients')
            """, (recipe_id,))
        
        logger.info(f"Flagged {len(zero_cost_recipes)} recipes with zero-cost ingredients")
        
        self.conn.commit()
        
        return {
            'high_cost': len(high_cost_recipes),
            'no_ingredients': len(empty_recipes),
            'zero_cost': len(zero_cost_recipes)
        }
    
    def run_p2_fixes(self):
        """Run P2 data quality fixes"""
        logger.info("Starting P2 data quality fixes...")
        
        # 1. Backfill prices
        backfilled, still_null = self.backfill_prices()
        
        # 2. Fix recipe sanity
        recipe_issues = self.fix_recipe_sanity()
        
        # 3. Run audit
        self.run_audit()
        
        # 4. Generate P2 delta report
        self.generate_delta_report()
        
        logger.info("P2 fixes completed")
        
        return {
            'prices_backfilled': backfilled,
            'prices_still_null': len(still_null),
            'recipe_issues': recipe_issues
        }
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    """Main ETL entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ETL Pipeline for Restaurant Calculator')
    parser.add_argument('command', choices=['ingest', 'p1', 'p2'], 
                       help='Command to run')
    parser.add_argument('--wipe', action='store_true',
                       help='Wipe inventory and vendor_products before ingestion')
    parser.add_argument('--files', nargs='+',
                       help='CSV files to ingest')
    
    args = parser.parse_args()
    
    etl = ETLPipeline()
    
    try:
        if args.command == 'ingest':
            if args.wipe:
                logger.info("Wiping inventory and vendor_products tables...")
                cursor = etl.conn.cursor()
                cursor.execute("DELETE FROM vendor_products")
                cursor.execute("DELETE FROM inventory")
                etl.conn.commit()
                logger.info("Tables wiped")
            
            # Process CSV files
            if args.files:
                for csv_file in args.files:
                    if Path(csv_file).exists():
                        logger.info(f"Processing {csv_file}")
                        etl.process_inventory_csv(csv_file)
                    else:
                        logger.error(f"File not found: {csv_file}")
            else:
                # Use default directory
                etl.run_full_etl()
        
        elif args.command == 'p1':
            etl.run_full_etl()
        
        elif args.command == 'p2':
            results = etl.run_p2_fixes()
            
            print("\nP2 Fix Results:")
            print(f"- Prices backfilled: {results['prices_backfilled']}")
            print(f"- Prices still null: {results['prices_still_null']}")
            print(f"- Recipes with >100% cost: {results['recipe_issues']['high_cost']}")
            print(f"- Recipes with no ingredients: {results['recipe_issues']['no_ingredients']}")
            print(f"- Recipes with zero cost: {results['recipe_issues']['zero_cost']}")
        
    finally:
        etl.close()

if __name__ == '__main__':
    main()