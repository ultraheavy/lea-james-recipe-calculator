#!/usr/bin/env python3
"""
Recipe CSV Staging Admin Review System
Provides Flask routes and functionality for reviewing and approving staged recipe CSV data
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import sqlite3
from datetime import datetime
import json
from typing import Dict, List, Tuple, Any
import re

# Create Blueprint
recipe_csv_staging_bp = Blueprint('recipe_csv_staging', __name__, url_prefix='/admin/recipe-csv-staging')

class RecipeCsvStagingAdmin:
    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = "restaurant_calculator.db"
        else:
            self.db_path = db_path
    
    def get_recipes_for_review(self, filters: Dict = None, page: int = 1, per_page: int = 50) -> Dict:
        """Get RECIPES for review (not individual ingredients)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get recipe-level summary data
        where_clauses = ["is_latest_version = 1"]
        params = []
        
        # Apply filters
        if filters:
            if filters.get('batch_id'):
                where_clauses.append("import_batch_id = ?")
                params.append(filters['batch_id'])
            
            if filters.get('review_status'):
                where_clauses.append("review_status = ?")
                params.append(filters['review_status'])
            
            if filters.get('is_prep_recipe') is not None:
                where_clauses.append("is_prep_recipe = ?")
                params.append(filters['is_prep_recipe'])
        
        # Count unique recipes
        count_query = f"""
            SELECT COUNT(DISTINCT recipe_name) 
            FROM stg_csv_recipes
            WHERE {' AND '.join(where_clauses)}
        """
        total_count = cursor.execute(count_query, params).fetchone()[0]
        
        # Get recipe summaries with pagination
        offset = (page - 1) * per_page
        recipe_query = f"""
            SELECT 
                recipe_name,
                COUNT(*) as ingredient_count,
                SUM(CAST(cost AS REAL)) as total_cost,
                MAX(is_prep_recipe) as is_prep_recipe,
                MAX(source_filename) as source_filename,
                MAX(import_batch_id) as import_batch_id,
                MIN(review_status) as review_status,
                MAX(needs_review) as needs_review,
                COUNT(CASE WHEN used_as_ingredient = 1 THEN 1 END) as prep_ingredient_count
            FROM stg_csv_recipes
            WHERE {' AND '.join(where_clauses)}
            GROUP BY recipe_name
            ORDER BY recipe_name
            LIMIT ? OFFSET ?
        """
        params.extend([per_page, offset])
        
        recipes = []
        for row in cursor.execute(recipe_query, params):
            recipe = dict(row)
            recipe['review_status'] = recipe['review_status'] or 'pending'
            recipes.append(recipe)
        
        conn.close()
        
        return {
            'recipes': recipes,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        }
    
    def get_recipe_ingredients(self, recipe_name: str) -> List[Dict]:
        """Get all ingredients for a specific recipe"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
            SELECT * FROM stg_csv_recipes
            WHERE recipe_name = ? AND is_latest_version = 1
            ORDER BY row_number
        """
        
        ingredients = []
        for row in cursor.execute(query, (recipe_name,)):
            ingredients.append(dict(row))
        
        conn.close()
        return ingredients
    
    def get_review_items(self, filters: Dict = None, page: int = 1, per_page: int = 50) -> Dict:
        """DEPRECATED - Use get_recipes_for_review instead"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Base query - by default only show latest versions
        where_clauses = ["is_latest_version = 1"]
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
            
            if filters.get('is_prep_recipe') is not None:
                where_clauses.append("is_prep_recipe = ?")
                params.append(filters['is_prep_recipe'])
            
            if filters.get('used_as_ingredient') is not None:
                where_clauses.append("used_as_ingredient = ?")
                params.append(filters['used_as_ingredient'])
            
            if filters.get('has_issues'):
                issues_clause = """(
                    validation_errors IS NOT NULL 
                    OR quantity IS NULL 
                    OR unit IS NULL 
                    OR cost IS NULL 
                    OR CAST(cost AS REAL) <= 0
                )"""
                where_clauses.append(issues_clause)
            
            if filters.get('show_all_versions'):
                # Remove the default latest version filter
                where_clauses = [w for w in where_clauses if w != "is_latest_version = 1"]
            
            if filters.get('search'):
                search_clause = "(recipe_name LIKE ? OR ingredient_name LIKE ?)"
                where_clauses.append(search_clause)
                search_term = f"%{filters['search']}%"
                params.extend([search_term, search_term])
        
        # Count query
        count_query = f"""
            SELECT COUNT(*) FROM stg_csv_recipes
            WHERE {' AND '.join(where_clauses)}
        """
        total_count = cursor.execute(count_query, params).fetchone()[0]
        
        # Data query with pagination
        offset = (page - 1) * per_page
        data_query = f"""
            SELECT 
                staging_id,
                recipe_name,
                ingredient_name,
                quantity,
                unit,
                cost,
                category,
                is_prep_recipe,
                used_as_ingredient,
                ingredient_source_type,
                ingredient_source_recipe_name,
                has_prep_dependencies,
                missing_prep_recipes,
                source_filename,
                source_timestamp,
                row_number,
                needs_review,
                review_status,
                validation_errors,
                is_duplicate,
                duplicate_of_recipe,
                import_batch_id,
                imported_at,
                reviewed_at,
                reviewed_by,
                committed,
                committed_at,
                is_latest_version,
                replaced_by_batch
            FROM stg_csv_recipes
            WHERE {' AND '.join(where_clauses)}
            ORDER BY recipe_name, row_number
            LIMIT ? OFFSET ?
        """
        params.extend([per_page, offset])
        
        items = []
        for row in cursor.execute(data_query, params):
            item = dict(row)
            # Parse validation flags
            item['flags'] = self._parse_validation_flags(item)
            items.append(item)
        
        conn.close()
        
        return {
            'items': items,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        }
    
    def _parse_validation_flags(self, item: Dict) -> List[str]:
        """Parse validation issues into displayable flags"""
        flags = []
        
        if item.get('validation_errors'):
            flags.extend(item['validation_errors'].split(', '))
        
        if not item.get('quantity'):
            flags.append('Missing quantity')
        
        if not item.get('unit'):
            flags.append('Missing unit')
        
        if not item.get('cost'):
            flags.append('Invalid cost')
        else:
            try:
                cost_val = float(item['cost'])
                if cost_val <= 0:
                    flags.append('Invalid cost')
            except (ValueError, TypeError):
                flags.append('Invalid cost')
        
        if item.get('is_duplicate'):
            flags.append(f"Duplicate of {item['duplicate_of_recipe']}")
        
        if item.get('has_prep_dependencies') and item.get('missing_prep_recipes'):
            flags.append(f"Missing prep: {item['missing_prep_recipes']}")
        
        return flags
    
    def get_batch_list(self) -> List[str]:
        """Get list of all import batches"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        batches = []
        query = """
            SELECT DISTINCT import_batch_id, 
                   COUNT(*) as count,
                   MIN(imported_at) as import_date
            FROM stg_csv_recipes
            GROUP BY import_batch_id
            ORDER BY import_date DESC
        """
        
        for row in cursor.execute(query):
            batches.append({
                'id': row[0],
                'count': row[1],
                'date': row[2]
            })
        
        conn.close()
        return batches
    
    def update_item(self, staging_id: int, updates: Dict) -> Dict:
        """Update a single staging item"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        result = {'success': False, 'message': ''}
        
        try:
            # Build update query
            update_fields = []
            params = []
            
            allowed_fields = [
                'recipe_name', 'ingredient_name', 'quantity', 'unit', 
                'cost', 'category', 'is_prep_recipe', 'review_status',
                'review_notes', 'needs_review'
            ]
            
            for field in allowed_fields:
                if field in updates:
                    update_fields.append(f"{field} = ?")
                    params.append(updates[field])
            
            if update_fields:
                update_fields.append("reviewed_at = CURRENT_TIMESTAMP")
                update_fields.append("reviewed_by = 'admin'")
                
                query = f"""
                    UPDATE stg_csv_recipes 
                    SET {', '.join(update_fields)}
                    WHERE staging_id = ?
                """
                params.append(staging_id)
                
                cursor.execute(query, params)
                conn.commit()
                
                result['success'] = True
                result['message'] = 'Item updated successfully'
            else:
                result['message'] = 'No valid fields to update'
                
        except Exception as e:
            conn.rollback()
            result['message'] = f"Error updating item: {str(e)}"
        finally:
            conn.close()
        
        return result
    
    def batch_action(self, staging_ids: List[int], action: str) -> Dict:
        """Perform batch action on multiple items"""
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
                    UPDATE stg_csv_recipes 
                    SET review_status = 'approved', 
                        needs_review = 0, 
                        reviewed_at = CURRENT_TIMESTAMP,
                        reviewed_by = 'admin'
                    WHERE staging_id = ?
                """
            elif action == 'reject':
                query = """
                    UPDATE stg_csv_recipes 
                    SET review_status = 'rejected',
                        reviewed_at = CURRENT_TIMESTAMP,
                        reviewed_by = 'admin'
                    WHERE staging_id = ?
                """
            elif action == 'delete':
                query = """
                    DELETE FROM stg_csv_recipes 
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
    
    def approve_recipe(self, recipe_name: str) -> Dict:
        """Approve all ingredients for a recipe"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        result = {'success': False, 'message': '', 'updated': 0}
        
        try:
            # Update all ingredients for this recipe
            query = """
                UPDATE stg_csv_recipes 
                SET review_status = 'approved', 
                    needs_review = 0, 
                    reviewed_at = CURRENT_TIMESTAMP,
                    reviewed_by = 'admin'
                WHERE recipe_name = ? AND is_latest_version = 1
            """
            
            cursor.execute(query, (recipe_name,))
            result['updated'] = cursor.rowcount
            conn.commit()
            
            result['success'] = True
            result['message'] = f'Approved {result["updated"]} ingredients for recipe "{recipe_name}"'
            
        except Exception as e:
            conn.rollback()
            result['message'] = f"Error approving recipe: {str(e)}"
        finally:
            conn.close()
        
        return result
    
    def reject_recipe(self, recipe_name: str, reason: str = None) -> Dict:
        """Reject all ingredients for a recipe"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        result = {'success': False, 'message': '', 'updated': 0}
        
        try:
            # Update all ingredients for this recipe
            query = """
                UPDATE stg_csv_recipes 
                SET review_status = 'rejected',
                    reviewed_at = CURRENT_TIMESTAMP,
                    reviewed_by = 'admin',
                    review_notes = ?
                WHERE recipe_name = ? AND is_latest_version = 1
            """
            
            cursor.execute(query, (reason or 'Rejected by admin', recipe_name))
            result['updated'] = cursor.rowcount
            conn.commit()
            
            result['success'] = True
            result['message'] = f'Rejected {result["updated"]} ingredients for recipe "{recipe_name}"'
            
        except Exception as e:
            conn.rollback()
            result['message'] = f"Error rejecting recipe: {str(e)}"
        finally:
            conn.close()
        
        return result
    
    def process_to_live(self, batch_id: str = None) -> Dict:
        """Process approved recipes to live recipe tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        results = {
            'processed_recipes': 0,
            'processed_ingredients': 0,
            'errors': 0,
            'details': []
        }
        
        try:
            # Get distinct approved recipes to commit, ordered to handle prep recipe dependencies
            if batch_id:
                recipe_query = """
                    WITH recipe_dependencies AS (
                        SELECT DISTINCT 
                            s1.recipe_name,
                            s1.is_prep_recipe,
                            CASE WHEN EXISTS (
                                SELECT 1 FROM stg_csv_recipes s2 
                                WHERE s2.ingredient_source_recipe_name = s1.recipe_name
                                AND s2.used_as_ingredient = 1
                            ) THEN 1 ELSE 0 END as is_dependency
                        FROM stg_csv_recipes s1
                        WHERE s1.review_status = 'approved' 
                        AND s1.committed = 0
                        AND s1.import_batch_id = ?
                    )
                    SELECT recipe_name, is_prep_recipe
                    FROM recipe_dependencies
                    ORDER BY is_dependency DESC, is_prep_recipe DESC
                """
                recipes_to_commit = cursor.execute(recipe_query, (batch_id,)).fetchall()
            else:
                recipe_query = """
                    WITH recipe_dependencies AS (
                        SELECT DISTINCT 
                            s1.recipe_name,
                            s1.is_prep_recipe,
                            CASE WHEN EXISTS (
                                SELECT 1 FROM stg_csv_recipes s2 
                                WHERE s2.ingredient_source_recipe_name = s1.recipe_name
                                AND s2.used_as_ingredient = 1
                            ) THEN 1 ELSE 0 END as is_dependency
                        FROM stg_csv_recipes s1
                        WHERE s1.review_status = 'approved' 
                        AND s1.committed = 0
                    )
                    SELECT recipe_name, is_prep_recipe
                    FROM recipe_dependencies
                    ORDER BY is_dependency DESC, is_prep_recipe DESC
                """
                recipes_to_commit = cursor.execute(recipe_query).fetchall()
            
            # Process each recipe
            for recipe_name, is_prep_recipe in recipes_to_commit:
                try:
                    # Check if recipe already exists
                    existing = cursor.execute(
                        "SELECT recipe_id FROM recipes_actual WHERE recipe_name = ?",
                        (recipe_name,)
                    ).fetchone()
                    
                    if existing:
                        results['details'].append(f"Recipe '{recipe_name}' already exists, skipping")
                        continue
                    
                    # Get first row of recipe data for metadata
                    if batch_id:
                        metadata_query = """
                            SELECT * FROM stg_csv_recipes 
                            WHERE recipe_name = ? 
                            AND import_batch_id = ?
                            LIMIT 1
                        """
                        recipe_data = cursor.execute(metadata_query, (recipe_name, batch_id)).fetchone()
                    else:
                        metadata_query = """
                            SELECT * FROM stg_csv_recipes 
                            WHERE recipe_name = ?
                            LIMIT 1
                        """
                        recipe_data = cursor.execute(metadata_query, (recipe_name,)).fetchone()
                    
                    # Insert recipe
                    cursor.execute("""
                        INSERT INTO recipes_actual (
                            recipe_name, 
                            recipe_type,
                            recipe_group,
                            status,
                            created_at
                        ) VALUES (?, ?, ?, 'Active', CURRENT_TIMESTAMP)
                    """, (
                        recipe_name, 
                        'PrepRecipe' if is_prep_recipe else 'Recipe',
                        'Prep' if is_prep_recipe else 'Main'  # Default grouping
                    ))
                    
                    recipe_id = cursor.lastrowid
                    results['processed_recipes'] += 1
                    
                    # Get all ingredients for this recipe
                    if batch_id:
                        ingredients_query = """
                            SELECT * FROM stg_csv_recipes 
                            WHERE recipe_name = ? 
                            AND review_status = 'approved'
                            AND import_batch_id = ?
                        """
                        ingredients = cursor.execute(ingredients_query, (recipe_name, batch_id)).fetchall()
                    else:
                        ingredients_query = """
                            SELECT * FROM stg_csv_recipes 
                            WHERE recipe_name = ? 
                            AND review_status = 'approved'
                        """
                        ingredients = cursor.execute(ingredients_query, (recipe_name,)).fetchall()
                    
                    # Insert ingredients
                    for idx, ingredient in enumerate(ingredients):
                        cursor.execute("""
                            INSERT INTO recipe_ingredients_actual (
                                recipe_id, 
                                ingredient_order,
                                ingredient_name, 
                                quantity, 
                                unit, 
                                total_cost,
                                created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        """, (
                            recipe_id,
                            idx + 1,  # ingredient_order
                            ingredient['ingredient_name'],
                            ingredient['quantity'] or 0,
                            ingredient['unit'] or 'each',
                            ingredient['cost'] or 0
                        ))
                        results['processed_ingredients'] += 1
                        
                        # Mark as committed
                        cursor.execute("""
                            UPDATE stg_csv_recipes 
                            SET committed = 1, 
                                committed_at = CURRENT_TIMESTAMP,
                                committed_by = 'admin',
                                committed_recipe_id = ?
                            WHERE staging_id = ?
                        """, (recipe_id, ingredient['staging_id']))
                    
                    results['details'].append(f"Successfully committed recipe '{recipe_name}' with {len(ingredients)} ingredients")
                    
                except Exception as e:
                    results['errors'] += 1
                    results['details'].append(f"Failed to process recipe '{recipe_name}': {str(e)}")
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            results['details'].append(f"Process error: {str(e)}")
            
        finally:
            conn.close()
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get overall statistics for staged recipes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Overall counts
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN needs_review = 1 THEN 1 ELSE 0 END) as needs_review,
                SUM(CASE WHEN review_status = 'approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN review_status = 'rejected' THEN 1 ELSE 0 END) as rejected,
                SUM(CASE WHEN review_status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN is_duplicate = 1 THEN 1 ELSE 0 END) as duplicates,
                SUM(CASE WHEN committed = 1 THEN 1 ELSE 0 END) as committed,
                SUM(CASE WHEN used_as_ingredient = 1 THEN 1 ELSE 0 END) as prep_ingredients,
                SUM(CASE WHEN has_prep_dependencies = 1 THEN 1 ELSE 0 END) as missing_deps
            FROM stg_csv_recipes
        """
        row = cursor.execute(query).fetchone()
        stats['overall'] = {
            'total': row[0] or 0,
            'needs_review': row[1] or 0,
            'approved': row[2] or 0,
            'rejected': row[3] or 0,
            'pending': row[4] or 0,
            'duplicates': row[5] or 0,
            'committed': row[6] or 0,
            'prep_ingredients': row[7] or 0,
            'missing_deps': row[8] or 0
        }
        
        # Recipe counts
        query = """
            SELECT COUNT(DISTINCT recipe_name) as recipe_count,
                   COUNT(DISTINCT CASE WHEN is_prep_recipe = 1 THEN recipe_name END) as prep_count
            FROM stg_csv_recipes
        """
        row = cursor.execute(query).fetchone()
        stats['recipes'] = {
            'total': row[0] or 0,
            'prep': row[1] or 0
        }
        
        # Issue breakdown
        query = """
            SELECT 
                SUM(CASE WHEN quantity IS NULL THEN 1 ELSE 0 END) as missing_quantity,
                SUM(CASE WHEN unit IS NULL THEN 1 ELSE 0 END) as missing_unit,
                SUM(CASE WHEN cost IS NULL OR CAST(cost AS REAL) <= 0 THEN 1 ELSE 0 END) as invalid_cost
            FROM stg_csv_recipes
            WHERE review_status != 'rejected'
        """
        row = cursor.execute(query).fetchone()
        stats['issues'] = {
            'missing_quantity': row[0] or 0,
            'missing_unit': row[1] or 0,
            'invalid_cost': row[2] or 0
        }
        
        conn.close()
        return stats

# Initialize admin instance
admin = RecipeCsvStagingAdmin()

# Routes
@recipe_csv_staging_bp.route('/')
def index():
    """Main review page - Shows RECIPES not ingredients"""
    # Get filters from request
    filters = {}
    if request.args.get('batch_id'):
        filters['batch_id'] = request.args.get('batch_id')
    if request.args.get('review_status'):
        filters['review_status'] = request.args.get('review_status')
    if request.args.get('is_prep_recipe'):
        filters['is_prep_recipe'] = request.args.get('is_prep_recipe') == '1'
    if request.args.get('search'):
        filters['search'] = request.args.get('search')
    
    # Get pagination params
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    # Get data
    data = admin.get_recipes_for_review(filters, page, per_page)
    batches = admin.get_batch_list()
    stats = admin.get_statistics()
    
    return render_template('recipe_csv_staging_review.html',
                         recipes=data['recipes'],
                         total=data['total'],
                         page=data['page'],
                         per_page=data['per_page'],
                         total_pages=data['total_pages'],
                         batches=batches,
                         stats=stats,
                         filters=filters)

@recipe_csv_staging_bp.route('/recipe/<recipe_name>/ingredients')
def get_recipe_ingredients(recipe_name):
    """Get ingredients for a specific recipe"""
    ingredients = admin.get_recipe_ingredients(recipe_name)
    return jsonify({'ingredients': ingredients})

@recipe_csv_staging_bp.route('/item/<int:staging_id>', methods=['GET', 'POST'])
def item(staging_id):
    """Get or update a single item"""
    if request.method == 'POST':
        updates = request.json
        result = admin.update_item(staging_id, updates)
        return jsonify(result)
    else:
        # Get single item
        conn = sqlite3.connect(admin.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        item = cursor.execute(
            "SELECT * FROM stg_csv_recipes WHERE staging_id = ?",
            (staging_id,)
        ).fetchone()
        
        conn.close()
        
        if item:
            return jsonify(dict(item))
        else:
            return jsonify({'error': 'Item not found'}), 404

@recipe_csv_staging_bp.route('/recipe/<recipe_name>/approve', methods=['POST'])
def approve_recipe(recipe_name):
    """Approve all ingredients for a recipe"""
    result = admin.approve_recipe(recipe_name)
    return jsonify(result)

@recipe_csv_staging_bp.route('/recipe/<recipe_name>/reject', methods=['POST'])
def reject_recipe(recipe_name):
    """Reject all ingredients for a recipe"""
    reason = request.json.get('reason') if request.json else None
    result = admin.reject_recipe(recipe_name, reason)
    return jsonify(result)

@recipe_csv_staging_bp.route('/batch-action', methods=['POST'])
def batch_action():
    """Perform batch action on multiple items"""
    staging_ids = request.json.get('staging_ids', [])
    action = request.json.get('action')
    
    if not staging_ids or not action:
        return jsonify({'error': 'Missing parameters'}), 400
    
    results = admin.batch_action(staging_ids, action)
    return jsonify(results)

@recipe_csv_staging_bp.route('/process-to-live', methods=['POST'])
def process_to_live():
    """Process approved recipes to live tables"""
    batch_id = request.json.get('batch_id')
    results = admin.process_to_live(batch_id)
    
    return jsonify(results)

@recipe_csv_staging_bp.route('/statistics')
def statistics():
    """Get current statistics"""
    stats = admin.get_statistics()
    return jsonify(stats)

@recipe_csv_staging_bp.route('/refresh-data', methods=['POST'])
def refresh_data():
    """Refresh staging data from CSV files"""
    from csv_recipe_loader import CSVRecipeLoaderV2
    
    try:
        loader = CSVRecipeLoaderV2()
        loader.init_database()
        
        # Always clear and reload
        results = loader.load_to_staging(clear_existing=True)
        
        # Check for duplicates and dependencies
        loader.check_duplicates()
        loader.check_prep_dependencies()
        
        return jsonify({
            'success': True,
            'message': f'Successfully loaded {results["successful_files"]} recipes',
            'details': {
                'loaded': results['successful_files'],
                'failed': results['failed_files'],
                'skipped': results['skipped_files'],
                'total_ingredients': results['total_ingredients'],
                'batch_id': results['batch_id']
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error refreshing data: {str(e)}'
        }), 500