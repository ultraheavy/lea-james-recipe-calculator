CREATE TABLE inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_code TEXT UNIQUE,
                item_description TEXT NOT NULL,
                vendor_name TEXT,
                current_price REAL,
                last_purchased_price REAL,
                last_purchased_date TEXT,
                unit_measure TEXT,
                purchase_unit TEXT,
                recipe_cost_unit TEXT,
                pack_size TEXT,
                yield_percent REAL DEFAULT 100,
                product_categories TEXT,
                close_watch BOOLEAN DEFAULT FALSE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            , density_g_per_ml DECIMAL(10,4), count_to_weight_g DECIMAL(10,2));
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_name TEXT NOT NULL UNIQUE,
                status TEXT DEFAULT 'Draft',
                recipe_group TEXT,
                recipe_type TEXT DEFAULT 'Recipe',
                food_cost REAL DEFAULT 0,
                food_cost_percentage REAL DEFAULT 0,
                labor_cost REAL DEFAULT 0,
                labor_cost_percentage REAL DEFAULT 0,
                menu_price REAL DEFAULT 0,
                gross_margin REAL DEFAULT 0,
                prime_cost REAL DEFAULT 0,
                prime_cost_percentage REAL DEFAULT 0,
                shelf_life TEXT,
                shelf_life_uom TEXT,
                prep_recipe_yield TEXT,
                prep_recipe_yield_uom TEXT,
                serving_size TEXT,
                serving_size_uom TEXT,
                per_serving REAL DEFAULT 0,
                station TEXT,
                procedure TEXT,
                cost_modified TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
CREATE TABLE recipe_ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER,
                ingredient_id INTEGER,
                ingredient_name TEXT,
                ingredient_type TEXT DEFAULT 'Product',
                quantity REAL,
                unit_of_measure TEXT,
                cost REAL DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, canonical_quantity DECIMAL(10,4), canonical_unit TEXT, conversion_status TEXT,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id),
                FOREIGN KEY (ingredient_id) REFERENCES inventory (id)
            );
CREATE TABLE menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                menu_group TEXT,
                item_description TEXT,
                recipe_id INTEGER,
                menu_price REAL DEFAULT 0,
                food_cost REAL DEFAULT 0,
                food_cost_percent REAL DEFAULT 0,
                gross_profit REAL DEFAULT 0,
                status TEXT DEFAULT 'Active',
                serving_size TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, version_id INTEGER,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            );
CREATE TABLE vendors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_name TEXT NOT NULL UNIQUE,
                contact_info TEXT,
                address TEXT,
                phone TEXT,
                email TEXT,
                active BOOLEAN DEFAULT TRUE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
CREATE INDEX idx_inventory_description ON inventory(item_description);
CREATE INDEX idx_recipes_name ON recipes(recipe_name);
CREATE INDEX idx_recipe_ingredients_recipe ON recipe_ingredients(recipe_id);
CREATE INDEX idx_menu_items_group ON menu_items(menu_group);
CREATE TABLE vendor_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER NOT NULL,
                vendor_id INTEGER NOT NULL,
                vendor_item_code TEXT,
                vendor_price REAL,
                last_purchased_date TEXT,
                last_purchased_price REAL,
                pack_size TEXT,
                unit_measure TEXT,
                is_primary BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (inventory_id) REFERENCES inventory(id),
                FOREIGN KEY (vendor_id) REFERENCES vendors(id),
                UNIQUE(inventory_id, vendor_id, vendor_item_code)
            );
CREATE INDEX idx_vendor_products_inventory 
            ON vendor_products(inventory_id)
        ;
CREATE INDEX idx_vendor_products_vendor 
            ON vendor_products(vendor_id)
        ;
CREATE INDEX idx_vendor_products_active 
            ON vendor_products(is_active)
        ;
CREATE TRIGGER update_inventory_last_purchase
            AFTER UPDATE OF last_purchased_date, last_purchased_price 
            ON vendor_products
            WHEN NEW.is_primary = 1
            BEGIN
                UPDATE inventory
                SET 
                    last_purchased_date = NEW.last_purchased_date,
                    last_purchased_price = NEW.last_purchased_price,
                    current_price = NEW.vendor_price,
                    updated_date = CURRENT_TIMESTAMP
                WHERE id = NEW.inventory_id;
            END;
CREATE TABLE menu_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_name TEXT NOT NULL UNIQUE,
                description TEXT,
                is_active BOOLEAN DEFAULT FALSE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                effective_date TEXT,
                notes TEXT
            );
CREATE VIEW menu_version_comparison AS
            SELECT 
                mi.item_name,
                mi.menu_group,
                mi.menu_price,
                mi.food_cost,
                mi.food_cost_percent,
                mi.gross_profit,
                mv.version_name,
                mv.is_active,
                r.recipe_name
            FROM menu_items mi
            JOIN menu_versions mv ON mi.version_id = mv.id
            LEFT JOIN recipes r ON mi.recipe_id = r.id
            ORDER BY mv.version_name, mi.menu_group, mi.item_name
/* menu_version_comparison(item_name,menu_group,menu_price,food_cost,food_cost_percent,gross_profit,version_name,is_active,recipe_name) */;
CREATE TABLE units (
                unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                symbol TEXT NOT NULL UNIQUE,
                dimension TEXT NOT NULL CHECK(dimension IN ('WEIGHT', 'VOLUME', 'COUNT')),
                to_canonical_factor DECIMAL(20,10) NOT NULL,
                is_precise BOOLEAN DEFAULT 1,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
CREATE TABLE ingredient_unit_equivalents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER NOT NULL,
                custom_unit_name TEXT NOT NULL,
                canonical_quantity DECIMAL(10,4) NOT NULL,
                canonical_unit_symbol TEXT NOT NULL,
                notes TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (inventory_id) REFERENCES inventory(id),
                UNIQUE(inventory_id, custom_unit_name)
            );
CREATE TABLE unit_conversion_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_ingredient_id INTEGER,
                from_quantity DECIMAL(10,4),
                from_unit TEXT,
                to_quantity DECIMAL(10,4),
                to_unit TEXT,
                conversion_method TEXT,
                conversion_status TEXT,
                error_message TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipe_ingredient_id) REFERENCES recipe_ingredients(id)
            );
CREATE INDEX idx_units_symbol ON units(symbol);
CREATE INDEX idx_units_dimension ON units(dimension);
CREATE INDEX idx_ingredient_equivalents ON ingredient_unit_equivalents(inventory_id);
CREATE TABLE ingredient_densities (
                    density_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ingredient_name TEXT NOT NULL UNIQUE,
                    density_g_per_ml DECIMAL(10,4) NOT NULL,
                    source TEXT,
                    notes TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
CREATE INDEX idx_ingredient_densities_name 
                ON ingredient_densities(ingredient_name)
            ;
CREATE TABLE vendor_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER,
                vendor_name TEXT,
                vendor_description TEXT,
                item_code TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (inventory_id) REFERENCES inventory (id),
                UNIQUE(inventory_id, vendor_name)
            );
