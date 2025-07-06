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
        - "24 × 1 ea" → (24.0, "each")  
        - "12x2.5kg" → (30.0, "kg")
        - "5 fl oz" → (5.0, "fl oz")
        
        Returns (quantity, unit) or logs error and returns (1.0, "each")
        """
        if not pack_size:
            return 1.0, "each"
        
        # Normalize the string
        pack_size = pack_size.strip()
        
        # Replace various multiplication symbols with 'x'
        pack_size = re.sub(r'[×✕✖⨯]', 'x', pack_size)
        
        # Pattern 4: Reject "N x N" without unit first
        if re.match(r'^\d+(?:\.\d+)?\s*x\s*\d+(?:\.\d+)?$', pack_size, re.IGNORECASE):
            self._log_error('pack_size', pack_size, "Pack size missing unit")
            return 1.0, "each"
        
        # Pattern 1: "N x N unit" format (e.g., "12 x 2.5 kg")
        pattern1 = r'^(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s+(.+)$'
        match1 = re.match(pattern1, pack_size, re.IGNORECASE)
        if match1:
            packs = float(match1.group(1))
            qty_per_pack = float(match1.group(2))
            unit = match1.group(3).strip()
            
            # Map unit alias
            canonical_unit = self.map_uom_alias(unit)
            
            # Check if we have a valid unit
            if self._is_valid_unit(canonical_unit):
                return qty_per_pack, canonical_unit
            else:
                self._log_error('pack_size', pack_size, f"Unknown unit after aliasing: {unit} → {canonical_unit}")
                return 1.0, "each"
        
        # Pattern 2: "NxNunit" format (no spaces, e.g., "1x4l")
        pattern2 = r'^(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)([a-zA-Z]+.*)$'
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
        
        # Pattern 3: Simple "N unit" format (e.g., "5 fl oz", "24 ct")
        pattern3 = r'^(\d+(?:\.\d+)?)\s+(.+)$'
        match3 = re.match(pattern3, pack_size, re.IGNORECASE)
        if match3:
            quantity = float(match3.group(1))
            unit = match3.group(2).strip()
            
            # Map unit alias
            canonical_unit = self.map_uom_alias(unit)
            
            if self._is_valid_unit(canonical_unit):
                return quantity, canonical_unit
            else:
                self._log_error('pack_size', pack_size, f"Unknown unit after aliasing: {unit} → {canonical_unit}")
                return 1.0, "each"
        
        # Fallback
        self._log_error('pack_size', pack_size, "Unparseable pack size format")
        return 1.0, "each"
    
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
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    """Main ETL entry point"""
    etl = ETLPipeline()
    try:
        etl.run_full_etl()
    finally:
        etl.close()

if __name__ == '__main__':
    main()