-- ======================================
-- FIX MENU ITEMS VERSION MAPPING
-- The app expects version_ids but we have menu_ids
-- ======================================

-- Drop and recreate the menu_items view with correct mapping
DROP VIEW IF EXISTS menu_items;

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
    -- Map menu_id to version_id for compatibility
    COALESCE(
        (SELECT ma.menu_id 
         FROM menu_assignments ma 
         WHERE ma.menu_item_id = mi.menu_item_id 
         LIMIT 1),
        4  -- Default to Master Menu
    ) as version_id
FROM menu_items_actual mi
LEFT JOIN recipes_actual r ON mi.recipe_id = r.recipe_id;