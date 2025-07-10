-- Document all current issues
CREATE TEMPORARY VIEW current_problems AS
SELECT 'Multiple V3 menus' as issue, COUNT(*) as count,
       GROUP_CONCAT(menu_name) as details
FROM menus WHERE menu_name LIKE '%V3%' OR menu_name LIKE '%v3%'
UNION ALL
SELECT 'Impossible food costs', COUNT(*), 
       GROUP_CONCAT(recipe_name || ': ' || ROUND(food_cost_percentage, 1) || '%', ', ')
FROM recipes WHERE food_cost_percentage > 100
UNION ALL
SELECT 'Menu items without recipes', COUNT(*),
       GROUP_CONCAT(item_name, ', ')
FROM menu_items WHERE recipe_id IS NULL
UNION ALL
SELECT 'Recipes with multiple menu items', COUNT(DISTINCT recipe_name),
       GROUP_CONCAT(recipe_name || ' (' || item_count || ' items)', ', ')
FROM (
   SELECT r.recipe_name, COUNT(mi.id) as item_count
   FROM recipes r 
   JOIN menu_items mi ON r.id = mi.recipe_id
   GROUP BY r.id, r.recipe_name
   HAVING item_count > 1
)
UNION ALL
SELECT 'Duplicate recipe names', COUNT(*),
       GROUP_CONCAT(recipe_name || ' (' || count || ')', ', ')
FROM (
   SELECT recipe_name, COUNT(*) as count
   FROM recipes
   GROUP BY recipe_name
   HAVING COUNT(*) > 1
);

.mode csv
.once analysis/current_problems.csv
SELECT * FROM current_problems;