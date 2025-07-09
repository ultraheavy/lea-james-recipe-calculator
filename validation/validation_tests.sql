-- ======================================
-- PHASE 5: COMPREHENSIVE SYSTEM VALIDATION
-- ======================================

-- Test 1: Validate 1:1 recipe-menu item constraint
SELECT 'Toast POS Compliance Check' as test,
       COUNT(*) as violations,
       'Should be 0' as expected
FROM (
    SELECT recipe_id, COUNT(*) as items
    FROM menu_items 
    GROUP BY recipe_id 
    HAVING COUNT(*) > 1
);

-- Test 2: Validate no impossible food costs
SELECT 'Reasonable Food Costs' as test,
       COUNT(*) as violations,
       'Should be 0' as expected
FROM recipes r
JOIN menu_items mi ON r.recipe_id = mi.recipe_id
WHERE r.menu_price > 0 AND (r.food_cost / r.menu_price) > 0.85;

-- Test 3: Validate menu system unity
SELECT 'V3 Menu Count' as test,
       COUNT(*) as count,
       'Should be 1' as expected
FROM menus WHERE menu_name LIKE '%V3%';

-- Test 4: Validate data integrity
SELECT 'Orphaned Ingredients' as test,
       COUNT(*) as violations,
       'Should be 0' as expected
FROM recipe_ingredients ri 
LEFT JOIN recipes r ON ri.recipe_id = r.recipe_id 
WHERE r.recipe_id IS NULL;

-- Test 5: Check recipe type distribution
SELECT 'Recipe Type Distribution' as test,
       recipe_type, COUNT(*) as count
FROM recipes
GROUP BY recipe_type;

-- Test 6: Check prep recipes have no menu prices
SELECT 'Prep Recipes Without Menu Prices' as test,
       COUNT(*) as correct,
       'Should equal total prep recipes' as expected
FROM recipes
WHERE recipe_type = 'PrepRecipe' AND menu_price IS NULL;

-- Test 7: Check final recipes have menu items
SELECT 'Final Recipes With Menu Items' as test,
       COUNT(DISTINCT r.recipe_id) as recipes_with_items,
       COUNT(DISTINCT CASE WHEN mi.recipe_id IS NULL THEN r.recipe_id END) as recipes_without_items
FROM recipes r
LEFT JOIN menu_items mi ON r.recipe_id = mi.recipe_id
WHERE r.recipe_type = 'Recipe';

-- Test 8: Menu assignments validation
SELECT 'Menu Item Assignments' as test,
       m.menu_name,
       COUNT(ma.assignment_id) as items_assigned
FROM menus m
LEFT JOIN menu_assignments ma ON m.menu_id = ma.menu_id
GROUP BY m.menu_id, m.menu_name;

-- Test 9: Recipe ingredients cost validation
SELECT 'Ingredients With Costs' as test,
       COUNT(*) as total_ingredients,
       COUNT(CASE WHEN total_cost > 0 THEN 1 END) as with_costs,
       COUNT(CASE WHEN total_cost = 0 THEN 1 END) as without_costs
FROM recipe_ingredients;

-- Test 10: Show migrated data summary
SELECT 'Migration Summary' as test,
       'Recipes' as entity, COUNT(*) as count FROM recipes
UNION ALL
SELECT 'Migration Summary', 'Menu Items', COUNT(*) FROM menu_items
UNION ALL
SELECT 'Migration Summary', 'Menus', COUNT(*) FROM menus
UNION ALL
SELECT 'Migration Summary', 'Menu Assignments', COUNT(*) FROM menu_assignments
UNION ALL
SELECT 'Migration Summary', 'Recipe Ingredients', COUNT(*) FROM recipe_ingredients;