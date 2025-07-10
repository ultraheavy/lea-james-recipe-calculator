"""
Activity Logging System for Dashboard Recent Activity
This module handles tracking user activities for the dashboard's recent activity section.
"""

import sqlite3
from datetime import datetime
import os

# Use the same database path as the main app
DATABASE = 'restaurant_calculator.db'

def get_db_connection():
    """Get database connection using the same pattern as main app"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_activity_table():
    """Initialize the activity_log table if it doesn't exist"""
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_type TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id INTEGER,
                entity_name TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                user_id TEXT DEFAULT 'system',
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index for faster queries
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_activity_log_date 
            ON activity_log(created_date DESC)
        ''')
        
        conn.commit()

def log_activity(activity_type, entity_type, entity_id, entity_name, action, details=None, user_id='system'):
    """
    Log an activity to the activity_log table
    
    Args:
        activity_type: Type of activity ('create', 'update', 'delete', 'import')
        entity_type: Type of entity ('recipe', 'inventory', 'menu_item', 'vendor')
        entity_id: ID of the entity (can be None for bulk operations)
        entity_name: Human-readable name of the entity
        action: Description of what was done
        details: Additional details (optional)
        user_id: User who performed the action (default: 'system')
    """
    init_activity_table()  # Ensure table exists
    
    with get_db_connection() as conn:
        conn.execute('''
            INSERT INTO activity_log 
            (activity_type, entity_type, entity_id, entity_name, action, details, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (activity_type, entity_type, entity_id, entity_name, action, details, user_id))
        conn.commit()

def get_recent_activities(limit=10):
    """
    Get recent activities for the dashboard
    
    Args:
        limit: Maximum number of activities to return (default: 10)
    
    Returns:
        List of activity dictionaries with formatted data
    """
    init_activity_table()  # Ensure table exists
    
    with get_db_connection() as conn:
        activities = conn.execute('''
            SELECT 
                activity_type,
                entity_type,
                entity_id,
                entity_name,
                action,
                details,
                created_date
            FROM activity_log 
            ORDER BY created_date DESC 
            LIMIT ?
        ''', (limit,)).fetchall()
        
        # Convert to list of dictionaries with formatted data
        formatted_activities = []
        for activity in activities:
            # Format the timestamp
            created_date = datetime.fromisoformat(activity['created_date'].replace('Z', '+00:00'))
            time_ago = get_time_ago(created_date)
            
            # Determine icon based on entity type
            icon_class = get_icon_class(activity['entity_type'], activity['activity_type'])
            
            formatted_activities.append({
                'entity_type': activity['entity_type'],
                'entity_name': activity['entity_name'],
                'action': activity['action'],
                'time_ago': time_ago,
                'icon_class': icon_class,
                'activity_type': activity['activity_type']
            })
        
        return formatted_activities

def get_time_ago(timestamp):
    """Convert timestamp to human-readable time ago format"""
    now = datetime.now()
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    diff = now - timestamp
    
    if diff.days > 0:
        if diff.days == 1:
            return "1 day ago"
        return f"{diff.days} days ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        if hours == 1:
            return "1 hour ago"
        return f"{hours} hours ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        if minutes == 1:
            return "1 minute ago"
        return f"{minutes} minutes ago"
    else:
        return "Just now"

def get_icon_class(entity_type, activity_type):
    """Get CSS icon class based on entity type and activity"""
    icon_map = {
        'recipe': 'icon-grains',
        'inventory': 'icon-produce', 
        'menu_item': 'icon-sauce',
        'vendor': 'icon-beverage',
        'menu': 'icon-misc'
    }
    return icon_map.get(entity_type, 'icon-misc')

# Convenience functions for common activities
def log_recipe_created(recipe_id, recipe_name):
    log_activity('create', 'recipe', recipe_id, recipe_name, 'New recipe created')

def log_recipe_updated(recipe_id, recipe_name, details=None):
    log_activity('update', 'recipe', recipe_id, recipe_name, 'Recipe updated', details)

def log_inventory_added(inventory_id, item_name):
    log_activity('create', 'inventory', inventory_id, item_name, 'New inventory item added')

def log_inventory_updated(inventory_id, item_name, details=None):
    log_activity('update', 'inventory', inventory_id, item_name, 'Inventory item updated', details)

def log_menu_item_created(menu_item_id, item_name):
    log_activity('create', 'menu_item', menu_item_id, item_name, 'New menu item added')

def log_menu_item_updated(menu_item_id, item_name, details=None):
    log_activity('update', 'menu_item', menu_item_id, item_name, 'Menu item updated', details)

def log_vendor_added(vendor_id, vendor_name):
    log_activity('create', 'vendor', vendor_id, vendor_name, 'New vendor added')

def log_bulk_import(entity_type, count, details=None):
    log_activity('import', entity_type, None, f'{count} {entity_type}s', f'Bulk import completed', details)

if __name__ == "__main__":
    # Test the activity logging system
    print("Testing activity logging system...")
    
    # Initialize table
    init_activity_table()
    
    # Add some test activities
    log_recipe_created(1, "Test Recipe")
    log_inventory_added(1, "Test Ingredient")
    log_menu_item_created(1, "Test Menu Item")
    
    # Get recent activities
    activities = get_recent_activities(5)
    
    print(f"Found {len(activities)} recent activities:")
    for activity in activities:
        print(f"- {activity['action']}: {activity['entity_name']} ({activity['time_ago']})")
    
    print("Activity logging system test completed!")
