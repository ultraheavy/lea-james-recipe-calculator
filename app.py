from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response, flash
import sqlite3
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
from unit_converter import UnitConverter

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

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

def cleanup_duplicate_menus(conn):
    """One-time cleanup of duplicate menus in production"""
    try:
        cursor = conn.cursor()
        
        # Check for duplicates
        cursor.execute("""
            SELECT menu_name, COUNT(*) as count 
            FROM menus 
            GROUP BY menu_name 
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        
        if duplicates:
            print(f"Found duplicate menus, cleaning up...")
            
            for menu_name, count in duplicates:
                # Keep the first one (lowest ID) and delete the rest
                cursor.execute("""
                    DELETE FROM menus 
                    WHERE menu_name = ? 
                    AND id NOT IN (
                        SELECT MIN(id) 
                        FROM menus 
                        WHERE menu_name = ?
                    )
                """, (menu_name, menu_name))
            
            conn.commit()
            print("Duplicate menus cleaned up!")
    except Exception as e:
        print(f"Warning: Could not cleanup duplicate menus: {e}")

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
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    effective_date TEXT,
                    notes TEXT
                )
            ''')
            
            # Add menus table for menu management
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS menus (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    menu_name TEXT NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT FALSE,
                    sort_order INTEGER DEFAULT 0,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Add menu_menu_items junction table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS menu_menu_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    menu_id INTEGER NOT NULL,
                    menu_item_id INTEGER NOT NULL,
                    sort_order INTEGER DEFAULT 0,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (menu_id) REFERENCES menus (id) ON DELETE CASCADE,
                    FOREIGN KEY (menu_item_id) REFERENCES menu_items (id) ON DELETE CASCADE,
                    UNIQUE(menu_id, menu_item_id)
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
            
            # Check if database is empty (no production data to import)
            cursor.execute('SELECT COUNT(*) FROM inventory')
            inventory_empty = cursor.fetchone()[0] == 0
            
            # Ensure at least one menu version exists (only if no production data will be imported)
            cursor.execute('SELECT COUNT(*) FROM menu_versions')
            if cursor.fetchone()[0] == 0 and inventory_empty:
                cursor.execute('''
                    INSERT INTO menu_versions (version_name, is_active) 
                    VALUES ('Current Menu', 1)
                ''')
            
            # Ensure default menus exist (only if no production data will be imported)
            
            cursor.execute('SELECT COUNT(*) FROM menus')
            if cursor.fetchone()[0] == 0 and inventory_empty:
                # Only create default menus if database is truly empty (not being imported)
                cursor.execute('''
                    INSERT INTO menus (menu_name, description, is_active, sort_order) 
                    VALUES 
                    ('Master Menu', 'Complete list of all menu items', 1, 1),
                    ('Current Menu', 'Currently active menu', 1, 2),
                    ('Future Menu', 'Planned menu changes', 0, 3)
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
            
            # Add vendor_descriptions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vendor_descriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inventory_id INTEGER,
                    vendor_name TEXT,
                    vendor_description TEXT,
                    item_code TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (inventory_id) REFERENCES inventory (id),
                    UNIQUE(inventory_id, vendor_name)
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
            
            # Clean up any duplicate menus that might exist
            cleanup_duplicate_menus(conn)
            
    except Exception as e:
        print(f"Database initialization error: {e}")
        import traceback
        print(traceback.format_exc())
        raise

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_theme():
    """Get the current theme from cookies or query parameter"""
    theme = request.args.get('theme') or request.cookies.get('theme', 'modern')
    return theme if theme in ['modern', 'neo', 'fam'] else 'modern'

def ensure_master_menu_assignment(conn, menu_item_id):
    """Ensure a menu item is assigned to the Master Menu"""
    cursor = conn.cursor()
    
    # Get Master Menu ID
    cursor.execute("SELECT id FROM menus WHERE menu_name = 'Master Menu'")
    result = cursor.fetchone()
    if not result:
        return False
    
    master_menu_id = result[0]
    
    # Check if already assigned
    cursor.execute("""
        SELECT id FROM menu_menu_items 
        WHERE menu_id = ? AND menu_item_id = ?
    """, (master_menu_id, menu_item_id))
    
    if not cursor.fetchone():
        # Add to Master Menu
        cursor.execute("""
            INSERT INTO menu_menu_items (menu_id, menu_item_id, sort_order)
            VALUES (?, ?, 0)
        """, (master_menu_id, menu_item_id))
    
    return True

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

@app.route('/set-theme/<theme>')
def set_theme(theme):
    """Set the UI theme"""
    if theme not in ['modern', 'neo', 'fam']:
        theme = 'modern'
    
    response = make_response(redirect(request.referrer or '/'))
    response.set_cookie('theme', theme, max_age=60*60*24*365)  # 1 year
    return response

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
    
    theme = get_theme()
    return render_template(f'index_{theme}.html', stats=stats)

@app.route('/inventory')
def inventory():
    with get_db() as conn:
        items = conn.execute('''
            SELECT i.*, 
                   v.vendor_name as primary_vendor_name,
                   vp.vendor_item_code,
                   vp.vendor_price as vendor_current_price,
                   vd.vendor_description
            FROM inventory i 
            LEFT JOIN vendor_products vp ON i.id = vp.inventory_id AND vp.is_primary = 1
            LEFT JOIN vendors v ON vp.vendor_id = v.id
            LEFT JOIN vendor_descriptions vd ON i.id = vd.inventory_id AND (vd.vendor_name = v.vendor_name OR vd.vendor_name = i.vendor_name)
            ORDER BY i.item_description
        ''').fetchall()
    theme = get_theme()
    return render_template(f'inventory_{theme}.html', items=items)

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
    
    theme = get_theme()
    return render_template(f'add_inventory_{theme}.html', vendors=vendors)

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
        item = conn.execute('''
            SELECT i.*, 
                   COUNT(DISTINCT ri.recipe_id) as recipe_count
            FROM inventory i
            LEFT JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
            WHERE i.id = ?
            GROUP BY i.id
        ''', (item_id,)).fetchone()
        vendors = conn.execute('SELECT DISTINCT vendor_name as name FROM vendors ORDER BY vendor_name').fetchall()
    
    if not item:
        return redirect(url_for('inventory'))
    
    theme = get_theme()
    return render_template(f'edit_inventory_{theme}.html', item=item, vendors=vendors)

@app.route('/inventory/delete/<int:item_id>', methods=['POST'])
def delete_inventory(item_id):
    """Delete inventory item and recalculate affected recipe costs"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Find which recipes will be affected BEFORE deleting
        affected_recipes = cursor.execute('''
            SELECT DISTINCT recipe_id FROM recipe_ingredients WHERE ingredient_id = ?
        ''', (item_id,)).fetchall()
        
        # Delete the ingredient from all recipes
        cursor.execute('DELETE FROM recipe_ingredients WHERE ingredient_id = ?', (item_id,))
        
        # Delete vendor products for this item
        cursor.execute('DELETE FROM vendor_products WHERE inventory_id = ?', (item_id,))
        
        # Delete the inventory item itself
        cursor.execute('DELETE FROM inventory WHERE id = ?', (item_id,))
        
        # Recalculate costs for all affected recipes
        for row in affected_recipes:
            recipe_id = row['recipe_id']
            cursor.execute('''
                UPDATE recipes 
                SET food_cost = (SELECT COALESCE(SUM(cost), 0) FROM recipe_ingredients WHERE recipe_id = ?),
                    prime_cost = (SELECT COALESCE(SUM(cost), 0) FROM recipe_ingredients WHERE recipe_id = ?) + COALESCE(labor_cost, 0)
                WHERE id = ?
            ''', (recipe_id, recipe_id, recipe_id))
        
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
    
    theme = get_theme()
    return render_template(f'inventory_vendors_{theme}.html', 
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
    theme = get_theme()
    return render_template(f'recipes_{theme}.html', recipes=recipes)

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
    
    # Get unique inventory items for dropdown
    with get_db() as conn:
        inventory = conn.execute('''
            WITH RankedInventory AS (
                SELECT *,
                    ROW_NUMBER() OVER (
                        PARTITION BY item_description 
                        ORDER BY 
                            CASE WHEN last_purchased_date IS NOT NULL THEN 1 ELSE 2 END,
                            last_purchased_date DESC,
                            current_price DESC
                    ) as rn
                FROM inventory
            )
            SELECT * FROM RankedInventory 
            WHERE rn = 1
            ORDER BY item_description
        ''').fetchall()
    
    theme = get_theme()
    return render_template(f'add_recipe_{theme}.html', inventory=inventory)

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
    
    theme = get_theme()
    return render_template(f'view_recipe_{theme}.html', recipe=recipe, ingredients=ingredients)

@app.route('/recipes/<int:recipe_id>/edit', methods=['GET', 'POST'])
@with_auto_commit
def edit_recipe(recipe_id):
    """Edit recipe details"""
    if request.method == 'POST':
        # Get form data
        recipe_name = request.form.get('recipe_name', '').strip()
        recipe_group = request.form.get('recipe_group', '').strip()
        recipe_type = request.form.get('recipe_type', 'Recipe')
        menu_price = float(request.form.get('menu_price', 0) or 0)
        status = request.form.get('status', 'Draft')
        shelf_life = request.form.get('shelf_life', '').strip()
        shelf_life_uom = request.form.get('shelf_life_uom', '').strip()
        serving_size = request.form.get('serving_size', '').strip()
        serving_size_uom = request.form.get('serving_size_uom', '').strip()
        prep_recipe_yield = request.form.get('prep_recipe_yield', '').strip()
        prep_recipe_yield_uom = request.form.get('prep_recipe_yield_uom', '').strip()
        station = request.form.get('station', '').strip()
        procedure = request.form.get('procedure', '').strip()
        
        # Validate required fields
        if not recipe_name:
            flash('Recipe name is required', 'error')
            return redirect(url_for('edit_recipe', recipe_id=recipe_id))
        
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                
                # Update recipe
                cursor.execute('''
                    UPDATE recipes 
                    SET recipe_name = ?, recipe_group = ?, recipe_type = ?, 
                        menu_price = ?, status = ?, shelf_life = ?, shelf_life_uom = ?,
                        serving_size = ?, serving_size_uom = ?, 
                        prep_recipe_yield = ?, prep_recipe_yield_uom = ?,
                        station = ?, procedure = ?,
                        updated_date = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (recipe_name, recipe_group, recipe_type, menu_price, 
                      status, shelf_life, shelf_life_uom, serving_size, serving_size_uom,
                      prep_recipe_yield, prep_recipe_yield_uom, station, procedure, recipe_id))
                
                # Recalculate food cost and percentages
                food_cost = cursor.execute('''
                    SELECT SUM(ri.cost) 
                    FROM recipe_ingredients ri 
                    WHERE ri.recipe_id = ?
                ''', (recipe_id,)).fetchone()[0] or 0
                
                food_cost_percentage = (food_cost / menu_price * 100) if menu_price > 0 else 0
                gross_margin = menu_price - food_cost if menu_price > 0 else 0
                
                cursor.execute('''
                    UPDATE recipes 
                    SET food_cost = ?, food_cost_percentage = ?, gross_margin = ?
                    WHERE id = ?
                ''', (food_cost, food_cost_percentage, gross_margin, recipe_id))
                
                # flash('Recipe updated successfully!', 'success')
                return redirect(url_for('view_recipe', recipe_id=recipe_id))
                
        except Exception as e:
            # flash(f'Error updating recipe: {str(e)}', 'error')
            print(f'Error updating recipe: {str(e)}')
            return redirect(url_for('edit_recipe', recipe_id=recipe_id))
    
    # GET request - display edit form
    with get_db() as conn:
        recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,)).fetchone()
        
        if not recipe:
            flash('Recipe not found', 'error')
            return redirect(url_for('recipes'))
        
        # Get recipe ingredients
        recipe_ingredients = conn.execute('''
            SELECT ri.*, i.item_description, i.current_price as unit_price
            FROM recipe_ingredients ri
            LEFT JOIN inventory i ON ri.ingredient_id = i.id
            WHERE ri.recipe_id = ?
            ORDER BY ri.ingredient_name
        ''', (recipe_id,)).fetchall()
        
        # Get menu items that use this recipe
        menu_usage = conn.execute('''
            SELECT mi.id, mi.item_name, mi.menu_price, mv.version_name, mv.is_active
            FROM menu_items mi
            LEFT JOIN menu_versions mv ON mi.version_id = mv.id
            WHERE mi.recipe_id = ?
            ORDER BY mv.is_active DESC, mv.version_name
        ''', (recipe_id,)).fetchall()
    
    theme = get_theme()
    return render_template(f'edit_recipe_{theme}.html', 
                         recipe=recipe, 
                         recipe_ingredients=recipe_ingredients,
                         menu_usage=menu_usage)

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
            
            # Calculate cost using proper unit conversion
            converter = UnitConverter(DATABASE)
            cost = converter.calculate_ingredient_cost(
                dict(ingredient),  # Convert Row to dict
                quantity,
                unit
            )
            
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
    
    # Get recipe and inventory for form - show unique ingredients only
    with get_db() as conn:
        recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,)).fetchone()
        # Get unique ingredients, preferring items with the most recent purchase
        inventory = conn.execute('''
            WITH RankedInventory AS (
                SELECT *,
                    ROW_NUMBER() OVER (
                        PARTITION BY item_description 
                        ORDER BY 
                            CASE WHEN last_purchased_date IS NOT NULL THEN 1 ELSE 2 END,
                            last_purchased_date DESC,
                            current_price DESC
                    ) as rn
                FROM inventory
            )
            SELECT * FROM RankedInventory 
            WHERE rn = 1
            ORDER BY item_description
        ''').fetchall()
    
    theme = get_theme()
    return render_template(f'add_recipe_ingredient_{theme}.html', recipe=recipe, inventory=inventory)

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
            
            # Calculate cost using proper unit conversion
            converter = UnitConverter(DATABASE)
            cost = converter.calculate_ingredient_cost(
                dict(ingredient),  # Convert Row to dict
                quantity,
                unit
            )
            
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
        # Get unique inventory items
        inventory = conn.execute('''
            WITH RankedInventory AS (
                SELECT *,
                    ROW_NUMBER() OVER (
                        PARTITION BY item_description 
                        ORDER BY 
                            CASE WHEN last_purchased_date IS NOT NULL THEN 1 ELSE 2 END,
                            last_purchased_date DESC,
                            current_price DESC
                    ) as rn
                FROM inventory
            )
            SELECT * FROM RankedInventory 
            WHERE rn = 1
            ORDER BY item_description
        ''').fetchall()
    
    if not ingredient:
        return redirect(url_for('view_recipe', recipe_id=recipe_id))
    
    theme = get_theme()
    return render_template(f'edit_recipe_ingredient_{theme}.html', 
                         recipe=recipe, ingredient=ingredient, inventory=inventory)

@app.route('/recipes/<int:recipe_id>/ingredients/delete/<int:ingredient_id>', methods=['POST'])
@with_auto_commit
def delete_recipe_ingredient(recipe_id, ingredient_id):
    """Delete an ingredient from a recipe"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Delete the ingredient
        cursor.execute('''
            DELETE FROM recipe_ingredients 
            WHERE id = ? AND recipe_id = ?
        ''', (ingredient_id, recipe_id))
        
        # Update recipe total cost
        cursor.execute('''
            UPDATE recipes 
            SET food_cost = COALESCE((SELECT SUM(cost) FROM recipe_ingredients WHERE recipe_id = ?), 0),
                prime_cost = COALESCE((SELECT SUM(cost) FROM recipe_ingredients WHERE recipe_id = ?), 0) + COALESCE(labor_cost, 0)
            WHERE id = ?
        ''', (recipe_id, recipe_id, recipe_id))
        
        conn.commit()
        flash('Ingredient removed successfully!', 'success')
    
    return redirect(url_for('view_recipe', recipe_id=recipe_id))

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
    
    theme = get_theme()
    return render_template(f'menu_{theme}.html', 
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
        export_format = request.args.get('export')
        
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
                price_change = 0
                fc_change = 0
                if v1_data and v2_data:
                    price_change = (v2_data['menu_price'] or 0) - (v1_data['menu_price'] or 0)
                    # Calculate food cost percentage change
                    v1_fc_pct = ((v1_data['food_cost'] or 0) / (v1_data['menu_price'] or 1) * 100) if v1_data['menu_price'] else 0
                    v2_fc_pct = ((v2_data['food_cost'] or 0) / (v2_data['menu_price'] or 1) * 100) if v2_data['menu_price'] else 0
                    fc_change = v2_fc_pct - v1_fc_pct
                
                comparison_data.append({
                    'item_name': item['item_name'],
                    'menu_group': item['menu_group'],
                    'v1_data': v1_data,
                    'v2_data': v2_data,
                    'price_change': price_change,
                    'fc_change': fc_change
                })
            
            # Calculate summary statistics
            v1_items = [item for item in comparison_data if item['v1_data']]
            v2_items = [item for item in comparison_data if item['v2_data']]
            
            # Calculate v1 stats
            v1_stats = {
                'total_items': len(v1_items),
                'avg_price': sum(item['v1_data']['menu_price'] or 0 for item in v1_items) / len(v1_items) if v1_items else 0,
                'avg_food_cost_pct': sum(((item['v1_data']['food_cost'] or 0) / (item['v1_data']['menu_price'] or 1) * 100) if item['v1_data']['menu_price'] else 0 for item in v1_items) / len(v1_items) if v1_items else 0
            }
            
            # Calculate v2 stats
            v2_stats = {
                'total_items': len(v2_items),
                'avg_price': sum(item['v2_data']['menu_price'] or 0 for item in v2_items) / len(v2_items) if v2_items else 0,
                'avg_food_cost_pct': sum(((item['v2_data']['food_cost'] or 0) / (item['v2_data']['menu_price'] or 1) * 100) if item['v2_data']['menu_price'] else 0 for item in v2_items) / len(v2_items) if v2_items else 0
            }
            
            # Calculate comparison stats
            new_items = [item for item in comparison_data if not item['v1_data'] and item['v2_data']]
            removed_items = [item for item in comparison_data if item['v1_data'] and not item['v2_data']]
            changed_items = [item for item in comparison_data if item['v1_data'] and item['v2_data'] and item['price_change'] != 0]
            common_items = [item for item in comparison_data if item['v1_data'] and item['v2_data'] and item['price_change'] == 0]
            
            total_price_change = sum(item['price_change'] for item in comparison_data if item['price_change'])
            margin_impact = v2_stats['avg_food_cost_pct'] - v1_stats['avg_food_cost_pct']
            
            stats = {
                'new_items': len(new_items),
                'removed_items': len(removed_items),
                'price_changes': len(changed_items),
                'common_items': len(common_items),
                'total_price_change': total_price_change,
                'margin_impact': margin_impact
            }
            
            # Handle CSV export
            if export_format == 'csv':
                import csv
                from io import StringIO
                
                output = StringIO()
                writer = csv.writer(output)
                
                # Write headers
                writer.writerow([
                    'Item Name', 'Menu Group',
                    f'{v1["version_name"]} Price', f'{v1["version_name"]} Cost', f'{v1["version_name"]} FC%',
                    f'{v2["version_name"]} Price', f'{v2["version_name"]} Cost', f'{v2["version_name"]} FC%',
                    'Price Change', 'FC% Change', 'Status'
                ])
                
                # Write data
                for item in comparison_data:
                    status = 'Unchanged'
                    if not item['v1_data']:
                        status = 'New'
                    elif not item['v2_data']:
                        status = 'Removed'
                    elif item['price_change'] != 0:
                        status = 'Changed'
                    
                    v1_price = item['v1_data']['menu_price'] if item['v1_data'] else ''
                    v1_cost = item['v1_data']['food_cost'] if item['v1_data'] else ''
                    v1_fc_pct = ((v1_cost / v1_price * 100) if v1_price and v1_cost else '') if item['v1_data'] else ''
                    
                    v2_price = item['v2_data']['menu_price'] if item['v2_data'] else ''
                    v2_cost = item['v2_data']['food_cost'] if item['v2_data'] else ''
                    v2_fc_pct = ((v2_cost / v2_price * 100) if v2_price and v2_cost else '') if item['v2_data'] else ''
                    
                    writer.writerow([
                        item['item_name'], item['menu_group'],
                        v1_price, v1_cost, f"{v1_fc_pct:.1f}%" if v1_fc_pct else '',
                        v2_price, v2_cost, f"{v2_fc_pct:.1f}%" if v2_fc_pct else '',
                        item['price_change'] if item['price_change'] else '',
                        f"{item['fc_change']:.1f}%" if item['fc_change'] else '',
                        status
                    ])
                
                # Create response
                response = make_response(output.getvalue())
                response.headers['Content-Disposition'] = f'attachment; filename=menu_comparison_{v1_id}_vs_{v2_id}.csv'
                response.headers['Content-Type'] = 'text/csv'
                return response
            
            theme = get_theme()
            return render_template(f'menu_compare_{theme}.html',
                                 menu_versions=menu_versions,
                                 v1_id=v1_id,
                                 v2_id=v2_id,
                                 v1=v1,
                                 v2=v2,
                                 v1_stats=v1_stats,
                                 v2_stats=v2_stats,
                                 stats=stats,
                                 comparison_data=comparison_data)
        
        theme = get_theme()
        return render_template(f'menu_compare_{theme}.html',
                             menu_versions=menu_versions,
                             v1_id=v1_id,
                             v2_id=v2_id)

@app.route('/menu/versions')
def menu_versions_page():
    """Manage menu versions"""
    with get_db() as conn:
        versions = conn.execute('''
            SELECT mv.*, 
                   COUNT(mi.id) as item_count,
                   SUM(mi.menu_price) as total_revenue
            FROM menu_versions mv
            LEFT JOIN menu_items mi ON mv.id = mi.version_id
            GROUP BY mv.id
            ORDER BY mv.id
        ''').fetchall()
    
    theme = get_theme()
    return render_template(f'menu_versions_{theme}.html', versions=versions)

@app.route('/menu/versions/add', methods=['GET', 'POST'])
def add_menu_version():
    """Create a new menu version"""
    if request.method == 'POST':
        with get_db() as conn:
            cursor = conn.cursor()
            
            version_name = request.form['version_name']
            description = request.form.get('description', '')
            is_active = request.form.get('is_active') == 'on'
            effective_date = request.form.get('effective_date', '')
            notes = request.form.get('notes', '')
            
            # If setting as active, deactivate all others
            if is_active:
                cursor.execute('UPDATE menu_versions SET is_active = 0')
            
            cursor.execute('''
                INSERT INTO menu_versions 
                (version_name, description, is_active, effective_date, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (version_name, description, is_active, effective_date, notes))
            
            conn.commit()
            
        return redirect(url_for('menu_versions_page'))
    
    theme = get_theme()
    return render_template(f'add_menu_version_{theme}.html')

@app.route('/menu/versions/edit/<int:version_id>', methods=['GET', 'POST'])
def edit_menu_version(version_id):
    """Edit a menu version"""
    if request.method == 'POST':
        with get_db() as conn:
            cursor = conn.cursor()
            
            version_name = request.form['version_name']
            description = request.form.get('description', '')
            is_active = request.form.get('is_active') == 'on'
            effective_date = request.form.get('effective_date', '')
            notes = request.form.get('notes', '')
            
            # If setting as active, deactivate all others
            if is_active:
                cursor.execute('UPDATE menu_versions SET is_active = 0')
            
            cursor.execute('''
                UPDATE menu_versions 
                SET version_name = ?, description = ?, is_active = ?, 
                    effective_date = ?, notes = ?
                WHERE id = ?
            ''', (version_name, description, is_active, effective_date, notes, version_id))
            
            conn.commit()
            
        return redirect(url_for('menu_versions_page'))
    
    with get_db() as conn:
        version = conn.execute('SELECT * FROM menu_versions WHERE id = ?', (version_id,)).fetchone()
    
    theme = get_theme()
    return render_template(f'edit_menu_version_{theme}.html', version=version)

@app.route('/menu/versions/delete/<int:version_id>', methods=['POST'])
def delete_menu_version(version_id):
    """Delete a menu version and all its items"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Don't delete if it's the only version or master list
        if version_id == 0:
            return jsonify({'error': 'Cannot delete the Master List'}), 400
            
        version_count = cursor.execute('SELECT COUNT(*) FROM menu_versions').fetchone()[0]
        if version_count <= 2:  # Master + 1 other
            return jsonify({'error': 'Cannot delete the last menu version'}), 400
        
        # Delete all menu items for this version
        cursor.execute('DELETE FROM menu_items WHERE version_id = ?', (version_id,))
        
        # Delete the version
        cursor.execute('DELETE FROM menu_versions WHERE id = ?', (version_id,))
        
        conn.commit()
    
    return redirect(url_for('menu_versions_page'))

@app.route('/menu/items/add', methods=['GET', 'POST'])
def add_menu_item():
    """Add a recipe to menu(s)"""
    if request.method == 'POST':
        with get_db() as conn:
            cursor = conn.cursor()
            
            recipe_id = request.form['recipe_id']
            menu_price = float(request.form['menu_price'])
            menu_group = request.form['menu_group']
            item_description = request.form.get('item_description', '')
            serving_size = request.form.get('serving_size', '')
            
            # Get recipe details
            recipe = cursor.execute('''
                SELECT recipe_name, food_cost 
                FROM recipes WHERE id = ?
            ''', (recipe_id,)).fetchone()
            
            # Calculate food cost percentage
            food_cost = recipe['food_cost'] or 0
            food_cost_percent = (food_cost / menu_price * 100) if menu_price > 0 else 0
            gross_profit = menu_price - food_cost
            
            # Get selected menu versions
            version_ids = request.form.getlist('version_ids')
            
            # Add to each selected menu version
            for version_id in version_ids:
                # Check if already exists
                exists = cursor.execute('''
                    SELECT id FROM menu_items 
                    WHERE recipe_id = ? AND version_id = ?
                ''', (recipe_id, version_id)).fetchone()
                
                if not exists:
                    cursor.execute('''
                        INSERT INTO menu_items 
                        (item_name, menu_group, item_description, recipe_id, 
                         menu_price, food_cost, food_cost_percent, gross_profit, 
                         serving_size, version_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (recipe['recipe_name'], menu_group, item_description, 
                          recipe_id, menu_price, food_cost, food_cost_percent, 
                          gross_profit, serving_size, version_id))
                    
                    # Ensure new item is added to Master Menu
                    new_item_id = cursor.lastrowid
                    ensure_master_menu_assignment(conn, new_item_id)
            
            conn.commit()
        
        return redirect(url_for('menu'))
    
    # GET request - show form
    with get_db() as conn:
        # Get all recipes
        recipes = conn.execute('''
            SELECT r.* 
            FROM recipes r
            ORDER BY r.recipe_name
        ''').fetchall()
        
        menu_versions = conn.execute('''
            SELECT * FROM menu_versions ORDER BY id
        ''').fetchall()
    
    theme = get_theme()
    return render_template(f'add_menu_item_{theme}.html', 
                         recipes=recipes, 
                         menu_versions=menu_versions)

@app.route('/menu/items/edit/<int:item_id>', methods=['GET', 'POST'])
@with_auto_commit
def edit_menu_item(item_id):
    """Edit a menu item"""
    if request.method == 'POST':
        with get_db() as conn:
            cursor = conn.cursor()
            
            menu_price = float(request.form['menu_price'])
            menu_group = request.form['menu_group']
            item_description = request.form.get('item_description', '')
            serving_size = request.form.get('serving_size', '')
            status = request.form.get('status', 'Active')
            recipe_id = request.form.get('recipe_id')  # Now changeable and optional
            recipe_id = int(recipe_id) if recipe_id else None
            selected_versions = request.form.getlist('version_ids')  # Multiple versions
            
            # Get the current menu item details
            current_item = cursor.execute('''
                SELECT * FROM menu_items WHERE id = ?
            ''', (item_id,)).fetchone()
            
            # Get the new recipe's food cost (if recipe selected)
            if recipe_id:
                recipe = cursor.execute('''
                    SELECT food_cost FROM recipes WHERE id = ?
                ''', (recipe_id,)).fetchone()
                food_cost = recipe['food_cost'] or 0
            else:
                food_cost = 0
            food_cost_percent = (food_cost / menu_price * 100) if menu_price > 0 else 0
            gross_profit = menu_price - food_cost
            
            # Update the existing menu item with new values
            cursor.execute('''
                UPDATE menu_items 
                SET menu_price = ?, menu_group = ?, item_description = ?,
                    serving_size = ?, status = ?, food_cost_percent = ?,
                    gross_profit = ?, recipe_id = ?, food_cost = ?,
                    updated_date = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (menu_price, menu_group, item_description, serving_size, 
                  status, food_cost_percent, gross_profit, recipe_id, food_cost, item_id))
            
            # Handle multi-version assignment
            # If no versions selected, keep the current item but update it
            if not selected_versions:
                # Just update the current item, don't delete it
                pass
            else:
                # First, get all current versions this item belongs to
                if current_item['recipe_id']:
                    current_versions = cursor.execute('''
                        SELECT version_id FROM menu_items 
                        WHERE item_name = ? AND recipe_id = ?
                    ''', (current_item['item_name'], current_item['recipe_id'])).fetchall()
                else:
                    current_versions = cursor.execute('''
                        SELECT version_id FROM menu_items 
                        WHERE item_name = ? AND recipe_id IS NULL
                    ''', (current_item['item_name'],)).fetchall()
                    
                current_version_ids = [v['version_id'] for v in current_versions]
                
                # Add to new versions if not already present
                for version_id in selected_versions:
                    version_id = int(version_id)
                    if version_id not in current_version_ids:
                        # Check if another item with this recipe already exists in this version
                        if recipe_id:
                            existing = cursor.execute('''
                                SELECT id FROM menu_items 
                                WHERE recipe_id = ? AND version_id = ?
                            ''', (recipe_id, version_id)).fetchone()
                        else:
                            existing = None  # No recipe, no conflict possible
                        
                        if not existing:
                            cursor.execute('''
                                INSERT INTO menu_items (
                                    item_name, recipe_id, menu_price, menu_group,
                                    food_cost, food_cost_percent, gross_profit,
                                    item_description, serving_size, status, version_id
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (current_item['item_name'], recipe_id, menu_price, menu_group,
                                  food_cost, food_cost_percent, gross_profit,
                                  item_description, serving_size, status, version_id))
                            
                            # Ensure new item is added to Master Menu
                            new_item_id = cursor.lastrowid
                            ensure_master_menu_assignment(conn, new_item_id)
                
                # Remove from versions not selected
                for v_id in current_version_ids:
                    if str(v_id) not in selected_versions:
                        # If this is the item we're editing, don't delete it, just update it
                        if v_id != current_item['version_id']:
                            if current_item['recipe_id']:
                                cursor.execute('''
                                    DELETE FROM menu_items 
                                    WHERE item_name = ? AND recipe_id = ? AND version_id = ?
                                ''', (current_item['item_name'], current_item['recipe_id'], v_id))
                            else:
                                cursor.execute('''
                                    DELETE FROM menu_items 
                                    WHERE item_name = ? AND recipe_id IS NULL AND version_id = ?
                                ''', (current_item['item_name'], v_id))
            
            conn.commit()
        
        return redirect(url_for('menu'))
    
    # GET request
    with get_db() as conn:
        item = conn.execute('''
            SELECT mi.*, r.recipe_name, r.food_cost as recipe_food_cost, r.status as recipe_status, mv.version_name
            FROM menu_items mi
            LEFT JOIN recipes r ON mi.recipe_id = r.id
            JOIN menu_versions mv ON mi.version_id = mv.id
            WHERE mi.id = ?
        ''', (item_id,)).fetchone()
        
        # Get all available recipes
        recipes = conn.execute('''
            SELECT id, recipe_name, food_cost, recipe_group
            FROM recipes
            ORDER BY recipe_name
        ''').fetchall()
        
        # Get all menu versions
        menu_versions = conn.execute('''
            SELECT id, version_name, is_active
            FROM menu_versions
            ORDER BY id
        ''').fetchall()
        
        # Get current versions this item belongs to
        current_versions = conn.execute('''
            SELECT version_id FROM menu_items 
            WHERE item_name = ? AND recipe_id = ?
        ''', (item['item_name'], item['recipe_id'])).fetchall()
        current_version_ids = [v['version_id'] for v in current_versions]
    
    theme = get_theme()
    return render_template(f'edit_menu_item_{theme}.html', 
                         item=item, 
                         recipes=recipes,
                         menu_versions=menu_versions,
                         current_version_ids=current_version_ids)

@app.route('/menu/items/delete/<int:item_id>', methods=['POST'])
def delete_menu_item(item_id):
    """Remove item from menu"""
    with get_db() as conn:
        conn.execute('DELETE FROM menu_items WHERE id = ?', (item_id,))
        conn.commit()
    
    return redirect(url_for('menu'))

@app.route('/menu/items/copy/<int:item_id>', methods=['POST'])
def copy_menu_item(item_id):
    """Copy a menu item to other menu versions"""
    version_ids = request.form.getlist('version_ids')
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get the item to copy
        item = cursor.execute('''
            SELECT * FROM menu_items WHERE id = ?
        ''', (item_id,)).fetchone()
        
        if item:
            # Copy to each selected version
            for version_id in version_ids:
                # Check if already exists
                exists = cursor.execute('''
                    SELECT id FROM menu_items 
                    WHERE recipe_id = ? AND version_id = ?
                ''', (item['recipe_id'], version_id)).fetchone()
                
                if not exists:
                    cursor.execute('''
                        INSERT INTO menu_items 
                        (item_name, menu_group, item_description, recipe_id,
                         menu_price, food_cost, food_cost_percent, gross_profit,
                         status, serving_size, version_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (item['item_name'], item['menu_group'], 
                          item['item_description'], item['recipe_id'],
                          item['menu_price'], item['food_cost'], 
                          item['food_cost_percent'], item['gross_profit'],
                          item['status'], item['serving_size'], version_id))
                    
                    # Ensure new item is added to Master Menu
                    new_item_id = cursor.lastrowid
                    ensure_master_menu_assignment(conn, new_item_id)
            
            conn.commit()
    
    return redirect(url_for('menu'))

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
        
        theme = get_theme()
        return render_template(f'pricing_analysis_{theme}.html',
                             menu_versions=menu_versions,
                             current_version_id=version_id,
                             target_food_cost=target_food_cost,
                             analysis_data=analysis_data,
                             summary=summary)

@app.route('/vendors')
def vendors():
    """Vendor management page"""
    with get_db() as conn:
        # Get vendors with product counts
        vendors = conn.execute('''
            SELECT v.*, 
                   COUNT(DISTINCT vp.inventory_id) as product_count,
                   COUNT(DISTINCT CASE WHEN vp.is_active = 1 THEN vp.inventory_id END) as active_product_count
            FROM vendors v
            LEFT JOIN vendor_products vp ON v.id = vp.vendor_id
            GROUP BY v.id
            ORDER BY v.vendor_name
        ''').fetchall()
        
        # Get top products for each vendor
        vendor_top_products = {}
        for vendor in vendors:
            if vendor['product_count'] > 0:
                top_products = conn.execute('''
                    SELECT i.item_description
                    FROM vendor_products vp
                    JOIN inventory i ON vp.inventory_id = i.id
                    WHERE vp.vendor_id = ? AND vp.is_active = 1
                    ORDER BY vp.is_primary DESC, i.item_description
                    LIMIT 3
                ''', (vendor['id'],)).fetchall()
                vendor_top_products[vendor['id']] = [p['item_description'] for p in top_products]
        
    theme = get_theme()
    # Use base template name for modern theme
    template_name = 'vendors.html' if theme == 'modern' else f'vendors_{theme}.html'
    return render_template(template_name, vendors=vendors, vendor_top_products=vendor_top_products)

@app.route('/vendors/<int:vendor_id>')
def vendor_detail(vendor_id):
    """Show detailed vendor information and their products"""
    with get_db() as conn:
        # Get vendor info
        vendor = conn.execute('SELECT * FROM vendors WHERE id = ?', (vendor_id,)).fetchone()
        if not vendor:
            return render_template('404_modern.html'), 404
            
        # Get vendor's products
        products = conn.execute('''
            SELECT vp.*, i.item_description, i.item_code, i.product_categories,
                   i.current_price as inventory_price,
                   CASE WHEN vp.vendor_price IS NOT NULL 
                        THEN ((vp.vendor_price - i.current_price) / i.current_price * 100)
                        ELSE 0 
                   END as price_variance,
                   (SELECT COUNT(DISTINCT vendor_id) 
                    FROM vendor_products vp2 
                    WHERE vp2.inventory_id = vp.inventory_id) as vendor_count
            FROM vendor_products vp
            JOIN inventory i ON vp.inventory_id = i.id
            WHERE vp.vendor_id = ?
            ORDER BY vp.is_primary DESC, vp.is_active DESC, i.item_description
        ''', (vendor_id,)).fetchall()
        
    theme = get_theme()
    template_name = 'vendor_detail.html' if theme == 'modern' else f'vendor_detail_{theme}.html'
    return render_template(template_name, vendor=vendor, products=products)

# Menu Management Routes
@app.route('/menus')
def menus():
    """List all menus"""
    with get_db() as conn:
        menus = conn.execute('''
            SELECT m.*, 
                   COUNT(DISTINCT mmi.menu_item_id) as item_count
            FROM menus m
            LEFT JOIN menu_menu_items mmi ON m.id = mmi.menu_id
            GROUP BY m.id
            ORDER BY m.sort_order, m.menu_name
        ''').fetchall()
    
    theme = get_theme()
    return render_template(f'menus_{theme}.html', menus=menus)

@app.route('/menus/create', methods=['GET', 'POST'])
def create_menu():
    """Create a new menu"""
    if request.method == 'POST':
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO menus (menu_name, description, is_active)
                VALUES (?, ?, ?)
            ''', (
                request.form['menu_name'],
                request.form.get('description', ''),
                1 if request.form.get('is_active') else 0
            ))
            return redirect(url_for('menus'))
    
    theme = get_theme()
    return render_template(f'create_menu_{theme}.html')

@app.route('/menus/<int:menu_id>/edit', methods=['GET', 'POST'])
def edit_menu(menu_id):
    """Edit menu details and manage items"""
    if request.method == 'POST':
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Update menu details
            cursor.execute('''
                UPDATE menus 
                SET menu_name = ?, description = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                request.form['menu_name'],
                request.form.get('description', ''),
                1 if request.form.get('is_active') else 0,
                menu_id
            ))
            
            return redirect(url_for('edit_menu', menu_id=menu_id))
    
    with get_db() as conn:
        # Get menu details
        menu = conn.execute('SELECT * FROM menus WHERE id = ?', (menu_id,)).fetchone()
        
        # Get all menu items with assignment status (distinct by item_name and recipe_id)
        menu_items = conn.execute('''
            SELECT DISTINCT mi.item_name, 
                   mi.recipe_id,
                   mi.menu_price,
                   mi.menu_group,
                   r.recipe_name,
                   r.food_cost,
                   r.food_cost_percentage,
                   CASE WHEN mmi.menu_id IS NOT NULL THEN 1 ELSE 0 END as is_assigned,
                   mmi.category,
                   mmi.sort_order as item_sort_order,
                   mmi.override_price,
                   MAX(mi.id) as id  -- Use MAX to get one ID per unique item
            FROM menu_items mi
            LEFT JOIN recipes r ON mi.recipe_id = r.id
            LEFT JOIN menu_menu_items mmi ON mi.id = mmi.menu_item_id AND mmi.menu_id = ?
            GROUP BY mi.item_name, mi.recipe_id
            ORDER BY mmi.category, mmi.sort_order, mi.item_name
        ''', (menu_id,)).fetchall()
        
        # Get categories
        categories = conn.execute('''
            SELECT * FROM menu_categories 
            WHERE menu_id = ? 
            ORDER BY sort_order
        ''', (menu_id,)).fetchall()
    
    theme = get_theme()
    return render_template(f'edit_menu_{theme}.html', 
                         menu=menu, 
                         menu_items=menu_items,
                         categories=categories)

@app.route('/menus/<int:menu_id>/items/toggle', methods=['POST'])
def toggle_menu_item(menu_id):
    """Add or remove item from menu"""
    menu_item_id = request.form.get('menu_item_id')
    action = request.form.get('action')
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        if action == 'add':
            cursor.execute('''
                INSERT OR IGNORE INTO menu_menu_items 
                (menu_id, menu_item_id, category, sort_order)
                VALUES (?, ?, ?, 0)
            ''', (menu_id, menu_item_id, request.form.get('category', 'Uncategorized')))
        else:
            cursor.execute('''
                DELETE FROM menu_menu_items 
                WHERE menu_id = ? AND menu_item_id = ?
            ''', (menu_id, menu_item_id))
    
    return redirect(url_for('edit_menu', menu_id=menu_id))

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
        # Development mode - debug is OFF by default for security
        # Set FLASK_DEBUG=1 or FLASK_DEBUG=true to enable debug mode
        is_debug = os.getenv('FLASK_DEBUG', 'false').lower() in ['true', '1']
        if is_debug:
            print("WARNING: Debug mode is enabled. Never use this in production!")
        app.run(debug=is_debug, host='0.0.0.0', port=8888)