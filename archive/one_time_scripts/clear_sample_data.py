#!/usr/bin/env python3
"""
Clear all sample data from database before importing real Toast data
"""

import sqlite3
import os

DATABASE = 'restaurant_calculator.db'

def clear_all_data():
    """Clear all existing data from all tables"""
    print("🧹 Clearing all sample data from database...")
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        # Clear all tables in correct order (respecting foreign keys)
        tables_to_clear = [
            'recipe_ingredients',
            'menu_items', 
            'recipes',
            'inventory',
            'vendors'
        ]
        
        for table in tables_to_clear:
            try:
                cursor.execute(f'DELETE FROM {table}')
                count = cursor.rowcount
                print(f"  - Cleared {count} records from {table}")
            except Exception as e:
                print(f"  - Error clearing {table}: {e}")
        
        # Reset auto-increment counters
        cursor.execute("DELETE FROM sqlite_sequence")
        
        conn.commit()
    
    print("✅ All sample data cleared successfully!")

def verify_empty_database():
    """Verify that all tables are empty"""
    print("🔍 Verifying database is empty...")
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        tables = ['inventory', 'recipes', 'recipe_ingredients', 'menu_items', 'vendors']
        
        for table in tables:
            try:
                count = cursor.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
                print(f"  - {table}: {count} records")
            except Exception as e:
                print(f"  - Error checking {table}: {e}")

if __name__ == '__main__':
    clear_all_data()
    verify_empty_database()
    print("\n✅ Database is ready for Toast data import!")
