-- Add prep recipe relationship fields to staging table
ALTER TABLE stg_csv_recipes ADD COLUMN used_as_ingredient BOOLEAN DEFAULT FALSE;
ALTER TABLE stg_csv_recipes ADD COLUMN ingredient_source_type TEXT DEFAULT 'inventory'; -- 'inventory' or 'recipe'
ALTER TABLE stg_csv_recipes ADD COLUMN ingredient_source_id INTEGER;
ALTER TABLE stg_csv_recipes ADD COLUMN ingredient_source_recipe_name TEXT;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_stg_csv_recipes_used_as_ingredient ON stg_csv_recipes(used_as_ingredient);
CREATE INDEX IF NOT EXISTS idx_stg_csv_recipes_source_type ON stg_csv_recipes(ingredient_source_type);
CREATE INDEX IF NOT EXISTS idx_stg_csv_recipes_source_recipe ON stg_csv_recipes(ingredient_source_recipe_name);

-- Add fields to track prep recipe dependencies
ALTER TABLE stg_csv_recipes ADD COLUMN has_prep_dependencies BOOLEAN DEFAULT FALSE;
ALTER TABLE stg_csv_recipes ADD COLUMN missing_prep_recipes TEXT; -- JSON array of missing prep recipe names