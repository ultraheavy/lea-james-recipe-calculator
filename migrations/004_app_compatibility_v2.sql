-- ======================================
-- APP COMPATIBILITY LAYER V2
-- Creates aliases to maintain compatibility with existing app code
-- ======================================

-- First, let's check what tables we actually have
-- The app expects tables with these names: recipes, recipe_ingredients, menu_items

-- Since we already renamed tables during cutover, we need to create 
-- aliases or views that the app can use

-- Create view aliases that map new column names to old ones
DROP VIEW IF EXISTS recipes_app;
CREATE VIEW recipes_app AS
SELECT 
    recipe_id as id,
    recipe_name,
    status,
    recipe_group,
    recipe_type,
    food_cost,
    CASE 
        WHEN menu_price > 0 
        THEN ROUND((food_cost / menu_price) * 100, 2)
        ELSE 0 
    END as food_cost_percentage,
    labor_cost,
    CASE 
        WHEN menu_price > 0 
        THEN ROUND((labor_cost / menu_price) * 100, 2)
        ELSE 0 
    END as labor_cost_percentage,
    menu_price,
    CASE 
        WHEN menu_price > 0 
        THEN menu_price - food_cost
        ELSE 0 
    END as gross_margin,
    food_cost + COALESCE(labor_cost, 0) as prime_cost,
    CASE 
        WHEN menu_price > 0 
        THEN ROUND(((food_cost + COALESCE(labor_cost, 0)) / menu_price) * 100, 2)
        ELSE 0 
    END as prime_cost_percentage,
    CAST(shelf_life_hours AS TEXT) as shelf_life,
    'hours' as shelf_life_uom,
    batch_yield as prep_recipe_yield,
    batch_yield_unit as prep_recipe_yield_uom,
    serving_size,
    serving_unit as serving_size_uom,
    CASE 
        WHEN serving_size > 0 
        THEN food_cost / serving_size
        ELSE 0 
    END as per_serving,
    station,
    instructions as procedure,
    last_cost_calculation as cost_modified,
    created_at as created_date,
    updated_at as updated_date
FROM recipes;

DROP VIEW IF EXISTS recipe_ingredients_app;
CREATE VIEW recipe_ingredients_app AS
SELECT 
    ingredient_id as id,
    recipe_id,
    inventory_id as ingredient_id,
    ingredient_name,
    CASE 
        WHEN inventory_id IS NOT NULL THEN 'Product'
        ELSE 'PrepRecipe'
    END as ingredient_type,
    quantity,
    unit as unit_of_measure,
    total_cost as cost,
    created_at as created_date,
    quantity as canonical_quantity,
    unit as canonical_unit,
    'complete' as conversion_status
FROM recipe_ingredients;

-- For menu_items, we need to handle the version_id concept
DROP VIEW IF EXISTS menu_items_app;
CREATE VIEW menu_items_app AS
SELECT 
    mi.menu_item_id as id,
    mi.item_name,
    mi.menu_category as menu_group,
    mi.description as item_description,
    mi.recipe_id,
    COALESCE(
        (SELECT ma.price_override FROM menu_assignments ma 
         WHERE ma.menu_item_id = mi.menu_item_id 
         AND ma.menu_id = (SELECT menu_id FROM menus WHERE status = 'Active' LIMIT 1)
         LIMIT 1),
        mi.current_price
    ) as menu_price,
    r.food_cost,
    CASE 
        WHEN mi.current_price > 0 
        THEN ROUND((r.food_cost / mi.current_price) * 100, 2)
        ELSE 0 
    END as food_cost_percent,
    CASE 
        WHEN mi.current_price > 0 
        THEN mi.current_price - r.food_cost
        ELSE 0 
    END as gross_profit,
    CASE WHEN mi.is_available THEN 'Active' ELSE 'Inactive' END as status,
    CAST(mi.current_price AS TEXT) as serving_size,
    mi.created_at as created_date,
    mi.updated_at as updated_date,
    -- Map to version_id for compatibility
    CASE 
        WHEN EXISTS (SELECT 1 FROM menu_assignments ma2 
                     JOIN menus m ON ma2.menu_id = m.menu_id 
                     WHERE ma2.menu_item_id = mi.menu_item_id 
                     AND m.menu_name = 'V3 Planning Menu')
        THEN 3
        WHEN EXISTS (SELECT 1 FROM menu_assignments ma2 
                     JOIN menus m ON ma2.menu_id = m.menu_id 
                     WHERE ma2.menu_item_id = mi.menu_item_id 
                     AND m.menu_name = 'Current Menu')
        THEN 2
        ELSE 1  -- Master Menu
    END as version_id
FROM menu_items mi
LEFT JOIN recipes r ON mi.recipe_id = r.recipe_id;

-- Check if menu_versions table exists, if not create view
DROP TABLE IF EXISTS menu_versions;
CREATE VIEW menu_versions AS
SELECT 
    menu_id as id,
    menu_name as version_name,
    description,
    CASE WHEN status = 'Active' THEN 1 ELSE 0 END as is_active,
    created_at as created_date,
    effective_date,
    description as notes
FROM menus;