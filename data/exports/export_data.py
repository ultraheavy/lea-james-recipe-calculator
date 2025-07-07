#!/usr/bin/env python3
"""
Export all data from the database to SQL files that can be committed to git.
This preserves all your actual data for deployment.
"""

import sqlite3
import os

DATABASE = 'restaurant_calculator.db'
EXPORT_DIR = 'data'

def export_data():
    """Export all table data to SQL insert statements."""
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row['name'] for row in cursor.fetchall()]
    
    print(f"Exporting data from {len(tables)} tables...")
    
    # Export each table
    all_inserts = []
    
    for table in tables:
        print(f"Exporting {table}...")
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        
        if rows:
            # Get column names
            columns = list(rows[0].keys())
            
            # Generate INSERT statements
            for row in rows:
                values = []
                for col in columns:
                    val = row[col]
                    if val is None:
                        values.append('NULL')
                    elif isinstance(val, (int, float)):
                        values.append(str(val))
                    else:
                        # Escape single quotes in strings
                        val = str(val).replace("'", "''")
                        values.append(f"'{val}'")
                
                insert = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)});"
                all_inserts.append(insert)
    
    # Write to file
    with open(os.path.join(EXPORT_DIR, 'production_data.sql'), 'w') as f:
        f.write("-- Production data export\n")
        f.write("-- This file contains all the actual data from your database\n\n")
        
        for insert in all_inserts:
            f.write(insert + "\n")
    
    print(f"Exported {len(all_inserts)} records to data/production_data.sql")
    
    # Also create a backup of the entire database
    import shutil
    shutil.copy2(DATABASE, os.path.join(EXPORT_DIR, 'restaurant_calculator_backup.db'))
    print(f"Database backup created at data/restaurant_calculator_backup.db")
    
    conn.close()

if __name__ == '__main__':
    export_data()