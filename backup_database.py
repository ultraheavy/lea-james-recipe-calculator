#!/usr/bin/env python3
"""
Database backup utility - creates timestamped backups before any operations
"""

import sqlite3
import shutil
from datetime import datetime
import os

def backup_database(db_path='restaurant_calculator.db', backup_dir='backups'):
    """Create a timestamped backup of the database"""
    
    # Create backup directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create backup filename
    backup_filename = f"{backup_dir}/backup_{timestamp}.db"
    
    # Copy the database
    shutil.copy2(db_path, backup_filename)
    
    print(f"✅ Database backed up to: {backup_filename}")
    
    # Keep only the last 10 backups
    cleanup_old_backups(backup_dir, keep=10)
    
    return backup_filename

def cleanup_old_backups(backup_dir, keep=10):
    """Remove old backups, keeping only the most recent ones"""
    
    # Get all backup files
    backups = []
    for file in os.listdir(backup_dir):
        if file.startswith('backup_') and file.endswith('.db'):
            backups.append(os.path.join(backup_dir, file))
    
    # Sort by modification time
    backups.sort(key=os.path.getmtime, reverse=True)
    
    # Remove old backups
    for backup in backups[keep:]:
        os.remove(backup)
        print(f"🗑️  Removed old backup: {backup}")

def restore_database(backup_path, db_path='restaurant_calculator.db'):
    """Restore database from a backup"""
    
    if not os.path.exists(backup_path):
        print(f"❌ Backup file not found: {backup_path}")
        return False
    
    # Create a safety backup of current database
    safety_backup = backup_database()
    
    try:
        # Restore from backup
        shutil.copy2(backup_path, db_path)
        print(f"✅ Database restored from: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        # Restore the safety backup
        shutil.copy2(safety_backup, db_path)
        return False

def list_backups(backup_dir='backups'):
    """List all available backups"""
    
    if not os.path.exists(backup_dir):
        print("No backups found")
        return []
    
    backups = []
    for file in os.listdir(backup_dir):
        if file.startswith('backup_') and file.endswith('.db'):
            path = os.path.join(backup_dir, file)
            size = os.path.getsize(path) / 1024 / 1024  # MB
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            backups.append({
                'filename': file,
                'path': path,
                'size_mb': round(size, 2),
                'created': mtime.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    # Sort by creation time, newest first
    backups.sort(key=lambda x: x['created'], reverse=True)
    
    return backups

if __name__ == "__main__":
    # Create a backup
    backup_database()
    
    # List available backups
    print("\n📁 Available backups:")
    for backup in list_backups():
        print(f"  - {backup['filename']} ({backup['size_mb']} MB) - {backup['created']}")