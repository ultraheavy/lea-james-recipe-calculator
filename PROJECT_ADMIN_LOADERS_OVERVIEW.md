# Project Admin Loaders and Data Flow Overview

## Overview

This project implements a comprehensive staging and review system for importing restaurant data from various sources. The system follows a consistent pattern:
1. Raw data is loaded into staging tables
2. Admin interfaces allow review and correction
3. Approved data flows to production tables

## Implemented Admin Loaders

### 1. Inventory Staging Admin (`inventory_staging_admin.py`)
- **URL**: `/admin/inventory-staging`
- **Purpose**: Import and review inventory items from CSV files
- **Source Data**: Items CSV export from xtraCHEF
- **Staging Table**: `stg_inventory_items` (in `restaurant_calculator.db`)
- **Production Table**: `inventory`
- **Template**: `templates/inventory_staging_review.html`
- **Loader**: `inventory_staging_loader.py`

### 2. Recipe Staging Admin (`recipe_staging_admin.py`)
- **URL**: `/admin/recipe-staging`
- **Purpose**: Import and review recipe summary data from CSV
- **Source Data**: Recipe list CSV export from xtraCHEF
- **Staging Table**: `stg_recipes` (in `restaurant_calculator.db`)
- **Production Tables**: `recipes_new`, `menu_items_new`
- **Template**: `templates/recipe_staging_review.html`
- **Loader**: `recipe_staging_loader.py`

### 3. Recipe PDF Staging Admin (`recipe_pdf_staging_admin.py`)
- **URL**: `/admin/recipe-pdf-staging`
- **Purpose**: Import and review detailed recipe ingredients from PDF files
- **Source Data**: Individual recipe PDFs
- **Staging Table**: `stg_pdf_recipes` (in `recipe_cost_app.db`)
- **Production Table**: `recipe_ingredients_new`
- **Template**: `templates/recipe_pdf_staging.html`
- **Loader**: `pdf_recipe_loader.py`
- **Parser**: `pdf_recipe_parser_v2.py`

### 4. Admin Migration Tool (`admin_migrate.py`)
- **Purpose**: Database migration management tool
- **Function**: Executes SQL migration scripts in sequence

## Database Structure

### Staging Tables

#### 1. `stg_inventory_items`
```sql
- staging_id (PK)
- import_batch_id
- needs_review
- review_status (pending/approved/rejected/corrected)
- FAM_Product_Name_raw/cleaned/flag
- Vendor_Name_raw/cleaned/flag
- Vendor_Item_Code_raw/cleaned/flag
- Vendor_Item_Description_raw/cleaned/flag
- Vendor_UOM_raw/cleaned/flag
- Inventory_UOM_raw/cleaned/flag
- Pack_qty_raw/cleaned/flag
- Size_qty_raw/cleaned/flag
- Size_UOM_raw/cleaned/flag
- Last_Purchased_Price_raw/cleaned/flag
- is_duplicate
- processed_to_live
```

#### 2. `stg_recipes`
```sql
- staging_id (PK)
- import_batch_id
- needs_review
- review_status
- recipe_name/flag
- recipe_type/flag (Recipe/PrepRecipe)
- recipe_group
- status/flag
- food_cost/raw/flag
- food_cost_percentage/raw/flag
- menu_price/raw/flag
- yield_quantity/raw/flag
- yield_unit/flag
- calculated_margin
- margin_variance
- is_duplicate
- matched_recipe_id
- processed_to_live
```

#### 3. `stg_pdf_recipes`
```sql
- staging_id (PK)
- recipe_name
- recipe_prefix
- ingredient_name
- quantity
- unit
- cost
- is_prep_recipe
- source_file
- needs_review
- approved
- approved_by
```

### Production Tables

