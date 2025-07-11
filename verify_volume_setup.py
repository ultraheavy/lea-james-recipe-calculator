#!/usr/bin/env python3
"""
Verify Railway Volume Setup
Run this after deployment to check if volume is working correctly
"""
import os
import sqlite3
import sys

def check_volume_setup():
    """Check if Railway volume is properly configured"""
    
    print("=== Railway Volume Verification ===\n")
    
    # 1. Check environment
    is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('RAILWAY_ENVIRONMENT')
    print(f"1. Environment:")
    print(f"   - FLASK_ENV: {os.getenv('FLASK_ENV', 'not set')}")
    print(f"   - RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'not set')}")
    print(f"   - Is Production: {is_production}")
    print()
    
    # 2. Check volume mount
    print(f"2. Volume Mount:")
    volume_exists = os.path.exists('/data')
    print(f"   - /data directory exists: {volume_exists}")
    
    if volume_exists:
        # Check permissions
        can_write = os.access('/data', os.W_OK)
        print(f"   - /data is writable: {can_write}")
        
        # List contents
        try:
            contents = os.listdir('/data')
            print(f"   - /data contents: {contents}")
        except Exception as e:
            print(f"   - Error listing /data: {e}")
    print()
    
    # 3. Check database paths
    print(f"3. Database Paths:")
    paths_to_check = [
        'restaurant_calculator.db',
        '/data/restaurant_calculator.db',
        os.getenv('DATABASE_PATH', 'not set')
    ]
    
    for path in paths_to_check:
        if path == 'not set':
            print(f"   - DATABASE_PATH env: not set")
        else:
            exists = os.path.exists(path) if isinstance(path, str) else False
            print(f"   - {path}: {'exists' if exists else 'not found'}")
            if exists:
                size = os.path.getsize(path) / 1024 / 1024
                print(f"     Size: {size:.2f} MB")
    print()
    
    # 4. Test database connection
    print(f"4. Database Connection Test:")
    
    # Try volume path first if in production
    if is_production and os.path.exists('/data/restaurant_calculator.db'):
        db_path = '/data/restaurant_calculator.db'
    elif os.path.exists('restaurant_calculator.db'):
        db_path = 'restaurant_calculator.db'
    else:
        print("   ❌ No database file found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recipes_actual")
        recipe_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM inventory")
        inventory_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"   ✅ Connected to: {db_path}")
        print(f"   - Tables: {table_count}")
        print(f"   - Recipes: {recipe_count}")
        print(f"   - Inventory: {inventory_count}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

if __name__ == "__main__":
    success = check_volume_setup()
    print("\n" + "="*40)
    if success:
        print("✅ Volume setup appears to be working!")
    else:
        print("❌ Volume setup needs attention")
    sys.exit(0 if success else 1)