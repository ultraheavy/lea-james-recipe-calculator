# DATA_MODEL.md - Sacred Database Structure

## 🏗️ **ESTABLISHED DATA ARCHITECTURE - DO NOT MODIFY**

### **XtraChef CSV Integration Mapping (IMMUTABLE)**

```csv
XtraChef CSV Column → Database Column → Purpose
==========================================
Invoice Item Code → item_code → Unique identifier from XtraChef
Product Name → item_description → What you actually buy (e.g., "Chicken Breast, Boneless")
Vendor Name → vendor_name → Who sells it (e.g., "Sysco Foods")
Price → current_price → Current cost per unit
Invoice Date → last_purchased_date → When last purchased
Unit → unit_measure → How it's sold (lb, case, each)
```

### **CRITICAL DISTINCTIONS (NEVER CONFUSE)**

#### **Product vs Vendor Information:**
- **`item_description`** = WHAT you buy (product name)
- **`vendor_name`** = WHO sells it (company name)  
- **`vendor_item_code`** = THEIR SKU for the product
- **`item_code`** = XtraChef's universal identifier

#### **WRONG vs RIGHT Examples:**
```sql
-- ❌ WRONG - Don't use vendor codes as product names
item_description = "SYS-12345"  

-- ✅ CORRECT - Use actual product names
item_description = "Chicken Breast, Boneless, 40lb Case"

-- ❌ WRONG - Don't duplicate vendor info
vendor_name = "Sysco Foods"
item_description = "Sysco Chicken Breast"

-- ✅ CORRECT - Separate vendor from product
vendor_name = "Sysco Foods" 
item_description = "Chicken Breast, Boneless, 40lb Case"
```

---

## 📊 **CORE TABLE RELATIONSHIPS (IMMUTABLE)**

### **inventory** (Primary Product Catalog)
```sql
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,           -- Internal PK
    item_code TEXT UNIQUE,                          -- XtraChef ID (sacred)
    item_description TEXT NOT NULL,                 -- Product name (what you buy)
    vendor_name TEXT,                               -- Primary vendor (who sells)
    current_price REAL DEFAULT 0,                   -- Current cost
    last_purchased_price REAL,                      -- Previous cost
    last_purchased_date TEXT,                       -- When last bought
    unit_measure TEXT,                              -- How sold (lb, case, each)
    purchase_unit TEXT,                             -- Purchasing unit
    recipe_cost_unit TEXT,                          -- Recipe usage unit
    pack_size TEXT,                                 -- Size/quantity per unit
    yield_percent REAL DEFAULT 100,                 -- Usable percentage
    product_categories TEXT,                        -- Food categories
    -- XtraChef integration fields (NEVER CHANGE)
    xtra_chef_id TEXT,                              -- XtraChef reference
    vendor_item_code TEXT,                          -- Vendor's SKU
    notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **recipes** (Recipe Definitions)
```sql
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_name TEXT NOT NULL,                      -- Display name
    recipe_group TEXT,                              -- Category
    recipe_type TEXT DEFAULT 'Recipe',              -- Type classification
    status TEXT DEFAULT 'Draft',                    -- Draft/Complete/Active
    food_cost REAL DEFAULT 0,                       -- Calculated ingredient cost
    labor_cost REAL DEFAULT 0,                      -- Prep time cost
    menu_price REAL DEFAULT 0,                      -- Selling price
    gross_margin REAL,                              -- Profit calculation
    prime_cost REAL,                                -- Food + Labor
    shelf_life TEXT,                                -- How long it lasts
    shelf_life_uom TEXT,                            -- Units (days/hours)
    prep_recipe_yield REAL,                         -- How much it makes
    serving_size TEXT,                              -- Portion size
    station TEXT,                                   -- Where made
    procedure TEXT,                                 -- How to make
    notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **recipe_ingredients** (Recipe-Inventory Link)
```sql
CREATE TABLE recipe_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,                     -- Links to recipes.id
    ingredient_id INTEGER NOT NULL,                 -- Links to inventory.id  
    quantity REAL NOT NULL,                         -- How much needed
    unit TEXT,                                      -- Unit of measure
    cost REAL DEFAULT 0,                            -- Calculated cost
    notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES inventory (id) ON DELETE CASCADE
);
```

---

## 🔗 **RELATIONSHIP FLOWS (ESTABLISHED)**

### **XtraChef → Inventory Flow:**
```
XtraChef CSV Export
    ↓ (import_xtrachef_data.py)
inventory table
    ↓ (user selection)
recipe_ingredients 
    ↓ (automatic calculation)
recipes.food_cost
    ↓ (menu pricing)
menu_items.profit_margin
```

