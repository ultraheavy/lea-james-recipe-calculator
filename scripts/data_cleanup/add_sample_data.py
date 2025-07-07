#!/usr/bin/env python3
"""
Add sample data to test the restaurant calculator app
"""

import sqlite3

DATABASE = 'restaurant_calculator.db'

def add_sample_data():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        # Add sample inventory items
        sample_inventory = [
            ('001', 'Ground Beef 80/20', 4.99, 'LB', 'LB', 'OZ', 85.0),
            ('002', 'Yellow Onions', 1.29, 'LB', 'LB', 'OZ', 90.0),
            ('003', 'Hamburger Buns', 2.49, 'EA', 'Package of 8', 'EA', 100.0),
            ('004', 'American Cheese', 3.99, 'LB', 'LB', 'OZ', 95.0),
            ('005', 'Lettuce Head', 1.99, 'EA', 'EA', 'OZ', 75.0),
            ('006', 'Tomatoes', 2.99, 'LB', 'LB', 'OZ', 80.0),
            ('007', 'Vegetable Oil', 8.99, 'Bottle', '1 Gallon', 'OZ', 100.0),
            ('008', 'Salt', 0.99, 'Box', 'Box', 'tsp', 100.0),
            ('009', 'Black Pepper', 3.99, 'Jar', 'Jar', 'tsp', 100.0),
            ('010', 'Flour', 2.99, 'Bag', '5 LB Bag', 'Cup', 100.0),
        ]
        
        for item in sample_inventory:
            try:
                cursor.execute('''
                    INSERT INTO inventory 
                    (item_number, item_description, current_price, unit_measure, 
                     purchase_unit, recipe_cost_unit, yield_percent)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', item)
            except sqlite3.IntegrityError:
                print(f"Item {item[0]} already exists, skipping...")
        
        # Add sample recipes
        sample_recipes = [
            ('Classic Hamburger', 1, '4 burgers', '1 day', 'Grill station', 
             '1. Form 4oz patties from ground beef\n2. Season with salt and pepper\n3. Grill 4 minutes per side\n4. Add cheese in last minute\n5. Toast buns\n6. Assemble with lettuce and tomato'),
            ('French Fries', 2, '4 servings', '1 shift', 'Fry station',
             '1. Cut potatoes into fries\n2. Soak in water 30 minutes\n3. Fry at 350°F for 3-4 minutes\n4. Season with salt immediately'),
            ('Basic Burger Sauce', 3, '1 cup', '3 days', 'Prep cook',
             '1. Mix mayonnaise with ketchup\n2. Add pickle relish and seasonings\n3. Refrigerate until needed'),
        ]
        
        for recipe in sample_recipes:
            try:
                cursor.execute('''
                    INSERT INTO recipes 
                    (recipe_name, recipe_number, yield_amount, shelf_life, station, procedure)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', recipe)
            except sqlite3.IntegrityError:
                print(f"Recipe {recipe[0]} already exists, skipping...")
        
        conn.commit()
        print("Sample data added successfully!")

if __name__ == '__main__':
    add_sample_data()
