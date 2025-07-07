#!/usr/bin/env python3
"""
backup_automation.py - Automated Database Backup System
PRIORITY 1 IMPLEMENTATION - CRITICAL FOR DATA PROTECTION

This script provides automated backup functionality for the restaurant
management system database with verification and rotation.
"""

import sqlite3
import shutil
import os
import sys
from datetime import datetime, timedelta
import hashlib
import json
import logging

class DatabaseBackupSystem:
    def __init__(self, source_db="restaurant_calculator.db", backup_dir="backups"):
        self.source_db = source_db
        self.backup_dir = backup_dir
        self.retention_days = 30
        self.verification_enabled = True
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('backup.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Create backup directory
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self):
        """Create a new database backup with timestamp"""
        try:
            # Check if source database exists
            if not os.path.exists(self.source_db):
                raise FileNotFoundError(f"Source database not found: {self.source_db}")
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"restaurant_calculator_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Create backup
            self.logger.info(f"Creating backup: {backup_path}")
            shutil.copy2(self.source_db, backup_path)
            
            # Verify backup if enabled
            if self.verification_enabled:
                if self.verify_backup(backup_path):
                    self.logger.info("✅ Backup created and verified successfully")
                else:
                    raise Exception("Backup verification failed")
            
            # Create backup metadata
            metadata = {
                "timestamp": timestamp,
                "source_file": self.source_db,
                "backup_file": backup_path,
                "source_size": os.path.getsize(self.source_db),
                "backup_size": os.path.getsize(backup_path),
                "source_checksum": self.calculate_checksum(self.source_db),
                "backup_checksum": self.calculate_checksum(backup_path),
                "verified": self.verification_enabled
            }
            
            metadata_path = backup_path.replace('.db', '_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return backup_path, metadata
            
        except Exception as e:
            self.logger.error(f"❌ Backup failed: {str(e)}")
            raise
    
    def verify_backup(self, backup_path):
        """Verify backup integrity by testing database operations"""
        try:
            # Test database connectivity
            with sqlite3.connect(backup_path) as conn:
                cursor = conn.cursor()
                
                # Test basic queries
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                
                if table_count == 0:
                    self.logger.error("Backup verification failed: No tables found")
                    return False
                
                # Test critical tables
                critical_tables = ['inventory', 'recipes', 'recipe_ingredients']
                for table in critical_tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        self.logger.info(f"Table {table}: {count} records")
                    except sqlite3.OperationalError:
                        self.logger.error(f"Critical table missing: {table}")
                        return False
                
                # Test data integrity
                cursor.execute("""
                    SELECT COUNT(*) FROM recipe_ingredients ri
                    LEFT JOIN recipes r ON ri.recipe_id = r.id
                    LEFT JOIN inventory i ON ri.ingredient_id = i.id
                    WHERE r.id IS NULL OR i.id IS NULL
                """)
                orphaned_records = cursor.fetchone()[0]
                
                if orphaned_records > 0:
                    self.logger.warning(f"Found {orphaned_records} orphaned recipe ingredients")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Backup verification failed: {str(e)}")
            return False
    
    def calculate_checksum(self, file_path):
        """Calculate MD5 checksum for file integrity verification"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def cleanup_old_backups(self):
        """Remove backups older than retention period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            removed_count = 0
            
            for filename in os.listdir(self.backup_dir):
                if filename.startswith("restaurant_calculator_backup_"):
                    file_path = os.path.join(self.backup_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        # Also remove metadata file if it exists
                        metadata_file = file_path.replace('.db', '_metadata.json')
                        if os.path.exists(metadata_file):
                            os.remove(metadata_file)
                        removed_count += 1
                        self.logger.info(f"Removed old backup: {filename}")
            
            if removed_count > 0:
                self.logger.info(f"Cleaned up {removed_count} old backups")
            else:
                self.logger.info("No old backups to clean up")
                
        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}")
    
    def list_backups(self):
        """List all available backups with metadata"""
        backups = []
        
        for filename in sorted(os.listdir(self.backup_dir)):
            if filename.startswith("restaurant_calculator_backup_") and filename.endswith(".db"):
                backup_path = os.path.join(self.backup_dir, filename)
                metadata_path = backup_path.replace('.db', '_metadata.json')
                
                backup_info = {
                    "filename": filename,
                    "path": backup_path,
                    "size": os.path.getsize(backup_path),
                    "created": datetime.fromtimestamp(os.path.getctime(backup_path)).isoformat()
                }
                
                # Load metadata if available
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        backup_info["metadata"] = json.load(f)
                
                backups.append(backup_info)
        
        return backups
    
    def restore_backup(self, backup_path, target_path=None):
        """Restore database from backup"""
        if target_path is None:
            target_path = self.source_db + ".restored"
        
        try:
            # Verify backup before restore
            if not self.verify_backup(backup_path):
                raise Exception("Backup verification failed - cannot restore")
            
            # Create restore
            shutil.copy2(backup_path, target_path)
            self.logger.info(f"✅ Database restored to: {target_path}")
            
            return target_path
            
        except Exception as e:
            self.logger.error(f"❌ Restore failed: {str(e)}")
            raise


def main():
    """Main backup execution function"""
    backup_system = DatabaseBackupSystem()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            backup_path, metadata = backup_system.create_backup()
            print(f"✅ Backup created: {backup_path}")
            
        elif command == "list":
            backups = backup_system.list_backups()
            print(f"📋 Found {len(backups)} backups:")
            for backup in backups:
                print(f"  {backup['filename']} ({backup['size']:,} bytes) - {backup['created']}")
                
        elif command == "cleanup":
            backup_system.cleanup_old_backups()
            
        elif command == "verify":
            if len(sys.argv) > 2:
                backup_path = sys.argv[2]
                if backup_system.verify_backup(backup_path):
                    print("✅ Backup verification passed")
                else:
                    print("❌ Backup verification failed")
            else:
                print("Usage: python backup_automation.py verify <backup_path>")
                
        elif command == "restore":
            if len(sys.argv) > 2:
                backup_path = sys.argv[2]
                target_path = sys.argv[3] if len(sys.argv) > 3 else None
                restored_path = backup_system.restore_backup(backup_path, target_path)
                print(f"✅ Database restored to: {restored_path}")
            else:
                print("Usage: python backup_automation.py restore <backup_path> [target_path]")
                
        else:
            print("Unknown command. Available: create, list, cleanup, verify, restore")
    else:
        # Default: create backup and cleanup old ones
        print("🔄 Running automated backup process...")
        backup_path, metadata = backup_system.create_backup()
        backup_system.cleanup_old_backups()
        print(f"✅ Automated backup complete: {backup_path}")


if __name__ == "__main__":
    main()