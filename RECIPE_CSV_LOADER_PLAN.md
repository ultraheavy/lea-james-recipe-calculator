# Individual Recipe CSV Loader Plan

## Current State

We have successfully implemented two CSV-based admin loaders:
1. **Inventory Staging Admin** - Loads and validates items from CSV exports
2. **Recipe Staging Admin** - Loads recipe summary data from xtraCHEF exports

The next phase is to implement a loader for individual recipe details.

## The Challenge

- **Data Source**: 70+ individual recipe CSV files exported from xtraCHEF
- **Location**: `/reference/LJ_DATA_Ref/updated_recipes_csv_pdf/csv/`
- **Format**: Each file contains detailed ingredient lists with quantities and units
- **Goal**: Parse and validate ingredient data, then link to existing inventory items

## The Opportunity

Unlike the PDF format (which had OCR accuracy issues), the CSV format provides:
- Clean, structured data
- Consistent formatting
- No OCR errors
- Reliable parsing

## Key Requirements

1. **Parse Ingredient Lines**
   - Extract quantity, unit, and ingredient name
   - Handle various formats (fractions, decimals, mixed units)
   - Identify prep instructions vs. ingredient names

2. **Match to Inventory**
   - Link ingredients to existing inventory items
   - Flag unmatched items for review
   - Handle variations in naming

3. **Staging & Validation**
   - Follow the same staging pattern as other loaders
   - Validate quantities and units
   - Check for reasonable values
   - Detect and handle duplicates

4. **Admin Interface**
   - Review interface similar to recipe staging admin
   - Ability to map unmatched ingredients
   - Bulk operations for approval
   - Commit to live recipe_ingredients table

## Technical Approach

### Database Schema
```sql
-- To be implemented
CREATE TABLE stg_recipe_ingredients (
    id INTEGER PRIMARY KEY,
    batch_id TEXT,
    source_filename TEXT,
    recipe_name TEXT,
    ingredient_line TEXT,
    parsed_quantity DECIMAL,
    parsed_unit TEXT,
    parsed_ingredient TEXT,
    matched_inventory_id INTEGER,
    validation_status TEXT,
    review_status TEXT,
    -- ... additional fields
);
```

### Parser Strategy
1. Use regex patterns to extract quantity/unit/ingredient
2. Normalize units to standard abbreviations
3. Apply fuzzy matching for ingredient names
4. Handle edge cases (ranges, optional ingredients, etc.)

### Integration Points
- Link to existing recipes via recipe name matching
- Connect to inventory items via ingredient matching
- Update recipe costs after successful import

## Implementation Timeline

**Phase 1: Parser Development**
- [ ] Analyze CSV file formats
- [ ] Develop parsing logic
- [ ] Create unit tests for edge cases

**Phase 2: Database & Staging**
- [ ] Create staging tables
- [ ] Implement loader script
- [ ] Add validation rules

**Phase 3: Admin Interface**
- [ ] Create review UI
- [ ] Add mapping interface
- [ ] Implement commit functionality

**Phase 4: Testing & Refinement**
- [ ] Test with full dataset
- [ ] Refine matching algorithms
- [ ] Handle edge cases

## Expected Outcomes

1. **Automated Import**: Bulk load all 70+ recipes efficiently
2. **Data Quality**: Validate and clean data during import
3. **Ingredient Mapping**: Link recipes to inventory with high accuracy
4. **Cost Accuracy**: Enable precise recipe costing

## Notes

- This approach leverages the cleaner CSV format after PDF parsing proved unreliable
- The staging pattern has proven successful with the other two loaders
- Focus on data quality and validation before committing to production

---

*Status: Planning Phase*  
*Last Updated: [Current Date]*