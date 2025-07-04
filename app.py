from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DATABASE = 'restaurant_calculator.db'

def init_database():
    """Initialize database with updated schema for Toast POS integration"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        # Enhanced inventory table to match Toast Item Library
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_code TEXT UNIQUE,
                item_description TEXT NOT NULL,
                vendor_name TEXT,
                current_price REAL,
                last_purchased_price REAL,
                last_purchased_date TEXT,
                unit_measure TEXT,
                purchase_unit TEXT,
                recipe_cost_unit TEXT,
                pack_size TEXT,
                yield_percent REAL DEFAULT 100,
                product_categories TEXT,
                close_watch BOOLEAN DEFAULT FALSE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Enhanced recipes table to match Toast Recipe data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_name TEXT NOT NULL UNIQUE,
                status TEXT DEFAULT 'Draft',
                recipe_group TEXT,
                recipe_type TEXT DEFAULT 'Recipe',
                food_cost REAL DEFAULT 0,
                food_cost_percentage REAL DEFAULT 0,
                labor_cost REAL DEFAULT 0,
                labor_cost_percentage REAL DEFAULT 0,
                menu_price REAL DEFAULT 0,
                gross_margin REAL DEFAULT 0,
                prime_cost REAL DEFAULT 0,
                prime_cost_percentage REAL DEFAULT 0,
                shelf_life TEXT,
                shelf_life_uom TEXT,
                prep_recipe_yield TEXT,
                prep_recipe_yield_uom TEXT,
                serving_size TEXT,
                serving_size_uom TEXT,
                per_serving REAL DEFAULT 0,
                station TEXT,
                procedure TEXT,
                cost_modified TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Recipe ingredients table with enhanced fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipe_ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER,
                ingredient_id INTEGER,
                ingredient_name TEXT,
                ingredient_type TEXT DEFAULT 'Product',
                quantity REAL,
                unit_of_measure TEXT,
                cost REAL DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id),
                FOREIGN KEY (ingredient_id) REFERENCES inventory (id)
            )
        ''')
        
        # Enhanced menu items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                menu_group TEXT,
                item_description TEXT,
                recipe_id INTEGER,
                menu_price REAL DEFAULT 0,
                food_cost REAL DEFAULT 0,
                food_cost_percent REAL DEFAULT 0,
                gross_profit REAL DEFAULT 0,
                status TEXT DEFAULT 'Active',
                serving_size TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        ''')
        
        # Add vendors table for vendor management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_name TEXT NOT NULL UNIQUE,
                contact_info TEXT,
                address TEXT,
                phone TEXT,
                email TEXT,
                active BOOLEAN DEFAULT TRUE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_inventory_description ON inventory(item_description)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_recipes_name ON recipes(recipe_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe ON recipe_ingredients(recipe_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_menu_items_group ON menu_items(menu_group)')
        
        conn.commit()

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Dashboard with enhanced statistics"""
    with get_db() as conn:
        inventory_count = conn.execute('SELECT COUNT(*) as count FROM inventory').fetchone()['count']
        recipe_count = conn.execute('SELECT COUNT(*) as count FROM recipes').fetchone()['count']
        menu_count = conn.execute('SELECT COUNT(*) as count FROM menu_items').fetchone()['count']
        vendor_count = conn.execute('SELECT COUNT(*) as count FROM vendors').fetchone()['count']
    
    stats = {
        'inventory_count': inventory_count,
        'recipe_count': recipe_count,
        'menu_count': menu_count,
        'vendor_count': vendor_count
    }
    
    return render_template('index.html', stats=stats)

@app.route('/inventory')
def inventory():
    with get_db() as conn:
        items = conn.execute('''
            SELECT i.* 
            FROM inventory i 
             
            ORDER BY i.item_code
        ''').fetchall()
    return render_template('inventory.html', items=items)

