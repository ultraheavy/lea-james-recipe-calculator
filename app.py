from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DATABASE = 'restaurant_calculator.db'

def init_database():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_number TEXT UNIQUE,
                item_description TEXT NOT NULL,
                current_price REAL,
                unit_measure TEXT,
                purchase_unit TEXT,
                recipe_cost_unit TEXT,
                yield_percent REAL DEFAULT 100
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_name TEXT NOT NULL,
                recipe_number INTEGER,
                total_cost REAL DEFAULT 0,
                yield_amount TEXT,
                shelf_life TEXT,
                station TEXT,
                procedure TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipe_ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER,
                ingredient_id INTEGER,
                quantity REAL,
                unit TEXT,
                cost REAL,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id),
                FOREIGN KEY (ingredient_id) REFERENCES inventory (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                menu_group TEXT,
                item_description TEXT,
                recipe_id INTEGER,
                menu_price REAL,
                food_cost REAL,
                food_cost_percent REAL,
                gross_profit REAL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        ''')
        
        conn.commit()

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventory')
def inventory():
    with get_db() as conn:
        items = conn.execute('SELECT * FROM inventory ORDER BY item_number').fetchall()
    return render_template('inventory.html', items=items)

@app.route('/inventory/add', methods=['GET', 'POST'])
def add_inventory():
    """Add new inventory item"""
    if request.method == 'POST':
        with get_db() as conn:
            conn.execute('''
                INSERT INTO inventory 
                (item_number, item_description, current_price, unit_measure, 
                 purchase_unit, recipe_cost_unit, yield_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.form['item_number'],
                request.form['item_description'],
                float(request.form['current_price']) if request.form['current_price'] else 0,
                request.form['unit_measure'],
                request.form['purchase_unit'],
                request.form['recipe_cost_unit'],
                float(request.form['yield_percent']) if request.form['yield_percent'] else 100
            ))
            conn.commit()
        
        return redirect(url_for('inventory'))
    
    return render_template('add_inventory.html')

@app.route('/recipes')
def recipes():
    with get_db() as conn:
        recipes = conn.execute('SELECT * FROM recipes ORDER BY recipe_number').fetchall()
    return render_template('recipes.html', recipes=recipes)

@app.route('/recipes/add', methods=['GET', 'POST'])
def add_recipe():
    """Add new recipe"""
    if request.method == 'POST':
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Insert recipe
            cursor.execute('''
                INSERT INTO recipes 
                (recipe_name, recipe_number, yield_amount, shelf_life, station, procedure)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                request.form['recipe_name'],
                int(request.form['recipe_number']) if request.form['recipe_number'] else None,
                request.form['yield_amount'],
                request.form['shelf_life'],
                request.form['station'],
                request.form['procedure']
            ))
            
            conn.commit()
        
        return redirect(url_for('recipes'))
    
    # Get inventory for dropdown
    with get_db() as conn:
        inventory = conn.execute('SELECT * FROM inventory ORDER BY item_description').fetchall()
    
    return render_template('add_recipe.html', inventory=inventory)

@app.route('/recipes/<int:recipe_id>')
def view_recipe(recipe_id):
    """View recipe details"""
    with get_db() as conn:
        recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,)).fetchone()
        ingredients = conn.execute('''
            SELECT ri.*, i.item_description, i.unit_measure 
            FROM recipe_ingredients ri 
            JOIN inventory i ON ri.ingredient_id = i.id 
            WHERE ri.recipe_id = ?
        ''', (recipe_id,)).fetchall()
    
    return render_template('view_recipe.html', recipe=recipe, ingredients=ingredients)

@app.route('/menu')
def menu():
    """Menu management page"""
    with get_db() as conn:
        menu_items = conn.execute('''
            SELECT m.*, r.recipe_name 
            FROM menu_items m 
            LEFT JOIN recipes r ON m.recipe_id = r.id 
            ORDER BY m.menu_group, m.item_name
        ''').fetchall()
    return render_template('menu.html', menu_items=menu_items)

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    init_database()
    app.run(debug=True, host='0.0.0.0', port=8888)
