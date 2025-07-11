#!/usr/bin/env python3
"""
Emergency production database fix script
Adds missing columns that are causing 500 errors on the production site
"""
import sqlite3
import sys
import os
from datetime import datetime

def fix_production_database(db_path):
    """Apply emergency fixes to production database"""
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Starting emergency database fixes...")
        
        # Check current schema
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='recipes'")
        recipes_schema = cursor.fetchone()
        
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='menu_versions'")
        menu_versions_schema = cursor.fetchone()
        
        # Fix 1: Add created_at to recipes if missing
        if recipes_schema and 'created_at' not in recipes_schema[0]:
            print("Adding created_at column to recipes table...")
            cursor.execute("""
                ALTER TABLE recipes 
                ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            cursor.execute("""
                UPDATE recipes 
                SET created_at = CURRENT_TIMESTAMP 
                WHERE created_at IS NULL
            """)
            print("✓ Added created_at to recipes")
        else:
            print("✓ recipes.created_at already exists")
        
        # Fix 2: Add updated_at to recipes if missing
        if recipes_schema and 'updated_at' not in recipes_schema[0]:
            print("Adding updated_at column to recipes table...")
            cursor.execute("""
                ALTER TABLE recipes 
                ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            cursor.execute("""
                UPDATE recipes 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE updated_at IS NULL
            """)
            print("✓ Added updated_at to recipes")
        else:
            print("✓ recipes.updated_at already exists")
        
        # Fix 3: Add status to menu_versions if missing
        if menu_versions_schema and 'status' not in menu_versions_schema[0]:
            print("Adding status column to menu_versions table...")
            cursor.execute("""
                ALTER TABLE menu_versions 
                ADD COLUMN status TEXT DEFAULT 'active'
            """)
            cursor.execute("""
                UPDATE menu_versions 
                SET status = 'active' 
                WHERE status IS NULL
            """)
            print("✓ Added status to menu_versions")
        else:
            print("✓ menu_versions.status already exists")
        
        # Fix 4: Add timestamps to menu_versions if missing
        if menu_versions_schema and 'created_at' not in menu_versions_schema[0]:
            print("Adding created_at column to menu_versions table...")
            cursor.execute("""
                ALTER TABLE menu_versions 
                ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            cursor.execute("""
                UPDATE menu_versions 
                SET created_at = CURRENT_TIMESTAMP 
                WHERE created_at IS NULL
            """)
            print("✓ Added created_at to menu_versions")
        else:
            print("✓ menu_versions.created_at already exists")
        
        if menu_versions_schema and 'updated_at' not in menu_versions_schema[0]:
            print("Adding updated_at column to menu_versions table...")
            cursor.execute("""
                ALTER TABLE menu_versions 
                ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
            cursor.execute("""
                UPDATE menu_versions 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE updated_at IS NULL
            """)
            print("✓ Added updated_at to menu_versions")
        else:
            print("✓ menu_versions.updated_at already exists")
        
        # Commit changes
        conn.commit()
        print("\n✅ All fixes applied successfully!")
        
        # Verify the fixes
        print("\nVerifying schema...")
        cursor.execute("PRAGMA table_info(recipes)")
        recipes_cols = [col[1] for col in cursor.fetchall()]
        print(f"Recipes columns: {', '.join(recipes_cols)}")
        
        cursor.execute("PRAGMA table_info(menu_versions)")
        menu_versions_cols = [col[1] for col in cursor.fetchall()]
        print(f"Menu versions columns: {', '.join(menu_versions_cols)}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        return False

if __name__ == "__main__":
    # Use the same database path as app.py
    DATABASE = os.environ.get('DATABASE_PATH', 'restaurant_calculator.db')
    
    print(f"Database path: {DATABASE}")
    success = fix_production_database(DATABASE)
    
    if success:
        print("\n🎉 Database fixes completed successfully!")
        print("The dashboard and pricing analysis pages should now work.")
    else:
        print("\n❌ Failed to apply database fixes.")
        sys.exit(1)