-- ======================================
-- FIX APP TABLE REFERENCES
-- The app expects tables named: recipes, menu_items, recipe_ingredients
-- But we have: recipes_actual, menu_items_actual, recipe_ingredients_actual
-- ======================================

-- First drop any views using these names
DROP VIEW IF EXISTS recipes;
DROP VIEW IF EXISTS menu_items;
DROP VIEW IF EXISTS recipe_ingredients;

-- Now create views that map the new schema to what the app expects
CREATE VIEW recipes AS
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
FROM recipes_actual;

CREATE VIEW recipe_ingredients AS
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
FROM recipe_ingredients_actual;

CREATE VIEW menu_items AS
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
FROM menu_items_actual mi
LEFT JOIN recipes_actual r ON mi.recipe_id = r.recipe_id;

-- Create/update menu_versions view if needed
DROP VIEW IF EXISTS menu_versions;
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