#!/usr/bin/env python3
"""
Admin interface for reviewing and approving staged PDF recipes.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
import sqlite3
from datetime import datetime
import json

# Create blueprint
pdf_staging_bp = Blueprint('pdf_staging', __name__, url_prefix='/admin/recipe-pdf-staging')


def get_db():
    """Get database connection."""
    # Use the same database file as the loader
    conn = sqlite3.connect('recipe_cost_app.db')
    conn.row_factory = sqlite3.Row
    return conn


@pdf_staging_bp.route('/')
def index():
    """Main staging review page."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get filter parameters
    needs_review = request.args.get('needs_review', 'false') == 'true'
    prep_only = request.args.get('prep_only', 'false') == 'true'
    recipe_filter = request.args.get('recipe', '')
    
    # Build query
    query = """
        SELECT 
            staging_id,
            recipe_name,
            recipe_prefix,
            ingredient_name,
            quantity,
            unit,
            cost,
            is_prep_recipe,
            source_file,
            source_text,
            needs_review,
            review_notes,
            approved,
            approved_by,
            approved_at
        FROM stg_pdf_recipes
        WHERE 1=1
    """
    params = []
    
    if needs_review:
        query += " AND needs_review = 1"
    
    if prep_only:
        query += " AND is_prep_recipe = 1"
    
    if recipe_filter:
        query += " AND recipe_name LIKE ?"
        params.append(f"%{recipe_filter}%")
    
    query += " ORDER BY recipe_name, staging_id"
    
    cursor.execute(query, params)
    ingredients = cursor.fetchall()
    
    # Group by recipe
    recipes = {}
    for ing in ingredients:
        recipe_name = ing['recipe_name']
        if recipe_name not in recipes:
            recipes[recipe_name] = {
                'name': recipe_name,
                'prefix': ing['recipe_prefix'],
                'is_prep': ing['is_prep_recipe'],
                'source_file': ing['source_file'],
                'ingredients': []
            }
        recipes[recipe_name]['ingredients'].append(dict(ing))
    
    # Get summary stats
    cursor.execute("SELECT COUNT(DISTINCT recipe_name) as total_recipes FROM stg_pdf_recipes")
    total_recipes = cursor.fetchone()['total_recipes']
    
    cursor.execute("SELECT COUNT(*) as total_ingredients FROM stg_pdf_recipes")
    total_ingredients = cursor.fetchone()['total_ingredients']
    
    cursor.execute("SELECT COUNT(*) as needs_review FROM stg_pdf_recipes WHERE needs_review = 1")
    total_needs_review = cursor.fetchone()['needs_review']
    
    cursor.execute("SELECT COUNT(*) as approved FROM stg_pdf_recipes WHERE approved = 1")
    total_approved = cursor.fetchone()['approved']
    
    conn.close()
    
    return render_template('recipe_pdf_staging.html',
                         recipes=recipes,
                         total_recipes=total_recipes,
                         total_ingredients=total_ingredients,
                         total_needs_review=total_needs_review,
                         total_approved=total_approved,
                         needs_review_filter=needs_review,
                         prep_only_filter=prep_only,
                         recipe_filter=recipe_filter)


@pdf_staging_bp.route('/update/<int:staging_id>', methods=['POST'])
def update_ingredient(staging_id):
    """Update a single ingredient."""
    data = request.get_json()
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Update the ingredient
        cursor.execute("""
            UPDATE stg_pdf_recipes
            SET ingredient_name = ?,
                quantity = ?,
                unit = ?,
                cost = ?,
                review_notes = ?,
                needs_review = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE staging_id = ?
        """, (
            data.get('ingredient_name'),
            data.get('quantity'),
            data.get('unit'),
            data.get('cost'),
            data.get('review_notes'),
            data.get('needs_review', False),
            staging_id
        ))
        
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Ingredient updated'})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        conn.close()


@pdf_staging_bp.route('/approve/<int:staging_id>', methods=['POST'])
def approve_ingredient(staging_id):
    """Approve a single ingredient."""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE stg_pdf_recipes
            SET approved = 1,
                approved_by = 'admin',
                approved_at = CURRENT_TIMESTAMP,
                needs_review = 0,
                updated_at = CURRENT_TIMESTAMP
            WHERE staging_id = ?
        """, (staging_id,))
        
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Ingredient approved'})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        conn.close()


@pdf_staging_bp.route('/approve-recipe', methods=['POST'])
def approve_recipe():
    """Approve all ingredients for a recipe."""
    recipe_name = request.json.get('recipe_name')
    
    if not recipe_name:
        return jsonify({'success': False, 'error': 'Recipe name required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE stg_pdf_recipes
            SET approved = 1,
                approved_by = 'admin',
                approved_at = CURRENT_TIMESTAMP,
                needs_review = 0,
                updated_at = CURRENT_TIMESTAMP
            WHERE recipe_name = ?
        """, (recipe_name,))
        
        rows_updated = cursor.rowcount
        conn.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Approved {rows_updated} ingredients for {recipe_name}'
        })
    
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        conn.close()