@app.route('/inventory/add', methods=['GET', 'POST'])
def add_inventory():
    """Add new inventory item with enhanced fields"""
    if request.method == 'POST':
        with get_db() as conn:
            conn.execute('''
                INSERT INTO inventory 
                (item_code, item_description, vendor_name, current_price, 
                 last_purchased_price, unit_measure, purchase_unit, 
                 recipe_cost_unit, pack_size, yield_percent, product_categories)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.form['item_code'],
                request.form['item_description'],
                request.form['vendor_name'],
                float(request.form['current_price']) if request.form['current_price'] else 0,
                float(request.form['last_purchased_price']) if request.form['last_purchased_price'] else 0,
                request.form['unit_measure'],
                request.form['purchase_unit'],
                request.form['recipe_cost_unit'],
                request.form['pack_size'],
                float(request.form['yield_percent']) if request.form['yield_percent'] else 100,
                request.form['product_categories']
            ))
            conn.commit()
        
        return redirect(url_for('inventory'))
    
    # Get vendors for dropdown
    with get_db() as conn:
        vendors = conn.execute('SELECT DISTINCT vendor_name FROM vendors ORDER BY vendor_name').fetchall()
    
    return render_template('add_inventory.html', vendors=vendors)

@app.route('/inventory/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_inventory(item_id):
    """Edit existing inventory item"""
    if request.method == 'POST':
        with get_db() as conn:
            conn.execute('''
                UPDATE inventory 
                SET item_code = ?, item_description = ?, vendor_name = ?, 
                    current_price = ?, unit_measure = ?, purchase_unit = ?, 
                    recipe_cost_unit = ?, yield_percent = ?, 
                    cost_per_recipe_unit = ?, conversion_factor = ?
                WHERE id = ?
            ''', (
                request.form['item_code'],
                request.form['item_description'],
                request.form['vendor_name'],
                float(request.form['current_price']) if request.form['current_price'] else 0,
                request.form['unit_measure'],
                request.form['purchase_unit'],
                request.form['recipe_cost_unit'],
                float(request.form['yield_percent']) if request.form['yield_percent'] else 100,
                float(request.form['cost_per_recipe_unit']) if request.form['cost_per_recipe_unit'] else 0,
                float(request.form['conversion_factor']) if request.form['conversion_factor'] else 1,
                item_id
            ))
            conn.commit()
        
        return redirect(url_for('inventory'))
    
    # Get item data and vendors for form
    with get_db() as conn:
        item = conn.execute('SELECT * FROM inventory WHERE id = ?', (item_id,)).fetchone()
        vendors = conn.execute('SELECT DISTINCT name FROM vendors ORDER BY name').fetchall()
    
    if not item:
        return redirect(url_for('inventory'))
    
    return render_template('edit_inventory.html', item=item, vendors=vendors)

@app.route('/recipes')
def recipes():
    with get_db() as conn:
        recipes = conn.execute('''
            SELECT r.*, COUNT(ri.id) as ingredient_count 
            FROM recipes r 
            LEFT JOIN recipe_ingredients ri ON r.id = ri.recipe_id 
            GROUP BY r.id 
            ORDER BY r.recipe_group, r.recipe_name
        ''').fetchall()
    return render_template('recipes.html', recipes=recipes)

@app.route('/recipes/add', methods=['GET', 'POST'])
def add_recipe():
    """Add new recipe with enhanced fields"""
    if request.method == 'POST':
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Insert recipe
            cursor.execute('''
                INSERT INTO recipes 
                (recipe_name, recipe_group, recipe_type, menu_price, 
                 shelf_life, shelf_life_uom, station, procedure, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.form['recipe_name'],
                request.form['recipe_group'],
                request.form.get('recipe_type', 'Recipe'),
                float(request.form['menu_price']) if request.form['menu_price'] else 0,
                request.form['shelf_life'],
                request.form['shelf_life_uom'],
                request.form['station'],
                request.form['procedure'],
                request.form.get('status', 'Draft')
            ))
            
            conn.commit()
        
        return redirect(url_for('recipes'))
    
    # Get inventory for dropdown
    with get_db() as conn:
        inventory = conn.execute('SELECT * FROM inventory ORDER BY item_description').fetchall()
    
    return render_template('add_recipe.html', inventory=inventory)

@app.route('/recipes/<int:recipe_id>')
def view_recipe(recipe_id):
    """View recipe details with enhanced information"""
    with get_db() as conn:
        recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,)).fetchone()
        ingredients = conn.execute('''
            SELECT ri.*, i.item_description, i.unit_measure, i.current_price
            FROM recipe_ingredients ri 
            JOIN inventory i ON ri.ingredient_id = i.id 
            WHERE ri.recipe_id = ?
        ''', (recipe_id,)).fetchall()
    
    return render_template('view_recipe.html', recipe=recipe, ingredients=ingredients)

