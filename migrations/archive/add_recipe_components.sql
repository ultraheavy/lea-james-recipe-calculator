-- Migration: Add recipe_components table for nested/prep recipe support
-- This provides a cleaner way to track recipes used as ingredients in other recipes

-- Create recipe_components table
CREATE TABLE IF NOT EXISTS recipe_components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_recipe_id INTEGER NOT NULL,
    component_recipe_id INTEGER NOT NULL,
    quantity DECIMAL(10,4) NOT NULL,
    unit_of_measure TEXT NOT NULL,
    cost DECIMAL(10,2) DEFAULT 0,
    notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (component_recipe_id) REFERENCES recipes(id) ON DELETE RESTRICT,
    UNIQUE(parent_recipe_id, component_recipe_id)
);

-- Create indexes for performance
CREATE INDEX idx_recipe_components_parent ON recipe_components(parent_recipe_id);
CREATE INDEX idx_recipe_components_component ON recipe_components(component_recipe_id);

-- Create view for easy recipe component analysis
CREATE VIEW recipe_component_details AS
SELECT 
    rc.id,
    rc.parent_recipe_id,
    parent.recipe_name as parent_recipe_name,
    parent.recipe_type as parent_recipe_type,
    rc.component_recipe_id,
    component.recipe_name as component_recipe_name,
    component.recipe_type as component_recipe_type,
    rc.quantity,
    rc.unit_of_measure,
    rc.cost,
    component.food_cost as component_unit_cost,
    component.prep_recipe_yield,
    component.prep_recipe_yield_uom,
    rc.notes
FROM recipe_components rc
JOIN recipes parent ON rc.parent_recipe_id = parent.id
JOIN recipes component ON rc.component_recipe_id = component.id;

-- Migrate existing prep recipe ingredients to recipe_components
-- This identifies recipe_ingredients that reference prep recipes
INSERT INTO recipe_components (
    parent_recipe_id,
    component_recipe_id,
    quantity,
    unit_of_measure,
    cost,
    notes
)
SELECT DISTINCT
    ri.recipe_id as parent_recipe_id,
    pr.id as component_recipe_id,
    ri.quantity,
    ri.unit_of_measure,
    ri.cost,
    'Migrated from recipe_ingredients' as notes
FROM recipe_ingredients ri
JOIN recipes pr ON ri.ingredient_name = pr.recipe_name
WHERE ri.ingredient_type = 'PrepRecipe'
  AND pr.recipe_type = 'PrepRecipe'
  AND NOT EXISTS (
    -- Avoid duplicates if migration runs multiple times
    SELECT 1 FROM recipe_components rc 
    WHERE rc.parent_recipe_id = ri.recipe_id 
      AND rc.component_recipe_id = pr.id
  );

-- Add trigger to update parent recipe costs when component costs change
CREATE TRIGGER update_parent_recipe_costs
AFTER UPDATE OF food_cost ON recipes
WHEN NEW.recipe_type = 'PrepRecipe'
BEGIN
    UPDATE recipe_components
    SET updated_date = CURRENT_TIMESTAMP
    WHERE component_recipe_id = NEW.id;
END;

-- Add column to track nesting depth (optional but useful)
ALTER TABLE recipes ADD COLUMN max_nesting_depth INTEGER DEFAULT 0;

-- Create recursive CTE view to calculate nesting depth
CREATE VIEW recipe_nesting_analysis AS
WITH RECURSIVE recipe_tree AS (
    -- Base case: recipes with no components
    SELECT 
        id as recipe_id,
        recipe_name,
        recipe_type,
        0 as depth,
        id || '' as path
    FROM recipes
    WHERE id NOT IN (SELECT DISTINCT parent_recipe_id FROM recipe_components)
    
    UNION ALL
    
    -- Recursive case: recipes that use other recipes
    SELECT 
        r.id as recipe_id,
        r.recipe_name,
        r.recipe_type,
        rt.depth + 1 as depth,
        rt.path || ' → ' || r.id as path
    FROM recipes r
    JOIN recipe_components rc ON r.id = rc.parent_recipe_id
    JOIN recipe_tree rt ON rc.component_recipe_id = rt.recipe_id
    WHERE rt.depth < 10  -- Prevent infinite recursion
)
SELECT 
    recipe_id,
    recipe_name,
    recipe_type,
    MAX(depth) as max_depth,
    GROUP_CONCAT(path, '; ') as all_paths
FROM recipe_tree
GROUP BY recipe_id, recipe_name, recipe_type;

-- Report on migration results
SELECT 
    'Migrated ' || COUNT(*) || ' prep recipe relationships to recipe_components table' as migration_status
FROM recipe_components
WHERE notes = 'Migrated from recipe_ingredients';