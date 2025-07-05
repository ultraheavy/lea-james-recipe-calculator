#!/usr/bin/env python3
"""
Re-import menu items from recipe data, linking them properly
"""

import sqlite3
import csv
from backup_database import backup_database

def reimport_menu_items():
    """Re-import menu items from the recipe summary CSV"""
    
    # First, backup the database
    print("📦 Creating database backup...")
    backup_database()
    
    conn = sqlite3.connect('restaurant_calculator.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Clear existing menu items
    print("\n🗑️  Clearing existing menu items...")
    cursor.execute('DELETE FROM menu_items')
    
    # Read the recipe summary CSV
    csv_path = 'reference/LJ_DATA_Ref/LEA_JANES_Recipe_List_Summary_7_4_2025, 7_51_55 PM.csv'
    
    print(f"\n📥 Importing menu items from: {csv_path}")
    
    imported_count = 0
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            recipe_name = row['RecipeName']
            recipe_group = row['RecipeGroup']
            recipe_type = row['Type']
            menu_price = float(row['MenuPrice']) if row['MenuPrice'] else 0
            food_cost = float(row['FoodCost']) if row['FoodCost'] else 0
            food_cost_percentage = float(row['FoodCostPercentage']) if row['FoodCostPercentage'] else 0
            gross_margin = float(row['GrossMargin']) if row['GrossMargin'] else 0
            
            # Skip prep recipes from menu items
            if recipe_type == 'PrepRecipe':
                continue
                
            # Skip items with $0 menu price
            if menu_price == 0:
                continue
            
            # Find matching recipe in database
            recipe = cursor.execute(
                'SELECT id FROM recipes WHERE recipe_name = ?', 
                (recipe_name,)
            ).fetchone()
            
            recipe_id = recipe['id'] if recipe else None
            
            # Calculate gross profit
            gross_profit = menu_price - food_cost if menu_price > 0 else 0
            
            # Insert menu item
            cursor.execute('''
                INSERT INTO menu_items 
                (item_name, menu_group, recipe_id, menu_price, 
                 food_cost, food_cost_percent, gross_profit)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                recipe_name,
                recipe_group or 'Main',
                recipe_id,
                menu_price,
                food_cost,
                food_cost_percentage,
                gross_profit
            ))
            
            imported_count += 1
            print(f"  ✓ {recipe_name} - ${menu_price:.2f} (Recipe ID: {recipe_id or 'No match'})")
    
    conn.commit()
    
    print(f"\n✅ Imported {imported_count} menu items")
    
    # Show summary
    total_items = cursor.execute('SELECT COUNT(*) FROM menu_items').fetchone()[0]
    linked_items = cursor.execute('SELECT COUNT(*) FROM menu_items WHERE recipe_id IS NOT NULL').fetchone()[0]
    
    print(f"\n📊 Menu Items Summary:")
    print(f"  - Total menu items: {total_items}")
    print(f"  - Linked to recipes: {linked_items}")
    print(f"  - Not linked: {total_items - linked_items}")
    
    conn.close()

if __name__ == "__main__":
    reimport_menu_items()