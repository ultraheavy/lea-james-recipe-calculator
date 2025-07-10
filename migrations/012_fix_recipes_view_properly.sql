-- ======================================
-- FIX RECIPES VIEW PROPERLY
-- Map all columns that the app expects
-- ======================================

DROP VIEW IF EXISTS recipes;

CREATE VIEW recipes AS
SELECT 
    recipe_id as id,
    recipe_name,
    status,
    notes,
    notes as recipe_notes,
    -- The app expects portions and portion_unit
    portions_per_batch as portions,
    serving_unit as portion_unit,
    -- The app expects target_yield
    batch_yield as target_yield,
    batch_yield_unit as units,
    food_cost,
    food_cost as prime_cost,
    labor_cost,
    ROUND((food_cost / NULLIF(menu_price, 0)) * 100, 2) as food_cost_percent,
    ROUND((food_cost / NULLIF(menu_price, 0)) * 100, 2) as food_cost_percentage,
    -- The app expects recipe_category (not in new schema, use recipe_type)
    recipe_type as recipe_category,
    recipe_type,
    recipe_group,
    created_at,
    updated_at,
    0 as version,
    -- Additional fields the app might expect
    serving_size,
    serving_unit,
    prep_time_minutes,
    cook_time_minutes,
    station,
    batch_yield,
    batch_yield_unit,
    menu_price,
    target_food_cost_percent,
    instructions,
    allergen_info,
    shelf_life_hours,
    last_cost_calculation
FROM recipes_actual;

-- Test the view
SELECT 'Recipes view fixed' as message, COUNT(*) as count FROM recipes;