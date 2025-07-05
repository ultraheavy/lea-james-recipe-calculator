#!/usr/bin/env python3
"""
Populate ingredient_densities table with common ingredient density values.
Density values are in g/ml for converting between volume and weight.
"""

import sqlite3

DATABASE = 'restaurant_calculator.db'

# Common ingredient densities (g/ml)
# Based on USDA and culinary reference data
DENSITY_DATA = [
    # Liquids
    {'ingredient_name': 'Water', 'density_g_per_ml': 1.0, 'source': 'Standard'},
    {'ingredient_name': 'Milk', 'density_g_per_ml': 1.03, 'source': 'USDA'},
    {'ingredient_name': 'Heavy Cream', 'density_g_per_ml': 0.994, 'source': 'USDA'},
    {'ingredient_name': 'Oil', 'density_g_per_ml': 0.92, 'source': 'Average vegetable oil'},
    {'ingredient_name': 'Olive Oil', 'density_g_per_ml': 0.915, 'source': 'USDA'},
    {'ingredient_name': 'Vegetable Oil', 'density_g_per_ml': 0.92, 'source': 'USDA'},
    {'ingredient_name': 'Vinegar', 'density_g_per_ml': 1.01, 'source': 'USDA'},
    {'ingredient_name': 'Honey', 'density_g_per_ml': 1.42, 'source': 'USDA'},
    {'ingredient_name': 'Corn Syrup', 'density_g_per_ml': 1.38, 'source': 'USDA'},
    {'ingredient_name': 'Molasses', 'density_g_per_ml': 1.4, 'source': 'USDA'},
    
    # Powders and granular ingredients  
    {'ingredient_name': 'All-Purpose Flour', 'density_g_per_ml': 0.529, 'source': 'King Arthur'},
    {'ingredient_name': 'Flour', 'density_g_per_ml': 0.529, 'source': 'King Arthur'},
    {'ingredient_name': 'Sugar', 'density_g_per_ml': 0.845, 'source': 'USDA'},
    {'ingredient_name': 'Granulated Sugar', 'density_g_per_ml': 0.845, 'source': 'USDA'},
    {'ingredient_name': 'Brown Sugar', 'density_g_per_ml': 0.721, 'source': 'USDA (packed)'},
    {'ingredient_name': 'Powdered Sugar', 'density_g_per_ml': 0.56, 'source': 'USDA'},
    {'ingredient_name': 'Salt', 'density_g_per_ml': 1.217, 'source': 'Table salt'},
    {'ingredient_name': 'Kosher Salt', 'density_g_per_ml': 0.69, 'source': 'Diamond Crystal'},
    {'ingredient_name': 'Baking Powder', 'density_g_per_ml': 0.721, 'source': 'USDA'},
    {'ingredient_name': 'Baking Soda', 'density_g_per_ml': 0.689, 'source': 'USDA'},
    {'ingredient_name': 'Cornstarch', 'density_g_per_ml': 0.629, 'source': 'USDA'},
    
    # Dairy products
    {'ingredient_name': 'Butter', 'density_g_per_ml': 0.911, 'source': 'USDA'},
    {'ingredient_name': 'Sour Cream', 'density_g_per_ml': 0.993, 'source': 'USDA'},
    {'ingredient_name': 'Yogurt', 'density_g_per_ml': 1.03, 'source': 'USDA'},
    {'ingredient_name': 'Cream Cheese', 'density_g_per_ml': 0.98, 'source': 'USDA'},
    
    # Sauces and condiments
    {'ingredient_name': 'Ketchup', 'density_g_per_ml': 1.14, 'source': 'USDA'},
    {'ingredient_name': 'Mayonnaise', 'density_g_per_ml': 0.91, 'source': 'USDA'},
    {'ingredient_name': 'Mustard', 'density_g_per_ml': 1.05, 'source': 'USDA'},
    {'ingredient_name': 'Soy Sauce', 'density_g_per_ml': 1.2, 'source': 'USDA'},
    {'ingredient_name': 'Hot Sauce', 'density_g_per_ml': 1.02, 'source': 'USDA'},
    
    # Proteins - these are less precise as they vary by cut
    {'ingredient_name': 'Ground Beef', 'density_g_per_ml': 0.97, 'source': 'Approximate'},
    {'ingredient_name': 'Chicken', 'density_g_per_ml': 1.04, 'source': 'Approximate'},
    {'ingredient_name': 'Fish', 'density_g_per_ml': 1.0, 'source': 'Approximate'},
    
    # Toast-specific ingredients from CSV  
    {'ingredient_name': 'BBQ Sauce', 'density_g_per_ml': 1.25, 'source': 'Approximate'},
    {'ingredient_name': 'Ranch Dressing', 'density_g_per_ml': 0.95, 'source': 'Approximate'},
    {'ingredient_name': 'Buffalo Sauce', 'density_g_per_ml': 1.02, 'source': 'Approximate'},
    {'ingredient_name': 'Alfredo Sauce', 'density_g_per_ml': 1.1, 'source': 'Approximate'},
    {'ingredient_name': 'Marinara Sauce', 'density_g_per_ml': 1.03, 'source': 'Approximate'},
    {'ingredient_name': 'Pesto', 'density_g_per_ml': 0.95, 'source': 'Approximate'},
]


def populate_densities():
    """Populate the ingredient_densities table."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='ingredient_densities'
        """)
        
        if not cursor.fetchone():
            print("Creating ingredient_densities table...")
            cursor.execute('''
                CREATE TABLE ingredient_densities (
                    density_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ingredient_name TEXT NOT NULL UNIQUE,
                    density_g_per_ml DECIMAL(10,4) NOT NULL,
                    source TEXT,
                    notes TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE INDEX idx_ingredient_densities_name 
                ON ingredient_densities(ingredient_name)
            ''')
        
        # Clear existing densities
        cursor.execute('DELETE FROM ingredient_densities')
        
        # Insert density data
        for item in DENSITY_DATA:
            cursor.execute('''
                INSERT INTO ingredient_densities (ingredient_name, density_g_per_ml, source)
                VALUES (?, ?, ?)
            ''', (
                item['ingredient_name'],
                item['density_g_per_ml'],
                item['source']
            ))
        
        conn.commit()
        print(f"Successfully populated {len(DENSITY_DATA)} ingredient densities")
        
        # Display some examples
        print("\nSample densities:")
        samples = cursor.execute('''
            SELECT ingredient_name, density_g_per_ml, source
            FROM ingredient_densities
            ORDER BY ingredient_name
            LIMIT 10
        ''').fetchall()
        
        for sample in samples:
            print(f"  {sample[0]}: {sample[1]} g/ml ({sample[2]})")
            
    except Exception as e:
        print(f"Error populating densities: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == '__main__':
    populate_densities()