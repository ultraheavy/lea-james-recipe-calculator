-- Create staging table for CSV recipe imports
CREATE TABLE IF NOT EXISTS stg_csv_recipes (
    staging_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Recipe information
    recipe_name TEXT NOT NULL,
    ingredient_name TEXT NOT NULL,
    quantity TEXT,
    unit TEXT,
    cost TEXT,
    category TEXT,
    is_prep_recipe BOOLEAN DEFAULT FALSE,
    
    -- Source information
    source_filename TEXT NOT NULL,
    row_number INTEGER,
    raw_data TEXT,
    
    -- Validation fields
    needs_review BOOLEAN DEFAULT FALSE,
    review_status TEXT DEFAULT 'pending', -- pending, approved, rejected
    review_notes TEXT,
    validation_errors TEXT,
    
    -- Duplicate detection
    is_duplicate BOOLEAN DEFAULT FALSE,
    duplicate_of_recipe TEXT,
    
    -- Import metadata
    import_batch_id TEXT NOT NULL,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    imported_by TEXT DEFAULT 'csv_import',
    
    -- Commit tracking
    committed BOOLEAN DEFAULT FALSE,
    committed_at TIMESTAMP,
    committed_by TEXT,
    committed_recipe_id INTEGER,
    
    -- Review tracking
    reviewed_at TIMESTAMP,
    reviewed_by TEXT
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_stg_csv_recipes_batch ON stg_csv_recipes(import_batch_id);
CREATE INDEX IF NOT EXISTS idx_stg_csv_recipes_recipe_name ON stg_csv_recipes(recipe_name);
CREATE INDEX IF NOT EXISTS idx_stg_csv_recipes_needs_review ON stg_csv_recipes(needs_review);
CREATE INDEX IF NOT EXISTS idx_stg_csv_recipes_review_status ON stg_csv_recipes(review_status);
CREATE INDEX IF NOT EXISTS idx_stg_csv_recipes_committed ON stg_csv_recipes(committed);
CREATE INDEX IF NOT EXISTS idx_stg_csv_recipes_duplicate ON stg_csv_recipes(is_duplicate);