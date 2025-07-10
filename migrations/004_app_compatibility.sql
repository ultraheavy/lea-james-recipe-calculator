-- ======================================
-- APP COMPATIBILITY LAYER
-- Creates views to maintain compatibility with existing app code
-- ======================================

-- Drop existing views if they exist
DROP VIEW IF EXISTS menu_version_comparison;
DROP VIEW IF EXISTS unified_menu_items;

-- Create compatibility view for recipes (maps new schema to old column names)
DROP VIEW IF EXISTS recipes_compat;
CREATE VIEW recipes_compat AS
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

-- Create compatibility view for recipe_ingredients
DROP VIEW IF EXISTS recipe_ingredients_compat;
CREATE VIEW recipe_ingredients_compat AS
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

-- Create compatibility view for menu_items (handles version_id)
DROP VIEW IF EXISTS menu_items_compat;
CREATE VIEW menu_items_compat AS
SELECT 
    mi.menu_item_id as id,
    mi.item_name,
    mi.menu_category as menu_group,
    mi.description as item_description,
    mi.recipe_id,
    COALESCE(ma.price_override, mi.current_price) as menu_price,
    r.food_cost,
    CASE 
        WHEN COALESCE(ma.price_override, mi.current_price) > 0 
        THEN ROUND((r.food_cost / COALESCE(ma.price_override, mi.current_price)) * 100, 2)
        ELSE 0 
    END as food_cost_percent,
    CASE 
        WHEN COALESCE(ma.price_override, mi.current_price) > 0 
        THEN COALESCE(ma.price_override, mi.current_price) - r.food_cost
        ELSE 0 
    END as gross_profit,
    CASE WHEN mi.is_available THEN 'Active' ELSE 'Inactive' END as status,
    mi.current_price as serving_size,
    mi.created_at as created_date,
    mi.updated_at as updated_date,
    COALESCE(
        (SELECT m.menu_id FROM menu_assignments ma2 
         JOIN menus m ON ma2.menu_id = m.menu_id 
         WHERE ma2.menu_item_id = mi.menu_item_id 
         AND m.status = 'Active' 
         LIMIT 1), 
        1
    ) as version_id
FROM menu_items mi
LEFT JOIN recipes r ON mi.recipe_id = r.recipe_id
LEFT JOIN menu_assignments ma ON mi.menu_item_id = ma.menu_item_id;

-- Create menu_versions view for compatibility
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

-- Create unified_menu_items view (already exists but recreate for consistency)
DROP VIEW IF EXISTS unified_menu_items;
CREATE VIEW unified_menu_items AS
SELECT 
    mi.menu_item_id as id,
    mi.item_name,
    mi.menu_category as menu_group,
    mi.description as item_description,
    mi.recipe_id,
    r.recipe_name,
    COALESCE(ma.price_override, mi.current_price) as menu_price,
    r.food_cost,
    CASE 
        WHEN COALESCE(ma.price_override, mi.current_price) > 0 
        THEN ROUND((r.food_cost / COALESCE(ma.price_override, mi.current_price)) * 100, 2)
        ELSE NULL 
    END as food_cost_percent,
    CASE WHEN mi.is_available THEN 'Active' ELSE 'Inactive' END as status,
    m.menu_name,
    m.menu_id,
    ma.category_section as category,
    ma.sort_order,
    ma.is_active as is_available
FROM menu_items mi
LEFT JOIN recipes r ON mi.recipe_id = r.recipe_id
LEFT JOIN menu_assignments ma ON mi.menu_item_id = ma.menu_item_id
LEFT JOIN menus m ON ma.menu_id = m.menu_id
WHERE m.menu_name IS NOT NULL;

-- Update the app to use compatibility views by renaming tables
ALTER TABLE recipes RENAME TO recipes_actual;
ALTER TABLE recipes_compat RENAME TO recipes;

ALTER TABLE recipe_ingredients RENAME TO recipe_ingredients_actual;
ALTER TABLE recipe_ingredients_compat RENAME TO recipe_ingredients;

ALTER TABLE menu_items RENAME TO menu_items_actual;
ALTER TABLE menu_items_compat RENAME TO menu_items;