@app.route('/recipes/<int:recipe_id>/ingredients/add', methods=['GET', 'POST'])
def add_recipe_ingredient(recipe_id):
    """Add ingredient to recipe"""
    if request.method == 'POST':
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get ingredient info for cost calculation
            ingredient = cursor.execute('SELECT * FROM inventory WHERE id = ?', 
                                      (request.form['ingredient_id'],)).fetchone()
            
            quantity = float(request.form['quantity'])
            unit = request.form.get('unit') or ingredient['unit_measure']
            
            # Calculate cost based on cost_per_recipe_unit
            cost = quantity * (ingredient['cost_per_recipe_unit'] or 0)
            
            # Insert recipe ingredient
            cursor.execute('''
                INSERT INTO recipe_ingredients 
                (recipe_id, ingredient_id, quantity, unit, cost)
                VALUES (?, ?, ?, ?, ?)
            ''', (recipe_id, request.form['ingredient_id'], quantity, unit, cost))
            
            # Update recipe total cost
            cursor.execute('''
                UPDATE recipes 
                SET food_cost = (SELECT SUM(cost) FROM recipe_ingredients WHERE recipe_id = ?),
                    total_cost = (SELECT SUM(cost) FROM recipe_ingredients WHERE recipe_id = ?) + COALESCE(labor_cost, 0)
                WHERE id = ?
            ''', (recipe_id, recipe_id, recipe_id))
            
            conn.commit()
        
        return redirect(url_for('view_recipe', recipe_id=recipe_id))
    
    # Get recipe and inventory for form
    with get_db() as conn:
        recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,)).fetchone()
        inventory = conn.execute('SELECT * FROM inventory ORDER BY item_description').fetchall()
    
    return render_template('add_recipe_ingredient.html', recipe=recipe, inventory=inventory)

@app.route('/recipes/<int:recipe_id>/ingredients/edit/<int:ingredient_id>', methods=['GET', 'POST'])
def edit_recipe_ingredient(recipe_id, ingredient_id):
    """Edit recipe ingredient"""
    if request.method == 'POST':
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get ingredient info for cost calculation
            ingredient = cursor.execute('SELECT * FROM inventory WHERE id = ?', 
                                      (request.form['ingredient_id'],)).fetchone()
            
            quantity = float(request.form['quantity'])
            unit = request.form.get('unit') or ingredient['unit_measure']
            
            # Calculate cost based on cost_per_recipe_unit
            cost = quantity * (ingredient['cost_per_recipe_unit'] or 0)
            
            # Update recipe ingredient
            cursor.execute('''
                UPDATE recipe_ingredients 
                SET ingredient_id = ?, quantity = ?, unit = ?, cost = ?
                WHERE id = ? AND recipe_id = ?
            ''', (request.form['ingredient_id'], quantity, unit, cost, 
                  ingredient_id, recipe_id))
            
            # Update recipe total cost
            cursor.execute('''
                UPDATE recipes 
                SET food_cost = (SELECT SUM(cost) FROM recipe_ingredients WHERE recipe_id = ?),
                    total_cost = (SELECT SUM(cost) FROM recipe_ingredients WHERE recipe_id = ?) + COALESCE(labor_cost, 0)
                WHERE id = ?
            ''', (recipe_id, recipe_id, recipe_id))
            
            conn.commit()
        
        return redirect(url_for('view_recipe', recipe_id=recipe_id))
    
    # Get recipe, ingredient, and inventory for form
    with get_db() as conn:
        recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,)).fetchone()
        ingredient = conn.execute('''
            SELECT ri.*, i.item_description 
            FROM recipe_ingredients ri
            JOIN inventory i ON ri.ingredient_id = i.id
            WHERE ri.id = ? AND ri.recipe_id = ?
        ''', (ingredient_id, recipe_id)).fetchone()
        inventory = conn.execute('SELECT * FROM inventory ORDER BY item_description').fetchall()
    
    if not ingredient:
        return redirect(url_for('view_recipe', recipe_id=recipe_id))
    
    return render_template('edit_recipe_ingredient.html', 
                         recipe=recipe, ingredient=ingredient, inventory=inventory)

@app.route('/menu')
def menu():
    """Menu management page with enhanced data"""
    with get_db() as conn:
        menu_items = conn.execute('''
            SELECT m.*, r.recipe_name, r.food_cost, r.recipe_group
            FROM menu_items m 
            LEFT JOIN recipes r ON m.recipe_id = r.id 
            ORDER BY m.menu_group, m.item_name
        ''').fetchall()
    return render_template('menu.html', menu_items=menu_items)

@app.route('/vendors')
def vendors():
    """Vendor management page"""
    with get_db() as conn:
        vendors = conn.execute('SELECT * FROM vendors ORDER BY vendor_name').fetchall()
    return render_template('vendors.html', vendors=vendors)

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    init_database()
    app.run(debug=True, host='0.0.0.0', port=8888)
