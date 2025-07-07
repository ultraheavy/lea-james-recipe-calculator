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