#!/usr/bin/env python3
"""
Automatic git commit utility for database changes
"""

import subprocess
import os
from datetime import datetime
import sqlite3
import hashlib
import json

class AutoCommit:
    """Automatically commit database changes to git"""
    
    def __init__(self, db_path='restaurant_calculator.db'):
        self.db_path = db_path
        self.state_file = '.db_state.json'
        
    def get_db_hash(self):
        """Calculate hash of database content"""
        with open(self.db_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def get_db_stats(self):
        """Get database statistics for commit message"""
        conn = sqlite3.connect(self.db_path)
        stats = {}
        
        tables = ['inventory', 'recipes', 'recipe_ingredients', 'menu_items', 'vendors', 'vendor_products']
        
        for table in tables:
            try:
                count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
                stats[table] = count
            except:
                stats[table] = 0
        
        conn.close()
        return stats
    
    def load_state(self):
        """Load previous database state"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {'hash': None, 'stats': {}}
    
    def save_state(self, state):
        """Save current database state"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f)
    
    def git_add_and_commit(self, message):
        """Add database and commit to git"""
        try:
            # Add database file
            subprocess.run(['git', 'add', self.db_path], check=True)
            
            # Add backup files if they exist
            if os.path.exists('backups'):
                subprocess.run(['git', 'add', 'backups/'], check=True)
            
            # Commit
            subprocess.run(['git', 'commit', '-m', message], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def generate_commit_message(self, old_stats, new_stats):
        """Generate descriptive commit message based on changes"""
        changes = []
        
        for table, new_count in new_stats.items():
            old_count = old_stats.get(table, 0)
            diff = new_count - old_count
            
            if diff > 0:
                changes.append(f"+{diff} {table}")
            elif diff < 0:
                changes.append(f"{diff} {table}")
        
        if not changes:
            return "chore: update database"
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        change_summary = ", ".join(changes[:3])  # First 3 changes
        
        if len(changes) > 3:
            change_summary += f" and {len(changes) - 3} more"
        
        return f"data: auto-commit database changes [{timestamp}]\n\n{change_summary}"
    
    def check_and_commit(self):
        """Check if database changed and commit if needed"""
        # Get current state
        current_hash = self.get_db_hash()
        current_stats = self.get_db_stats()
        
        # Load previous state
        prev_state = self.load_state()
        
        # Check if changed
        if current_hash != prev_state['hash']:
            # Generate commit message
            message = self.generate_commit_message(
                prev_state.get('stats', {}), 
                current_stats
            )
            
            # Commit changes
            if self.git_add_and_commit(message):
                print(f"✅ Auto-committed database changes: {message.split('[')[0].strip()}")
                
                # Save new state
                self.save_state({
                    'hash': current_hash,
                    'stats': current_stats
                })
                return True
            else:
                print("❌ Failed to commit database changes")
                return False
        
        return False

def integrate_with_flask(app):
    """Integrate auto-commit with Flask app"""
    from functools import wraps
    
    auto_commit = AutoCommit()
    
    def with_auto_commit(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            # Check and commit after the request
            auto_commit.check_and_commit()
            return result
        return decorated_function
    
    # Decorator for routes that modify database
    return with_auto_commit

if __name__ == "__main__":
    # Manual run
    auto_commit = AutoCommit()
    if auto_commit.check_and_commit():
        print("Database changes committed")
    else:
        print("No database changes detected")