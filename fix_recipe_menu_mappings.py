#!/usr/bin/env python3
"""
Fix recipe-menu item mappings based on Toast export data
Uses the LEA_JANES_Recipe_List_Summary as the authoritative source
"""

import sqlite3
import csv

def load_toast_mappings():
    """Load the correct recipe mappings from Toast export"""
    toast_file = 'reference/LJ_DATA_Ref/LEA_JANES_Recipe_List_Summary_7_4_2025, 7_51_55 PM.csv'
    
    mappings = {}
    with open(toast_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            recipe_name = row['RecipeName']
            recipe_type = row['Type']
            menu_price = float(row['MenuPrice']) if row['MenuPrice'] else 0
            status = row['Status']
            
            # Only track recipes with menu prices (actual menu items)
            if menu_price > 0 and recipe_type == 'Recipe':
                mappings[recipe_name] = {
                    'price': menu_price,
                    'status': status,
                    'type': recipe_type
                }
    
    return mappings

def analyze_current_mappings():
    """Analyze current database mappings vs Toast data"""
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    print("=== ANALYZING RECIPE-MENU ITEM MAPPINGS ===\n")
    
    # Get Toast mappings
    toast_mappings = load_toast_mappings()
    print(f"Found {len(toast_mappings)} menu items in Toast export\n")
    
    # Get current database mappings
    db_mappings = cursor.execute("""
        SELECT mi.id, mi.item_name, r.recipe_name, mi.menu_price, r.status
        FROM menu_items mi
        JOIN recipes r ON mi.recipe_id = r.id
        WHERE mi.id IN (SELECT menu_item_id FROM menu_menu_items WHERE menu_id = 5) -- Current Menu
        ORDER BY mi.item_name
    """).fetchall()
    
    issues = []
    correct = []
    
    for item_id, item_name, recipe_name, db_price, db_status in db_mappings:
        # Check if recipe exists in Toast data
        if recipe_name in toast_mappings:
            toast_data = toast_mappings[recipe_name]
            
            # Check price match
            if abs(float(db_price) - toast_data['price']) > 0.01:
                issues.append({
                    'item': item_name,
                    'recipe': recipe_name,
                    'issue': f"Price mismatch: DB=${db_price} vs Toast=${toast_data['price']}"
                })
            else:
                correct.append(f"{item_name} → {recipe_name} (${db_price})")
        else:
            # Recipe not in Toast export as a menu item
            issues.append({
                'item': item_name,
                'recipe': recipe_name,
                'issue': "Recipe not found in Toast menu items"
            })
    
    print(f"✓ Correct mappings: {len(correct)}")
    print(f"✗ Issues found: {len(issues)}\n")
    
    if issues:
        print("Issues to fix:")
        for issue in issues[:10]:  # Show first 10
            print(f"  - {issue['item']}: {issue['issue']}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")
    
    conn.close()
    return issues, toast_mappings

def fix_menu_prices():
    """Update menu prices to match Toast export"""
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    print("\n=== FIXING MENU PRICES ===\n")
    
    toast_mappings = load_toast_mappings()
    
    cursor.execute("BEGIN TRANSACTION")
    
    try:
        fixed_count = 0
        
        # Get all menu items with their recipes
        items = cursor.execute("""
            SELECT mi.id, mi.item_name, r.recipe_name, mi.menu_price
            FROM menu_items mi
            JOIN recipes r ON mi.recipe_id = r.id
        """).fetchall()
        
        for item_id, item_name, recipe_name, current_price in items:
            if recipe_name in toast_mappings:
                correct_price = toast_mappings[recipe_name]['price']
                
                if abs(float(current_price) - correct_price) > 0.01:
                    # Update price
                    cursor.execute("""
                        UPDATE menu_items 
                        SET menu_price = ?,
                            food_cost_percent = ROUND((food_cost / ?) * 100, 2),
                            gross_profit = ? - food_cost
                        WHERE id = ?
                    """, (correct_price, correct_price, correct_price, item_id))
                    
                    print(f"Fixed {item_name}: ${current_price} → ${correct_price}")
                    fixed_count += 1
        
        # Also update recipe menu prices
        for recipe_name, data in toast_mappings.items():
            cursor.execute("""
                UPDATE recipes 
                SET menu_price = ?
                WHERE recipe_name = ? AND recipe_type = 'Recipe'
            """, (data['price'], recipe_name))
        
        cursor.execute("COMMIT")
        print(f"\n✓ Fixed {fixed_count} menu item prices")
        
    except Exception as e:
        cursor.execute("ROLLBACK")
        print(f"✗ Error: {e}")
        raise
    
    finally:
        conn.close()

def create_missing_menu_items():
    """Create menu items for recipes that should be on the menu"""
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    print("\n=== CHECKING FOR MISSING MENU ITEMS ===\n")
    
    toast_mappings = load_toast_mappings()
    
    # Find recipes that exist but have no menu items
    missing = cursor.execute("""
        SELECT r.id, r.recipe_name, r.recipe_group, r.food_cost
        FROM recipes r
        WHERE r.recipe_name IN ({})
        AND r.recipe_type = 'Recipe'
        AND NOT EXISTS (
            SELECT 1 FROM menu_items mi WHERE mi.recipe_id = r.id
        )
    """.format(','.join('?' * len(toast_mappings))), 
    list(toast_mappings.keys())).fetchall()
    
    if missing:
        print(f"Found {len(missing)} recipes without menu items:")
        for recipe_id, recipe_name, group, food_cost in missing:
            toast_data = toast_mappings[recipe_name]
            print(f"  - {recipe_name} (${toast_data['price']})")
    else:
        print("✓ All Toast menu items have corresponding entries")
    
    conn.close()

def validate_final_state():
    """Validate the final state matches Toast export"""
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    print("\n=== FINAL VALIDATION ===\n")
    
    # Check menu prices match
    mismatches = cursor.execute("""
        SELECT mi.item_name, r.recipe_name, mi.menu_price, r.menu_price as recipe_price
        FROM menu_items mi
        JOIN recipes r ON mi.recipe_id = r.id
        WHERE mi.id IN (SELECT menu_item_id FROM menu_menu_items WHERE menu_id = 5)
        AND ABS(mi.menu_price - r.menu_price) > 0.01
        AND r.recipe_type = 'Recipe'
    """).fetchall()
    
    if mismatches:
        print(f"✗ Found {len(mismatches)} price mismatches between menu_items and recipes")
    else:
        print("✓ All menu prices are consistent")
    
    # Check food cost percentages
    high_costs = cursor.execute("""
        SELECT mi.item_name, mi.food_cost_percent
        FROM menu_items mi
        WHERE mi.food_cost_percent > 50
        AND mi.id IN (SELECT menu_item_id FROM menu_menu_items WHERE menu_id = 5)
    """).fetchall()
    
    if high_costs:
        print(f"\n⚠️  {len(high_costs)} menu items have >50% food cost:")
        for name, pct in high_costs[:5]:
            print(f"  - {name}: {pct:.1f}%")
    
    conn.close()

if __name__ == "__main__":
    # Analyze current state
    issues, mappings = analyze_current_mappings()
    
    if issues:
        # Fix prices
        fix_menu_prices()
    
    # Check for missing items
    create_missing_menu_items()
    
    # Validate
    validate_final_state()
    
    print("\n🎉 Recipe-menu item mapping review complete!")