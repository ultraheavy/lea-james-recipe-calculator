#!/usr/bin/env python3
"""
Initialize database - import if empty, otherwise just ensure tables exist
"""
import sqlite3
import os
from datetime import datetime

def needs_import():
    """Check if database needs to be imported"""
    db_path = 'restaurant_calculator.db'
    
    if not os.path.exists(db_path):
        return True
    
    # Check if database has tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
    table_count = cursor.fetchone()[0]
    
    # Check if inventory has data
    try:
        cursor.execute("SELECT COUNT(*) FROM inventory")
        inventory_count = cursor.fetchone()[0]
    except:
        inventory_count = 0
    
    conn.close()
    
    # Need import if no tables or no inventory data
    return table_count < 10 or inventory_count == 0

def import_database():
    """Import database from exports/latest.sql"""
    db_path = 'restaurant_calculator.db'
    import_file = 'exports/latest.sql'
    
    if not os.path.exists(import_file):
        print(f"ERROR: Import file {import_file} not found!")
        return False
    
    print(f"Importing database from {import_file}...")
    
    # Remove existing database to do clean import
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Import using Python sqlite3 module
    try:
        # Read the SQL file
        with open(import_file, 'r') as f:
            sql_script = f.read()
        
        # Create new database and execute the script
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.executescript(sql_script)
        conn.commit()
        conn.close()
        
        print("Database import successful!")
        return True
    except Exception as e:
        print(f"ERROR: Database import failed: {e}")
        return False

def ensure_vendor_descriptions():
    """Ensure vendor_descriptions table exists"""
    db_path = 'restaurant_calculator.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
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
            conn.commit()
            print("Created vendor_descriptions table")
    except Exception as e:
        print(f"Error ensuring vendor_descriptions: {e}")
    finally:
        conn.close()

def main():
    """Main initialization logic"""
    print("Database initialization starting...")
    
    if needs_import():
        print("Database needs import...")
        if import_database():
            print("Import completed successfully!")
        else:
            print("Import failed - app may not work correctly")
            # Don't exit - let app try to start anyway
    else:
        print("Database already initialized")
        # Just ensure critical tables exist
        ensure_vendor_descriptions()
    
    print("Database initialization complete!")

if __name__ == '__main__':
    main()