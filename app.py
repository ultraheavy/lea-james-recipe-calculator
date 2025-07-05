from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Support for production deployment
if os.getenv('FLASK_ENV') == 'production':
    # In production, use a persistent volume or local directory
    DATABASE = os.getenv('DATABASE_PATH', 'restaurant_calculator.db')
else:
    # In development, use local file
    DATABASE = 'restaurant_calculator.db'

# Set up auto-commit decorator (optional)
try:
    from auto_commit import integrate_with_flask
    with_auto_commit = integrate_with_flask(app)
except ImportError:
    # If auto_commit is not available, create a dummy decorator
    def with_auto_commit(func):
        return func

def import_production_data(conn):
    """Import production data if available and database is empty."""
    try:
        cursor = conn.cursor()
        
        # Check if we already have data
        cursor.execute('SELECT COUNT(*) FROM inventory')
        if cursor.fetchone()[0] > 0:
            print("Database already has data, skipping import")
            return  # Already has data
        
        # Check if production data file exists
        data_file = os.path.join('data', 'production_data.sql')
        if os.path.exists(data_file):
            print(f"Found production data file: {data_file}")
            with open(data_file, 'r') as f:
                sql_content = f.read()
                
            # Split by lines and execute each INSERT statement
            lines = sql_content.strip().split('\n')
            insert_count = 0
            
            for line in lines:
                line = line.strip()
                if line and line.startswith('INSERT INTO') and line.endswith(';'):
                    try:
                        cursor.execute(line)
                        insert_count += 1
                    except Exception as e:
                        print(f"Error executing line: {e}")
                        print(f"Problematic SQL: {line[:100]}...")
            
            conn.commit()
            print(f"Production data imported successfully! Inserted {insert_count} records.")
        else:
            print(f"No production data file found at: {data_file}")
    except Exception as e:
        print(f"Warning: Could not import production data: {e}")
        import traceback
        print(traceback.format_exc())
        # Don't raise - let the app continue with empty database

