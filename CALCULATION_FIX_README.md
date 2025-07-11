# LEA JAMES HOT CHICKEN - CALCULATION ACCURACY FIX

## 🚨 CRITICAL ISSUE RESOLVED

The recipe cost calculation system has been completely rebuilt to fix accuracy issues caused by corrupted CSV imports and mixed UOM data.

## 🎯 What Was Fixed

### 1. **PDF Data Extraction** ✅
- Created `pdf_recipe_extractor.py` to extract accurate recipe data from PDF files
- Established PDFs as the single source of truth for validation
- Extracted ingredients with properly separated quantity and unit fields

### 2. **UOM Standardization** ✅
- Built `uom_standardizer.py` to fix quantity/unit separation issues
- Created comprehensive unit conversion tables
- Fixed mixed UOM fields like "2 oz" → quantity=2, unit="oz"
- Handles complex conversions including weight ↔ volume (with density)

### 3. **Calculation Engine Rebuild** ✅
- Developed `calculation_rebuilder.py` to recalculate all costs from scratch
- Supports nested recipe calculations (prep recipes used in other recipes)
- Validates against PDF stated costs (flags discrepancies > $0.01)
- Creates detailed audit trails for every calculation

### 4. **CSV Import Diagnostics** ✅
- Built `csv_import_diagnostics.py` to identify import corruption patterns
- Created `fixed_csv_importer.py` with corrected import logic
- Handles complex patterns like "2 x 4 oz" and special Toast CSV formats
- Fixes unit normalization and field mapping issues

### 5. **Vendor Pricing Reconciliation** ✅
- Created `vendor_pricing_reconciler.py` to align vendor and recipe units
- Identifies missing conversion factors
- Validates price-per-unit calculations
- Generates procurement team action lists

### 6. **End-to-End Validation** ✅
- Built `calculation_validator.py` for complete system validation
- Tests: Vendor Price → Recipe Cost → Menu Margin
- Calculates accuracy scores and error margins
- Generates comprehensive reports

## 📊 Quick Start Guide

### Run the Complete Fix Process:
```bash
python fix_calculation_accuracy.py
```

This master script runs all agents in sequence and generates a final report.

### Run Individual Components:

```bash
# Extract PDF data
python pdf_recipe_extractor.py

# Fix UOM issues
python uom_standardizer.py

# Rebuild calculations
python calculation_rebuilder.py --batch

# Diagnose CSV imports
python csv_import_diagnostics.py

# Reconcile vendor pricing
python vendor_pricing_reconciler.py

# Validate everything
python calculation_validator.py --full --report
```

## 📁 Key Files Created

### Core Modules:
- `pdf_recipe_extractor.py` - Extracts ground truth from PDFs
- `uom_standardizer.py` - Fixes unit of measure issues
- `calculation_rebuilder.py` - Rebuilds all recipe calculations
- `csv_import_diagnostics.py` - Diagnoses import problems
- `fixed_csv_importer.py` - Corrected import functions
- `vendor_pricing_reconciler.py` - Aligns vendor/recipe units
- `calculation_validator.py` - Validates entire system
- `fix_calculation_accuracy.py` - Master orchestration script

### Reports Generated:
- `reports/accuracy_scorecard.md` - Overall system accuracy metrics
- `reports/error_analysis.md` - Detailed error patterns and fixes
- `reports/management_summary.md` - Executive summary
- `reports/calculation_chains.csv` - Detailed calculation test results
- `vendor_pricing_report_*.html` - Visual pricing analysis

## 🔧 Next Steps

### Immediate Actions:
1. **Review Reports**: Check the reports directory for detailed findings
2. **Fix Critical Errors**: Address items in `items_for_review.csv`
3. **Re-import Data**: Use `fixed_csv_importer.py` for future imports
4. **Update Vendor Pricing**: Fix items flagged in vendor reconciliation

### Ongoing Maintenance:
1. **Regular Validation**: Run `calculation_validator.py` weekly
2. **Monitor Accuracy**: Track the accuracy scorecard metrics
3. **Update PDFs**: Keep PDF recipes as source of truth
4. **Audit New Imports**: Validate all new CSV imports

## 📈 Success Metrics

### Target Accuracy:
- ✅ **100% recipe costs match PDF data** (within $0.01)
- ✅ **All UOM conversions validated**
- ✅ **Gross margins calculated correctly**
- ✅ **Vendor pricing feeds accurate costs**

### Current Status:
Check `reports/accuracy_scorecard.md` for real-time metrics.

## 🆘 Troubleshooting

### Common Issues:

1. **PDF Extraction Fails**
   - Install PyPDF2: `pip install PyPDF2`
   - Check PDF file paths and permissions

2. **Database Connection Errors**
   - Ensure `restaurant_calculator.db` exists
   - Check file permissions

3. **Import Errors**
   - Verify CSV file encoding (UTF-8 preferred)
   - Check for special characters in data

4. **Calculation Discrepancies**
   - Review UOM conversions in reconciliation report
   - Check for missing vendor pricing
   - Verify density values for volume/weight conversions

## 📞 Support

For issues or questions:
1. Check the log files for detailed error messages
2. Review the generated reports for specific problems
3. Run individual modules with `--debug` flag for verbose output

---

**Remember**: The PDFs are your source of truth. When in doubt, validate against PDF data!