# Vendor Pricing Reconciliation Engine

## Overview
The Vendor Pricing Reconciliation Engine ensures vendor pricing properly supports recipe calculations by auditing, validating, and aligning units of measure (UOM) between vendor products and recipe requirements.

## Features

### 1. Audit Functions
- **UOM Matching**: Checks if vendor UOM matches recipe usage UOM
- **Missing Conversions**: Identifies missing conversion factors between units
- **Price Validation**: Validates price-per-unit calculations
- **Pack Size Analysis**: Accounts for case/pack sizes correctly

### 2. Price Validation
- Compares contract prices vs last purchased prices
- Flags items with missing pricing data
- Identifies outdated vendor prices (>90 days)
- Calculates accurate price per unit considering pack sizes

### 3. UOM Alignment
- Creates conversion mappings between vendor units and recipe units
- Handles complex vendor pack sizes (e.g., "case of 24 x 12oz cans")
- Calculates conversion factors for all vendor/recipe unit pairs
- Flags impossible conversions requiring manual intervention

### 4. Reporting & Recommendations
- Generates comprehensive HTML reports with issue summaries
- Creates actionable fix lists for procurement team
- Provides prioritized recommendations
- Exports CSV files for data correction

## Usage

### Basic Usage
```python
python vendor_pricing_reconciler.py
```

### Programmatic Usage
```python
from vendor_pricing_reconciler import VendorPricingReconciler

# Initialize reconciler
reconciler = VendorPricingReconciler('restaurant_calculator.db')

# Run full reconciliation
results = reconciler.full_reconciliation()

# Access specific audit functions
reconciler.audit_vendor_uom_matches()
reconciler.check_outdated_prices(days_threshold=120)

# Export fix lists
reconciler.export_fix_lists()

# Close connection
reconciler.close()
```

## Output Files

### 1. HTML Report
- `vendor_pricing_reconciliation_[timestamp].html`
- Comprehensive visual report with:
  - Summary statistics
  - Detailed issue listings
  - Prioritized recommendations
  - Actionable next steps

### 2. Fix Lists (CSV)
- `fix_list_missing_prices_[timestamp].csv`: Items needing price updates
- `fix_list_conversions_needed_[timestamp].csv`: Required unit conversions
- `fix_list_outdated_prices_[timestamp].csv`: Items with stale pricing

## Issue Categories

### Critical Issues
- **Missing Prices**: Items without vendor pricing cannot be costed
- **Impossible Conversions**: Incompatible unit dimensions (e.g., pieces to pounds)

### High Priority Issues
- **UOM Mismatches**: Vendor and recipe units differ, need conversion
- **Missing Density Data**: Volume to weight conversions require density

### Medium Priority Issues
- **Outdated Prices**: Prices not updated in >90 days
- **Pack Size Issues**: Non-standard formats preventing calculations
- **Price Discrepancies**: >10% difference between contract and last purchase

## Conversion Support

### Standard Conversions
- Weight: kg ↔ g ↔ lb ↔ oz
- Volume: l ↔ ml ↔ gal ↔ qt ↔ fl oz
- Count: each ↔ dozen ↔ case

### Complex Pack Sizes
- "24 x 12oz cans" → 12 oz per unit
- "case of 24" → 24 each per case
- "1x4l" → 4 liters per unit

### Unit Aliases
The system recognizes common variations:
- "pounds", "lbs", "lb" → "lb"
- "ounces", "oz" → "oz"
- "each", "ea", "unit" → "each"

## Recommendations

### Immediate Actions
1. Update missing vendor prices
2. Create UOM conversion mappings
3. Resolve impossible conversions

### Process Improvements
1. Implement quarterly price reviews
2. Standardize pack size formats
3. Automate vendor price imports

### Data Quality
1. Maintain consistent UOM naming
2. Regular price update cycles
3. Document conversion factors

## Configuration

### UOM Aliases
Edit `uom_aliases.json` to add custom unit mappings

### Conversion Factors
Extend `_load_uom_conversions()` method for custom conversions

### Report Thresholds
- Outdated price threshold: 90 days (configurable)
- Price discrepancy threshold: 10% (configurable)

## Integration

The reconciler works with existing tables:
- `inventory`: Item master data
- `vendor_products`: Vendor-specific pricing
- `vendors`: Vendor information
- `recipe_ingredients`: Recipe requirements

## Error Handling

The system logs all issues found during reconciliation:
- Missing data is flagged but doesn't stop processing
- Impossible conversions are documented for manual review
- All issues are categorized by severity

## Best Practices

1. Run reconciliation weekly or after major data imports
2. Address critical issues first (missing prices, impossible conversions)
3. Use fix lists for bulk data updates
4. Review and approve recommendations before implementation
5. Keep vendor pricing current (<90 days old)
6. Standardize units across vendors where possible