#### Core Recipe System
```sql
recipes_new
├── recipe_id (PK)
├── recipe_name (UNIQUE)
├── recipe_type (Recipe/PrepRecipe)
├── recipe_group
├── status
├── batch_yield/unit (for prep recipes)
├── food_cost (calculated)
├── menu_price (for final recipes)
└── created_at/updated_at

menu_items_new
├── menu_item_id (PK)
├── item_name
├── recipe_id (FK, UNIQUE - 1:1 with recipe)
├── menu_category
├── current_price
└── is_available

recipe_ingredients_new
├── ingredient_id (PK)
├── recipe_id (FK)
├── quantity
├── unit
├── ingredient_name
├── inventory_id (FK)
└── unit_cost/total_cost

inventory
├── id (PK)
├── item_code (UNIQUE)
├── item_description
├── vendor_name
├── current_price
├── unit_measure
└── purchase_unit
```

## Data Flow

### 1. Inventory Import Flow
```
CSV File → inventory_staging_loader.py → stg_inventory_items
         → Review in Admin UI → Approve/Reject
         → Approved items → inventory table
```

### 2. Recipe Summary Import Flow
```
CSV File → recipe_staging_loader.py → stg_recipes
         → Review in Admin UI → Validate calculations
         → Approved recipes → recipes_new + menu_items_new
```

### 3. Recipe Details Import Flow
```
PDF Files → pdf_recipe_parser_v2.py → Parse ingredients
          → pdf_recipe_loader.py → stg_pdf_recipes
          → Review in Admin UI → Approve ingredients
          → Approved items → recipe_ingredients_new
```

## Integration Points

### 1. Flask Application (`app.py`)
All admin interfaces are registered as Flask blueprints:
```python
from inventory_staging_admin import inventory_staging_bp
app.register_blueprint(inventory_staging_bp)

from recipe_staging_admin import recipe_staging_bp
app.register_blueprint(recipe_staging_bp)

from recipe_pdf_staging_admin import pdf_staging_bp
app.register_blueprint(pdf_staging_bp)
```

### 2. Database Connections
- Main database: `restaurant_calculator.db`
  - Contains: inventory, recipes, staging tables
- Secondary database: `recipe_cost_app.db`
  - Contains: PDF recipe staging

### 3. Key Features Across All Admin Interfaces
- Batch import tracking
- Duplicate detection
- Data validation and flagging
- Review workflow (pending → approved/rejected)
- Audit trail (who approved, when)
- Bulk operations support
- Filter and search capabilities
- Progress tracking

### 4. Common Patterns
- All staging tables include:
  - `needs_review` flag for items requiring attention
  - `review_status` workflow state
  - `import_batch_id` for tracking imports
  - `processed_to_live` flag when moved to production
  - Raw and cleaned value pairs with validation flags

## Missing Components

Based on the analysis, there is **no dedicated Menu Items staging admin** implemented yet. The menu items are created as a side effect of recipe imports, maintaining the 1:1 relationship between recipes and menu items as required by the Toast POS system.

## File Structure
```
/LJ_Test_Doca/
├── Admin Interfaces/
│   ├── inventory_staging_admin.py
│   ├── recipe_staging_admin.py
│   ├── recipe_pdf_staging_admin.py
│   └── admin_migrate.py
├── Data Loaders/
│   ├── inventory_staging_loader.py
│   ├── recipe_staging_loader.py
│   ├── pdf_recipe_loader.py
│   └── pdf_recipe_parser_v2.py
├── Templates/
│   ├── inventory_staging_review.html
│   ├── recipe_staging_review.html
│   └── recipe_pdf_staging.html
├── Migrations/
│   ├── create_staging_inventory_table.sql
│   ├── create_staging_recipes_table.sql
│   ├── create_stg_pdf_recipes.sql
│   └── create_recipes_tables.sql
└── app.py (Blueprint registration)
```

## Application Access
- Base URL: `http://localhost:8888`
- Admin URLs:
  - `/admin/inventory-staging` - Inventory review
  - `/admin/recipe-staging` - Recipe summary review
  - `/admin/recipe-pdf-staging` - Recipe details review