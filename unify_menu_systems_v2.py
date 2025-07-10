#!/usr/bin/env python3
"""
Unify the dual menu system (menu_versions vs menus tables)
Ensures consistency and removes duplicates
"""

import sqlite3
from datetime import datetime

def analyze_menu_systems():
    """Analyze current state of both menu systems"""
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    print("=== MENU SYSTEM ANALYSIS ===\n")
    
    # Check menu_versions
    print("1. Menu Versions Table:")
    versions = cursor.execute("""
        SELECT mv.*, COUNT(mi.id) as item_count
        FROM menu_versions mv
        LEFT JOIN menu_items mi ON mi.version_id = mv.id
        GROUP BY mv.id
        ORDER BY mv.id
    """).fetchall()
    
    for v in versions:
        print(f"   ID: {v[0]}, Name: {v[1]}, Active: {v[3]}, Items: {v[-1]}")
    
    # Check menus table
    print("\n2. Menus Table:")
    menus = cursor.execute("""
        SELECT m.*, COUNT(mmi.menu_item_id) as item_count
        FROM menus m
        LEFT JOIN menu_menu_items mmi ON m.id = mmi.menu_id
        GROUP BY m.id
        ORDER BY m.id
    """).fetchall()
    
    for m in menus:
        print(f"   ID: {m[0]}, Name: {m[1]}, Active: {m[3]}, Items: {m[-1]}")
    
    # Check for orphaned items
    orphans = cursor.execute("""
        SELECT COUNT(*) FROM menu_items 
        WHERE version_id IS NULL OR version_id = 0
    """).fetchone()[0]
    
    print(f"\n3. Orphaned menu items (no version_id): {orphans}")
    
    conn.close()
    return versions, menus

def unify_menu_systems():
    """Unify the menu systems - use menus table as primary"""
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    print("\n=== UNIFYING MENU SYSTEMS ===\n")
    
    cursor.execute("BEGIN TRANSACTION")
    
    try:
        # Step 1: Ensure all menu_items have proper menu assignments
        print("1. Checking menu item assignments...")
        
        # Get items that have version_id but no menu assignment
        unassigned = cursor.execute("""
            SELECT mi.id, mi.item_name, mi.version_id, mv.version_name
            FROM menu_items mi
            JOIN menu_versions mv ON mi.version_id = mv.id
            WHERE mi.id NOT IN (SELECT menu_item_id FROM menu_menu_items)
        """).fetchall()
        
        if unassigned:
            print(f"   Found {len(unassigned)} unassigned items")
            # These items need to be assigned to appropriate menus
            # For now, we'll report them
            for item in unassigned[:5]:  # Show first 5
                print(f"     - {item[1]} (version: {item[3]})")
        
        # Step 2: Remove the duplicate "weird" menu
        print("\n2. Removing invalid menus...")
        cursor.execute("DELETE FROM menu_menu_items WHERE menu_id IN (SELECT id FROM menus WHERE menu_name = 'weird')")
        cursor.execute("DELETE FROM menus WHERE menu_name = 'weird'")
        print("   Removed 'weird' menu")
        
        # Step 3: Ensure V3 Planning Menu is properly set up
        print("\n3. Checking V3 Planning Menu...")
        v3_menu = cursor.execute("SELECT * FROM menus WHERE menu_name = 'V3 Planning Menu'").fetchone()
        if v3_menu:
            print(f"   V3 Planning Menu exists (ID: {v3_menu[0]}, Active: {v3_menu[3]})")
            # Ensure it's inactive until ready
            if v3_menu[3] == 1:  # is_active
                cursor.execute("UPDATE menus SET is_active = 0 WHERE id = ?", (v3_menu[0],))
                print("   Set V3 Planning Menu to inactive")
        
        # Step 4: Sync active status between systems
        print("\n4. Syncing active status...")
        # Only Current Menu should be active
        cursor.execute("UPDATE menu_versions SET is_active = 0 WHERE version_name != 'Current Menu'")
        cursor.execute("UPDATE menu_versions SET is_active = 1 WHERE version_name = 'Current Menu'")
        cursor.execute("UPDATE menus SET is_active = 0 WHERE menu_name != 'Current Menu'")
        cursor.execute("UPDATE menus SET is_active = 1 WHERE menu_name = 'Current Menu'")
        print("   Set 'Current Menu' as the only active menu")
        
        cursor.execute("COMMIT")
        print("\n✓ Menu systems unified successfully!")
        
    except Exception as e:
        cursor.execute("ROLLBACK")
        print(f"\n✗ Error: {e}")
        raise
    
    finally:
        conn.close()

def create_menu_view():
    """Create a unified view for menu management"""
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    print("\n=== CREATING UNIFIED MENU VIEW ===\n")
    
    # Drop existing view if it exists
    cursor.execute("DROP VIEW IF EXISTS unified_menu_items")
    
    # Create unified view
    cursor.execute("""
        CREATE VIEW unified_menu_items AS
        SELECT 
            mi.id,
            mi.item_name,
            mi.menu_group,
            mi.item_description,
            mi.recipe_id,
            r.recipe_name,
            mi.menu_price,
            mi.food_cost,
            mi.food_cost_percent,
            mi.status,
            m.menu_name,
            m.id as menu_id,
            mmi.category,
            mmi.sort_order,
            mmi.is_available
        FROM menu_items mi
        LEFT JOIN recipes r ON mi.recipe_id = r.id
        LEFT JOIN menu_menu_items mmi ON mi.id = mmi.menu_item_id
        LEFT JOIN menus m ON mmi.menu_id = m.id
        WHERE m.menu_name IS NOT NULL
    """)
    
    print("✓ Created unified_menu_items view")
    
    conn.commit()
    conn.close()

def validate_unification():
    """Validate the unification was successful"""
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    print("\n=== VALIDATION RESULTS ===\n")
    
    # Check for consistency
    issues = []
    
    # Test 1: All items should have menu assignments
    orphans = cursor.execute("""
        SELECT COUNT(*) FROM menu_items 
        WHERE id NOT IN (SELECT menu_item_id FROM menu_menu_items)
    """).fetchone()[0]
    
    if orphans > 0:
        issues.append(f"{orphans} menu items have no menu assignment")
    
    # Test 2: No duplicate menu names
    dupes = cursor.execute("""
        SELECT menu_name, COUNT(*) as cnt 
        FROM menus 
        GROUP BY menu_name 
        HAVING cnt > 1
    """).fetchall()
    
    if dupes:
        issues.append(f"Duplicate menu names found: {dupes}")
    
    # Test 3: Only one active menu
    active = cursor.execute("SELECT COUNT(*) FROM menus WHERE is_active = 1").fetchone()[0]
    if active != 1:
        issues.append(f"{active} active menus found (should be 1)")
    
    if issues:
        print("✗ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ All validation checks passed!")
    
    conn.close()
    
    return len(issues) == 0

if __name__ == "__main__":
    # Analyze current state
    analyze_menu_systems()
    
    # Unify the systems
    unify_menu_systems()
    
    # Create unified view
    create_menu_view()
    
    # Validate
    if validate_unification():
        print("\n🎉 Menu system unification completed successfully!")
    else:
        print("\n⚠️  Menu system unified but some issues remain")