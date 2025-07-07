#!/usr/bin/env python3
"""
Temporary admin script to run database migrations
REMOVE THIS FILE AFTER USE!
"""
import sqlite3
import os
from datetime import datetime

def run_migration():
    db_path = 'restaurant_calculator.db'
    
    # Create backup first
    backup_path = f'backups/pre_migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    os.makedirs('backups', exist_ok=True)
    
    print(f"Creating backup at {backup_path}...")
    with open(db_path, 'rb') as f_in:
        with open(backup_path, 'wb') as f_out:
            f_out.write(f_in.read())
    
    print("Running migration...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create table
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
        
        # Populate data
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
        print(f"Migration successful! Created vendor_descriptions table with {count} records.")
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    run_migration()