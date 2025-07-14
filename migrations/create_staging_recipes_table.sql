-- Create staging table for recipe list import
-- This table stores raw data from xtraCHEF export with transformation and validation

-- Drop existing views first
DROP VIEW IF EXISTS vw_stg_recipes_review;
DROP VIEW IF EXISTS vw_stg_recipes_batch_summary;
DROP VIEW IF EXISTS vw_stg_recipes_validation_issues;

-- Drop table
DROP TABLE IF EXISTS stg_recipes;

CREATE TABLE stg_recipes (
    -- Primary key
    staging_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Metadata fields
    original_row_number INTEGER,
    import_batch_id TEXT,
    import_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    needs_review BOOLEAN DEFAULT FALSE,
    review_status TEXT DEFAULT 'pending', -- pending, approved, rejected, corrected
    review_notes TEXT,
    validation_errors TEXT, -- JSON array of validation issues
    
    -- Raw source data (original xtraCHEF headers)
    source_row_json TEXT, -- Complete raw row as JSON
    
    -- Mapped data fields (transformed to new structure)
    -- FAM_Location_Name
    location_name TEXT,
    
    -- Recipe_Name
    recipe_name TEXT,
    recipe_name_flag TEXT,
    
    -- Status
    status TEXT,
    status_flag TEXT,
    
    -- Recipe_Group
    recipe_group TEXT,
    
    -- Recipe_Type
    recipe_type TEXT,
    recipe_type_flag TEXT,
    
    -- Recipe_Food_Cost
    food_cost REAL,
    food_cost_raw TEXT,
    food_cost_flag TEXT,
    
    -- Food_Cost_Percentage
    food_cost_percentage REAL,
    food_cost_percentage_raw TEXT,
    food_cost_percentage_flag TEXT,
    
    -- Labor_Cost
    labor_cost REAL DEFAULT 0,
    labor_cost_raw TEXT,
    
    -- Labor_Cost_Percentage
    labor_cost_percentage REAL DEFAULT 0,
    labor_cost_percentage_raw TEXT,
    
    -- Menu_Price
    menu_price REAL,
    menu_price_raw TEXT,
    menu_price_flag TEXT,
    
    -- Prep_Recipe_Yield_Percentage
    prep_recipe_yield_percentage REAL DEFAULT 100,
    prep_recipe_yield_percentage_raw TEXT,
    
    -- Gross_Margin
    gross_margin REAL,
    gross_margin_raw TEXT,
    gross_margin_flag TEXT,
    
    -- Prime_Cost
    prime_cost REAL,
    prime_cost_raw TEXT,
    
    -- Prime_Cost_Percentage
    prime_cost_percentage REAL,
    prime_cost_percentage_raw TEXT,
    
    -- Date_Cost_Modified
    cost_modified_date TEXT,
    cost_modified_date_raw TEXT,
    cost_modified_date_flag TEXT,
    
    -- Shelf_Life
    shelf_life TEXT,
    
    -- Shelf_Life_Uom
    shelf_life_uom TEXT,
    
    -- Prep_Recipe_Yield
    yield_quantity TEXT,
    yield_quantity_raw TEXT,
    yield_quantity_flag TEXT,
    
    -- Prep_Recipe_Yield_Uom
    yield_unit TEXT,
    yield_unit_flag TEXT,
    
    -- Serving
    serving TEXT,
    
    -- Serving_Size
    serving_size TEXT,
    serving_size_raw TEXT,
    
    -- Serving_Size_Uom
    serving_size_uom TEXT,
    
    -- Per_Serving
    per_serving REAL,
    per_serving_raw TEXT,
    per_serving_flag TEXT,
    
    -- Calculated fields for validation
    calculated_margin REAL,
    calculated_food_cost_percent REAL,
    margin_variance REAL,
    
    -- Processing metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_to_live BOOLEAN DEFAULT FALSE,
    processed_date TIMESTAMP,
    
    -- Duplicate detection
    duplicate_check_hash TEXT,
    is_duplicate BOOLEAN DEFAULT FALSE,
    duplicate_of_staging_id INTEGER,
    
    -- Link to existing recipe if found
    matched_recipe_id INTEGER
);

