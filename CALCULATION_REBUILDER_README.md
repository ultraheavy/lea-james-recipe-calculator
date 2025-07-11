# Recipe Cost Calculation Rebuilder

## Overview

The `calculation_rebuilder.py` module provides a comprehensive system for rebuilding recipe cost calculations from scratch with full transparency, proper unit conversions, and validation against PDF source data.

## Key Features

1. **Complete Cost Rebuild** - Calculates recipe costs from ingredient level up
2. **Unit Conversion Support** - Uses the standardized UOM system for accurate conversions
3. **Nested Recipe Handling** - Properly calculates costs for prep recipes used in other recipes
4. **PDF Validation** - Validates calculations against extracted PDF data
5. **Detailed Audit Trails** - Logs every calculation step for transparency
6. **Comprehensive Reporting** - Generates detailed reports with variance analysis
7. **Batch Processing** - Can recalculate all recipes with a single command

## Installation

```bash
# Ensure dependencies are installed
pip install PyPDF2  # Optional, for PDF validation support
```

## Usage

### Command Line Interface

```bash
# Calculate a specific recipe by ID
python calculation_rebuilder.py --recipe-id 67

# Calculate a recipe by name (partial match supported)
python calculation_rebuilder.py --recipe-name "Nashville Chicken"

# Run batch calculation for all recipes
python calculation_rebuilder.py --batch

# Validate against PDF data
python calculation_rebuilder.py --validate-pdf

# Generate comprehensive report
python calculation_rebuilder.py --report

# Specify custom database
python calculation_rebuilder.py --db custom_database.db --batch
```

### Python API

```python
from calculation_rebuilder import CalculationRebuilder

# Initialize the rebuilder
rebuilder = CalculationRebuilder('restaurant_calculator.db')

# Calculate single recipe cost
calculation = rebuilder.calculate_recipe_cost_from_scratch(recipe_id=67)
print(f"Total Cost: ${calculation['total_cost']}")
print(f"Variance from PDF: ${calculation['variance_from_pdf']}")

# Validate against PDF cost
validation = rebuilder.validate_against_pdf_cost(recipe_id=67, pdf_cost=Decimal('15.50'))
print(f"Is Valid: {validation['is_valid']}")

# Calculate gross margin
margin = rebuilder.calculate_gross_margin(recipe_id=67, menu_price=Decimal('25.00'))
print(f"Food Cost %: {margin['food_cost_percent']}%")

# Batch recalculate all recipes
results = rebuilder.batch_recalculate_all_recipes(recipe_type='Recipe')
print(f"Success rate: {results['successful']}/{results['total_recipes']}")

# Generate comprehensive report
report_path = rebuilder.generate_comprehensive_report()
print(f"Report saved to: {report_path}")
```

## Core Methods

### `calculate_recipe_cost_from_scratch(recipe_id, include_nested=True)`
Calculates the complete cost for a recipe with full transparency.

**Returns:**
- `total_cost`: Calculated total cost
- `cost_per_serving`: Cost per serving/portion
- `ingredients`: Detailed breakdown of each ingredient cost
- `calculation_steps`: Step-by-step calculation log
- `warnings`: Any calculation warnings
- `errors`: Any calculation errors
- `variance_from_pdf`: Difference from PDF stated cost

### `validate_against_pdf_cost(recipe_id, pdf_cost)`
Validates calculated cost against PDF stated cost.

**Returns:**
- `is_valid`: Whether variance is within $0.01 threshold
- `variance`: Dollar amount difference
- `variance_percent`: Percentage difference
- `validation_notes`: Detailed validation information

### `calculate_gross_margin(recipe_id, menu_price=None)`
Calculates gross margin and food cost percentage.

**Returns:**
- `menu_price`: Selling price
- `food_cost`: Calculated food cost
- `gross_profit`: Dollar profit margin
- `gross_margin_percent`: Profit margin percentage
- `food_cost_percent`: Food cost as percentage of menu price
- `pricing_recommendation`: Suggested pricing actions

### `batch_recalculate_all_recipes(recipe_type=None, save_report=True)`
Recalculates all recipes with optional filtering.

**Returns:**
- `total_recipes`: Number of recipes processed
- `successful`: Successful calculations
- `failed`: Failed calculations
- `recipes`: Detailed results for each recipe
- `summary_stats`: Aggregate statistics

### `create_calculation_audit_trail(recipe_id=None)`
Creates detailed audit trail of all calculations.

### `generate_comprehensive_report(output_dir="reports")`
Generates complete report package including:
- Batch calculation results (JSON/CSV)
- PDF validation report
- Audit trail
- Summary markdown report

## Output Files

### Calculation Details
```
calculation_details_67_20250711_102538.json
```
Contains complete calculation breakdown for a single recipe.

### Batch Reports
```
calculation_report_20250711_102538.json
calculation_report_20250711_102538.csv
```
Summary of all recipe calculations in both JSON and CSV formats.

### Comprehensive Report Directory
```
reports/calculation_report_20250711_102538/
├── batch_calculations.json
├── pdf_validation.json
├── audit_trail.json
└── SUMMARY.md
```

## Calculation Logic

### 1. Ingredient Cost Calculation
- Parses quantity and unit from recipe ingredients
- Converts units if necessary using UOMStandardizer
- Applies yield adjustments where applicable
- Handles both inventory items and nested prep recipes

### 2. Unit Conversion
- Supports weight ↔ volume conversions (requires density)
- Handles count ↔ weight conversions
- Package size conversions
- Falls back gracefully when conversion not possible

### 3. Nested Recipe Handling
- Recursively calculates prep recipe costs
- Uses batch yield to determine unit cost
- Properly propagates errors up the chain

### 4. Validation
- Compares calculated cost to PDF stated cost
- Flags variances greater than $0.01
- Provides detailed variance analysis

## Error Handling

The module includes comprehensive error handling:
- Missing pricing information
- Invalid unit conversions
- Missing yield information for prep recipes
- Database connection issues
- PDF parsing errors (when PDF support enabled)

## Best Practices

1. **Regular Recalculation** - Run batch calculations periodically to catch pricing changes
2. **PDF Validation** - Use PDF validation to ensure calculation accuracy
3. **Review Warnings** - Check calculation warnings for potential issues
4. **Export Reports** - Save calculation reports for audit purposes
5. **Handle Nested Recipes** - Ensure prep recipes have proper yield information

## Troubleshooting

### Common Issues

1. **"Recipe not found"** - Check recipe ID exists in recipes_actual table
2. **"Cannot convert units"** - Add density or conversion factors for ingredients
3. **"Missing yield information"** - Update prep recipes with batch_yield data
4. **"PDF support not available"** - Install PyPDF2: `pip install PyPDF2`

### Debug Mode

Set logging to DEBUG for detailed calculation traces:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Database Schema Requirements

The module expects the following tables:
- `recipes_actual` - Main recipe information
- `recipe_ingredients_actual` - Recipe ingredient details
- `inventory` - Inventory items with pricing
- `menu_items` - Menu pricing information

## Future Enhancements

1. Labor cost calculations
2. Prime cost analysis
3. Historical cost tracking
4. Automated pricing recommendations
5. Integration with vendor APIs for real-time pricing