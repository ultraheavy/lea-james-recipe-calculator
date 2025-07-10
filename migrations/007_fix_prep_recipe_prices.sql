-- ======================================
-- FIX PREP RECIPE PRICES
-- Prep recipes should not have menu prices
-- ======================================

-- Update menu items that are linked to prep recipes to have $0 price
UPDATE menu_items_actual
SET current_price = 0.00
WHERE recipe_id IN (
    SELECT recipe_id 
    FROM recipes_actual 
    WHERE recipe_type = 'PrepRecipe'
);

-- Also fix the ones that were clearly prep recipes based on name patterns
UPDATE menu_items_actual
SET current_price = 0.00
WHERE item_name IN (
    SELECT item_name 
    FROM menu_items_actual mi
    JOIN recipes_actual r ON mi.recipe_id = r.recipe_id
    WHERE r.recipe_type = 'PrepRecipe'
       OR r.menu_price IS NULL
       OR r.menu_price = 0
       OR mi.menu_category = 'Ingredient'
);

-- Verify the fix
SELECT 'Fixed prep recipe prices. Items with $0 price:' as message,
       COUNT(*) as count
FROM menu_items_actual
WHERE current_price = 0;