# System Architecture - Lea James Recipe Cost Calculator

## Overview

This document illustrates how all components of the recipe cost calculator system fit together.

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA SOURCES (CSV Files)                          │
├─────────────────────────┬─────────────────────────┬───────────────────────┤
│   Items/Inventory CSV   │   Recipe Summary CSV    │  Individual Recipe    │
│ (MODIFIED_Lea_Janes_    │ (MODIFIED_Lea_Janes_    │      CSVs (70+)      │
│   Items_list_latest)    │ Recipe_List_Summary)    │   (One per recipe)   │
└───────────┬─────────────┴──────────┬──────────────┴───────────┬───────────┘
            │                        │                          │
            ▼                        ▼                          ▼
┌─────────────────────────┬─────────────────────────┬───────────────────────┐
│  INVENTORY STAGING      │   RECIPE STAGING        │  RECIPE CSV LOADER    │
│      ADMIN              │       ADMIN             │   (To Be Built)       │
│  (/inventory-staging)   │   (/recipe-staging)     │ (/recipe-csv-staging) │
├─────────────────────────┼─────────────────────────┼───────────────────────┤
│ • Upload CSV            │ • Upload CSV            │ • Upload CSVs         │
│ • Validate items        │ • Validate recipes      │ • Parse ingredients   │
│ • Review & approve      │ • Create menu items     │ • Map to inventory    │
│ • Batch tracking        │ • Review & approve      │ • Review & approve    │
└───────────┬─────────────┴──────────┬──────────────┴───────────┬───────────┘
            │                        │                          │
            ▼                        ▼                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          STAGING TABLES                                     │
├─────────────────────────┬─────────────────────────┬───────────────────────┤
│  stg_toast_inventory    │    stg_recipes          │  stg_recipe_details   │
│  • Item validation      │  • Recipe metadata      │  • Ingredients list   │
│  • Duplicate checks     │  • Cost summary         │  • Quantities         │
│  • Review status        │  • Menu item link       │  • Inventory mapping  │
└───────────┬─────────────┴──────────┬──────────────┴───────────┬───────────┘
            │                        │                          │
            ▼                        ▼                          ▼
        APPROVED                 APPROVED                   APPROVED
            │                        │                          │
            ▼                        ▼                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PRODUCTION TABLES                                   │
├─────────────────────────┬─────────────────────────┬───────────────────────┤
│   toast_inventory       │      recipes            │   recipe_ingredients  │
│  • Master item list     │  • Recipe definitions   │  • Recipe components  │
│  • Current pricing      │  • Cost calculations    │  • Inventory links    │
│  • Vendor info         │  • Menu pricing         │  • Quantities         │
└─────────────────────────┴──────────┬──────────────┴───────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        APPLICATION FEATURES                                 │
├─────────────────────────┬─────────────────────────┬───────────────────────┤
│   Recipe Calculator     │   Profit Analysis       │    Menu Builder       │
│  • Cost breakdown       │  • Margin calculations  │  • Price optimization │
│  • What-if scenarios    │  • Trend analysis       │  • Menu engineering   │
│  • Inventory impact     │  • Performance metrics  │  • Category analysis  │
└─────────────────────────┴─────────────────────────┴───────────────────────┘
```

## Key Integration Points

### 1. **Toast POS Constraint**
- Every recipe MUST have exactly one menu item (1:1 relationship)
- Menu items are automatically created during recipe import
- This maintains compatibility with Toast POS system

### 2. **Staging Workflow**
All data follows the same pattern:
```
Upload → Validate → Review → Approve/Reject → Production
```

### 3. **Batch Processing**
- Each upload creates a batch with unique ID
- Allows tracking of data lineage
- Enables rollback if needed

### 4. **Data Validation Layers**
1. **Format Validation**: CSV structure, required fields
2. **Business Rule Validation**: Prices > 0, valid UOMs
3. **Referential Integrity**: Recipe ingredients must exist in inventory
4. **Duplicate Detection**: Prevent double imports

### 5. **Status Tracking**
Each staged record has:
- `review_status`: pending, approved, rejected
- `validation_errors`: JSON field with specific issues
- `batch_id`: Links to upload batch
- `source_filename`: Original file reference

## Database Relationships

```sql
-- Simplified relationship diagram
toast_inventory (1) ←→ (N) recipe_ingredients
                              ↓
                            (N) ↓
                              ↓
recipes (1) ←→ (1) menu_items
```

## URL Routes Summary

- `/` - Main dashboard
- `/inventory-staging` - Items CSV import admin
- `/recipe-staging` - Recipe summary CSV import admin  
- `/recipe-csv-staging` - Individual recipe CSV import (planned)
- `/admin-tools` - Database migration management
- `/recipes` - Recipe cost calculator
- `/inventory` - Inventory management

## Next Steps

1. **Implement Recipe CSV Loader**
   - Parse individual recipe CSV files
   - Extract ingredients with quantities
   - Map to existing inventory items
   - Handle prep recipes and sub-recipes

2. **Data Completeness**
   - Import all 70+ recipe CSV files
   - Validate ingredient mappings
   - Calculate accurate recipe costs

3. **Enhanced Features**
   - Recipe comparison tools
   - Seasonal menu planning
   - Supplier price tracking
   - Waste tracking integration