### **Cost Calculation Chain (NEVER BREAK):**
```sql
-- 1. Inventory item price updated from XtraChef
UPDATE inventory SET current_price = ? WHERE item_code = ?;

-- 2. Recipe ingredient cost recalculated  
UPDATE recipe_ingredients 
SET cost = (quantity * (SELECT current_price FROM inventory WHERE id = ingredient_id))
WHERE ingredient_id = ?;

-- 3. Recipe total cost recalculated
UPDATE recipes 
SET food_cost = (SELECT SUM(cost) FROM recipe_ingredients WHERE recipe_id = ?)
WHERE id = ?;

-- 4. Menu item profit recalculated
UPDATE menu_items 
SET profit_margin = ((menu_price - (SELECT food_cost FROM recipes WHERE id = recipe_id)) / menu_price * 100)
WHERE recipe_id = ?;
```

---

## 🏷️ **NAMING CONVENTIONS (ENFORCED)**

### **Product Naming Standards:**
```
Format: [Primary Descriptor], [Details], [Package Size]
Examples:
- "Chicken Breast, Boneless, 40lb Case"
- "Tomatoes, Roma, 25lb Box"  
- "Oil, Vegetable, 35lb Jug"
- "Flour, All Purpose, 50lb Bag"
```

### **Vendor Naming Standards:**
```
Format: [Company Name] (no product details)
Examples:
- "Sysco Foods"
- "US Foods" 
- "Restaurant Depot"
- "Performance Food Group"
```

### **Unit Standards:**
```
Weight: lb, oz, kg, g
Volume: gal, qt, pt, cup, fl oz, ml, l
Count: each, case, box, bag, dozen
```

---

## 🔄 **XtraChef Sync Process (PROTECTED)**

### **CSV Import Mapping (NEVER CHANGE):**
```python
# SACRED MAPPING - DO NOT MODIFY
csv_mapping = {
    'Invoice Item Code': 'item_code',           # XtraChef unique ID
    'Product Name': 'item_description',         # What you buy
    'Vendor': 'vendor_name',                    # Who sells it
    'Price': 'current_price',                   # Cost per unit
    'Unit': 'unit_measure',                     # How sold
    'Invoice Date': 'last_purchased_date',      # When purchased
    'Category': 'product_categories'            # Food category
}
```

### **Update Process (ESTABLISHED):**
1. **Export from XtraChef** → CSV file
2. **Run import script** → Updates inventory prices
3. **Automatic recalculation** → Recipe costs update
4. **Menu analysis** → Profit margins recalculate

---

## 🎯 **CUSTOM ITEMS (Future Estimation)**

### **For Items Not Yet Purchased:**
```sql
-- Custom items for cost estimation
INSERT INTO inventory (
    item_code,              -- Custom: "CUSTOM-001"
    item_description,       -- "Wagyu Beef, A5 Grade, 10lb"
    vendor_name,           -- "Specialty Meat Co"
    current_price,         -- Estimated: 150.00
    unit_measure,          -- "lb"
    product_categories,    -- "Proteins"
    notes                  -- "ESTIMATED PRICING - NOT PURCHASED"
);
```

### **Estimation Workflow:**
1. **Research vendors** → Get price quotes
2. **Add as custom item** → Mark as estimated
3. **Build test recipes** → Calculate potential costs
4. **Analyze profitability** → Before committing to purchase
5. **Convert to real** → When actually purchased

---

## ⚖️ **DATA INTEGRITY RULES**

### **Immutable Constraints:**
- **Primary Keys**: Never change existing IDs
- **Foreign Keys**: Never break recipe→ingredient links
- **XtraChef Links**: Never modify item_code mapping
- **Cost Calculations**: Never hardcode, always calculate

### **Validation Rules:**
```sql
-- All prices must be positive
CHECK (current_price >= 0)

-- Yield must be between 0-100%
CHECK (yield_percent > 0 AND yield_percent <= 100)

-- Quantities must be positive  
CHECK (quantity > 0)

-- Required fields cannot be NULL
CHECK (item_description IS NOT NULL)
CHECK (recipe_name IS NOT NULL)
```

---

## 🚨 **CHANGE AUTHORIZATION MATRIX**

| Component | ADD | MODIFY | DELETE | Authorization Required |
|-----------|-----|---------|---------|----------------------|
| XtraChef mapping | ❌ | ❌ | ❌ | OWNER ONLY |
| inventory schema | ✅ | ❌ | ❌ | SENIOR DEV |
| recipe_ingredients | ✅ | ✅ | ✅ | STANDARD |
| Cost calculations | ❌ | ⚠️ | ❌ | SENIOR DEV |
| UI/Templates | ✅ | ✅ | ✅ | STANDARD |

**Legend:**
- ✅ = Allowed with standard process
- ⚠️ = Allowed with approval and testing
- ❌ = Forbidden without owner permission

---

**Remember: This data model represents real restaurant inventory and costs. Breaking it impacts actual business operations and financial calculations.**