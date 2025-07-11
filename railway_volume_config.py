#!/usr/bin/env python3
"""
Railway Volume Configuration Helper
This script helps configure the app to use Railway volumes for database storage
"""
import os
import shutil
from pathlib import Path

def get_database_path():
    """
    Determine the correct database path based on environment
    Priority:
    1. Railway volume path (/data/restaurant_calculator.db)
    2. Local development path (./restaurant_calculator.db)
    """
    # Check if running on Railway with volume
    if os.path.exists('/data'):
        print("✅ Railway volume detected at /data")
        print(f"  Volume writable: {os.access('/data', os.W_OK)}")
        return '/data/restaurant_calculator.db'
    
    # Check Railway environment without volume
    if os.getenv('RAILWAY_ENVIRONMENT'):
        print("⚠️  Running on Railway but no volume found at /data")
    
    # Local development
    print("Using local database path")
    return 'restaurant_calculator.db'

def migrate_database_to_volume():
    """
    One-time migration: Copy existing database to volume if needed
    """
    volume_path = '/data/restaurant_calculator.db'
    local_path = 'restaurant_calculator.db'
    
    # Only run if on Railway and volume exists
    if not os.path.exists('/data'):
        print("No Railway volume found, skipping migration")
        return False
    
    # Check if database already exists in volume
    if os.path.exists(volume_path):
        print(f"Database already exists at {volume_path}")
        return True
    
    # Check if local database exists to migrate
    if os.path.exists(local_path):
        print(f"Migrating database from {local_path} to {volume_path}")
        try:
            shutil.copy2(local_path, volume_path)
            print("✅ Database migrated successfully!")
            return True
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    else:
        print("⚠️  No existing database found to migrate")
        return False

def setup_volume_database():
    """
    Ensure database exists in the correct location
    Returns the path to use
    """
    db_path = get_database_path()
    
    # If using Railway volume, attempt migration
    if db_path.startswith('/data'):
        migrate_database_to_volume()
    
    return db_path

if __name__ == "__main__":
    # Test the configuration
    print("=== Railway Volume Configuration Test ===")
    db_path = setup_volume_database()
    print(f"\nDatabase path: {db_path}")
    print(f"Database exists: {os.path.exists(db_path)}")
    
    if os.path.exists(db_path):
        size = os.path.getsize(db_path) / 1024 / 1024  # MB
        print(f"Database size: {size:.2f} MB")