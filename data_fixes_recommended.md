# Data Fix Recommendations - Restaurant Inventory System

Generated: 2025-07-07
Based on comprehensive data validation analysis

## 🚨 CRITICAL: READ BEFORE IMPLEMENTING ANY FIXES

**All changes must be:**
1. Backed up before implementation
2. Tested on a copy first
3. Verified to not break recipe calculations
4. Approved by system owner

---

## 📊 Executive Summary

### Data Quality Metrics
- **Total Inventory Items**: 250
- **Vendor Completeness**: 100.0%
- **Price Completeness**: 100.0%
- **Item Code Completeness**: 100.0%
- **Recipe Linkage**: 99.0% (208 of 210 links valid)

### Key Issues Found
1. **47 potential duplicate products** across vendors
2. **9 naming convention issues** in product descriptions
3. **2 unmapped recipe ingredients**
4. **1 vendor naming inconsistency** (JAKE'S, INC. vs JAKES, INC.)
5. **5 illogical quantities/units** in recipes

---

## 🔧 PRIORITY 1: Critical Data Fixes (Immediate Action Required)

### 1.1 Unmapped Recipe Ingredients
**Issue**: 2 recipe ingredients have no link to inventory items
**Impact**: Recipe costs cannot be calculated

**Affected Items**:
```
Recipe: Pickled Shallot (ID: 22)
- Missing ingredient mapping

Recipe: Alabama White BBQ (ID: 52)
- Missing ingredient mapping
```

**Fix Process**:
```sql
-- First, identify the specific unmapped ingredients
SELECT ri.*, r.recipe_name 
FROM recipe_ingredients ri
JOIN recipes r ON ri.recipe_id = r.id
WHERE (ri.ingredient_id IS NULL OR ri.ingredient_id = 0)
AND r.id IN (22, 52);

-- Then map to appropriate inventory items
-- Example (DO NOT RUN without verification):
-- UPDATE recipe_ingredients 
-- SET ingredient_id = [correct_inventory_id]
-- WHERE id = [specific_recipe_ingredient_id];
```

### 1.2 Vendor Naming Standardization
**Issue**: JAKE'S, INC. vs JAKES, INC. (missing apostrophe)
**Impact**: Reporting and vendor analysis fragmentation

**Fix Process**:
```sql
-- Standardize to JAKE'S, INC. (with apostrophe)
UPDATE inventory 
SET vendor_name = 'JAKE''S, INC.'
WHERE vendor_name = 'JAKES, INC.';

-- Verify no recipe calculations are affected
SELECT COUNT(*) FROM inventory WHERE vendor_name = 'JAKE''S, INC.';
```

---

## 🔧 PRIORITY 2: Data Quality Improvements (Within 1 Week)

### 2.1 Product Description Standardization
**Issue**: 9 items with ALL CAPS descriptions
**Examples**:
- "JUICE" (ID: multiple)
- "SYSCO RELIANCE MAYONNAISE" (ID: varies)

**Fix Process**:
```python
# Script to standardize product names
import sqlite3

def standardize_product_names():
    conn = sqlite3.connect('restaurant_calculator.db')
    cursor = conn.cursor()
    
    # Get items with all caps names
    items = cursor.execute("""
        SELECT id, item_description 
        FROM inventory 
        WHERE item_description = UPPER(item_description)
        AND LENGTH(item_description) > 3
    """).fetchall()
    
    for item_id, desc in items:
        # Convert to title case, preserving certain acronyms
        new_desc = desc.title()
        # Preserve common acronyms
        new_desc = new_desc.replace('Bbq', 'BBQ')
        new_desc = new_desc.replace('Sysco', 'SYSCO')
        
        print(f"Update: {desc} -> {new_desc}")
        # cursor.execute("UPDATE inventory SET item_description = ? WHERE id = ?", 
        #                (new_desc, item_id))
    
    # conn.commit()
    conn.close()
```

### 2.2 Duplicate Product Consolidation
**Issue**: 47 potential duplicate products across vendors
**Priority Examples**:
1. Products with identical descriptions but different vendors
2. Products with minor description variations

**Investigation Required**:
- Verify if these are legitimate (different brands/qualities)
- Check price variations to identify potential consolidation candidates

---

## 🔧 PRIORITY 3: Long-term Data Hygiene (Within 1 Month)

### 3.1 Missing Unit of Measure
**Issue**: 20 inventory items (8%) missing unit_measure
**Impact**: Recipe calculations may be inaccurate

**Fix Process**:
1. Export list of items missing units
2. Research standard units for each product category
3. Update with appropriate units

### 3.2 Recipe Quantity Validation
**Issue**: 5 recipe ingredients with illogical quantities
**Examples**:
- Quantities over 1000 (likely data entry errors)
- Missing units of measure

**Investigation Script**:
```sql
SELECT 
    r.recipe_name,
    ri.ingredient_name,
    ri.quantity,
    ri.unit_of_measure,
    i.item_description,
    i.unit_measure as inventory_unit
FROM recipe_ingredients ri
JOIN recipes r ON ri.recipe_id = r.id
LEFT JOIN inventory i ON ri.ingredient_id = i.id
WHERE ri.quantity > 100 
   OR ri.unit_of_measure IS NULL
   OR ri.unit_of_measure = ''
ORDER BY ri.quantity DESC;
```

---

## 📋 Implementation Checklist

### Before Starting Any Fixes:
- [ ] Create full database backup
- [ ] Document current state metrics
- [ ] Get approval for changes
- [ ] Set up test environment

### For Each Fix:
- [ ] Test fix on backup copy first
- [ ] Verify recipe calculations still work
- [ ] Document what was changed
- [ ] Update validation metrics

### After Fixes:
- [ ] Run full validation suite again
- [ ] Compare before/after metrics
- [ ] Test critical workflows
- [ ] Update documentation

---

## 🚫 DO NOT Fix Without Investigation

1. **Potential Duplicate Products**: May be legitimate variations
2. **Custom Items**: Pricing may be estimates - verify before changing
3. **Unit Conversions**: Must maintain calculation accuracy
4. **Historical Data**: May be needed for reporting

---

## 📈 Expected Outcomes After Fixes

- Recipe linkage: 99.0% → 100%
- Vendor consistency: Improved reporting accuracy
- Product naming: Standardized for better searching
- Data quality score: Significant improvement

---

## 🔄 Ongoing Maintenance Recommendations

1. **Weekly**: Run validation script to catch new issues
2. **Monthly**: Review vendor product assignments
3. **Quarterly**: Full data quality audit
4. **Before Major Updates**: Complete validation suite

---

## 📞 Escalation Path

If you encounter:
- Recipe calculations breaking → STOP immediately
- Vendor relationships unclear → Consult with purchasing team
- Custom items questions → Check with chef/kitchen manager
- System errors → Restore from backup, document issue

---

**Remember**: Data quality is an ongoing process. These fixes address current issues, but regular monitoring is essential for maintaining system integrity.