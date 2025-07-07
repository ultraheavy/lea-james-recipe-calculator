-- Migration: Add vendor_descriptions table
-- Date: 2025-01-07
-- Purpose: Fix inventory page error by adding missing table

-- Create the vendor_descriptions table if it doesn't exist
CREATE TABLE IF NOT EXISTS vendor_descriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_id INTEGER,
    vendor_name TEXT,
    vendor_description TEXT,
    item_code TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inventory_id) REFERENCES inventory (id),
    UNIQUE(inventory_id, vendor_name)
);

-- Populate with existing vendor descriptions from inventory
INSERT OR IGNORE INTO vendor_descriptions (inventory_id, vendor_name, vendor_description, item_code)
SELECT id, vendor_name, item_description, item_code
FROM inventory
WHERE vendor_name IS NOT NULL;

-- Verify the migration
SELECT COUNT(*) as vendor_descriptions_count FROM vendor_descriptions;