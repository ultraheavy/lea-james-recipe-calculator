#!/usr/bin/env python3
"""
Database synchronization script for production deployment
"""
import os
import sqlite3
import shutil
from datetime import datetime

def export_database_for_production():
    """Export local database to production format"""
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'backups/db_backup_{timestamp}.db'
    os.makedirs('backups', exist_ok=True)
    shutil.copy2('restaurant_calculator.db', backup_path)
    print(f"✓ Created backup: {backup_path}")
    
    # Export to SQL
    os.system('sqlite3 restaurant_calculator.db .dump > data/production_data.sql')
    print("✓ Exported database to data/production_data.sql")
    
    # Get statistics
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    stats = {}
    tables = ['inventory', 'recipes', 'menu_items', 'vendors', 'vendor_descriptions']
    for table in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        stats[table] = cursor.fetchone()[0]
    
    conn.close()
    
    # Create summary file
    with open('data/production_data_summary.txt', 'w') as f:
        f.write(f"Database Export Summary\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*30}\n")
        for table, count in stats.items():
            f.write(f"{table}: {count} records\n")
    
    print("\nDatabase Statistics:")
    for table, count in stats.items():
        print(f"  {table}: {count} records")
    
    print("\n✓ Export complete!")
    print("\nNext steps:")
    print("1. git add data/production_data.sql data/production_data_summary.txt")
    print("2. git commit -m 'Update production database'")
    print("3. git push")
    print("4. railway up (or wait for automatic deployment)")

if __name__ == "__main__":
    export_database_for_production()