def init_database():
    """Initialize database with updated schema for Toast POS integration"""
    try:
        print(f"Database path: {DATABASE}")
        
        # Ensure database directory exists
        db_dir = os.path.dirname(DATABASE)
        if db_dir and not os.path.exists(db_dir):
            print(f"Creating database directory: {db_dir}")
            os.makedirs(db_dir, exist_ok=True)
            
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
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    density_g_per_ml DECIMAL(10,4),
                    count_to_weight_g DECIMAL(10,2)
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
                    canonical_quantity REAL,
                    canonical_unit TEXT,
                    conversion_status TEXT,
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
            
            # Add vendor products table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vendor_products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inventory_id INTEGER,
                    vendor_id INTEGER,
                    vendor_item_code TEXT,
                    vendor_price REAL,
                    last_purchased_date TEXT,
                    last_purchased_price REAL,
                    pack_size TEXT,
                    unit_measure TEXT,
                    is_primary BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (inventory_id) REFERENCES inventory (id),
                    FOREIGN KEY (vendor_id) REFERENCES vendors (id)
                )
            ''')
            
            # Add menu versions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS menu_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version_name TEXT NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT FALSE,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Update menu_items to include version_id
            cursor.execute('''
                PRAGMA table_info(menu_items)
            ''')
            columns = [col[1] for col in cursor.fetchall()]
            if 'version_id' not in columns:
                cursor.execute('''
                    ALTER TABLE menu_items ADD COLUMN version_id INTEGER DEFAULT 1
                ''')
            
            # Ensure at least one menu version exists
            cursor.execute('SELECT COUNT(*) FROM menu_versions')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO menu_versions (version_name, is_active) 
                    VALUES ('Current Menu', 1)
                ''')
            
            # Add units table for conversion system
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS units (
                    unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    symbol TEXT NOT NULL UNIQUE,
                    dimension TEXT NOT NULL,
                    to_canonical_factor REAL NOT NULL,
                    is_precise BOOLEAN DEFAULT TRUE,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Add ingredient densities table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ingredient_densities (
                    density_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ingredient_name TEXT NOT NULL UNIQUE,
                    density_g_per_ml REAL NOT NULL,
                    source TEXT,
                    notes TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_inventory_description ON inventory(item_description)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_recipes_name ON recipes(recipe_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe ON recipe_ingredients(recipe_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_menu_items_group ON menu_items(menu_group)')
            
            conn.commit()
            print("Database schema created successfully!")
            
            # Import production data if available and database is empty
            import_production_data(conn)
            
    except Exception as e:
        print(f"Database initialization error: {e}")
        import traceback
        print(traceback.format_exc())
        raise

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/health')
def health():
    """Health check endpoint for debugging"""
    try:
        with get_db() as conn:
            # Test database connection
            conn.execute('SELECT 1')
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            table_names = [t['name'] for t in tables]
            
        return jsonify({
            'status': 'healthy',
            'database': DATABASE,
            'tables': table_names,
            'table_count': len(table_names)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'database': DATABASE,
            'error': str(e)
        }), 500

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
    
    return render_template('index_modern.html', stats=stats)

@app.route('/inventory')
def inventory():
    with get_db() as conn:
        items = conn.execute('''
            SELECT i.* 
            FROM inventory i 
             
            ORDER BY i.item_code
        ''').fetchall()
    return render_template('inventory_modern.html', items=items)

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
                    recipe_cost_unit = ?, yield_percent = ?
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
                item_id
            ))
            conn.commit()
        
        return redirect(url_for('inventory'))
    
    # Get item data and vendors for form
    with get_db() as conn:
        item = conn.execute('SELECT * FROM inventory WHERE id = ?', (item_id,)).fetchone()
        vendors = conn.execute('SELECT DISTINCT vendor_name as name FROM vendors ORDER BY vendor_name').fetchall()
    
    if not item:
        return redirect(url_for('inventory'))
    
    return render_template('edit_inventory.html', item=item, vendors=vendors)

@app.route('/inventory/delete/<int:item_id>', methods=['POST'])
def delete_inventory(item_id):
    """Delete inventory item and its recipe ingredient references"""
    with get_db() as conn:
        # Check if item is used in any recipes
        usage_count = conn.execute('''
            SELECT COUNT(*) FROM recipe_ingredients WHERE ingredient_id = ?
        ''', (item_id,)).fetchone()[0]
        
        if usage_count > 0:
            # Item is in use, we'll remove it from recipes first
            conn.execute('DELETE FROM recipe_ingredients WHERE ingredient_id = ?', (item_id,))
        
        # Delete the inventory item
        conn.execute('DELETE FROM inventory WHERE id = ?', (item_id,))
        conn.commit()
    
    return redirect(url_for('inventory'))

@app.route('/inventory/vendors/<int:item_id>')
def inventory_vendors(item_id):
    """Manage vendors for an inventory item"""
    with get_db() as conn:
        # Get inventory item
        item = conn.execute('SELECT * FROM inventory WHERE id = ?', (item_id,)).fetchone()
        if not item:
            return "Item not found", 404
        
        # Get all vendors for dropdown
        vendors = conn.execute('SELECT * FROM vendors ORDER BY vendor_name').fetchall()
        
        # Get vendor products for this item
        vendor_products = conn.execute('''
            SELECT vp.*, v.vendor_name
            FROM vendor_products vp
            JOIN vendors v ON vp.vendor_id = v.id
            WHERE vp.inventory_id = ?
            ORDER BY vp.is_primary DESC, vp.is_active DESC, v.vendor_name
        ''', (item_id,)).fetchall()
    
    return render_template('inventory_vendors.html', 
                         item=item, 
                         vendors=vendors, 
                         vendor_products=vendor_products)

@app.route('/inventory/vendors/<int:item_id>/add', methods=['POST'])
def add_vendor_product(item_id):
    """Add a vendor product for an inventory item"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if this is the first vendor product for this item
        existing_count = cursor.execute('''
            SELECT COUNT(*) FROM vendor_products WHERE inventory_id = ?
        ''', (item_id,)).fetchone()[0]
        
        # Insert vendor product
        cursor.execute('''
            INSERT INTO vendor_products 
            (inventory_id, vendor_id, vendor_item_code, vendor_price, 
             pack_size, unit_measure, is_primary)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            item_id,
            request.form['vendor_id'],
            request.form['vendor_item_code'],
            float(request.form['vendor_price']),
            request.form.get('pack_size', ''),
            request.form.get('unit_measure', ''),
            existing_count == 0  # First vendor is primary by default
        ))
        
        conn.commit()
    
    return redirect(url_for('inventory_vendors', item_id=item_id))

@app.route('/inventory/vendors/<int:item_id>/set-primary/<int:vp_id>', methods=['POST'])
def set_primary_vendor(item_id, vp_id):
    """Set a vendor product as primary for an inventory item"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Remove primary flag from all vendor products for this item
        cursor.execute('''
            UPDATE vendor_products SET is_primary = 0 WHERE inventory_id = ?
        ''', (item_id,))
        
        # Set this vendor product as primary
        cursor.execute('''
            UPDATE vendor_products SET is_primary = 1 WHERE id = ?
        ''', (vp_id,))
        
        conn.commit()
    
    return redirect(url_for('inventory_vendors', item_id=item_id))

@app.route('/inventory/vendors/<int:item_id>/toggle-active/<int:vp_id>', methods=['POST'])
def toggle_vendor_active(item_id, vp_id):
    """Toggle active status of a vendor product"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Toggle active status
        cursor.execute('''
            UPDATE vendor_products 
            SET is_active = NOT is_active 
            WHERE id = ?
        ''', (vp_id,))
        
        conn.commit()
    
    return redirect(url_for('inventory_vendors', item_id=item_id))

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
    return render_template('recipes_modern.html', recipes=recipes)

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
            LEFT JOIN inventory i ON ri.ingredient_id = i.id 
            WHERE ri.recipe_id = ?
        ''', (recipe_id,)).fetchall()
    
    return render_template('view_recipe_modern.html', recipe=recipe, ingredients=ingredients)

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
            
            # Calculate cost based on current_price
            cost = quantity * (ingredient['current_price'] or 0)
            
            # Insert recipe ingredient
            cursor.execute('''
                INSERT INTO recipe_ingredients 
                (recipe_id, ingredient_id, ingredient_name, quantity, unit_of_measure, cost)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (recipe_id, request.form['ingredient_id'], ingredient['item_description'], 
                  quantity, unit, cost))
            
            # Update recipe total cost
            cursor.execute('''
                UPDATE recipes 
                SET food_cost = (SELECT SUM(cost) FROM recipe_ingredients WHERE recipe_id = ?),
                    prime_cost = (SELECT SUM(cost) FROM recipe_ingredients WHERE recipe_id = ?) + COALESCE(labor_cost, 0)
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
            
            # Calculate cost based on current_price
            cost = quantity * (ingredient['current_price'] or 0)
            
            # Update recipe ingredient
            cursor.execute('''
                UPDATE recipe_ingredients 
                SET ingredient_id = ?, ingredient_name = ?, quantity = ?, unit_of_measure = ?, cost = ?
                WHERE id = ? AND recipe_id = ?
            ''', (request.form['ingredient_id'], ingredient['item_description'], 
                  quantity, unit, cost, ingredient_id, recipe_id))
            
            # Update recipe total cost
            cursor.execute('''
                UPDATE recipes 
                SET food_cost = (SELECT SUM(cost) FROM recipe_ingredients WHERE recipe_id = ?),
                    prime_cost = (SELECT SUM(cost) FROM recipe_ingredients WHERE recipe_id = ?) + COALESCE(labor_cost, 0)
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

@app.route('/recipes/delete/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    """Delete recipe and all its ingredients"""
    with get_db() as conn:
        # Delete all recipe ingredients first
        conn.execute('DELETE FROM recipe_ingredients WHERE recipe_id = ?', (recipe_id,))
        
        # Delete the recipe
        conn.execute('DELETE FROM recipes WHERE id = ?', (recipe_id,))
        
        conn.commit()
    
    return redirect(url_for('recipes'))

@app.route('/menu')
def menu():
    """Menu management page with version support"""
    with get_db() as conn:
        # Get menu versions
        menu_versions = conn.execute('''
            SELECT * FROM menu_versions ORDER BY id
        ''').fetchall()
        
        # Get requested version or default to active version
        version_id = request.args.get('version_id', type=int)
        if not version_id:
            # Get active version
            active_version = conn.execute('''
                SELECT id FROM menu_versions WHERE is_active = 1 LIMIT 1
            ''').fetchone()
            version_id = active_version['id'] if active_version else 1
        
        # Get menu items for selected version
        menu_items = conn.execute('''
            SELECT m.*, r.recipe_name, r.food_cost, r.recipe_group
            FROM menu_items m 
            LEFT JOIN recipes r ON m.recipe_id = r.id 
            WHERE m.version_id = ?
            ORDER BY m.menu_group, m.item_name
        ''', (version_id,)).fetchall()
    
    return render_template('menu_modern.html', 
                         menu_items=menu_items,
                         menu_versions=menu_versions,
                         current_version_id=version_id)

@app.route('/menu/compare')
def menu_compare():
    """Compare menu versions side by side"""
    with get_db() as conn:
        # Get all menu versions
        menu_versions = conn.execute('SELECT * FROM menu_versions ORDER BY id').fetchall()
        
        # Get selected versions
        v1_id = request.args.get('v1', type=int, default=1)
        v2_id = request.args.get('v2', type=int, default=2)
        
        if v1_id and v2_id:
            # Get version names
            v1 = conn.execute('SELECT * FROM menu_versions WHERE id = ?', (v1_id,)).fetchone()
            v2 = conn.execute('SELECT * FROM menu_versions WHERE id = ?', (v2_id,)).fetchone()
            
            # Get all unique items from both versions
            all_items = conn.execute('''
                SELECT DISTINCT item_name, menu_group
                FROM menu_items
                WHERE version_id IN (?, ?)
                ORDER BY menu_group, item_name
            ''', (v1_id, v2_id)).fetchall()
            
            comparison_data = []
            for item in all_items:
                # Get data from version 1
                v1_data = conn.execute('''
                    SELECT * FROM menu_items 
                    WHERE item_name = ? AND version_id = ?
                ''', (item['item_name'], v1_id)).fetchone()
                
                # Get data from version 2
                v2_data = conn.execute('''
                    SELECT * FROM menu_items 
                    WHERE item_name = ? AND version_id = ?
                ''', (item['item_name'], v2_id)).fetchone()
                
                # Calculate changes
                price_change = None
                cost_change = None
                if v1_data and v2_data:
                    price_change = (v2_data['menu_price'] or 0) - (v1_data['menu_price'] or 0)
                    cost_change = (v2_data['food_cost'] or 0) - (v1_data['food_cost'] or 0)
                
                comparison_data.append({
                    'item_name': item['item_name'],
                    'menu_group': item['menu_group'],
                    'v1_data': v1_data,
                    'v2_data': v2_data,
                    'price_change': price_change,
                    'cost_change': cost_change
                })
            
            # Calculate summary statistics
            v1_items = [item for item in comparison_data if item['v1_data']]
            v2_items = [item for item in comparison_data if item['v2_data']]
            
            summary = {
                'v1_count': len(v1_items),
                'v2_count': len(v2_items),
                'v1_avg_price': sum(item['v1_data']['menu_price'] or 0 for item in v1_items) / len(v1_items) if v1_items else 0,
                'v2_avg_price': sum(item['v2_data']['menu_price'] or 0 for item in v2_items) / len(v2_items) if v2_items else 0,
                'v1_avg_cost_percent': sum(item['v1_data']['food_cost_percent'] or 0 for item in v1_items) / len(v1_items) if v1_items else 0,
                'v2_avg_cost_percent': sum(item['v2_data']['food_cost_percent'] or 0 for item in v2_items) / len(v2_items) if v2_items else 0,
                'items_added': len([item for item in comparison_data if not item['v1_data'] and item['v2_data']]),
                'items_removed': len([item for item in comparison_data if item['v1_data'] and not item['v2_data']]),
                'items_changed': len([item for item in comparison_data if item['v1_data'] and item['v2_data']])
            }
            
            return render_template('menu_compare.html',
                                 menu_versions=menu_versions,
                                 v1_id=v1_id,
                                 v2_id=v2_id,
                                 v1_name=v1['version_name'] if v1 else 'Version 1',
                                 v2_name=v2['version_name'] if v2 else 'Version 2',
                                 comparison_data=comparison_data,
                                 summary=summary)
        
        return render_template('menu_compare.html',
                             menu_versions=menu_versions,
                             v1_id=v1_id,
                             v2_id=v2_id)

@app.route('/pricing-analysis')
def pricing_analysis():
    """Pricing analysis and recommendations page"""
    with get_db() as conn:
        # Get menu versions
        menu_versions = conn.execute('SELECT * FROM menu_versions ORDER BY id').fetchall()
        
        # Get parameters
        target_food_cost = request.args.get('target_food_cost', type=float, default=30.0)
        version_id = request.args.get('version_id', type=int)
        
        if not version_id:
            # Get active version
            active_version = conn.execute('''
                SELECT id FROM menu_versions WHERE is_active = 1 LIMIT 1
            ''').fetchone()
            version_id = active_version['id'] if active_version else 1
        
        # Get menu items with recipe costs
        menu_items = conn.execute('''
            SELECT m.*, r.food_cost as recipe_food_cost
            FROM menu_items m 
            LEFT JOIN recipes r ON m.recipe_id = r.id 
            WHERE m.version_id = ? AND m.menu_price > 0
            ORDER BY m.menu_group, m.item_name
        ''', (version_id,)).fetchall()
        
        analysis_data = []
        total_items = 0
        items_above_target = 0
        items_below_target = 0
        total_price = 0
        total_food_cost_percent = 0
        items_needing_adjustment = 0
        total_price_increase = 0
        
        for item in menu_items:
            food_cost = item['food_cost'] or item['recipe_food_cost'] or 0
            menu_price = item['menu_price'] or 0
            
            if menu_price > 0:
                current_fc_percent = (food_cost / menu_price * 100) if menu_price > 0 else 0
                recommended_price = food_cost / (target_food_cost / 100) if target_food_cost > 0 else menu_price
                price_change = recommended_price - menu_price
                price_change_percent = (price_change / menu_price * 100) if menu_price > 0 else 0
                new_margin = recommended_price - food_cost
                needs_adjustment = current_fc_percent > target_food_cost
                
                analysis_data.append({
                    'id': item['id'],
                    'item_name': item['item_name'],
                    'menu_group': item['menu_group'],
                    'menu_price': menu_price,
                    'food_cost': food_cost,
                    'food_cost_percent': current_fc_percent,
                    'recommended_price': recommended_price,
                    'price_change': price_change,
                    'price_change_percent': price_change_percent,
                    'new_margin': new_margin,
                    'needs_adjustment': needs_adjustment
                })
                
                # Summary calculations
                total_items += 1
                total_price += menu_price
                total_food_cost_percent += current_fc_percent
                
                if current_fc_percent > target_food_cost:
                    items_above_target += 1
                    items_needing_adjustment += 1
                    total_price_increase += price_change
                elif current_fc_percent < target_food_cost:
                    items_below_target += 1
        
        # Calculate summary
        summary = None
        if total_items > 0:
            summary = {
                'avg_food_cost_percent': total_food_cost_percent / total_items,
                'items_above_target': items_above_target,
                'items_below_target': items_below_target,
                'items_needing_adjustment': items_needing_adjustment,
                'avg_menu_price': total_price / total_items,
                'avg_price_increase': total_price_increase / items_needing_adjustment if items_needing_adjustment > 0 else 0,
                'total_revenue_impact': total_price_increase
            }
        
        return render_template('pricing_analysis_modern.html',
                             menu_versions=menu_versions,
                             current_version_id=version_id,
                             target_food_cost=target_food_cost,
                             analysis_data=analysis_data,
                             summary=summary)

@app.route('/vendors')
def vendors():
    """Vendor management page"""
    with get_db() as conn:
        vendors = conn.execute('SELECT * FROM vendors ORDER BY vendor_name').fetchall()
    return render_template('vendors.html', vendors=vendors)

# Error handlers for production
@app.errorhandler(404)
def not_found(error):
    return render_template('404_modern.html'), 404

@app.errorhandler(500)
def internal_error(error):
    import traceback
    app.logger.error(f"Internal error: {error}")
    app.logger.error(traceback.format_exc())
    return render_template('500_modern.html'), 500

@app.errorhandler(Exception)
def handle_exception(error):
    import traceback
    app.logger.error(f"Unhandled exception: {error}")
    app.logger.error(traceback.format_exc())
    return render_template('500_modern.html'), 500

# Initialize database on module load (for production)
# This ensures database is ready before any requests
print("Initializing database...")
os.makedirs('templates', exist_ok=True)

# Always initialize database when module loads
init_database()

if __name__ == '__main__':
    # Production mode
    if os.getenv('FLASK_ENV') == 'production':
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
    else:
        # Development mode
        app.run(debug=True, host='0.0.0.0', port=8888)