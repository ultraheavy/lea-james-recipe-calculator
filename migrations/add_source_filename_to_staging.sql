-- Add source_filename column to staging tables for better traceability

-- Add to inventory staging table
ALTER TABLE stg_inventory_items ADD COLUMN source_filename TEXT;

-- Add to recipe staging table  
ALTER TABLE stg_recipes ADD COLUMN source_filename TEXT;

-- Add indexes for better query performance
CREATE INDEX idx_stg_inventory_source ON stg_inventory_items(source_filename, original_row_number);
CREATE INDEX idx_stg_recipes_source ON stg_recipes(source_filename, original_row_number);