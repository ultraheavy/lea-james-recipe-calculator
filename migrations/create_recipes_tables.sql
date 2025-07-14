-- Create main recipes table
CREATE TABLE IF NOT EXISTS recipes (
    recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_name TEXT UNIQUE NOT NULL,
    recipe_prefix TEXT,
    is_prep_recipe BOOLEAN DEFAULT FALSE,
    yield TEXT,
    yield_uom TEXT,
    shelf_life TEXT,
    shelf_life_uom TEXT,
    serving_size TEXT,
    serving_uom TEXT,
    prep_time TEXT,
    cook_time TEXT,
    allergens TEXT,
    source_file TEXT,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT DEFAULT 'pdf_import',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create recipe ingredients table
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    ingredient_name TEXT NOT NULL,
    quantity TEXT,
    unit TEXT,
    cost TEXT,
    source_file TEXT,
    source_text TEXT,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id) ON DELETE CASCADE
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_recipes_name ON recipes(recipe_name);
CREATE INDEX IF NOT EXISTS idx_recipes_prep ON recipes(is_prep_recipe);
CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe ON recipe_ingredients(recipe_id);
CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_name ON recipe_ingredients(ingredient_name);

-- Add committed flag to staging table
ALTER TABLE stg_pdf_recipes ADD COLUMN committed BOOLEAN DEFAULT FALSE;
ALTER TABLE stg_pdf_recipes ADD COLUMN committed_at TIMESTAMP;
ALTER TABLE stg_pdf_recipes ADD COLUMN committed_recipe_id INTEGER;

-- Create index for committed status
CREATE INDEX IF NOT EXISTS idx_stg_pdf_recipes_committed ON stg_pdf_recipes(committed);