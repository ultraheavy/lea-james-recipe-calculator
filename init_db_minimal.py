#!/usr/bin/env python3
"""
Minimal database initialization - just add missing tables
"""
import sqlite3
import os

def init_database():
    """Initialize database with only the required missing tables"""
    db_path = 'restaurant_calculator.db'
    
    if not os.path.exists(db_path):
        print(f"ERROR: Database {db_path} does not exist!")
        return
    
    print("Checking database schema...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Only create vendor_descriptions if missing
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
            print("Created vendor_descriptions table successfully.")
        else:
            print("vendor_descriptions table already exists.")
        
        print("Database check complete!")
        
    except Exception as e:
        conn.rollback()
        print(f"Database initialization failed: {e}")
        # Don't raise - let the app start anyway
    finally:
        conn.close()

if __name__ == '__main__':
    init_database()