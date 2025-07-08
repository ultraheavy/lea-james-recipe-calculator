#!/usr/bin/env python3
"""
One-time migration to clean up duplicate menus in production
"""
import sqlite3
import os

def cleanup_duplicate_menus():
    """Remove duplicate menu entries keeping only the first of each type"""
    
    db_path = os.environ.get('DATABASE_PATH', 'restaurant_calculator.db')
    
    if not os.path.exists(db_path):
        print("Database not found, skipping cleanup")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check for duplicates
        cursor.execute("""
            SELECT menu_name, COUNT(*) as count 
            FROM menus 
            GROUP BY menu_name 
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        
        if not duplicates:
            print("No duplicate menus found")
            return
            
        print(f"Found {len(duplicates)} menu types with duplicates")
        
        for menu_name, count in duplicates:
            print(f"  {menu_name}: {count} copies")
            
            # Keep the first one (lowest ID) and delete the rest
            cursor.execute("""
                DELETE FROM menus 
                WHERE menu_name = ? 
                AND id NOT IN (
                    SELECT MIN(id) 
                    FROM menus 
                    WHERE menu_name = ?
                )
            """, (menu_name, menu_name))
            
            deleted = cursor.rowcount
            print(f"    Deleted {deleted} duplicate(s)")
        
        conn.commit()
        print("\nDuplicate menus cleaned up successfully!")
        
        # Verify final state
        cursor.execute("SELECT id, menu_name FROM menus ORDER BY id")
        final_menus = cursor.fetchall()
        print("\nFinal menu list:")
        for menu_id, name in final_menus:
            print(f"  {menu_id}: {name}")
            
    except Exception as e:
        print(f"Error during cleanup: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup_duplicate_menus()