-- Create indexes for performance
CREATE INDEX idx_stg_recipes_needs_review ON stg_recipes(needs_review);
CREATE INDEX idx_stg_recipes_review_status ON stg_recipes(review_status);
CREATE INDEX idx_stg_recipes_batch ON stg_recipes(import_batch_id);
CREATE INDEX idx_stg_recipes_duplicate ON stg_recipes(duplicate_check_hash);
CREATE INDEX idx_stg_recipes_processed ON stg_recipes(processed_to_live);
CREATE INDEX idx_stg_recipes_recipe_name ON stg_recipes(recipe_name);
CREATE INDEX idx_stg_recipes_food_cost_flag ON stg_recipes(food_cost_flag);

-- Create view for admin review
CREATE VIEW vw_stg_recipes_review AS
SELECT 
    staging_id,
    original_row_number,
    import_batch_id,
    needs_review,
    review_status,
    
    -- Basic info
    location_name,
    recipe_name,
    recipe_name_flag,
    status,
    recipe_group,
    recipe_type,
    recipe_type_flag,
    
    -- Costs and pricing
    food_cost,
    food_cost_flag,
    food_cost_percentage,
    food_cost_percentage_flag,
    menu_price,
    menu_price_flag,
    gross_margin,
    gross_margin_flag,
    
    -- Calculated validations
    calculated_margin,
    calculated_food_cost_percent,
    margin_variance,
    
    -- Yields and servings
    yield_quantity,
    yield_unit,
    yield_quantity_flag,
    serving_size,
    serving_size_uom,
    per_serving,
    per_serving_flag,
    
    -- Metadata
    cost_modified_date,
    validation_errors,
    review_notes,
    is_duplicate,
    matched_recipe_id,
    created_at
FROM stg_recipes
WHERE review_status = 'pending'
ORDER BY needs_review DESC, staging_id;

-- Create summary view for batch statistics
CREATE VIEW vw_stg_recipes_batch_summary AS
SELECT 
    import_batch_id,
    COUNT(*) as total_rows,
    SUM(CASE WHEN needs_review = 1 THEN 1 ELSE 0 END) as needs_review_count,
    SUM(CASE WHEN review_status = 'approved' THEN 1 ELSE 0 END) as approved_count,
    SUM(CASE WHEN review_status = 'rejected' THEN 1 ELSE 0 END) as rejected_count,
    SUM(CASE WHEN is_duplicate = 1 THEN 1 ELSE 0 END) as duplicate_count,
    SUM(CASE WHEN food_cost = 0 OR food_cost IS NULL THEN 1 ELSE 0 END) as zero_cost_count,
    SUM(CASE WHEN ABS(margin_variance) > 0.05 THEN 1 ELSE 0 END) as margin_variance_count,
    MIN(created_at) as batch_start,
    MAX(created_at) as batch_end
FROM stg_recipes
GROUP BY import_batch_id;

-- Create validation issues view
CREATE VIEW vw_stg_recipes_validation_issues AS
SELECT 
    staging_id,
    recipe_name,
    CASE 
        WHEN food_cost = 0 OR food_cost IS NULL THEN 'Zero or missing food cost'
        WHEN food_cost_percentage > 100 THEN 'Food cost % over 100%'
        WHEN food_cost_percentage = 0 AND recipe_type = 'Recipe' THEN 'Recipe with 0% food cost'
        WHEN menu_price = 0 AND recipe_type = 'Recipe' THEN 'Recipe with no menu price'
        WHEN ABS(margin_variance) > 0.05 THEN 'Margin calculation variance > 5%'
        WHEN yield_quantity IS NULL AND recipe_type = 'PrepRecipe' THEN 'Prep recipe missing yield'
        WHEN per_serving = 0 AND recipe_type = 'Recipe' THEN 'Zero per serving cost'
        ELSE 'Other'
    END as issue_type,
    food_cost,
    food_cost_percentage,
    menu_price,
    gross_margin,
    calculated_margin,
    margin_variance
FROM stg_recipes
WHERE needs_review = 1
ORDER BY 
    CASE issue_type
        WHEN 'Zero or missing food cost' THEN 1
        WHEN 'Food cost % over 100%' THEN 2
        WHEN 'Recipe with 0% food cost' THEN 3
        WHEN 'Recipe with no menu price' THEN 4
        WHEN 'Margin calculation variance > 5%' THEN 5
        ELSE 6
    END,
    recipe_name;