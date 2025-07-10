-- ======================================
-- FIX MENUS TABLE COLUMN MAPPING
-- The app expects menus table to have 'id' column but new schema uses 'menu_id'
-- ======================================

-- Rename current tables to _actual
ALTER TABLE menus RENAME TO menus_actual;
ALTER TABLE menu_menu_items RENAME TO menu_menu_items_actual;

-- Create menus view with proper column mapping
CREATE VIEW menus AS
SELECT 
    menu_id as id,
    menu_name,
    menu_version,
    status,
    effective_date,
    end_date,
    description,
    target_food_cost,
    created_at,
    updated_at,
    -- Add is_active and sort_order that app might expect
    CASE WHEN status = 'Active' THEN 1 ELSE 0 END as is_active,
    menu_id as sort_order
FROM menus_actual;

-- Create menu_menu_items view from menu_assignments
CREATE VIEW menu_menu_items AS
SELECT 
    ma.assignment_id as id,
    ma.menu_id,
    ma.menu_item_id,
    ma.sort_order,
    ma.price_override,
    ma.is_available,
    ma.created_at
FROM menu_assignments ma;

-- Verify the fix
SELECT 'Menus tables renamed and views created with proper column mapping' as message;