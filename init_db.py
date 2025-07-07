#!/usr/bin/env python3
"""
Database initialization and migration script
Runs automatically on Railway deployment
"""
import sqlite3
import os
from datetime import datetime

def init_database():
    """Initialize database with required tables and migrations"""
    db_path = 'restaurant_calculator.db'
    
    # Only create backup if database exists
    if os.path.exists(db_path):
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, f'pre_migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        
        print(f"Creating backup at {backup_path}...")
        with open(db_path, 'rb') as f_in:
            with open(backup_path, 'wb') as f_out:
                f_out.write(f_in.read())
    
    print("Checking database schema...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if vendor_descriptions table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='vendor_descriptions'
        """)
        
        if not cursor.fetchone():
            print("Creating vendor_descriptions table...")
            cursor.execute('''
                CREATE TABLE vendor_descriptions (
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
            
            # Populate data from inventory
            print("Populating vendor descriptions...")
            cursor.execute('''
                INSERT OR IGNORE INTO vendor_descriptions (inventory_id, vendor_name, vendor_description, item_code)
                SELECT id, vendor_name, item_description, item_code
                FROM inventory
                WHERE vendor_name IS NOT NULL
            ''')
            
            # Get count
            cursor.execute('SELECT COUNT(*) FROM vendor_descriptions')
            count = cursor.fetchone()[0]
            
            conn.commit()
            print(f"Created vendor_descriptions table with {count} records.")
        else:
            print("vendor_descriptions table already exists.")
        
        # Check for units table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='units'")
        if not cursor.fetchone():
            print("Creating units table...")
            cursor.execute('''
                CREATE TABLE units (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unit_name TEXT NOT NULL UNIQUE,
                    unit_type TEXT NOT NULL,
                    to_base_factor REAL NOT NULL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert basic units
            cursor.executemany('''
                INSERT INTO units (unit_name, unit_type, to_base_factor) VALUES (?, ?, ?)
            ''', [
                ('g', 'weight', 1.0),
                ('kg', 'weight', 1000.0),
                ('oz', 'weight', 28.3495),
                ('lb', 'weight', 453.592),
                ('ml', 'volume', 1.0),
                ('l', 'volume', 1000.0),
                ('tsp', 'volume', 4.92892),
                ('tbsp', 'volume', 14.7868),
                ('cup', 'volume', 236.588),
                ('fl oz', 'volume', 29.5735),
                ('each', 'count', 1.0),
                ('dozen', 'count', 12.0),
                ('ct', 'count', 1.0)
            ])
            print("Created units table with basic units")
        
        # Check for ingredient_densities table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ingredient_densities'")
        if not cursor.fetchone():
            print("Creating ingredient_densities table...")
            cursor.execute('''
                CREATE TABLE ingredient_densities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ingredient_name TEXT NOT NULL UNIQUE,
                    density_g_per_ml REAL NOT NULL,
                    notes TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("Created ingredient_densities table")
        
        # Check if menu_items table exists before trying to query it
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='menu_items'")
        if cursor.fetchone():
            # After all tables are set up, recalculate costs if needed
            cursor.execute('''
                SELECT COUNT(*) FROM menu_items 
                WHERE menu_price > 0 AND food_cost > 0 
                AND food_cost / menu_price > 1.0
            ''')
            
            high_cost_count = cursor.fetchone()[0]
            if high_cost_count > 10:  # If more than 10 items have >100% food cost
                print(f"\nDetected {high_cost_count} items with impossible food costs.")
                print("Running cost recalculation...")
                conn.commit()  # Commit table changes first
                conn.close()   # Close connection
                
                # Import and run the recalculation
                from recalculate_all_costs import recalculate_all_costs
                recalculate_all_costs()
                
                return  # Exit early since we closed the connection
        else:
            print("WARNING: menu_items table does not exist - database may be incomplete!")
        
        # Add any future migrations here
        
        print("Database initialization complete!")
        
    except Exception as e:
        conn.rollback()
        print(f"Database initialization failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    init_database()