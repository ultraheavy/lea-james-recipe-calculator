#!/usr/bin/env python3
"""
Export the entire database structure and data to SQL file
"""
import sqlite3
import os
from datetime import datetime

def export_database():
    """Export complete database to SQL file"""
    db_path = 'restaurant_calculator.db'
    
    if not os.path.exists(db_path):
        print(f"ERROR: Database {db_path} does not exist!")
        return
    
    # Create exports directory
    os.makedirs('exports', exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    export_file = f'exports/database_export_{timestamp}.sql'
    
    print(f"Exporting database to {export_file}...")
    
    # Use sqlite3 command line for complete dump
    os.system(f'sqlite3 {db_path} .dump > {export_file}')
    
    # Also create a latest.sql for easy deployment
    os.system(f'cp {export_file} exports/latest.sql')
    
    # Get file size
    size = os.path.getsize(export_file)
    print(f"Export complete! File size: {size:,} bytes")
    print(f"Created: {export_file}")
    print(f"Also saved as: exports/latest.sql")
    
    # Show table counts
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\nDatabase summary:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  {table_name}: {count:,} records")
    
    conn.close()

if __name__ == '__main__':
    export_database()