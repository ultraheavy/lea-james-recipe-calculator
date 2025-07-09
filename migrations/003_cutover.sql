-- ======================================
-- PHASE 4: SYSTEM CUTOVER
-- ======================================

-- Step 1: Backup old tables
ALTER TABLE recipes RENAME TO recipes_old;
ALTER TABLE menu_items RENAME TO menu_items_old;
ALTER TABLE menus RENAME TO menus_old;
ALTER TABLE recipe_ingredients RENAME TO recipe_ingredients_old;
ALTER TABLE menu_menu_items RENAME TO menu_menu_items_old;
ALTER TABLE menu_categories RENAME TO menu_categories_old;

-- Step 2: Activate new tables
ALTER TABLE recipes_new RENAME TO recipes;
ALTER TABLE menu_items_new RENAME TO menu_items;
ALTER TABLE menus_new RENAME TO menus;
ALTER TABLE recipe_ingredients_new RENAME TO recipe_ingredients;
ALTER TABLE menu_assignments_new RENAME TO menu_assignments;

-- Step 3: Create views for backward compatibility (if needed)
DROP VIEW IF EXISTS menu_version_comparison;
CREATE VIEW menu_version_comparison AS
SELECT 
    mi.item_name,
    mi.menu_category as menu_group,
    mi.current_price as menu_price,
    r.food_cost,
    CASE 
        WHEN r.menu_price > 0 
        THEN ROUND((r.food_cost / r.menu_price) * 100, 2)
        ELSE NULL 
    END as food_cost_percent,
    CASE 
        WHEN r.menu_price > 0 
        THEN r.menu_price - r.food_cost
        ELSE NULL 
    END as gross_profit,
    m.menu_name as version_name,
    CASE WHEN m.status = 'Active' THEN 1 ELSE 0 END as is_active,
    r.recipe_name
FROM menu_items mi
JOIN recipes r ON mi.recipe_id = r.recipe_id
JOIN menu_assignments ma ON mi.menu_item_id = ma.menu_item_id
JOIN menus m ON ma.menu_id = m.menu_id
ORDER BY m.menu_name, mi.menu_category, mi.item_name;

-- Step 4: Create helper view for unified menu items
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