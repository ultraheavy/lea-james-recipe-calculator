#!/usr/bin/env python3
"""
Cleanup script for old migration tables
Run this ONLY after confirming the new schema is working properly
"""

import sqlite3
import os
from datetime import datetime

DATABASE = 'restaurant_calculator.db'

def backup_before_cleanup():
    """Create a backup before cleanup"""
    backup_name = f"restaurant_calculator_before_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    os.system(f"cp {DATABASE} {backup_name}")
    print(f"✅ Backup created: {backup_name}")
    return backup_name

def list_old_tables():
    """List all old tables that will be removed"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_old%'")
        old_tables = [row[0] for row in cursor.fetchall()]
    return old_tables

def cleanup_old_tables():
    """Remove old migration backup tables"""
    old_tables = list_old_tables()
    
    if not old_tables:
        print("✅ No old tables found to cleanup")
        return
    
    print(f"Found {len(old_tables)} old tables:")
    for table in old_tables:
        print(f"  - {table}")
    
    response = input("\n⚠️  Are you sure you want to drop these tables? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Cleanup cancelled")
        return
    
    # Create backup first
    backup_name = backup_before_cleanup()
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        for table in old_tables:
            try:
                cursor.execute(f"DROP TABLE {table}")
                print(f"✅ Dropped table: {table}")
            except Exception as e:
                print(f"❌ Error dropping {table}: {e}")
        
        conn.commit()
    
    print(f"\n✅ Cleanup complete! Backup saved as: {backup_name}")

if __name__ == "__main__":
    print("=== DATABASE CLEANUP TOOL ===")
    print("This will remove old migration backup tables")
    cleanup_old_tables()
