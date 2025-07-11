-- Menu System Unification Migration Script
-- This migrates from the dual menu system (menu_versions + menus) to unified menus_actual
-- Run this on production after backing up your database!

-- Step 1: Backup existing data (run these manually first!)
-- sqlite3 restaurant_calculator.db ".backup restaurant_calculator_backup.db"

-- Step 2: Check if migration is needed
SELECT 'Current menu_versions count:', COUNT(*) FROM menu_versions;
SELECT 'Current menus count:', COUNT(*) FROM menus;
SELECT 'Current menus_actual count:', COUNT(*) FROM menus_actual;

-- Step 3: Create menus_actual table if it doesn't exist
CREATE TABLE IF NOT EXISTS menus_actual (
    menu_id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_name TEXT NOT NULL UNIQUE,
    menu_version TEXT NOT NULL,
    status TEXT DEFAULT 'Draft' CHECK (status IN ('Draft', 'Testing', 'Active', 'Archived')),
    effective_date DATE,
    end_date DATE,
    description TEXT,
    target_food_cost REAL DEFAULT 30.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 4: Migrate data from menu_versions to menus_actual (if not already done)
INSERT OR IGNORE INTO menus_actual (menu_name, menu_version, status, description, created_at)
SELECT 
    name,
    name, -- Use name as version for now
    CASE WHEN is_active = 1 THEN 'Active' ELSE 'Draft' END,
    'Migrated from menu_versions',
    created_at
FROM menu_versions
WHERE NOT EXISTS (
    SELECT 1 FROM menus_actual 
    WHERE menus_actual.menu_name = menu_versions.name
);

-- Step 5: Create menu_menu_items_actual if it doesn't exist
CREATE TABLE IF NOT EXISTS menu_menu_items_actual (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    category TEXT,
    display_order INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (menu_id) REFERENCES menus_actual(menu_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes_actual(id),
    UNIQUE(menu_id, recipe_id)
);

-- Step 6: Migrate menu items relationships
-- First, ensure we have the relationships from the old system
INSERT OR IGNORE INTO menu_menu_items_actual (menu_id, recipe_id, category, display_order)
SELECT 
    ma.menu_id,
    mi.recipe_id,
    mi.category,
    mi.position
FROM menu_items mi
JOIN menu_versions mv ON mi.version_id = mv.id
JOIN menus_actual ma ON ma.menu_name = mv.name
WHERE mi.recipe_id IS NOT NULL
  AND EXISTS (SELECT 1 FROM recipes_actual WHERE id = mi.recipe_id);

-- Step 7: Update app routes (this is handled in code, not SQL)
-- The app.py file should now use menus_actual instead of menu_versions

-- Step 8: Verification queries
SELECT '=== MIGRATION VERIFICATION ===' as info;
SELECT 'Menus migrated:', COUNT(*) FROM menus_actual;
SELECT 'Menu items migrated:', COUNT(*) FROM menu_menu_items_actual;
SELECT 'Active menus:', COUNT(*) FROM menus_actual WHERE status = 'Active';

-- Step 9: List migrated menus
SELECT '=== MIGRATED MENUS ===' as info;
SELECT menu_id, menu_name, menu_version, status FROM menus_actual ORDER BY menu_id;

-- Optional: Clean up old tables (only after verifying everything works!)
-- DROP TABLE IF EXISTS menu_versions;
-- DROP TABLE IF EXISTS menu_items;
-- But keep them for now as backup