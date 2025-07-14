#!/usr/bin/env python3
"""Clear staging data for fresh import"""

import sqlite3

def clear_staging_data():
    conn = sqlite3.connect("restaurant_calculator.db")
    cursor = conn.cursor()
    
    try:
        # Clear all staging data
        cursor.execute("DELETE FROM stg_inventory_items")
        conn.commit()
        
        count = cursor.rowcount
        print(f"Cleared {count} rows from staging table")
        
    except Exception as e:
        print(f"Error clearing data: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clear_staging_data()