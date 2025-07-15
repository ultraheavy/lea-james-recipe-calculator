#!/usr/bin/env python3
"""
Test duplicate recipe handling by creating test CSV files
"""

import os
import shutil
from datetime import datetime

# Test directory
test_dir = "test_csv_duplicates"
os.makedirs(test_dir, exist_ok=True)

# Sample recipe content
sample_csv = """Location,Lea James Hot Chicken,,,,Date & Time,07/08/2025 3:01,
Prep Recipe Name,{recipe_name},,,,,,
,,,,,,,
Type,Portion,Portion Size,Batch Size,Shelf Life,PrepRecipe Yield,Prep Time,Cook Time
Sauces,1,1 ea,4 gallon,7 Days,100%,15 mins,5 mins
,,,,,,,
Food Cost,Labor Cost,Prime Cost,Unit Cost,,,,
$10.00,$0.00,$10.00,$2.50/ea,,,,
,,,,,,,
Ingredient,Type,Measurement,Yield,Usable Yield,Cost,,
"Dry Goods, Salt, Kosher",Product,1 pound,100%,100%,$2.00,,
"Dry Goods, Pepper, Black",Product,0.5 pound,100%,100%,$3.00,,
"Produce, Onion, Yellow",Product,2 pound,100%,100%,$5.00,,
"""

# Create duplicate files for testing
recipes_to_duplicate = [
    ("Test Sauce Alpha", ["20250708_141000", "20250708_213000", "20250709_090000"]),
    ("Test Marinade Beta", ["20250708_141500", "20250708_213500"]),
    ("Test Dressing Gamma", ["20250708_142000"])
]

print(f"Creating test duplicate files in {test_dir}/")
for recipe_name, timestamps in recipes_to_duplicate:
    for ts in timestamps:
        filename = f"{recipe_name}_Lea James Hot Chicken_{ts}.csv"
        filepath = os.path.join(test_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(sample_csv.format(recipe_name=recipe_name))
        
        print(f"  Created: {filename}")

print("\nTest files created. Now testing the loader...")

# Import and test the loader
from csv_recipe_loader_v2 import CSVRecipeLoaderV2

loader = CSVRecipeLoaderV2(csv_dir=test_dir)

# Analyze files
print("\nAnalyzing files for duplicates...")
recipe_files = loader.analyze_csv_files()

print("\nDuplicate analysis results:")
for recipe_key, versions in recipe_files.items():
    if len(versions) > 1:
        print(f"\n{versions[0]['recipe_name']}:")
        print(f"  Found {len(versions)} versions")
        for v in versions:
            print(f"    - {v['filename']} (timestamp: {v['timestamp']})")

# Select files
files_to_load = loader.select_files_to_load(recipe_files)

print(f"\nWould load {len(files_to_load)} files out of {sum(len(v) for v in recipe_files.values())} total")

# Cleanup
print("\nCleaning up test files...")
shutil.rmtree(test_dir)
print("Done!")