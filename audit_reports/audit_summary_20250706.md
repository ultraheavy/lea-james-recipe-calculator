# Data Audit Summary Report
Generated: 2025-07-06

## Overview
Total validation failures found: 284 issues across 4 tables

## Summary by Table

| Table | Issue Count | Percentage |
|-------|-------------|------------|
| vendor_products | 167 | 58.8% |
| recipe_ingredients | 66 | 23.2% |
| inventory | 42 | 14.8% |
| recipes | 9 | 3.2% |

## Key Issues Identified

### 1. Inventory Table (42 issues)
- **Invalid Units**: Common invalid units include:
  - `ct` (should be `count` or `each`)
  - `piece` (should be `each`)
  - `loaf`, `slice` (bread-specific units not in standard UOM list)
  - `jug`, `bottle`, `btl` (container types not standard units)
  - `ltr` (should be `l` or `liter`)
  - `bg` (should be `bag`)
  - `unit` (too generic)
  
- **Invalid Pack Size Formats**: Many pack sizes missing units:
  - `1 x 1`, `1 x 2`, `1 x 4`, `1 x 5` (missing unit after quantity)
  - `5 fl oz`, `8.5 fl oz`, `128 fl oz` (should include "x" separator)
  - `12 x 32 fl oz`, `24 x 16 fl oz` (spaces in "fl oz" causing parse issues)

### 2. Recipe Ingredients Table (66 issues)
- **Invalid Units**:
  - `slice` (not in standard UOM list)
  - `tablespoon` (should be abbreviated)
  - `fl ounce` (should be `fl oz`)
  - Missing unit_of_measure (2 cases)
  
- **Ingredient Name Mismatches** (majority of issues):
  - Recipe ingredients pointing to wrong inventory items
  - Examples:
    - "French Fries Recipe" → "Dry Goods, Bread, French Toast, Thick Slice"
    - "Kale Kimchi Recipe" → "PD KALE CHOPPED"
    - "Fried Chicken Tender" → "Dry Goods, Chicken Base, Paste"
    - "Charred Onion Ranch" → "Dry Goods, Ranch Dressing, with Jalapeno"

### 3. Recipes Table (9 issues)
- **Missing Ingredients**: 4 recipes have no ingredients at all
  - Recipe IDs: 97, 100, 102, 105
- **No Costed Ingredients**: 2 recipes have ingredients but no costs
  - Recipe IDs: 72, 74
- **High Food Cost Percentage**: 2 recipes with >100% food cost
  - Recipe 81: 120.0%
  - Recipe 87: 122.5%
- **Invalid UOM**: 
  - `portions` (should be `each` or specific count unit)

### 4. Vendor Products Table (167 issues)
- **Pack Size Format Issues** (all 167 issues):
  - Same pattern as inventory: missing units in "N x N" format
  - Examples: `1 x 1`, `1 x 4`, `6 x 27.4`, `24 x 1`
  - All need unit specification after the second number

## Critical Data Quality Issues

1. **Unit Standardization**: Need to expand valid UOM list or standardize existing units
2. **Pack Size Format**: Systematic issue with missing units in pack sizes
3. **Ingredient Mapping**: Many recipe ingredients linked to completely wrong inventory items
4. **Missing Recipe Data**: Several recipes have no ingredients defined
5. **Cost Calculation**: Some recipes showing impossible food cost percentages

## Recommendations

1. **Immediate Actions**:
   - Fix pack size formats by adding missing units
   - Correct ingredient mappings in recipe_ingredients
   - Add missing ingredients to empty recipes
   
2. **Data Standardization**:
   - Expand valid UOM list to include common culinary units
   - Create mapping table for unit aliases (ct → count, etc.)
   
3. **Validation Enhancement**:
   - Add pack size format validation during import
   - Implement ingredient name fuzzy matching
   - Add food cost percentage bounds checking

4. **Process Improvements**:
   - Review XtraChef import process for data quality
   - Add validation step before committing imports
   - Create data quality dashboard for ongoing monitoring