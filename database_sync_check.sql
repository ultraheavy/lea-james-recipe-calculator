-- Database Sync Check Script
-- Run this on both local and production databases to compare

-- Menu System Check
SELECT 'MENU TABLES' as category;
SELECT 'menus_actual count', COUNT(*) FROM menus_actual;
SELECT 'menu_items_actual count', COUNT(*) FROM menu_items_actual;
SELECT 'menu_menu_items_actual count', COUNT(*) FROM menu_menu_items_actual;

-- Active Menus
SELECT 'ACTIVE MENUS' as category;
SELECT menu_id, menu_name, menu_version, status FROM menus_actual WHERE status = 'Active';

-- Inventory Check
SELECT 'INVENTORY' as category;
SELECT 'inventory count', COUNT(*) FROM inventory;
SELECT 'vendors count', COUNT(*) FROM vendors;
SELECT 'vendor_products count', COUNT(*) FROM vendor_products;

-- Recipe System Check
SELECT 'RECIPES' as category;
SELECT 'recipes_actual count', COUNT(*) FROM recipes_actual;
SELECT 'recipe_ingredients_actual count', COUNT(*) FROM recipe_ingredients_actual;

-- Recent Activity
SELECT 'RECENT ACTIVITY' as category;
SELECT 'Last inventory update', MAX(updated_date) FROM inventory;
SELECT 'Last recipe update', MAX(updated_date) FROM recipes_actual;
EOF < /dev/null