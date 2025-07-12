-- Create staging table for inventory items import
-- This table stores raw data with validation flags and metadata

-- Drop existing views first
DROP VIEW IF EXISTS vw_stg_inventory_review;
DROP VIEW IF EXISTS vw_stg_inventory_batch_summary;

-- Drop table
DROP TABLE IF EXISTS stg_inventory_items;

CREATE TABLE stg_inventory_items (
    -- Primary key
    staging_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Metadata fields
    original_row_number INTEGER,
    import_batch_id TEXT,
    import_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    needs_review BOOLEAN DEFAULT FALSE,
    review_status TEXT DEFAULT 'pending', -- pending, approved, rejected, corrected
    review_notes TEXT,
    
    -- Mapped data fields (both raw and cleaned values)
    -- FAM_Product_Name (from Product(s))
    FAM_Product_Name_raw TEXT,
    FAM_Product_Name_cleaned TEXT,
    FAM_Product_Name_flag TEXT,
    
    -- FAM_Restaurant_Location_Name (from Location Name)
    FAM_Restaurant_Location_Name_raw TEXT,
    FAM_Restaurant_Location_Name_cleaned TEXT,
    FAM_Restaurant_Location_Name_flag TEXT,
    
    -- Vendor_Name
    Vendor_Name_raw TEXT,
    Vendor_Name_cleaned TEXT,
    Vendor_Name_flag TEXT,
    
    -- Vendor_Item_Code (from Item Code)
    Vendor_Item_Code_raw TEXT,
    Vendor_Item_Code_cleaned TEXT,
    Vendor_Item_Code_flag TEXT,
    
    -- Vendor_Item_Description (from Item Description)
    Vendor_Item_Description_raw TEXT,
    Vendor_Item_Description_cleaned TEXT,
    Vendor_Item_Description_flag TEXT,
    
    -- Vendor_UOM (from UOM)
    Vendor_UOM_raw TEXT,
    Vendor_UOM_cleaned TEXT,
    Vendor_UOM_flag TEXT,
    
    -- Inventory_UOM (from Item UOM)
    Inventory_UOM_raw TEXT,
    Inventory_UOM_cleaned TEXT,
    Inventory_UOM_flag TEXT,
    
    -- Pack_qty (from Pack)
    Pack_qty_raw TEXT,
    Pack_qty_cleaned INTEGER,
    Pack_qty_flag TEXT,
    
    -- Size_qty (from Size)
    Size_qty_raw TEXT,
    Size_qty_cleaned REAL,
    Size_qty_flag TEXT,
    
    -- Size_UOM (from Unit)
    Size_UOM_raw TEXT,
    Size_UOM_cleaned TEXT,
    Size_UOM_flag TEXT,
    
    -- Last_Purchased_Date (from Last Purchased Date)
    Last_Purchased_Date_raw TEXT,
    Last_Purchased_Date_cleaned DATE,
    Last_Purchased_Date_flag TEXT,
    
    -- Last_Purchased_Price (from Last Purchased Price ($))
    Last_Purchased_Price_raw TEXT,
    Last_Purchased_Price_cleaned REAL,
    Last_Purchased_Price_flag TEXT,
    
    -- Processing metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_to_live BOOLEAN DEFAULT FALSE,
    processed_date TIMESTAMP,
    
    -- Duplicate detection
    duplicate_check_hash TEXT,
    is_duplicate BOOLEAN DEFAULT FALSE,
    duplicate_of_staging_id INTEGER
);

-- Create indexes for performance
CREATE INDEX idx_stg_inventory_needs_review ON stg_inventory_items(needs_review);
CREATE INDEX idx_stg_inventory_review_status ON stg_inventory_items(review_status);
CREATE INDEX idx_stg_inventory_batch ON stg_inventory_items(import_batch_id);
CREATE INDEX idx_stg_inventory_duplicate ON stg_inventory_items(duplicate_check_hash);
CREATE INDEX idx_stg_inventory_processed ON stg_inventory_items(processed_to_live);

-- Create view for admin review
CREATE VIEW vw_stg_inventory_review AS
SELECT 
    staging_id,
    original_row_number,
    import_batch_id,
    needs_review,
    review_status,
    
    -- Show cleaned values with flags
    FAM_Product_Name_cleaned as product_name,
    FAM_Product_Name_flag as product_flag,
    
    Vendor_Name_cleaned as vendor,
    Vendor_Item_Code_cleaned as item_code,
    Vendor_Item_Description_cleaned as description,
    
    Vendor_UOM_cleaned as vendor_uom,
    Vendor_UOM_flag as vendor_uom_flag,
    
    Inventory_UOM_cleaned as inventory_uom,
    Inventory_UOM_flag as inventory_uom_flag,
    
    Pack_qty_cleaned as pack_qty,
    Size_qty_cleaned as size_qty,
    Size_UOM_cleaned as size_uom,
    Size_UOM_flag as size_uom_flag,
    
    Last_Purchased_Price_cleaned as last_price,
    Last_Purchased_Price_flag as price_flag,
    
    Last_Purchased_Date_cleaned as last_date,
    
    review_notes,
    created_at
FROM stg_inventory_items
WHERE review_status = 'pending'
ORDER BY needs_review DESC, staging_id;

-- Create summary view for batch statistics
CREATE VIEW vw_stg_inventory_batch_summary AS
SELECT 
    import_batch_id,
    COUNT(*) as total_rows,
    SUM(CASE WHEN needs_review = 1 THEN 1 ELSE 0 END) as needs_review_count,
    SUM(CASE WHEN review_status = 'approved' THEN 1 ELSE 0 END) as approved_count,
    SUM(CASE WHEN review_status = 'rejected' THEN 1 ELSE 0 END) as rejected_count,
    SUM(CASE WHEN is_duplicate = 1 THEN 1 ELSE 0 END) as duplicate_count,
    MIN(created_at) as batch_start,
    MAX(created_at) as batch_end
FROM stg_inventory_items
GROUP BY import_batch_id;