#!/usr/bin/env python3
"""
Inventory Staging Admin Review System
Provides Flask routes and functionality for reviewing and approving staged inventory data
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import sqlite3
from datetime import datetime
import json
from typing import Dict, List, Tuple, Any
import re

# Create Blueprint
inventory_staging_bp = Blueprint('inventory_staging', __name__, url_prefix='/admin/inventory-staging')

class InventoryStagingAdmin:
    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = "restaurant_calculator.db"
        else:
            self.db_path = db_path
    
    def get_review_items(self, filters: Dict = None, page: int = 1, per_page: int = 50) -> Dict:
        """Get items for review with filtering and pagination"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Base query
        where_clauses = ["1=1"]
        params = []
        
        if filters:
            if filters.get('batch_id'):
                where_clauses.append("import_batch_id = ?")
                params.append(filters['batch_id'])
            
            if filters.get('needs_review') is not None:
                where_clauses.append("needs_review = ?")
                params.append(filters['needs_review'])
            
            if filters.get('review_status'):
                where_clauses.append("review_status = ?")
                params.append(filters['review_status'])
            
            if filters.get('is_duplicate') is not None:
                where_clauses.append("is_duplicate = ?")
                params.append(filters['is_duplicate'])
            
            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                where_clauses.append("""
                    (FAM_Product_Name_cleaned LIKE ? OR 
                     Vendor_Name_cleaned LIKE ? OR 
                     Vendor_Item_Code_cleaned LIKE ? OR
                     Vendor_Item_Description_cleaned LIKE ?)
                """)
                params.extend([search_term] * 4)
        
        where_sql = " AND ".join(where_clauses)
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM stg_inventory_items WHERE {where_sql}"
        total_items = cursor.execute(count_query, params).fetchone()[0]
        
        # Get paginated results
        offset = (page - 1) * per_page
        query = f"""
            SELECT * FROM stg_inventory_items 
            WHERE {where_sql}
            ORDER BY needs_review DESC, staging_id DESC
            LIMIT ? OFFSET ?
        """
        params.extend([per_page, offset])
        
        items = []
        for row in cursor.execute(query, params):
            item = dict(row)
            # Parse flags
            item['flags'] = self._parse_flags(item)
            items.append(item)
        
        conn.close()
        
        return {
            'items': items,
            'total': total_items,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_items + per_page - 1) // per_page
        }
    
    def _parse_flags(self, item: Dict) -> List[Dict]:
        """Parse all flags from an item"""
        flags = []
        
        # Check each field for flags
        field_mappings = [
            ('FAM_Product_Name', 'Product Name'),
            ('Vendor_Name', 'Vendor'),
            ('Vendor_Item_Code', 'Item Code'),
            ('Vendor_Item_Description', 'Description'),
            ('Vendor_UOM', 'Vendor UOM'),
            ('Inventory_UOM', 'Inventory UOM'),
            ('Pack_qty', 'Pack Qty'),
            ('Size_qty', 'Size Qty'),
            ('Size_UOM', 'Size UOM'),
            ('Last_Purchased_Date', 'Last Purchase Date'),
            ('Last_Purchased_Price', 'Last Price')
        ]
        
        for field, display_name in field_mappings:
            flag_value = item.get(f"{field}_flag")
            if flag_value:
                severity = 'warning'
                if 'error' in flag_value or 'invalid' in flag_value:
                    severity = 'error'
                elif 'empty' in flag_value:
                    severity = 'info'
                
                flags.append({
                    'field': field,
                    'display_name': display_name,
                    'message': flag_value,
                    'severity': severity
                })
        
        return flags
    
    def get_batch_list(self) -> List[Dict]:
        """Get list of all import batches"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
            SELECT 
                import_batch_id,
                COUNT(*) as total_rows,
                SUM(CASE WHEN needs_review = 1 THEN 1 ELSE 0 END) as needs_review,
                SUM(CASE WHEN review_status = 'approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN review_status = 'rejected' THEN 1 ELSE 0 END) as rejected,
                SUM(CASE WHEN is_duplicate = 1 THEN 1 ELSE 0 END) as duplicates,
                MIN(created_at) as import_date
            FROM stg_inventory_items
            GROUP BY import_batch_id
            ORDER BY MIN(created_at) DESC
        """
        
        batches = []
        for row in cursor.execute(query):
            batches.append({
                'batch_id': row[0],
                'total_rows': row[1],
                'needs_review': row[2],
                'approved': row[3],
                'rejected': row[4],
                'duplicates': row[5],
                'import_date': row[6],
                'pending': row[1] - row[3] - row[4]
            })
        
        conn.close()
        return batches
    
    def update_item(self, staging_id: int, updates: Dict) -> bool:
        """Update a staged item"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Build update query
            set_clauses = []
            params = []
            
            # Update cleaned values
            for field, value in updates.items():
                if field.endswith('_cleaned'):
                    set_clauses.append(f"{field} = ?")
                    params.append(value)
            
            # Update metadata
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            
            if updates.get('review_status'):
                set_clauses.append("review_status = ?")
                params.append(updates['review_status'])
            
            if updates.get('review_notes'):
                set_clauses.append("review_notes = ?")
                params.append(updates['review_notes'])
            
            # Update needs_review based on status
            if updates.get('review_status') == 'approved':
                set_clauses.append("needs_review = 0")
            
            params.append(staging_id)
            
            query = f"""
                UPDATE stg_inventory_items 
                SET {', '.join(set_clauses)}
                WHERE staging_id = ?
            """
            
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Error updating item: {e}")
            return False
    
    def batch_update(self, staging_ids: List[int], action: str) -> Dict:
        """Perform batch actions on multiple items"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            if action == 'approve':
                query = """
                    UPDATE stg_inventory_items 
                    SET review_status = 'approved', needs_review = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE staging_id = ?
                """
            elif action == 'reject':
                query = """
                    UPDATE stg_inventory_items 
                    SET review_status = 'rejected', updated_at = CURRENT_TIMESTAMP
                    WHERE staging_id = ?
                """
            elif action == 'delete':
                query = """
                    DELETE FROM stg_inventory_items 
                    WHERE staging_id = ?
                """
            else:
                raise ValueError(f"Invalid action: {action}")
            
            for staging_id in staging_ids:
                try:
                    cursor.execute(query, (staging_id,))
                    results['success'] += 1
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"ID {staging_id}: {str(e)}")
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            results['errors'].append(f"Batch error: {str(e)}")
            
        finally:
            conn.close()
        
        return results
    
    def process_to_live(self, batch_id: str = None) -> Dict:
        """Process approved items to live inventory table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        results = {
            'processed': 0,
            'errors': 0,
            'details': []
        }
        
        try:
            # Select approved items without validation issues
            if batch_id:
                query = """
                    SELECT * FROM stg_inventory_items 
                    WHERE review_status = 'approved' 
                    AND processed_to_live = 0 
                    AND needs_review = 0
                    AND import_batch_id = ?
                """
                params = [batch_id]
            else:
                query = """
                    SELECT * FROM stg_inventory_items 
                    WHERE review_status = 'approved' 
                    AND processed_to_live = 0
                    AND needs_review = 0
                """
                params = []
            
            approved_items = cursor.execute(query, params).fetchall()
            
            for item in approved_items:
                try:
                    # Here you would insert into your live inventory table
                    # For now, just mark as processed
                    cursor.execute("""
                        UPDATE stg_inventory_items 
                        SET processed_to_live = 1, processed_date = CURRENT_TIMESTAMP
                        WHERE staging_id = ?
                    """, (item[0],))  # staging_id is first column
                    
                    results['processed'] += 1
                    
                except Exception as e:
                    results['errors'] += 1
                    results['details'].append(f"Failed to process item {item[0]}: {str(e)}")
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            results['details'].append(f"Process error: {str(e)}")
            
        finally:
            conn.close()
        
        return results


# Initialize admin handler
admin = InventoryStagingAdmin()

# Routes
@inventory_staging_bp.route('/')
def index():
    """Main review dashboard"""
    # Get filter parameters
    filters = {
        'batch_id': request.args.get('batch_id'),
        'needs_review': request.args.get('needs_review', type=int),
        'review_status': request.args.get('review_status'),
        'is_duplicate': request.args.get('is_duplicate', type=int),
        'search': request.args.get('search')
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    page = request.args.get('page', 1, type=int)
    per_page_str = request.args.get('per_page', '50')
    
    # Handle "all" case
    if per_page_str == 'all':
        per_page = 10000  # Large number to get all items
    else:
        try:
            per_page = int(per_page_str)
        except ValueError:
            per_page = 50
    
    # Get data
    result = admin.get_review_items(filters, page, per_page)
    batches = admin.get_batch_list()
    
    return render_template('inventory_staging_review.html',
                         items=result['items'],
                         total=result['total'],
                         page=result['page'],
                         per_page=per_page_str if per_page_str == 'all' else per_page,
                         total_pages=result['total_pages'],
                         batches=batches,
                         filters=filters)

@inventory_staging_bp.route('/item/<int:staging_id>', methods=['GET', 'POST'])
def edit_item(staging_id):
    """Edit individual item"""
    if request.method == 'POST':
        updates = request.get_json()
        success = admin.update_item(staging_id, updates)
        
        if success:
            return jsonify({'success': True, 'message': 'Item updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update item'}), 500
    
    # GET - return item details
    conn = sqlite3.connect(admin.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    item = cursor.execute("SELECT * FROM stg_inventory_items WHERE staging_id = ?", (staging_id,)).fetchone()
    conn.close()
    
    if item:
        return jsonify(dict(item))
    else:
        return jsonify({'error': 'Item not found'}), 404

@inventory_staging_bp.route('/batch-action', methods=['POST'])
def batch_action():
    """Perform batch actions"""
    data = request.get_json()
    staging_ids = data.get('staging_ids', [])
    action = data.get('action')
    
    if not staging_ids or not action:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    results = admin.batch_update(staging_ids, action)
    return jsonify(results)

@inventory_staging_bp.route('/process-to-live', methods=['POST'])
def process_to_live():
    """Process approved items to live inventory"""
    batch_id = request.json.get('batch_id')
    results = admin.process_to_live(batch_id)
    
    return jsonify(results)