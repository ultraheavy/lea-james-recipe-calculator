-- ======================================
-- RESTORE LOST MENU ITEMS
-- We incorrectly enforced a UNIQUE constraint on recipe_id
-- This caused 72 menu items to be lost during migration
-- ======================================

-- First, we need to remove the UNIQUE constraint on recipe_id
-- SQLite doesn't support ALTER TABLE DROP CONSTRAINT, so we need to recreate the table

-- 1. Create new table without UNIQUE constraint
CREATE TABLE menu_items_new (
    menu_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    recipe_id INTEGER NOT NULL, -- REMOVED UNIQUE constraint
    
    -- Menu Organization
    menu_category TEXT NOT NULL,
    menu_subcategory TEXT,
    description TEXT,
    
    -- Customer-Facing Information
    allergen_warnings TEXT,
    dietary_tags TEXT,
    
    -- Pricing & Availability
    current_price REAL,
    is_available BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    migrated_from_old_id INTEGER,
    version_id INTEGER DEFAULT 1,
    
    FOREIGN KEY (recipe_id) REFERENCES recipes_actual(recipe_id) ON DELETE RESTRICT
);

-- 2. Copy existing data
INSERT INTO menu_items_new SELECT * FROM menu_items_actual;

-- 3. Restore lost menu items from old system
INSERT INTO menu_items_new (
    item_name,
    recipe_id,
    menu_category,
    menu_subcategory,
    description,
    current_price,
    is_available,
    sort_order,
    migrated_from_old_id,
    version_id
)
SELECT 
    mo.item_name,
    mo.recipe_id,
    COALESCE(mo.menu_group, 'Other'),
    NULL as menu_subcategory,
    mo.item_description,
    mo.menu_price,
    CASE WHEN mo.status = 'Active' THEN 1 ELSE 0 END,
    0 as sort_order,
    mo.id as migrated_from_old_id,
    mo.version_id
FROM menu_items_old mo
WHERE mo.id NOT IN (
    SELECT migrated_from_old_id 
    FROM menu_items_actual 
    WHERE migrated_from_old_id IS NOT NULL
)
AND mo.recipe_id IN (SELECT recipe_id FROM recipes_actual);

-- 4. Drop old table and rename new one
DROP TABLE menu_items_actual;
ALTER TABLE menu_items_new RENAME TO menu_items_actual;

-- 5. Recreate the view
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
    COALESCE(
        (SELECT ma.menu_id 
         FROM menu_assignments ma 
         WHERE ma.menu_item_id = mi.menu_item_id 
         LIMIT 1),
        mi.version_id
    ) as version_id
FROM menu_items_actual mi
LEFT JOIN recipes_actual r ON mi.recipe_id = r.recipe_id;

-- Report results
SELECT 'Restored menu items. New count:' as message, COUNT(*) as count FROM menu_items_actual;