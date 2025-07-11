# Calculation Validator - End-to-End Validation System

## Overview

The Calculation Validator is a comprehensive testing system that validates the entire calculation chain from vendor prices through recipe costs to menu margins. It ensures calculation accuracy by comparing against PDF stated values and provides detailed accuracy scoring and error analysis.

## Features

### 1. Full System Validation
- **Vendor Price Validation**: Checks pricing data completeness and currency
- **UOM Conversion Testing**: Validates unit conversions used in calculations
- **Recipe Calculation Chains**: Tests complete calculation flow for each recipe
- **Menu Margin Validation**: Ensures gross margin calculations are accurate
- **PDF Comparison**: Validates against stated costs from PDF documentation

### 2. Validation Checkpoints
The system tests accuracy at each critical point:
- Vendor price → Ingredient cost conversion
- Ingredient costs → Recipe total cost
- Recipe cost → Menu item food cost percentage
- Food cost → Gross margin calculation

### 3. Accuracy Scoring
- Calculates percentage of recipes with correct costs (within $0.01)
- Tracks average error margins across all calculations
- Identifies systematic calculation errors
- Flags recipes requiring manual review

### 4. Comprehensive Reporting
- **Accuracy Scorecard**: Overall system accuracy metrics
- **Error Analysis**: Detailed breakdown of calculation failures
- **Management Summary**: Executive-level overview with recommendations
- **Drill-down Details**: CSV exports for detailed analysis

## Installation

```bash
# Ensure all dependencies are installed
pip install pandas

# The validator depends on these modules (should be in same directory):
# - calculation_rebuilder.py
# - uom_standardizer.py
# - vendor_pricing_reconciler.py
```

## Usage

### Command Line Interface

```bash
# Run full system validation
python calculation_validator.py --full

# Run quick validation on sample recipes
python calculation_validator.py --quick

# Validate specific recipes
python calculation_validator.py --recipe-ids 123 456 789

# Generate comprehensive report
python calculation_validator.py --full --report

# Use custom database
python calculation_validator.py --full --db /path/to/database.db
```

### Python API

```python
from calculation_validator import CalculationValidator

# Initialize validator
validator = CalculationValidator('restaurant_calculator.db')

# Run full validation
results = validator.run_full_system_validation()

# Check overall accuracy
accuracy = results['accuracy_metrics']['overall_accuracy']
print(f"System accuracy: {accuracy:.1f}%")

# Generate report
report_dir = validator.generate_validation_report()
```

## Validation Process

### 1. Vendor Pricing Validation
```
✓ All inventory items have current prices
✓ Pack sizes and purchase units are properly formatted
✓ Pricing data is not older than 90 days
```

### 2. UOM Conversion Testing
```
✓ Standard conversions (lb → oz, kg → g, etc.)
✓ Volume conversions (gal → fl oz, L → ml, etc.)
✓ Count conversions (dozen → each, etc.)
```

### 3. Recipe Calculation Chains
Tests the complete flow:
```
Vendor Price ($24.50/case)
    ↓ [Pack size conversion]
Ingredient Unit Cost ($2.04/lb)
    ↓ [Recipe quantity × unit cost]
Ingredient Total Cost ($4.08)
    ↓ [Sum all ingredients]
Recipe Total Cost ($12.45)
    ↓ [Compare to PDF]
Validation Result (✓ Within $0.01)
```

### 4. Menu Margin Validation
```
Menu Price: $18.95
Food Cost: $5.68
Food Cost %: 30.0%
Gross Margin: 70.0%
Status: ✓ Within target range (25-35%)
```

## Output Reports

### 1. Accuracy Scorecard (`accuracy_scorecard.md`)
```markdown
# Calculation Accuracy Scorecard

## Overall Metrics
- Overall Accuracy: 94.5%
- Calculation Success Rate: 97.2%
- Confidence Level: HIGH
- Average Variance: $0.03

## Component Validation
| Component | Status | Details |
|-----------|--------|---------|
| Vendor Pricing | ✅ PASSED | 487/512 items priced |
| UOM Conversions | ✅ PASSED | 45/45 conversions passed |
| Recipe Calculations | ⚠️ WARNING | 132/145 chains validated |
| Menu Margins | ✅ PASSED | 89/92 items validated |
| PDF Accuracy | ✅ PASSED | 94.5% accuracy rate |
```

### 2. Error Analysis (`error_analysis.md`)
- Lists systematic errors found
- Shows recipes with largest variances
- Identifies patterns in failures

### 3. Management Summary (`management_summary.md`)
- Executive overview of system health
- Priority action items
- Risk assessment
- Financial impact analysis

### 4. Detailed Data Exports
- `calculation_chains.csv`: All calculation test results
- `items_for_review.csv`: Items requiring manual attention
- `validation_results.json`: Complete raw validation data

## Interpreting Results

### Confidence Levels
- **HIGH** (95%+ accuracy): System is reliable for production use
- **MEDIUM** (85-94% accuracy): Generally accurate but needs attention
- **LOW** (<85% accuracy): Significant issues requiring immediate action

### Common Issues and Solutions

#### Missing Vendor Pricing
**Issue**: Inventory items without current prices
**Solution**: Update vendor pricing data in the inventory system

#### UOM Conversion Failures
**Issue**: Cannot convert between units (e.g., "each" to "lb")
**Solution**: Add density or count-to-weight data for affected items

#### Large Cost Variances
**Issue**: Calculated cost differs significantly from PDF
**Solution**: Review ingredient quantities and unit conversions

#### Poor Menu Margins
**Issue**: Food cost percentage exceeds 35%
**Solution**: Review menu pricing or reduce recipe costs

## Best Practices

1. **Run Regular Validations**
   - Weekly quick validations
   - Monthly full system validations
   - After any major data updates

2. **Monitor Trends**
   - Track accuracy metrics over time
   - Watch for degradation in calculation accuracy
   - Identify seasonal pricing impacts

3. **Act on Recommendations**
   - Address critical issues immediately
   - Schedule regular review of high-priority items
   - Update pricing data regularly

4. **Maintain Data Quality**
   - Keep vendor prices current
   - Ensure pack sizes are properly formatted
   - Add missing density/conversion data

## Integration with Other Modules

The Calculation Validator works seamlessly with:

- **Calculation Rebuilder**: Provides the core calculation engine
- **UOM Standardizer**: Handles unit conversions
- **Vendor Pricing Reconciler**: Ensures pricing data integrity
- **PDF Recipe Extractor**: Compares against source documentation

## Troubleshooting

### "Dependencies not available" Error
Ensure all required modules are in the same directory:
- calculation_rebuilder.py
- uom_standardizer.py
- vendor_pricing_reconciler.py

### Database Connection Error
Check that the database path is correct and the file exists

### Low Accuracy Scores
1. Check vendor pricing data completeness
2. Review UOM conversion configurations
3. Verify recipe ingredient quantities
4. Ensure PDF values are correctly imported

## Example Workflow

```bash
# 1. Run full validation
python calculation_validator.py --full --report

# 2. Review management summary
cat validation_reports/*/management_summary.md

# 3. Check items needing attention
cat validation_reports/*/items_for_review.csv

# 4. Fix identified issues
# - Update vendor prices
# - Add missing conversions
# - Correct recipe quantities

# 5. Re-run validation to confirm fixes
python calculation_validator.py --quick

# 6. Generate updated report for management
python calculation_validator.py --full --report
```

## Support

For issues or questions:
1. Check the error analysis report for specific error patterns
2. Review the validation_results.json for detailed error messages
3. Run quick validation on problem recipes for rapid testing