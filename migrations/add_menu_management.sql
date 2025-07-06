-- Menu Management Schema
-- This adds support for creating multiple menus and assigning menu items

-- Create menus table
CREATE TABLE IF NOT EXISTS menus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Menu to menu_item mapping table
CREATE TABLE IF NOT EXISTS menu_menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_id INTEGER NOT NULL,
    menu_item_id INTEGER NOT NULL,
    category TEXT,
    sort_order INTEGER DEFAULT 0,
    is_available BOOLEAN DEFAULT 1,
    override_price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE,
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE,
    UNIQUE(menu_id, menu_item_id)
);

-- Menu categories for organization
CREATE TABLE IF NOT EXISTS menu_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_id INTEGER NOT NULL,
    category_name TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0,
    FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE,
    UNIQUE(menu_id, category_name)
);

-- Add some default menus
INSERT INTO menus (menu_name, description, is_active) VALUES
    ('Main Menu', 'Primary restaurant menu', 1),
    ('Catering Menu', 'Special items for catering orders', 1),
    ('Seasonal Specials', 'Limited time offerings', 0);

-- Add default categories
INSERT INTO menu_categories (menu_id, category_name, sort_order) VALUES
    (1, 'Starters', 1),
    (1, 'Mains', 2),
    (1, 'Sides', 3),
    (1, 'Beverages', 4),
    (1, 'Desserts', 5),
    (2, 'Party Platters', 1),
    (2, 'Individual Boxes', 2),
    (2, 'Beverages', 3);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_menu_menu_items_menu_id ON menu_menu_items(menu_id);
CREATE INDEX IF NOT EXISTS idx_menu_menu_items_item_id ON menu_menu_items(menu_item_id);
CREATE INDEX IF NOT EXISTS idx_menu_categories_menu_id ON menu_categories(menu_id);