#!/usr/bin/env python3
"""
Import database from SQL export file
Used in production to restore complete database
"""
import sqlite3
import os
from datetime import datetime

def import_database():
    """Import database from exports/latest.sql"""
    db_path = 'restaurant_calculator.db'
    import_file = 'exports/latest.sql'
    
    # Check if import file exists
    if not os.path.exists(import_file):
        print(f"ERROR: Import file {import_file} not found!")
        print("Make sure to run export_database.py before deployment")
        return False
    
    # Backup existing database if it exists
    if os.path.exists(db_path):
        os.makedirs('backups', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f'backups/pre_import_{timestamp}.db'
        os.rename(db_path, backup_path)
        print(f"Backed up existing database to {backup_path}")
    
    print(f"Importing database from {import_file}...")
    
    # Import using sqlite3 command
    result = os.system(f'sqlite3 {db_path} < {import_file}')
    
    if result == 0:
        print("Database import successful!")
        
        # Verify the import
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Imported {len(tables)} tables")
        
        # Check key tables
        for table in ['inventory', 'recipes', 'menu_items', 'vendor_descriptions']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} records")
        
        conn.close()
        return True
    else:
        print("ERROR: Database import failed!")
        return False

if __name__ == '__main__':
    import_database()