@pdf_staging_bp.route('/delete/<int:staging_id>', methods=['DELETE'])
def delete_ingredient(staging_id):
    """Delete a single ingredient."""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM stg_pdf_recipes WHERE staging_id = ?", (staging_id,))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Ingredient deleted'})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        conn.close()


@pdf_staging_bp.route('/stats')
def get_stats():
    """Get staging table statistics."""
    conn = get_db()
    cursor = conn.cursor()
    
    stats = {}
    
    # Recipe counts
    cursor.execute("SELECT COUNT(DISTINCT recipe_name) as count FROM stg_pdf_recipes")
    stats['total_recipes'] = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(DISTINCT recipe_name) as count FROM stg_pdf_recipes WHERE is_prep_recipe = 1")
    stats['prep_recipes'] = cursor.fetchone()['count']
    
    # Ingredient counts
    cursor.execute("SELECT COUNT(*) as count FROM stg_pdf_recipes")
    stats['total_ingredients'] = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM stg_pdf_recipes WHERE needs_review = 1")
    stats['needs_review'] = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM stg_pdf_recipes WHERE approved = 1")
    stats['approved'] = cursor.fetchone()['count']
    
    # Cost analysis
    cursor.execute("SELECT COUNT(*) as count FROM stg_pdf_recipes WHERE cost IS NULL OR cost = '' OR cost = '0' OR cost = '0.00'")
    stats['missing_costs'] = cursor.fetchone()['count']
    
    # Ready to commit
    cursor.execute("""
        SELECT COUNT(DISTINCT recipe_name) as count 
        FROM stg_pdf_recipes 
        WHERE approved = 1 AND needs_review = 0 AND committed = 0
    """)
    stats['ready_to_commit'] = cursor.fetchone()['count']
    
    conn.close()
    
    return jsonify(stats)


