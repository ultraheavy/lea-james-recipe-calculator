#!/usr/bin/env python3
"""
Add menu versioning system to track V2 and V3 menus
"""

import sqlite3
from backup_database import backup_database
from datetime import datetime

def add_menu_versioning():
    """Create menu versioning tables and migrate data"""
    
    # First, backup the database
    print("📦 Creating database backup...")
    backup_database()
    
    conn = sqlite3.connect('restaurant_calculator.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Create menu_versions table
        print("\n🔨 Creating menu_versions table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_name TEXT NOT NULL UNIQUE,
                description TEXT,
                is_active BOOLEAN DEFAULT FALSE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                effective_date TEXT,
                notes TEXT
            )
        ''')
        
        # Add version_id to menu_items table
        print("\n🔧 Adding version support to menu_items...")
        
        # Check if version_id column exists
        columns = cursor.execute("PRAGMA table_info(menu_items)").fetchall()
        has_version_id = any(col['name'] == 'version_id' for col in columns)
        
        if not has_version_id:
            cursor.execute('''
                ALTER TABLE menu_items ADD COLUMN version_id INTEGER
            ''')
        
        # Create default menu versions
        print("\n📝 Creating initial menu versions...")
        
        # V1 - Current menu
        cursor.execute('''
            INSERT OR IGNORE INTO menu_versions (version_name, description, is_active, effective_date)
            VALUES (?, ?, ?, ?)
        ''', ('V1 - Current', 'Current active menu', True, datetime.now().strftime('%Y-%m-%d')))
        v1_id = cursor.lastrowid
        
        # V2 - Next version
        cursor.execute('''
            INSERT OR IGNORE INTO menu_versions (version_name, description, is_active)
            VALUES (?, ?, ?)
        ''', ('V2 - Planning', 'Next menu version in planning', False))
        v2_id = cursor.lastrowid
        
        # V3 - Future version
        cursor.execute('''
            INSERT OR IGNORE INTO menu_versions (version_name, description, is_active)
            VALUES (?, ?, ?)
        ''', ('V3 - Future', 'Future menu version for long-term planning', False))
        v3_id = cursor.lastrowid
        
        # Update existing menu items to V1
        print("\n🔄 Assigning existing menu items to V1...")
        cursor.execute('''
            UPDATE menu_items 
            SET version_id = ? 
            WHERE version_id IS NULL
        ''', (v1_id,))
        
        # Create menu comparison view
        print("\n👁️ Creating menu comparison view...")
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS menu_version_comparison AS
            SELECT 
                mi.item_name,
                mi.menu_group,
                mi.menu_price,
                mi.food_cost,
                mi.food_cost_percent,
                mi.gross_profit,
                mv.version_name,
                mv.is_active,
                r.recipe_name
            FROM menu_items mi
            JOIN menu_versions mv ON mi.version_id = mv.id
            LEFT JOIN recipes r ON mi.recipe_id = r.id
            ORDER BY mv.version_name, mi.menu_group, mi.item_name
        ''')
        
        conn.commit()
        
        # Show summary
        versions = cursor.execute('SELECT * FROM menu_versions ORDER BY id').fetchall()
        
        print(f"\n📊 Menu Versions Summary:")
        for version in versions:
            item_count = cursor.execute(
                'SELECT COUNT(*) FROM menu_items WHERE version_id = ?', 
                (version['id'],)
            ).fetchone()[0]
            
            status = "Active" if version['is_active'] else "Inactive"
            print(f"  - {version['version_name']}: {item_count} items ({status})")
        
        print("\n✅ Menu versioning system created successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    add_menu_versioning()