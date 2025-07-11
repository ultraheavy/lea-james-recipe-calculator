-- Emergency Production Database Fix
-- This creates the missing tables needed for the new code

-- Create menus_actual table
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

-- Insert default menus if none exist
INSERT OR IGNORE INTO menus_actual (menu_name, menu_version, status, description) 
VALUES 
    ('Current Menu', 'Current', 'Active', 'Current active menu'),
    ('Master Menu', 'Master', 'Active', 'Master menu with all items');

-- Create menu_menu_items_actual table
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