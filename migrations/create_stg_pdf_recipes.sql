-- Create staging table for parsed PDF recipes
-- Each row represents one ingredient from a recipe

CREATE TABLE IF NOT EXISTS stg_pdf_recipes (
    staging_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_name TEXT NOT NULL,
    recipe_prefix TEXT,
    ingredient_name TEXT NOT NULL,
    quantity TEXT,
    unit TEXT,
    cost TEXT,
    is_prep_recipe BOOLEAN DEFAULT FALSE,
    source_file TEXT NOT NULL,
    source_text TEXT,
    needs_review BOOLEAN DEFAULT TRUE,
    
    -- Review and approval fields
    review_notes TEXT,
    approved BOOLEAN DEFAULT FALSE,
    approved_by TEXT,
    approved_at TIMESTAMP,
    
    -- Additional metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for efficient querying
CREATE INDEX idx_stg_pdf_recipes_recipe_name ON stg_pdf_recipes(recipe_name);
CREATE INDEX idx_stg_pdf_recipes_needs_review ON stg_pdf_recipes(needs_review);
CREATE INDEX idx_stg_pdf_recipes_approved ON stg_pdf_recipes(approved);
CREATE INDEX idx_stg_pdf_recipes_is_prep ON stg_pdf_recipes(is_prep_recipe);