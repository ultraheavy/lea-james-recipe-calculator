# Recipe List CSV Staging Loader Implementation

## Overview
This implementation provides a complete staging system for loading and validating recipe data from xtraCHEF exports before committing to the live database.

## Components Created

### 1. Database Schema (`migrations/create_staging_recipes_table.sql`)
- Staging table `stg_recipes` with comprehensive validation fields
- Views for review, batch summary, and validation issues
- Indexes for performance optimization
- Duplicate detection and tracking

### 2. CSV Loader (`recipe_staging_loader.py`)
- Transforms original xtraCHEF headers to new structure
- Validates data according to business rules:
  - Food cost percentage thresholds (< 10%, > 40%)
  - Gross margin < 60% flagging
  - Zero food cost detection
  - Draft status flagging
  - Non-standard status holding
  - Prep recipe yield requirements
- Handles extremely high percentages (auto-divides by 100 if > 1000%)
- Matches recipes to existing entries
- Generates duplicate detection hashes

### 3. Admin Interface (`recipe_staging_admin.py`)
- Full CRUD operations on staged data
- Filtering by batch, status, cost issues, etc.
- Duplicate management (merge/version/reject)
- Bulk operations for approval/rejection
- Commit to live functionality

### 4. Frontend UI (`templates/recipe_staging_review.html`)
- Summary cards showing key metrics
- Advanced filtering interface
- Inline editing capabilities
- Visual flags for issues (zero cost, high %, low margin)
- Duplicate group management
- Bulk selection and actions
- Responsive design

## Usage Instructions

### 1. Initialize the Staging Table
```bash
python recipe_staging_loader.py --init
```

### 2. Load CSV Data
```bash
python recipe_staging_loader.py /path/to/Lea_Janes_Recipe_List_Summary.csv
```

Or use the test script:
```bash
python test_recipe_staging.py
```

### 3. Access Admin Interface
Navigate to: http://localhost:8888/admin/staging/recipes-list/

### 4. Review Process
1. **Filter** - Use filters to focus on specific issues
2. **Review** - Check flagged items and validation errors
3. **Edit** - Click on editable fields to correct values
4. **Approve/Hold/Reject** - Set review status for each item
5. **Handle Duplicates** - Choose merge, version, or reject
6. **Commit** - Push approved items to live tables

## Validation Rules Implemented

### Food Cost Validation
- **Zero Cost**: Always flagged for review
- **< 10%**: Flagged as potentially missing data
- **> 40%**: Flagged for profitability review
- **> 100%**: Flagged as possible formatting error
- **> 1000%**: Auto-corrected (divided by 100)

### Status Handling
- **Draft**: Imported but flagged for review
- **Test/Non-standard**: Set to "hold" status
- **Valid statuses**: Published, Approved, Active, Complete

### Required Fields
- Recipe Name (always required)
- Food Cost (flagged if missing/zero)
- Menu Price (flagged if missing for Recipe type)
- Yield & Yield UOM (required for PrepRecipe type)

### Margin Validation
- Gross margin < 60% flagged
- Negative margins flagged
- Margin calculation variance > 5% flagged

### Duplicate Handling
Options provided:
- **Reject**: Mark duplicate as rejected
- **Merge**: Overwrite existing recipe
- **Version**: Create with suffix (e.g., -v2)

## Integration Points

### With Existing System
- Matches staged recipes to existing recipes table
- Updates existing recipes on merge
- Creates new recipes for non-matches

### Future Integrations
- Link to inventory items (via FAM_Product_Name)
- Cross-reference with PDF recipe details
- Connect to ingredient mapping system

## Admin Features

### Filtering Options
- By batch ID
- By review status (pending/approved/rejected/hold)
- By recipe type (Recipe/PrepRecipe)
- By recipe status (Draft/Complete/etc.)
- By cost issues (zero/low/high/extreme)
- By margin issues
- Search by recipe name

### Bulk Operations
- Select all/none
- Bulk approve/hold/reject
- Commit all approved or selected items

### Inline Editing
- Click any editable field to modify
- Auto-saves on blur or Enter
- Recalculates margins when costs/prices change

## Security & Data Integrity

### Validation
- All numeric fields parsed and validated
- Date formats standardized
- Required fields enforced
- Business rules applied consistently

### Audit Trail
- Original row data preserved as JSON
- All changes tracked with timestamps
- Review notes and status history
- Processing dates recorded

### Error Handling
- Individual row errors don't stop batch
- Detailed error messages per row
- Validation errors displayed in UI
- Commit errors reported but don't rollback entire batch

## Performance Considerations

- Batch processing with progress tracking
- Indexed fields for fast filtering
- Pagination for large datasets
- Efficient duplicate detection
- Optimized views for common queries

## Next Steps

1. **Test with Production Data**: Load actual xtraCHEF export
2. **Review Validation Thresholds**: Adjust based on business feedback
3. **Enhance Duplicate Logic**: Add fuzzy matching for similar names
4. **Add Export Functionality**: Export approved/rejected items
5. **Create Audit Reports**: Track changes and approvals
6. **Integration with Inventory**: Link ingredients to inventory items
7. **PDF Recipe Linking**: Connect to parsed PDF recipe data