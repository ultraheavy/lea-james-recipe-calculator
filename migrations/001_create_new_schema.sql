-- ======================================
-- NEW DATABASE SCHEMA BASED ON PDF STRUCTURE
-- ======================================

-- recipes_new (matches PDF recipe format exactly)
CREATE TABLE recipes_new (
    recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_name TEXT NOT NULL UNIQUE,
    
    -- Toast POS Classification (from XtraChef exports)
    recipe_type TEXT NOT NULL CHECK (recipe_type IN ('Recipe', 'PrepRecipe')),
    recipe_group TEXT NOT NULL, -- Main, Sides, Sauces, Ingredient
    status TEXT DEFAULT 'Draft' CHECK (status IN ('Draft', 'Complete', 'Active', 'Retired')),
    
    -- PDF Recipe Header Information
    serving_size REAL,
    serving_unit TEXT,
    prep_time_minutes INTEGER,
    cook_time_minutes INTEGER,
    station TEXT,
    
    -- Yield Information (for prep recipes only)
    batch_yield REAL, -- 10 lb, 50 portions, 4 gallons
    batch_yield_unit TEXT,
    portions_per_batch INTEGER,
    
    -- Cost Information (calculated, not input)
    food_cost REAL DEFAULT 0,
    labor_cost REAL DEFAULT 0,
    
    -- Menu Pricing (only for final recipes, NULL for prep recipes)
    menu_price REAL,
    target_food_cost_percent REAL DEFAULT 30,
    
    -- Additional Recipe Information
    instructions TEXT,
    notes TEXT,
    allergen_info TEXT,
    shelf_life_hours INTEGER,
    
    -- Audit Trail
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_cost_calculation TIMESTAMP,
    migrated_from_old_id INTEGER -- tracks original recipe ID
);

-- menu_items_new (what customers see on menu)
CREATE TABLE menu_items_new (
    menu_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    recipe_id INTEGER NOT NULL UNIQUE, -- ENFORCES Toast POS 1:1 constraint
    
    -- Menu Organization
    menu_category TEXT NOT NULL, -- Entrees, Sides, Beverages
    menu_subcategory TEXT,
    description TEXT,
    
    -- Customer-Facing Information
    allergen_warnings TEXT,
    dietary_tags TEXT, -- vegetarian, gluten-free, etc.
    
    -- Pricing & Availability
    current_price REAL,
    is_available BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    migrated_from_old_id INTEGER,
    
    FOREIGN KEY (recipe_id) REFERENCES recipes_new(recipe_id) ON DELETE RESTRICT
);

-- menus_new (unified menu system)
CREATE TABLE menus_new (
    menu_id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_name TEXT NOT NULL UNIQUE,
    menu_version TEXT NOT NULL, -- "Current", "V3 Planning", "Summer 2025"
    
    -- Menu Status & Timeline
    status TEXT DEFAULT 'Draft' CHECK (status IN ('Draft', 'Testing', 'Active', 'Archived')),
    effective_date DATE,
    end_date DATE,
    
    -- Menu Configuration
    description TEXT,
    target_food_cost REAL DEFAULT 30.0,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- menu_assignments_new (which items appear on which menus)
CREATE TABLE menu_assignments_new (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_id INTEGER NOT NULL,
    menu_item_id INTEGER NOT NULL,
    
    -- Assignment Configuration
    category_section TEXT, -- where on menu it appears
    sort_order INTEGER DEFAULT 0,
    price_override REAL, -- different price for this specific menu
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (menu_id) REFERENCES menus_new(menu_id) ON DELETE CASCADE,
    FOREIGN KEY (menu_item_id) REFERENCES menu_items_new(menu_item_id) ON DELETE CASCADE,
    UNIQUE(menu_id, menu_item_id) -- prevent duplicate assignments
);

-- recipe_ingredients_new (matches PDF ingredient list format)
CREATE TABLE recipe_ingredients_new (
    ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    
    -- PDF Layout: Quantity | Unit | Ingredient Name | Cost
    ingredient_order INTEGER DEFAULT 0,
    quantity REAL NOT NULL,
    unit TEXT NOT NULL,
    ingredient_name TEXT NOT NULL, -- must match inventory.item_description
    inventory_id INTEGER, -- FK to inventory table
    
    -- Cost Information (calculated from inventory prices)
    unit_cost REAL DEFAULT 0,
    total_cost REAL DEFAULT 0,
    
    -- Additional Information
    is_optional BOOLEAN DEFAULT FALSE,
    preparation_notes TEXT, -- "diced", "chopped fine", etc.
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    migrated_from_old_id INTEGER,
    
    FOREIGN KEY (recipe_id) REFERENCES recipes_new(recipe_id) ON DELETE CASCADE,
    FOREIGN KEY (inventory_id) REFERENCES inventory(id)
);

-- Create indexes for performance
CREATE INDEX idx_recipes_new_name ON recipes_new(recipe_name);
CREATE INDEX idx_recipes_new_type ON recipes_new(recipe_type);
CREATE INDEX idx_menu_items_new_recipe ON menu_items_new(recipe_id);
CREATE INDEX idx_menu_assignments_new_menu ON menu_assignments_new(menu_id);
CREATE INDEX idx_menu_assignments_new_item ON menu_assignments_new(menu_item_id);
CREATE INDEX idx_recipe_ingredients_new_recipe ON recipe_ingredients_new(recipe_id);
CREATE INDEX idx_recipe_ingredients_new_inventory ON recipe_ingredients_new(inventory_id);