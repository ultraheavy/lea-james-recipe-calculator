#!/usr/bin/env python3
"""
Test script to demonstrate CSV import issues and fixes
"""

import sqlite3
from fixed_csv_importer import FixedCSVImporter
from pathlib import Path

def demonstrate_uom_parsing():
    """Demonstrate UOM parsing improvements"""
    print("=" * 60)
    print("UNIT OF MEASURE PARSING DEMONSTRATION")
    print("=" * 60)
    
    importer = FixedCSVImporter()
    
    # Test cases showing common problematic patterns
    test_measurements = [
        "2 x 4 oz",      # Complex pattern
        "10 oz",         # Simple pattern
        "5",             # No unit
        "1 slice",       # Unit with quantity
        "each",          # Just unit
        "2.5 lb",        # Decimal quantity
        "12 x 16 fl",    # Abbreviated fluid ounce
        "6 ea",          # Abbreviated each
        "1 x 5 lb",      # Single multiplier
        "3x4oz",         # No spaces
    ]
    
    print("\nOriginal -> Parsed (Quantity, Unit):")
    print("-" * 50)
    for measurement in test_measurements:
        quantity, unit = importer.parse_measurement(measurement)
        normalized_unit = importer.normalize_unit(unit)
        print(f"{measurement:15} -> ({quantity:6.1f}, '{normalized_unit}')")
        
def demonstrate_pack_size_issues():
    """Show pack size mapping problems from diagnostics"""
    print("\n" * 2)
    print("=" * 60)
    print("PACK SIZE MAPPING ISSUES FROM DIAGNOSTICS")
    print("=" * 60)
    
    # Connect to database to show actual discrepancies
    conn = sqlite3.connect('restaurant_calculator.db')
    conn.row_factory = sqlite3.Row
    
    # Get some examples of pack size mismatches
    cursor = conn.execute("""
        SELECT item_code, item_description, pack_size 
        FROM inventory 
        WHERE pack_size LIKE '%cs%' 
           OR pack_size LIKE '%case%'
           OR pack_size LIKE '%ct%'
        LIMIT 10
    """)
    
    print("\nProblematic pack sizes in database:")
    print("-" * 80)
    print(f"{'Item Code':15} {'Description':40} {'Pack Size':20}")
    print("-" * 80)
    
    for row in cursor:
        print(f"{row['item_code']:15} {row['item_description'][:40]:40} {row['pack_size']:20}")
        
    conn.close()
    
def demonstrate_csv_parsing():
    """Demonstrate parsing a real Toast CSV file"""
    print("\n" * 2)
    print("=" * 60)
    print("TOAST CSV PARSING DEMONSTRATION")
    print("=" * 60)
    
    # Find a sample recipe CSV
    csv_dir = Path('data/sources/data_sources_from_toast')
    recipe_files = list(csv_dir.glob('FC-*.csv'))
    
    if recipe_files:
        sample_file = recipe_files[0]
        print(f"\nParsing: {sample_file.name}")
        print("-" * 50)
        
        importer = FixedCSVImporter()
        recipe_data = importer.parse_toast_recipe_csv(str(sample_file))
        
        print(f"Recipe Name: {recipe_data['recipe_name']}")
        print(f"Ingredient Count: {len(recipe_data['ingredients'])}")
        print("\nFirst 5 ingredients:")
        print("-" * 80)
        print(f"{'Name':30} {'Qty':8} {'Unit':10} {'Cost':10}")
        print("-" * 80)
        
        for ing in recipe_data['ingredients'][:5]:
            print(f"{ing['name'][:30]:30} {ing['quantity']:8.2f} {ing['unit']:10} ${ing['cost']:9.2f}")
            
def show_diagnostic_summary():
    """Show summary of diagnostic findings"""
    print("\n" * 2)
    print("=" * 60)
    print("CSV IMPORT DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    # Read the summary file
    summary_files = list(Path('.').glob('csv_import_diagnostic_summary_*.txt'))
    if summary_files:
        latest_summary = sorted(summary_files)[-1]
        print(f"\nFrom: {latest_summary}")
        print("-" * 50)
        
        with open(latest_summary, 'r') as f:
            lines = f.readlines()
            
        # Show key findings
        in_summary = False
        for line in lines:
            if 'SUMMARY' in line:
                in_summary = True
            elif 'ISSUE BREAKDOWN' in line:
                in_summary = False
                break
            elif in_summary and line.strip():
                print(line.rstrip())
                
    print("\n" + "-" * 50)
    print("KEY FINDINGS:")
    print("1. 307 pack size mapping errors (cs->case, ct->count, etc.)")
    print("2. Unit abbreviations not normalized (fl->fl oz, ea->each)")
    print("3. Complex measurements like '2 x 4 oz' not parsed correctly")
    print("4. Toast CSV format requires special handling for headers")
    
def main():
    """Run all demonstrations"""
    print("\nCSV IMPORT FIXES DEMONSTRATION")
    print("=" * 80)
    
    demonstrate_uom_parsing()
    demonstrate_pack_size_issues()
    demonstrate_csv_parsing()
    show_diagnostic_summary()
    
    print("\n" * 2)
    print("RECOMMENDED ACTIONS:")
    print("=" * 60)
    print("1. Re-import all CSV data using fixed_csv_importer.py")
    print("2. Normalize all unit abbreviations in the database")
    print("3. Parse complex measurements during import")
    print("4. Add validation to catch formula fields")
    print("5. Handle Toast's special CSV header format")
    print("\nUse the fixed_csv_importer.py module for future imports!")

if __name__ == '__main__':
    main()