@pdf_staging_bp.route('/commit-to-database', methods=['POST'])
def commit_to_database():
    """Commit approved recipes to main database."""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Get distinct approved recipes that haven't been committed
        cursor.execute("""
            SELECT DISTINCT recipe_name, recipe_prefix, is_prep_recipe, source_file
            FROM stg_pdf_recipes
            WHERE approved = 1 AND needs_review = 0 AND committed = 0
            ORDER BY recipe_name
        """)
        
        recipes_to_commit = cursor.fetchall()
        
        committed_count = 0
        skipped_count = 0
        errors = []
        
        for recipe in recipes_to_commit:
            recipe_name = recipe['recipe_name']
            
            # Check if recipe already exists
            cursor.execute("SELECT recipe_id FROM recipes WHERE recipe_name = ?", (recipe_name,))
            existing = cursor.fetchone()
            
            if existing:
                skipped_count += 1
                errors.append(f"Recipe '{recipe_name}' already exists - skipped")
                continue
            
            try:
                # Begin transaction for this recipe
                conn.execute("BEGIN")
                
                # Insert into recipes table
                cursor.execute("""
                    INSERT INTO recipes (
                        recipe_name, recipe_prefix, is_prep_recipe, 
                        source_file, created_by
                    ) VALUES (?, ?, ?, ?, 'pdf_import')
                """, (
                    recipe_name,
                    recipe['recipe_prefix'],
                    recipe['is_prep_recipe'],
                    recipe['source_file']
                ))
                
                recipe_id = cursor.lastrowid
                
                # Get all ingredients for this recipe
                cursor.execute("""
                    SELECT ingredient_name, quantity, unit, cost, source_text
                    FROM stg_pdf_recipes
                    WHERE recipe_name = ? AND approved = 1 AND needs_review = 0
                """, (recipe_name,))
                
                ingredients = cursor.fetchall()
                
                # Insert ingredients
                for ing in ingredients:
                    cursor.execute("""
                        INSERT INTO recipe_ingredients (
                            recipe_id, ingredient_name, quantity, unit, cost,
                            source_file, source_text
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        recipe_id,
                        ing['ingredient_name'],
                        ing['quantity'],
                        ing['unit'],
                        ing['cost'],
                        recipe['source_file'],
                        ing['source_text']
                    ))
                
                # Mark staging rows as committed
                cursor.execute("""
                    UPDATE stg_pdf_recipes
                    SET committed = 1, 
                        committed_at = CURRENT_TIMESTAMP,
                        committed_recipe_id = ?
                    WHERE recipe_name = ? AND approved = 1 AND needs_review = 0
                """, (recipe_id, recipe_name))
                
                conn.commit()
                committed_count += 1
                
            except Exception as e:
                conn.rollback()
                errors.append(f"Error committing '{recipe_name}': {str(e)}")
        
        return jsonify({
            'success': True,
            'committed': committed_count,
            'skipped': skipped_count,
            'errors': errors,
            'message': f'Committed {committed_count} recipes, skipped {skipped_count}'
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        conn.close()


@pdf_staging_bp.route('/ready-to-commit')
def ready_to_commit():
    """Get list of recipes ready to commit."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            recipe_name,
            recipe_prefix,
            is_prep_recipe,
            COUNT(*) as ingredient_count,
            SUM(CASE WHEN cost IS NULL OR cost = '' OR cost = '0' OR cost = '0.00' THEN 1 ELSE 0 END) as missing_costs
        FROM stg_pdf_recipes
        WHERE approved = 1 AND needs_review = 0 AND committed = 0
        GROUP BY recipe_name, recipe_prefix, is_prep_recipe
        ORDER BY recipe_name
    """)
    
    ready_recipes = []
    for row in cursor.fetchall():
        ready_recipes.append({
            'recipe_name': row['recipe_name'],
            'recipe_prefix': row['recipe_prefix'],
            'is_prep_recipe': row['is_prep_recipe'],
            'ingredient_count': row['ingredient_count'],
            'missing_costs': row['missing_costs']
        })
    
    # Check for duplicates
    recipe_names = [r['recipe_name'] for r in ready_recipes]
    if recipe_names:
        placeholders = ','.join('?' * len(recipe_names))
        cursor.execute(f"""
            SELECT recipe_name FROM recipes 
            WHERE recipe_name IN ({placeholders})
        """, recipe_names)
        
        existing_names = {row['recipe_name'] for row in cursor.fetchall()}
        
        for recipe in ready_recipes:
            recipe['already_exists'] = recipe['recipe_name'] in existing_names
    
    conn.close()
    
    return jsonify(ready_recipes)


@pdf_staging_bp.route('/committed-recipes')
def committed_recipes():
    """View committed recipes."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get committed recipes with stats
    cursor.execute("""
        SELECT 
            r.recipe_id,
            r.recipe_name,
            r.recipe_prefix,
            r.is_prep_recipe,
            r.source_file,
            r.created_at,
            COUNT(ri.ingredient_id) as ingredient_count
        FROM recipes r
        LEFT JOIN recipe_ingredients ri ON r.recipe_id = ri.recipe_id
        WHERE r.created_by = 'pdf_import'
        GROUP BY r.recipe_id
        ORDER BY r.created_at DESC
    """)
    
    committed = []
    for row in cursor.fetchall():
        committed.append({
            'recipe_id': row['recipe_id'],
            'recipe_name': row['recipe_name'],
            'recipe_prefix': row['recipe_prefix'],
            'is_prep_recipe': row['is_prep_recipe'],
            'source_file': row['source_file'],
            'created_at': row['created_at'],
            'ingredient_count': row['ingredient_count']
        })
    
    conn.close()
    
    return render_template('committed_recipes.html', committed_recipes=committed)


@pdf_staging_bp.route('/recipe-details/<int:recipe_id>')
def recipe_details(recipe_id):
    """Get recipe details including ingredients."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get recipe info
    cursor.execute("""
        SELECT * FROM recipes WHERE recipe_id = ?
    """, (recipe_id,))
    
    recipe = cursor.fetchone()
    if not recipe:
        return jsonify({'error': 'Recipe not found'}), 404
    
    # Get ingredients
    cursor.execute("""
        SELECT * FROM recipe_ingredients WHERE recipe_id = ? ORDER BY ingredient_id
    """, (recipe_id,))
    
    ingredients = cursor.fetchall()
    
    conn.close()
    
    return jsonify({
        'recipe': dict(recipe),
        'ingredients': [dict(ing) for ing in ingredients]
    })