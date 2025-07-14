#!/usr/bin/env python3
"""
Recipe Staging Admin Review System
Provides Flask routes and functionality for reviewing and approving staged recipe data
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import sqlite3
from datetime import datetime
import json
from typing import Dict, List, Tuple, Any, Optional
import re

# Create Blueprint
recipe_staging_bp = Blueprint('recipe_staging', __name__, url_prefix='/admin/recipe-staging')

class RecipeStagingAdmin:
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
        
        # Handle 'all' per_page
        if per_page == 'all':
            per_page = 99999
        else:
            per_page = int(per_page)
        
        # Base query
        where_clauses = ["1=1"]
        params = []
        
        if filters:
            if filters.get('batch_id'):
                where_clauses.append("import_batch_id = ?")
                params.append(filters['batch_id'])
            
            if filters.get('needs_review') is not None:
                where_clauses.append("needs_review = ?")
                params.append(int(filters['needs_review']))
            
            if filters.get('review_status'):
                where_clauses.append("review_status = ?")
                params.append(filters['review_status'])
            
            if filters.get('is_duplicate') is not None:
                where_clauses.append("is_duplicate = ?")
                params.append(filters['is_duplicate'])
            
            if filters.get('recipe_type'):
                where_clauses.append("recipe_type = ?")
                params.append(filters['recipe_type'])
            
            if filters.get('status'):
                where_clauses.append("status = ?")
                params.append(filters['status'])
            
            if filters.get('food_cost_issue'):
                issue_type = filters['food_cost_issue']
                if issue_type == 'zero':
                    where_clauses.append("(food_cost = 0 OR food_cost IS NULL)")
                elif issue_type == 'low':
                    where_clauses.append("food_cost_percentage < 10")
                elif issue_type == 'high':
                    where_clauses.append("food_cost_percentage > 40")
                elif issue_type == 'extreme':
                    where_clauses.append("food_cost_percentage > 100")
            
            if filters.get('margin_issue'):
                where_clauses.append("gross_margin < 60")
            
            if filters.get('search'):
                search_term = f"%{filters['search']}%"
                where_clauses.append("""
                    (recipe_name LIKE ? OR 
                     recipe_group LIKE ? OR 
                     status LIKE ?)
                """)
                params.extend([search_term] * 3)
        
        where_sql = " AND ".join(where_clauses)
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM stg_recipes WHERE {where_sql}"
        total_items = cursor.execute(count_query, params).fetchone()[0]
        
        # Get paginated results
        offset = (page - 1) * per_page
        query = f"""
            SELECT * FROM stg_recipes 
            WHERE {where_sql}
            ORDER BY 
                CASE review_status 
                    WHEN 'hold' THEN 1
                    WHEN 'pending' THEN 2
                    WHEN 'approved' THEN 3
                    ELSE 4
                END,
                needs_review DESC, 
                staging_id DESC
            LIMIT ? OFFSET ?
        """
        params.extend([per_page, offset])
        
        items = []
        for row in cursor.execute(query, params):
            item = dict(row)
            # Parse JSON fields
            if item.get('validation_errors'):
                try:
                    item['validation_errors'] = json.loads(item['validation_errors'])
                except:
                    item['validation_errors'] = []
            
            # Add display flags
            item['has_zero_cost'] = (item.get('food_cost') or 0) == 0
            item['has_low_cost_pct'] = (item.get('food_cost_percentage') or 0) < 10
            item['has_high_cost_pct'] = (item.get('food_cost_percentage') or 0) > 40
            item['has_extreme_cost_pct'] = (item.get('food_cost_percentage') or 0) > 100
            item['has_low_margin'] = (item.get('gross_margin') or 100) < 60
            item['has_negative_margin'] = (item.get('calculated_margin') or 0) < 0
            
            items.append(item)
        
        # Get batch summary with corrected field name
        batch_query = """
            SELECT 
                import_batch_id as batch_id,
                COUNT(*) as total_rows,
                SUM(CASE WHEN needs_review = 1 THEN 1 ELSE 0 END) as needs_review,
                SUM(CASE WHEN review_status = 'approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN review_status = 'hold' THEN 1 ELSE 0 END) as on_hold,
                MIN(created_at) as batch_date
            FROM stg_recipes
            GROUP BY import_batch_id
            ORDER BY batch_date DESC
        """
        batches = [dict(row) for row in cursor.execute(batch_query)]
        
        conn.close()
        
        return {
            'items': items,
            'total': total_items,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_items + per_page - 1) // per_page if per_page < 99999 else 1,
            'batches': batches
        }
    
    def get_validation_summary(self, batch_id: str = None) -> Dict:
        """Get summary of validation issues"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        where_clause = "WHERE import_batch_id = ?" if batch_id else ""
        params = [batch_id] if batch_id else []
        
        query = f"""
            SELECT 
                COUNT(*) as total_recipes,
                SUM(CASE WHEN needs_review = 1 THEN 1 ELSE 0 END) as needs_review,
                SUM(CASE WHEN review_status = 'hold' THEN 1 ELSE 0 END) as on_hold,
                SUM(CASE WHEN status = 'Draft' THEN 1 ELSE 0 END) as draft_count,
                SUM(CASE WHEN food_cost = 0 OR food_cost IS NULL THEN 1 ELSE 0 END) as zero_cost,
                SUM(CASE WHEN food_cost_percentage < 10 THEN 1 ELSE 0 END) as low_cost_pct,
                SUM(CASE WHEN food_cost_percentage > 40 THEN 1 ELSE 0 END) as high_cost_pct,
                SUM(CASE WHEN food_cost_percentage > 100 THEN 1 ELSE 0 END) as extreme_cost_pct,
                SUM(CASE WHEN gross_margin < 60 THEN 1 ELSE 0 END) as low_margin,
                SUM(CASE WHEN calculated_margin < 0 THEN 1 ELSE 0 END) as negative_margin,
                SUM(CASE WHEN menu_price = 0 AND recipe_type = 'Recipe' THEN 1 ELSE 0 END) as missing_price,
                SUM(CASE WHEN ABS(margin_variance) > 5 THEN 1 ELSE 0 END) as margin_issues,
                SUM(CASE WHEN yield_quantity IS NULL AND recipe_type = 'PrepRecipe' THEN 1 ELSE 0 END) as missing_yield,
                SUM(CASE WHEN is_duplicate = 1 THEN 1 ELSE 0 END) as duplicates,
                SUM(CASE WHEN matched_recipe_id IS NOT NULL THEN 1 ELSE 0 END) as matched_existing
            FROM stg_recipes
            {where_clause}
        """
        
        result = cursor.execute(query, params).fetchone()
        summary = dict(result) if result else {}
        
        # Get issue breakdown
        issues_query = f"""
            SELECT 
                CASE 
                    WHEN food_cost = 0 OR food_cost IS NULL THEN 'Zero/Missing Food Cost'
                    WHEN food_cost_percentage < 10 THEN 'Food Cost % Below 10%'
                    WHEN food_cost_percentage > 100 THEN 'Food Cost % > 100%'
                    WHEN food_cost_percentage > 40 THEN 'Food Cost % > 40%'
                    WHEN gross_margin < 60 THEN 'Gross Margin < 60%'
                    WHEN calculated_margin < 0 THEN 'Negative Margin'
                    WHEN menu_price = 0 AND recipe_type = 'Recipe' THEN 'Recipe Missing Menu Price'
                    WHEN ABS(margin_variance) > 5 THEN 'Margin Calculation Variance'
                    WHEN yield_quantity IS NULL AND recipe_type = 'PrepRecipe' THEN 'Prep Recipe Missing Yield'
                    WHEN status = 'Draft' THEN 'Draft Status'
                    ELSE 'Other'
                END as issue_type,
                COUNT(*) as count,
                GROUP_CONCAT(recipe_name, ', ') as examples
            FROM stg_recipes
            {where_clause}
            {"AND" if where_clause else "WHERE"} needs_review = 1
            GROUP BY issue_type
            ORDER BY count DESC
        """
        
        issues = []
        for row in cursor.execute(issues_query, params):
            issue = dict(row)
            # Limit examples to first 3
            if issue.get('examples'):
                examples = issue['examples'].split(', ')
                if len(examples) > 3:
                    issue['examples'] = ', '.join(examples[:3]) + f' (+{len(examples)-3} more)'
            issues.append(issue)
        
        summary['issues'] = issues
        
        # Get status breakdown  
        status_query = f"""
            SELECT status, COUNT(*) as count
            FROM stg_recipes
            {where_clause}
            GROUP BY status
            ORDER BY count DESC
        """
        
        summary['status_breakdown'] = [dict(row) for row in cursor.execute(status_query, params)]
        
        conn.close()
        return summary
    
    def get_duplicate_groups(self, batch_id: str = None) -> List[Dict]:
        """Get groups of duplicate recipes"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        where_clause = "WHERE sr.import_batch_id = ?" if batch_id else ""
        params = [batch_id] if batch_id else []
        
        query = f"""
            SELECT 
                sr.duplicate_check_hash,
                COUNT(*) as duplicate_count,
                GROUP_CONCAT(sr.staging_id) as staging_ids,
                GROUP_CONCAT(sr.recipe_name || ' (' || sr.status || ')') as recipe_names,
                MIN(sr.recipe_name) as primary_name,
                EXISTS(SELECT 1 FROM recipes r WHERE r.recipe_name = MIN(sr.recipe_name)) as exists_in_live
            FROM stg_recipes sr
            {where_clause}
            {"AND" if where_clause else "WHERE"} sr.duplicate_check_hash IN (
                SELECT duplicate_check_hash 
                FROM stg_recipes 
                GROUP BY duplicate_check_hash 
                HAVING COUNT(*) > 1
            )
            GROUP BY sr.duplicate_check_hash
            ORDER BY duplicate_count DESC, primary_name
        """
        
        duplicates = []
        for row in cursor.execute(query, params):
            dup = dict(row)
            dup['staging_ids'] = [int(x) for x in dup['staging_ids'].split(',')]
            dup['recipe_names'] = dup['recipe_names'].split(',')
            duplicates.append(dup)
        
        conn.close()
        return duplicates
    
    def handle_duplicate(self, staging_id: int, action: str, suffix: str = None) -> bool:
        """Handle duplicate recipe with specified action"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if action == 'reject':
                cursor.execute("""
                    UPDATE stg_recipes 
                    SET review_status = 'rejected',
                        review_notes = 'Rejected as duplicate',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE staging_id = ?
                """, (staging_id,))
            
            elif action == 'create_version':
                # Add suffix to recipe name
                if not suffix:
                    suffix = '-v2'
                
                cursor.execute("""
                    UPDATE stg_recipes 
                    SET recipe_name = recipe_name || ?,
                        is_duplicate = 0,
                        duplicate_of_staging_id = NULL,
                        duplicate_check_hash = NULL,
                        review_notes = 'Created as new version',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE staging_id = ?
                """, (suffix, staging_id))
            
            elif action == 'merge':
                # Mark for merging/overwriting
                cursor.execute("""
                    UPDATE stg_recipes 
                    SET review_status = 'approved',
                        review_notes = 'Approved to merge/overwrite existing',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE staging_id = ?
                """, (staging_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error handling duplicate: {e}")
            return False
        finally:
            conn.close()
    
    def update_item(self, staging_id: int, updates: Dict) -> bool:
        """Update a staged item"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Build update query
            set_clauses = []
            params = []
            
            # Updatable fields
            updatable_fields = [
                'recipe_name', 'status', 'recipe_group', 'recipe_type',
                'food_cost', 'food_cost_percentage', 'menu_price',
                'gross_margin', 'yield_quantity', 'yield_unit',
                'serving_size', 'serving_size_uom', 'per_serving',
                'review_status', 'review_notes', 'labor_cost',
                'labor_cost_percentage', 'prime_cost', 'prime_cost_percentage'
            ]
            
            for field in updatable_fields:
                if field in updates:
                    set_clauses.append(f"{field} = ?")
                    params.append(updates[field])
            
            # Recalculate if financial fields updated
            if any(f in updates for f in ['food_cost', 'menu_price']):
                cursor.execute("SELECT food_cost, menu_price FROM stg_recipes WHERE staging_id = ?", (staging_id,))
                current = cursor.fetchone()
                
                food_cost = float(updates.get('food_cost', current[0] or 0))
                menu_price = float(updates.get('menu_price', current[1] or 0))
                
                if menu_price > 0:
                    calculated_margin = ((menu_price - food_cost) / menu_price) * 100
                    calculated_food_cost_pct = (food_cost / menu_price) * 100
                    
                    set_clauses.extend([
                        "calculated_margin = ?",
                        "calculated_food_cost_percent = ?",
                        "margin_variance = calculated_margin - gross_margin"
                    ])
                    params.extend([calculated_margin, calculated_food_cost_pct])
            
            # Re-validate if key fields changed
            if any(f in updates for f in ['food_cost', 'food_cost_percentage', 'menu_price', 'gross_margin', 'status']):
                set_clauses.append("needs_review = 1")  # Re-flag for review
            
            # Update timestamp
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            
            # Clear needs_review if explicitly approved
            if updates.get('review_status') == 'approved':
                set_clauses.append("needs_review = 0")
            
            query = f"""
                UPDATE stg_recipes 
                SET {', '.join(set_clauses)}
                WHERE staging_id = ?
            """
            params.append(staging_id)
            
            cursor.execute(query, params)
            conn.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            print(f"Error updating item: {e}")
            return False
        finally:
            conn.close()
    
    def bulk_update_status(self, staging_ids: List[int], status: str) -> int:
        """Bulk update review status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            placeholders = ','.join(['?' for _ in staging_ids])
            query = f"""
                UPDATE stg_recipes 
                SET review_status = ?,
                    updated_at = CURRENT_TIMESTAMP,
                    needs_review = CASE WHEN ? = 'approved' THEN 0 ELSE needs_review END
                WHERE staging_id IN ({placeholders})
            """
            params = [status, status] + staging_ids
            
            cursor.execute(query, params)
            conn.commit()
            
            return cursor.rowcount
            
        except Exception as e:
            conn.rollback()
            print(f"Error in bulk update: {e}")
            return 0
        finally:
            conn.close()
    
    def batch_action(self, staging_ids: List[int], action: str) -> Dict:
        """Handle batch actions matching inventory staging pattern"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        result = {'success': 0, 'failed': 0}
        
        try:
            for staging_id in staging_ids:
                try:
                    if action == 'approve':
                        cursor.execute("""
                            UPDATE stg_recipes 
                            SET review_status = 'approved',
                                needs_review = 0,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE staging_id = ?
                        """, (staging_id,))
                    elif action == 'hold':
                        cursor.execute("""
                            UPDATE stg_recipes 
                            SET review_status = 'hold',
                                updated_at = CURRENT_TIMESTAMP
                            WHERE staging_id = ?
                        """, (staging_id,))
                    elif action == 'reject':
                        cursor.execute("""
                            UPDATE stg_recipes 
                            SET review_status = 'rejected',
                                updated_at = CURRENT_TIMESTAMP
                            WHERE staging_id = ?
                        """, (staging_id,))
                    elif action == 'delete':
                        cursor.execute("""
                            DELETE FROM stg_recipes 
                            WHERE staging_id = ?
                        """, (staging_id,))
                    
                    if cursor.rowcount > 0:
                        result['success'] += 1
                    else:
                        result['failed'] += 1
                        
                except Exception as e:
                    print(f"Error processing staging_id {staging_id}: {e}")
                    result['failed'] += 1
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            print(f"Error in batch action: {e}")
            raise
        finally:
            conn.close()
        
        return result
    
    def commit_to_live(self, staging_ids: List[int] = None) -> Dict:
        """Commit approved items to live recipes table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'errors': 0,
            'skipped_hold': 0
        }
        
        try:
            # Build query - exclude items on hold and those with validation issues
            where_clause = "WHERE review_status = 'approved' AND processed_to_live = 0 AND needs_review = 0"
            params = []
            
            if staging_ids:
                placeholders = ','.join(['?' for _ in staging_ids])
                where_clause += f" AND staging_id IN ({placeholders})"
                params.extend(staging_ids)
            
            query = f"""
                SELECT * FROM stg_recipes
                {where_clause}
            """
            
            for row in cursor.execute(query, params):
                staging_id = row['staging_id']
                
                # Skip non-standard statuses unless explicitly approved
                if row['status'] not in ['Published', 'Approved', 'Active', 'Complete', 'Draft']:
                    if row['review_status'] != 'approved':
                        stats['skipped_hold'] += 1
                        continue
                
                try:
                    # Check if recipe exists
                    existing = cursor.execute(
                        "SELECT id FROM recipes WHERE recipe_name = ?",
                        (row['recipe_name'],)
                    ).fetchone()
                    
                    if existing:
                        # Update existing recipe
                        cursor.execute("""
                            UPDATE recipes SET
                                status = ?,
                                recipe_group = ?,
                                recipe_type = ?,
                                food_cost = ?,
                                food_cost_percentage = ?,
                                labor_cost = ?,
                                labor_cost_percentage = ?,
                                menu_price = ?,
                                gross_margin = ?,
                                prime_cost = ?,
                                prime_cost_percentage = ?,
                                shelf_life = ?,
                                shelf_life_uom = ?,
                                prep_recipe_yield = ?,
                                prep_recipe_yield_uom = ?,
                                serving_size = ?,
                                serving_size_uom = ?,
                                per_serving = ?,
                                cost_modified = ?,
                                updated_date = CURRENT_TIMESTAMP
                            WHERE id = ?
                        """, (
                            row['status'], row['recipe_group'], row['recipe_type'],
                            row['food_cost'], row['food_cost_percentage'],
                            row['labor_cost'], row['labor_cost_percentage'],
                            row['menu_price'], row['gross_margin'],
                            row['prime_cost'], row['prime_cost_percentage'],
                            row['shelf_life'], row['shelf_life_uom'],
                            row['yield_quantity'], row['yield_unit'],
                            row['serving_size'], row['serving_size_uom'],
                            row['per_serving'], row['cost_modified_date'],
                            existing[0]
                        ))
                        stats['updated'] += 1
                    else:
                        # Create new recipe
                        cursor.execute("""
                            INSERT INTO recipes (
                                recipe_name, status, recipe_group, recipe_type,
                                food_cost, food_cost_percentage, labor_cost,
                                labor_cost_percentage, menu_price, gross_margin,
                                prime_cost, prime_cost_percentage, shelf_life,
                                shelf_life_uom, prep_recipe_yield, prep_recipe_yield_uom,
                                serving_size, serving_size_uom, per_serving,
                                cost_modified
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            row['recipe_name'], row['status'], row['recipe_group'],
                            row['recipe_type'], row['food_cost'], row['food_cost_percentage'],
                            row['labor_cost'], row['labor_cost_percentage'],
                            row['menu_price'], row['gross_margin'], row['prime_cost'],
                            row['prime_cost_percentage'], row['shelf_life'], row['shelf_life_uom'],
                            row['yield_quantity'], row['yield_unit'], row['serving_size'],
                            row['serving_size_uom'], row['per_serving'], row['cost_modified_date']
                        ))
                        stats['created'] += 1
                    
                    # Mark as processed
                    cursor.execute("""
                        UPDATE stg_recipes 
                        SET processed_to_live = 1,
                            processed_date = CURRENT_TIMESTAMP
                        WHERE staging_id = ?
                    """, (staging_id,))
                    
                    stats['processed'] += 1
                    
                except Exception as e:
                    print(f"Error processing staging_id {staging_id}: {e}")
                    stats['errors'] += 1
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
        
        return stats

# Initialize admin instance
admin = RecipeStagingAdmin()

# Routes
@recipe_staging_bp.route('/')
def index():
    """Main staging review page"""
    # Get filters from request
    filters = {}
    if request.args.get('batch_id'):
        filters['batch_id'] = request.args.get('batch_id')
    if request.args.get('needs_review'):
        filters['needs_review'] = request.args.get('needs_review')
    if request.args.get('review_status'):
        filters['review_status'] = request.args.get('review_status')
    if request.args.get('recipe_type'):
        filters['recipe_type'] = request.args.get('recipe_type')
    if request.args.get('status'):
        filters['status'] = request.args.get('status')
    if request.args.get('food_cost_issue'):
        filters['food_cost_issue'] = request.args.get('food_cost_issue')
    if request.args.get('margin_issue'):
        filters['margin_issue'] = True
    if request.args.get('search'):
        filters['search'] = request.args.get('search')
    
    page = int(request.args.get('page', 1))
    per_page_str = request.args.get('per_page', '50')
    per_page = per_page_str if per_page_str == 'all' else int(per_page_str)
    
    # Get data
    data = admin.get_review_items(filters, page, per_page)
    
    # Get validation summary
    batch_id = filters.get('batch_id')
    summary = admin.get_validation_summary(batch_id)
    
    # Get duplicates if requested
    show_duplicates = request.args.get('show_duplicates') == '1'
    duplicates = admin.get_duplicate_groups(batch_id) if show_duplicates else []
    
    return render_template('recipe_staging_review.html',
                         items=data['items'],
                         total=data['total'],
                         page=data['page'],
                         per_page=data['per_page'],
                         total_pages=data['total_pages'],
                         batches=data['batches'],
                         filters=filters,
                         summary=summary,
                         duplicates=duplicates,
                         show_duplicates=show_duplicates)

@recipe_staging_bp.route('/item/<int:staging_id>', methods=['GET', 'POST'])
def edit_item(staging_id):
    """Update a single staged item - matches inventory staging pattern"""
    if request.method == 'POST':
        updates = request.json
        
        if admin.update_item(staging_id, updates):
            return jsonify({'success': True, 'message': 'Item updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update item'}), 400
    else:
        # GET method - return item details (if needed)
        return jsonify({'success': False, 'message': 'GET not implemented'}), 501

@recipe_staging_bp.route('/batch-action', methods=['POST'])
def batch_action():
    """Handle batch actions - matches inventory staging pattern"""
    data = request.json
    staging_ids = data.get('staging_ids', [])
    action = data.get('action')
    
    if not staging_ids or not action:
        return jsonify({'success': False, 'message': 'Missing required parameters'}), 400
    
    # Convert string IDs to integers
    staging_ids = [int(sid) for sid in staging_ids]
    
    result = admin.batch_action(staging_ids, action)
    
    return jsonify({
        'success': result['success'],
        'failed': result['failed'],
        'message': f'Successfully {action}d {result["success"]} items'
    })

@recipe_staging_bp.route('/process-to-live', methods=['POST'])
def process_to_live():
    """Process approved items to live database"""
    data = request.json
    batch_id = data.get('batch_id')
    
    try:
        # Get approved staging IDs for the batch if specified
        staging_ids = None
        if batch_id:
            conn = sqlite3.connect(admin.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT staging_id 
                FROM stg_recipes 
                WHERE import_batch_id = ? AND review_status = 'approved'
            """, (batch_id,))
            staging_ids = [row[0] for row in cursor.fetchall()]
            conn.close()
        
        stats = admin.commit_to_live(staging_ids)
        
        return jsonify({
            'processed': stats['processed'],
            'errors': stats['errors'],
            'details': [
                f"Created: {stats['created']}",
                f"Updated: {stats['updated']}",
                f"Skipped (on hold): {stats['skipped_hold']}"
            ]
        })
    except Exception as e:
        return jsonify({
            'processed': 0,
            'errors': 1,
            'details': [str(e)]
        }), 500

@recipe_staging_bp.route('/api/summary')
def api_summary():
    """Get validation summary as JSON"""
    batch_id = request.args.get('batch_id')
    summary = admin.get_validation_summary(batch_id)
    return jsonify(summary)

@recipe_staging_bp.route('/api/duplicates')
def api_duplicates():
    """Get duplicate groups as JSON"""
    batch_id = request.args.get('batch_id')
    duplicates = admin.get_duplicate_groups(batch_id)
    return jsonify(duplicates)