-- ======================================
-- FIX MISSING TABLES
-- The app expects menu_categories table
-- ======================================

-- 1. Create menu_categories table
CREATE TABLE IF NOT EXISTS menu_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_id INTEGER NOT NULL,
    category_name TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0,
    FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE
);

-- 2. Copy data from old table
INSERT INTO menu_categories (id, menu_id, category_name, sort_order)
SELECT id, menu_id, category_name, sort_order 
FROM menu_categories_old;

-- 3. Fix food_cost_percentage column in recipes view
-- The app queries for food_cost_percentage but our view provides food_cost_percent
DROP VIEW IF EXISTS recipes;

CREATE VIEW recipes AS
SELECT 
    recipe_id as id,
    recipe_name,
    status,
    recipe_notes as notes,
    target_yield as portions,
    units as portion_unit,
    food_cost,
    food_cost as prime_cost,
    labor_cost,
    ROUND((food_cost / NULLIF(menu_price, 0)) * 100, 2) as food_cost_percent,
    ROUND((food_cost / NULLIF(menu_price, 0)) * 100, 2) as food_cost_percentage,
    recipe_category,
    recipe_type,
    recipe_group,
    created_at,
    updated_at,
    0 as version
FROM recipes_actual;

-- Report
SELECT 'Fixed missing tables and columns' as message;