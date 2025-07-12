#!/usr/bin/env python3
"""
Inventory Staging Loader
Loads inventory data from CSV into staging table with validation and flagging
"""

import csv
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import re
from typing import Dict, List, Tuple, Any

class InventoryStagingLoader:
    def __init__(self, db_path: str = "restaurant_calculator.db"):
        self.db_path = db_path
        self.config_path = Path("config/column_map_inventory.json")
        self.column_config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Load column mapping configuration"""
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def _create_batch_id(self) -> str:
        """Generate unique batch ID for this import"""
        return f"INV_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _clean_value(self, value: str, data_type: str) -> Tuple[Any, str]:
        """Clean and validate a value based on its type - ALWAYS returns something"""
        if not value or value.strip() == "":
            # Return appropriate defaults based on type
            if data_type == "integer":
                return None, "empty_integer"
            elif data_type == "float":
                return None, "empty_float"
            elif data_type == "boolean":
                return None, "empty_boolean"
            elif data_type == "date":
                return None, "empty_date"
            else:  # string
                return "", "empty_string"
            
        value = value.strip()
        
        if data_type == "string":
            return value, None
            
        elif data_type == "integer":
            try:
                cleaned = int(value)
                return cleaned, None
            except ValueError:
                # Store original value and flag it
                try:
                    # Try float first
                    cleaned = float(value)
                    return int(cleaned), "converted_from_float"
                except:
                    return None, f"invalid_integer: {value}"
                
        elif data_type == "float":
            try:
                # Remove $ and commas
                cleaned = value.replace('$', '').replace(',', '')
                result = float(cleaned)
                return result, None
            except ValueError:
                return None, f"invalid_float: {value}"
                
        elif data_type == "boolean":
            if value.upper() in ['TRUE', 'YES', '1']:
                return True, None
            elif value.upper() in ['FALSE', 'NO', '0']:
                return False, None
            else:
                return False, f"invalid_boolean_defaulted_false: {value}"
                
        elif data_type == "date":
            # Try various date formats
            for fmt in ['%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d']:
                try:
                    parsed = datetime.strptime(value, fmt)
                    return parsed.date(), None
                except ValueError:
                    continue
            return None, f"invalid_date: {value}"
            
        return value, None
    
    def _validate_row(self, row_data: Dict, cleaned_data: Dict) -> Tuple[bool, List[str]]:
        """Validate a row and return needs_review flag and list of issues - NEVER rejects, only flags"""
        issues = []
        needs_review = False
        
        for original_col, config in self.column_config.items():
            target_col = config['target']
            
            # Check required fields - just flag, don't reject
            if config.get('required', False):
                cleaned_val = cleaned_data.get(f"{target_col}_cleaned")
                if cleaned_val is None or (isinstance(cleaned_val, str) and cleaned_val.strip() == ""):
                    issues.append(f"{target_col}: required field is empty")
                    needs_review = True
            
            # Check validation rules
            if 'validation' in config:
                val_rules = config['validation']
                cleaned_val = cleaned_data.get(f"{target_col}_cleaned")
                
                # Check if empty
                if val_rules.get('flag_if_empty', False):
                    if cleaned_val is None or (isinstance(cleaned_val, str) and cleaned_val.strip() == ""):
                        issues.append(f"{target_col}: {val_rules.get('description', 'field is empty')}")
                        needs_review = True
                
                # Check if zero (for numeric fields)
                if val_rules.get('flag_if_zero', False):
                    if isinstance(cleaned_val, (int, float)) and cleaned_val == 0:
                        issues.append(f"{target_col}: {val_rules.get('description', 'value is zero')}")
                        needs_review = True
            
            # Check for any conversion flags
            flag = cleaned_data.get(f"{target_col}_flag")
            if flag and not flag.startswith("empty_"):  # Don't double-report empty fields
                needs_review = True
        
        return needs_review, issues
    
    def _create_duplicate_hash(self, row_data: Dict) -> str:
        """Create hash for duplicate detection"""
        # Use vendor, item code, and product name for duplicate detection
        key_parts = [
            row_data.get('Vendor Name', ''),
            row_data.get('Item Code', ''),
            row_data.get('Product(s)', '')
        ]
        key_string = '|'.join(str(p).strip().lower() for p in key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def load_csv_to_staging(self, csv_path: str) -> Dict[str, Any]:
        """Load CSV file into staging table"""
        batch_id = self._create_batch_id()
        stats = {
            'batch_id': batch_id,
            'total_rows': 0,
            'loaded_rows': 0,
            'error_rows': 0,
            'needs_review': 0,
            'duplicates': 0,
            'excluded_old_purchases': 0,
            'excluded_no_product': 0,
            'errors': []
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                    stats['total_rows'] += 1
                    
                    # EXCLUSION RULE 1: Check if product name is empty
                    product_name = row.get('Product(s)', '').strip()
                    if not product_name:
                        stats['excluded_no_product'] += 1
                        continue  # Skip this row entirely
                    
                    # EXCLUSION RULE 2: Check last purchase date (6 months cutoff)
                    last_purchase_date_str = row.get('Last Purchased Date', '').strip()
                    exclude_old = False
                    if last_purchase_date_str:
                        # Try to parse the date
                        for fmt in ['%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d']:
                            try:
                                last_purchase_date = datetime.strptime(last_purchase_date_str, fmt)
                                # Calculate 6 months ago from today
                                six_months_ago = datetime.now() - timedelta(days=180)  # Approx 6 months
                                if last_purchase_date < six_months_ago:
                                    exclude_old = True
                                break
                            except ValueError:
                                continue
                    
                    if exclude_old:
                        stats['excluded_old_purchases'] += 1
                        continue  # Skip this row entirely
                    
                    # If we get here, the row passes exclusion rules - proceed with loading
                    insert_data = {
                        'staging_id': None,  # Auto-increment
                        'original_row_number': row_num,
                        'import_batch_id': batch_id,
                        'needs_review': False  # Default to false
                    }
                    
                    try:
                        # Create duplicate hash
                        insert_data['duplicate_check_hash'] = self._create_duplicate_hash(row)
                    except Exception as e:
                        # Even if hash fails, still load the row
                        insert_data['duplicate_check_hash'] = f"hash_error_row_{row_num}"
                        insert_data['needs_review'] = True
                    
                    # Process each mapped column
                    flags = []
                    all_issues = []
                    
                    for original_col, config in self.column_config.items():
                        target_col = config['target']
                        
                        try:
                            raw_value = row.get(original_col, '')
                            
                            # Always store raw value
                            insert_data[f"{target_col}_raw"] = raw_value
                            
                            # Try to clean and validate
                            cleaned_value, flag = self._clean_value(raw_value, config['type'])
                            insert_data[f"{target_col}_cleaned"] = cleaned_value
                            
                            if flag:
                                insert_data[f"{target_col}_flag"] = flag
                                flags.append(f"{target_col}: {flag}")
                                
                        except Exception as e:
                            # If cleaning fails, store raw value and flag error
                            insert_data[f"{target_col}_cleaned"] = None
                            insert_data[f"{target_col}_flag"] = f"processing_error: {str(e)}"
                            all_issues.append(f"{target_col}: processing error")
                            insert_data['needs_review'] = True
                    
                    # Validate row
                    try:
                        needs_review, issues = self._validate_row(row, insert_data)
                        if needs_review:
                            insert_data['needs_review'] = True
                        all_issues.extend(issues)
                    except Exception as e:
                        insert_data['needs_review'] = True
                        all_issues.append(f"validation_error: {str(e)}")
                    
                    if insert_data['needs_review']:
                        stats['needs_review'] += 1
                        insert_data['review_notes'] = '; '.join(all_issues + flags)[:1000]  # Limit length
                    
                    # Check for duplicates (but don't fail if it errors)
                    try:
                        cursor.execute("""
                            SELECT staging_id FROM stg_inventory_items 
                            WHERE duplicate_check_hash = ? 
                            AND import_batch_id != ?
                            LIMIT 1
                        """, (insert_data['duplicate_check_hash'], batch_id))
                        
                        duplicate = cursor.fetchone()
                        if duplicate:
                            insert_data['is_duplicate'] = True
                            insert_data['duplicate_of_staging_id'] = duplicate[0]
                            stats['duplicates'] += 1
                    except Exception as e:
                        # Don't fail on duplicate check errors
                        pass
                    
                    # Build INSERT query - ALWAYS insert something
                    try:
                        columns = []
                        values = []
                        placeholders = []
                        
                        for key, value in insert_data.items():
                            if key != 'staging_id':  # Skip auto-increment field
                                columns.append(key)
                                values.append(value)
                                placeholders.append('?')
                        
                        query = f"""
                            INSERT INTO stg_inventory_items ({', '.join(columns)})
                            VALUES ({', '.join(placeholders)})
                        """
                        
                        cursor.execute(query, values)
                        stats['loaded_rows'] += 1
                        
                    except Exception as e:
                        # Last resort - try minimal insert with just raw data
                        try:
                            minimal_query = """
                                INSERT INTO stg_inventory_items 
                                (original_row_number, import_batch_id, needs_review, review_notes)
                                VALUES (?, ?, ?, ?)
                            """
                            error_msg = f"Failed to insert full row: {str(e)}. Row data: {str(row)[:500]}"
                            cursor.execute(minimal_query, (row_num, batch_id, True, error_msg))
                            stats['loaded_rows'] += 1
                            stats['needs_review'] += 1
                        except Exception as final_e:
                            stats['error_rows'] += 1
                            stats['errors'].append({
                                'row': row_num,
                                'error': f"Complete failure: {str(final_e)}",
                                'data': row
                            })
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            stats['errors'].append({
                'type': 'fatal',
                'error': str(e)
            })
            
        finally:
            conn.close()
        
        return stats
    
    def get_batch_summary(self, batch_id: str) -> Dict[str, Any]:
        """Get summary statistics for a batch"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_rows,
                SUM(CASE WHEN needs_review = 1 THEN 1 ELSE 0 END) as needs_review,
                SUM(CASE WHEN is_duplicate = 1 THEN 1 ELSE 0 END) as duplicates,
                SUM(CASE WHEN review_status = 'approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN review_status = 'rejected' THEN 1 ELSE 0 END) as rejected
            FROM stg_inventory_items
            WHERE import_batch_id = ?
        """, (batch_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'batch_id': batch_id,
            'total_rows': result[0],
            'needs_review': result[1],
            'duplicates': result[2],
            'approved': result[3],
            'rejected': result[4]
        }


def main():
    """Example usage"""
    loader = InventoryStagingLoader()
    
    # Load the original CSV
    csv_path = "reference/LJ_DATA_Ref/Lea_Janes_Items_list_latest.csv"
    
    print("Loading inventory data to staging...")
    stats = loader.load_csv_to_staging(csv_path)
    
    print(f"\nImport Complete!")
    print(f"Batch ID: {stats['batch_id']}")
    print(f"Total rows: {stats['total_rows']}")
    print(f"Loaded: {stats['loaded_rows']}")
    print(f"Excluded (no product): {stats['excluded_no_product']}")
    print(f"Excluded (old purchase): {stats['excluded_old_purchases']}")
    print(f"Needs review: {stats['needs_review']}")
    print(f"Duplicates: {stats['duplicates']}")
    print(f"Errors: {stats['error_rows']}")
    
    if stats['errors']:
        print("\nErrors encountered:")
        for error in stats['errors'][:5]:  # Show first 5 errors
            print(f"  Row {error.get('row', 'N/A')}: {error.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()