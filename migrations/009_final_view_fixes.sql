-- ======================================
-- FINAL VIEW FIXES SUMMARY
-- This documents all the views created for app compatibility
-- ======================================

-- Summary of views created:
-- 1. recipes - Maps recipes_actual columns to old schema names
-- 2. recipe_ingredients - Maps recipe_ingredients_actual to old schema
-- 3. menu_items - Maps menu_items_actual with proper version_id mapping
-- 4. menus - Maps menus_actual with id column for app compatibility
-- 5. menu_menu_items - Maps menu_assignments to old menu_menu_items structure

-- Verify all views exist
SELECT 'View Status Report:' as message;

SELECT 
    name as view_name,
    CASE 
        WHEN type = 'view' THEN 'OK - View exists'
        ELSE 'ERROR - Not a view'
    END as status
FROM sqlite_master 
WHERE name IN ('recipes', 'recipe_ingredients', 'menu_items', 'menus', 'menu_menu_items')
ORDER BY name;

-- Count records accessible through views
SELECT 'Record counts through views:' as message;

SELECT 'recipes view' as view_name, COUNT(*) as count FROM recipes
UNION ALL
SELECT 'recipe_ingredients view' as view_name, COUNT(*) as count FROM recipe_ingredients
UNION ALL
SELECT 'menu_items view' as view_name, COUNT(*) as count FROM menu_items
UNION ALL
SELECT 'menus view' as view_name, COUNT(*) as count FROM menus
UNION ALL
SELECT 'menu_menu_items view' as view_name, COUNT(*) as count FROM menu_menu_items;