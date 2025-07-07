#!/usr/bin/env python3
"""
Complete fix for pack sizes based on analysis of original CSV data
"""

import sqlite3
import re

DATABASE = 'restaurant_calculator.db'

def fix_all_pack_sizes():
    """Fix pack sizes based on patterns found in the data"""
    
    fixes = [
        # Cheese sauce - 6 x 5 lb loaves
        (138, '6 x 5 lb', 'Cheese sauce comes in 5 lb loaves'),
        
        # Salt - 9 x 3 lb boxes
        (711, '9 x 3 lb', 'Kosher salt typically in 3 lb boxes'),
        
        # More specific fixes based on common patterns
    ]
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        
        # Apply specific fixes
        for item_id, new_pack_size, reason in fixes:
            print(f"Fixing item {item_id}: {new_pack_size} ({reason})")
            cursor.execute('UPDATE inventory SET pack_size = ? WHERE id = ?', 
                         (new_pack_size, item_id))
        
        # Fix items where unit_measure gives us a clue
        cursor.execute('''
            UPDATE inventory 
            SET pack_size = pack_size || ' ' || unit_measure
            WHERE pack_size LIKE '% x %'
              AND pack_size NOT LIKE '% x % %'
              AND unit_measure IN ('lb', 'oz', 'kg', 'g')
              AND pack_size NOT LIKE '% lb%' 
              AND pack_size NOT LIKE '% oz%'
              AND pack_size NOT LIKE '% kg%'
              AND pack_size NOT LIKE '% g%'
        ''')
        
        # Fix common case patterns
        updates = [
            # Milk - gallons
            ("UPDATE inventory SET pack_size = '4 x 1 gal' WHERE item_description LIKE '%Milk%' AND pack_size = '4 x 1'", 'Fix milk gallons'),
            
            # Cream - quarts  
            ("UPDATE inventory SET pack_size = '12 x 1 qt' WHERE item_description LIKE '%Cream%' AND pack_size = '12 x 1'", 'Fix cream quarts'),
            
            # Eggs - dozen
            ("UPDATE inventory SET pack_size = '15 dz' WHERE item_description LIKE '%Egg%' AND pack_size = '1 x 180'", 'Fix eggs to 15 dozen'),
            
            # Fix other "1 x N" patterns based on description
            ("UPDATE inventory SET pack_size = pack_size || ' lb' WHERE pack_size LIKE '1 x %' AND item_description LIKE '%Chicken%' AND pack_size NOT LIKE '% lb%'", 'Fix chicken pounds'),
        ]
        
        for query, description in updates:
            print(f"\n{description}...")
            cursor.execute(query)
            print(f"  Updated {cursor.rowcount} items")
        
        conn.commit()
        print("\nPack size fixes completed!")

if __name__ == '__main__':
    fix_all_pack_sizes()