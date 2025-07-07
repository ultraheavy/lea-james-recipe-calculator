#!/usr/bin/env python3
"""
Populate the units table with standard unit conversions.
All conversions are to canonical units:
- Weight: grams
- Volume: milliliters  
- Count: each
"""

import sqlite3
from datetime import datetime

DATABASE = 'restaurant_calculator.db'

# Standard unit conversions
UNIT_DATA = [
    # WEIGHT UNITS (canonical: grams)
    {'name': 'Gram', 'symbol': 'g', 'dimension': 'WEIGHT', 'to_canonical_factor': 1.0, 'is_precise': True},
    {'name': 'Grams', 'symbol': 'grams', 'dimension': 'WEIGHT', 'to_canonical_factor': 1.0, 'is_precise': True},
    {'name': 'Kilogram', 'symbol': 'kg', 'dimension': 'WEIGHT', 'to_canonical_factor': 1000.0, 'is_precise': True},
    {'name': 'Milligram', 'symbol': 'mg', 'dimension': 'WEIGHT', 'to_canonical_factor': 0.001, 'is_precise': True},
    
    # Imperial weight
    {'name': 'Pound', 'symbol': 'lb', 'dimension': 'WEIGHT', 'to_canonical_factor': 453.59237, 'is_precise': True},
    {'name': 'Pounds', 'symbol': 'lbs', 'dimension': 'WEIGHT', 'to_canonical_factor': 453.59237, 'is_precise': True},
    {'name': 'Ounce', 'symbol': 'oz', 'dimension': 'WEIGHT', 'to_canonical_factor': 28.349523125, 'is_precise': True},
    {'name': 'Ounces', 'symbol': 'ounces', 'dimension': 'WEIGHT', 'to_canonical_factor': 28.349523125, 'is_precise': True},
    
    # VOLUME UNITS (canonical: milliliters)
    {'name': 'Milliliter', 'symbol': 'ml', 'dimension': 'VOLUME', 'to_canonical_factor': 1.0, 'is_precise': True},
    {'name': 'Milliliters', 'symbol': 'milliliters', 'dimension': 'VOLUME', 'to_canonical_factor': 1.0, 'is_precise': True},
    {'name': 'Liter', 'symbol': 'l', 'dimension': 'VOLUME', 'to_canonical_factor': 1000.0, 'is_precise': True},
    {'name': 'Liters', 'symbol': 'liters', 'dimension': 'VOLUME', 'to_canonical_factor': 1000.0, 'is_precise': True},
    
    # Imperial volume  
    {'name': 'Fluid Ounce', 'symbol': 'fl oz', 'dimension': 'VOLUME', 'to_canonical_factor': 29.5735295625, 'is_precise': True},
    {'name': 'Fluid Ounces', 'symbol': 'fl ounces', 'dimension': 'VOLUME', 'to_canonical_factor': 29.5735295625, 'is_precise': True},
    {'name': 'Cup', 'symbol': 'cup', 'dimension': 'VOLUME', 'to_canonical_factor': 236.588237, 'is_precise': True},
    {'name': 'Cups', 'symbol': 'cups', 'dimension': 'VOLUME', 'to_canonical_factor': 236.588237, 'is_precise': True},
    {'name': 'Pint', 'symbol': 'pt', 'dimension': 'VOLUME', 'to_canonical_factor': 473.176473, 'is_precise': True},
    {'name': 'Pints', 'symbol': 'pints', 'dimension': 'VOLUME', 'to_canonical_factor': 473.176473, 'is_precise': True},
    {'name': 'Quart', 'symbol': 'qt', 'dimension': 'VOLUME', 'to_canonical_factor': 946.352946, 'is_precise': True},
    {'name': 'Quarts', 'symbol': 'quarts', 'dimension': 'VOLUME', 'to_canonical_factor': 946.352946, 'is_precise': True},
    {'name': 'Gallon', 'symbol': 'gal', 'dimension': 'VOLUME', 'to_canonical_factor': 3785.411784, 'is_precise': True},
    {'name': 'Gallons', 'symbol': 'gallons', 'dimension': 'VOLUME', 'to_canonical_factor': 3785.411784, 'is_precise': True},
    
    # Kitchen volume measurements
    {'name': 'Tablespoon', 'symbol': 'tbsp', 'dimension': 'VOLUME', 'to_canonical_factor': 14.7867648, 'is_precise': True},
    {'name': 'Tablespoons', 'symbol': 'tablespoons', 'dimension': 'VOLUME', 'to_canonical_factor': 14.7867648, 'is_precise': True},
    {'name': 'Teaspoon', 'symbol': 'tsp', 'dimension': 'VOLUME', 'to_canonical_factor': 4.92892159, 'is_precise': True},
    {'name': 'Teaspoons', 'symbol': 'teaspoons', 'dimension': 'VOLUME', 'to_canonical_factor': 4.92892159, 'is_precise': True},
    
    # COUNT UNITS (canonical: each)
    {'name': 'Each', 'symbol': 'each', 'dimension': 'COUNT', 'to_canonical_factor': 1.0, 'is_precise': True},
    {'name': 'Each', 'symbol': 'ea', 'dimension': 'COUNT', 'to_canonical_factor': 1.0, 'is_precise': True},
    {'name': 'Piece', 'symbol': 'piece', 'dimension': 'COUNT', 'to_canonical_factor': 1.0, 'is_precise': True},
    {'name': 'Pieces', 'symbol': 'pieces', 'dimension': 'COUNT', 'to_canonical_factor': 1.0, 'is_precise': True},
    {'name': 'Unit', 'symbol': 'unit', 'dimension': 'COUNT', 'to_canonical_factor': 1.0, 'is_precise': True},
    {'name': 'Units', 'symbol': 'units', 'dimension': 'COUNT', 'to_canonical_factor': 1.0, 'is_precise': True},
    {'name': 'Dozen', 'symbol': 'dozen', 'dimension': 'COUNT', 'to_canonical_factor': 12.0, 'is_precise': True},
    {'name': 'Dozen', 'symbol': 'doz', 'dimension': 'COUNT', 'to_canonical_factor': 12.0, 'is_precise': True},
    
    # Common Toast POS variations
    {'name': 'Ounce Weight', 'symbol': 'oz wt', 'dimension': 'WEIGHT', 'to_canonical_factor': 28.349523125, 'is_precise': True},
    {'name': 'Pound Weight', 'symbol': 'lb wt', 'dimension': 'WEIGHT', 'to_canonical_factor': 453.59237, 'is_precise': True},
    {'name': 'Fluid Ounce', 'symbol': 'fl.oz', 'dimension': 'VOLUME', 'to_canonical_factor': 29.5735295625, 'is_precise': True},
    {'name': 'Fluid Ounce', 'symbol': 'fluid oz', 'dimension': 'VOLUME', 'to_canonical_factor': 29.5735295625, 'is_precise': True},
]


def populate_units():
    """Populate the units table with standard conversions."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Clear existing units
        cursor.execute('DELETE FROM units')
        
        # Insert unit data
        for unit in UNIT_DATA:
            cursor.execute('''
                INSERT INTO units (name, symbol, dimension, to_canonical_factor, is_precise)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                unit['name'],
                unit['symbol'],
                unit['dimension'],
                unit['to_canonical_factor'],
                unit['is_precise']
            ))
        
        conn.commit()
        print(f"Successfully populated {len(UNIT_DATA)} units")
        
        # Display summary
        for dimension in ['WEIGHT', 'VOLUME', 'COUNT']:
            count = cursor.execute('SELECT COUNT(*) FROM units WHERE dimension = ?', (dimension,)).fetchone()[0]
            print(f"  {dimension}: {count} units")
            
    except Exception as e:
        print(f"Error populating units: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == '__main__':
    populate_units()