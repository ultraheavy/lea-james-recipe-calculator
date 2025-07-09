# CSV Data Mapping & Relationships - CORRECTED Source of Truth

## 📊 **CORRECTED CSV FILE STRUCTURE ANALYSIS**

### **File 1: Recipe Summary** (`LEA_JANES_Recipe_List_Summary_7_4_2025 7_51_55 PM.csv`)
**Purpose**: Master list of all recipes with calculated costs and menu pricing

| Column Name | Data Type | Example Value | Purpose | FK/PK Relationship |
|------------|-----------|---------------|---------|-------------------|
| `LocationName` | String | "Lea James Hot Chicken" | Restaurant identifier | - |
| `RecipeName` | String | "FC-03 Whole Wings" | **PRIMARY KEY** | PK for recipe links |
| `Status` | String | "Draft" | Recipe approval state | - |
| `RecipeGroup` | String | "Main" | Menu category | - |
| `Type` | String | "Recipe" or "PrepRecipe" | Recipe classification | - |
| `FoodCost` | Decimal(2) | 1.62 | Calculated total ingredient cost | CALCULATED |
| `MenuPrice` | Decimal(2) | 14.00 | Selling price | - |
| `GrossMargin` | Decimal(2) | 88.42 | Profit percentage | CALCULATED |
| `ServingSize` | Integer | 1 | Portion count | - |
| `ServingSizeUom` | String | "each" | Unit of measure | - |

---

### **File 2: Inventory Items** (`Lea_Janes__Item_LIST_READY_FOR_IMPORT_latest.csv`)
**Purpose**: XtraChef inventory with vendor info and pricing - **Product(s) is the KEY field**

| Column Name | Data Type | Example Value | Purpose | FK/PK Relationship |
|------------|-----------|---------------|---------|-------------------|
| `Location Name` | String | "Lea James Hot Chicken" | Restaurant identifier | - |
| `Vendor Name` | String | "Buckhead Meat & Seafood OF HOUSTON" | Supplier company name | - |
| `Item Code` | String | "58897_XC11484066" | XtraChef internal ID | - |
| `Item Description` | String | "4 \| 10#av CHICKEN WING BUFFALO 1812 JNT" | Vendor-specific product description | - |
| `UOM` | String | "lb" | Purchase unit of measure | **CRITICAL for calculations** |
| `Pack` | Decimal | 4.0 | Package quantity | **CRITICAL for calculations** |
| `Size` | Decimal | 10.0 | Package size | **CRITICAL for calculations** |
| `Unit` | String | "ea" | Individual unit | **CRITICAL for calculations** |
| `Contracted Price ($)` | Decimal(2) | 42.90 | Current cost per UOM | **CRITICAL for calculations** |
| `Last Purchased Price ($)` | Decimal(2) | 42.90 | Previous cost | - |
| `Last Purchased Date` | Date | "3/18/2025" | When last bought | - |
| **`Product(s)`** | String | **"Protein, Chicken, Wing"** | **PRIMARY KEY - Standardized ingredient name** | **PK for recipe ingredients** |

---

### **File 3: Recipe Details** (Individual recipe CSVs like `Plain Jane Sandwich_...csv`)
**Purpose**: Detailed ingredient lists and procedures for each recipe - **NEEDS RESTRUCTURING**

#### **Header Section:**
| Field | Example Value | Purpose | Data Type |
|-------|---------------|---------|-----------|
| Location | "Lea James Hot Chicken" | Restaurant identifier | String |
| Recipe Name | "Plain Jane Sandwich" | **Links to Recipe Summary** | String (FK) |
| Type | "Main" | Menu category | String |
| Menu Price | "$15" | Selling price | Decimal(2) |
| Food Cost | "$3.14" | Total ingredient cost | Decimal(2) |
| Gross Margin | "79.05%" | Profit percentage | Decimal(2) |

#### **Ingredients Section - CURRENT PROBLEMATIC STRUCTURE:**
| Column Name | Current Example | Problem |
|------------|-----------------|---------|
| `Ingredient` | "Protein, Chicken, Tenders" | ✅ Correct - matches Product(s) |
| `Measurement` | "8 oz" | ❌ **MIXED quantity and unit** |

#### **Ingredients Section - CORRECTED STRUCTURE NEEDED:**
| Column Name | Data Type | Example Value | Purpose | FK/PK Relationship |
|------------|-----------|---------------|---------|-------------------|
| `Ingredient` | String | "Protein, Chicken, Tenders" | **FOREIGN KEY to Product(s)** | **Links to Inventory** |
| `Type` | String | "Product" or "PrepRecipe" | Ingredient classification | - |
| `Quantity` | Decimal | 8.0 | **Amount needed (numeric only)** | **CRITICAL for calculations** |
| `Unit` | String | "oz" | **Unit of measure (separate)** | **CRITICAL for calculations** |
| `Yield` | Decimal(2) | 100.00 | Usable percentage | **CRITICAL for calculations** |
| `Extended_Cost` | Decimal(2) | 2.01 | Calculated cost | **CALCULATED** |

---

## 🔗 **CORRECTED DATA RELATIONSHIPS**

### **Primary Keys (PKs):**
1. **Recipe Summary**: `RecipeName` (e.g., "Plain Jane Sandwich")
2. **Inventory**: **`Product(s)`** (e.g., "Protein, Chicken, Tenders") - **NOT Item Code**
3. **Recipe Details**: Combination of `Recipe Name` + `Ingredient`

### **Foreign Keys (FKs):**
1. **Recipe Details → Recipe Summary**: `Recipe Name` field
2. **Recipe Details → Inventory**: **`Ingredient` field EXACTLY MATCHES `Product(s)` field**

### **CRITICAL CORRECTION:**
- Recipe `Ingredient` = "Protein, Chicken, Tenders"
- Inventory `Product(s)` = "Protein, Chicken, Tenders"  
- **EXACT MATCH REQUIRED** - This is the standardized ingredient name from XtraChef

---

## 📋 **CORRECTED DATA RELATIONSHIP FLOW**

```
XtraChef System
    ↓ (standardized product names)
Inventory Items (Product(s) = standardized ingredient names)
    ↓ (Product(s) as FK)
Recipe Ingredients (Ingredient matches Product(s))
    ↓ (Recipe Name as FK)
Recipe Summary (Master recipes with calculated costs)
    ↓ (Cost calculations)
Menu Items with Profit Analysis
```

### **CORRECTED Cost Calculation Chain:**
1. **Recipe Detail** specifies `Ingredient` + `Quantity` + `Unit` (e.g., "Protein, Chicken, Tenders", 8, "oz")
2. **`Ingredient` EXACTLY MATCHES `Product(s)`** in inventory 
3. **Inventory Item** provides `Contracted Price ($)` per `UOM` with `Pack` + `Size` conversion factors
4. **Unit Conversion**: Recipe `Unit` → Inventory `UOM` (oz → lb conversion)
5. **Extended Cost** = (Quantity ÷ Conversion Factor) × (Contracted Price ÷ Pack ÷ Size) × Yield%
6. **Recipe Food Cost** = Sum of all ingredient extended costs (rounded to 2 decimals)
7. **Gross Margin** = (Menu Price - Food Cost) ÷ Menu Price × 100 (rounded to 2 decimals)

---

## ⚠️ **CRITICAL ISSUES IDENTIFIED & SOLUTIONS**

### **1. Measurement Field Must Be Split**
**Problem**: "8 oz" in one field prevents calculations
**Solution**: 
- `Quantity`: 8.0 (numeric)
- `Unit`: "oz" (text)

### **2. Unit Conversion System Required**
**Problem**: Recipe units (oz, each, cup) vs Inventory UOM (lb, case, gallon)
**Solution**: Unit conversion table for calculations

### **3. Financial Fields Must Use Decimal(2)**
**Problem**: Inconsistent decimal places in cost fields
**Solution**: All currency fields rounded to 2 decimal places

### **4. Pack/Size/UOM Critical for Calculations**
**Problem**: Inventory calculation complexity not accounted for
**Solution**: 
- UOM = "case", Pack = 4, Size = 10, Unit = "lb"
- Means: 1 case = 4 packages of 10 lbs each = 40 lbs total
- Price per lb = Contracted Price ÷ (Pack × Size)

---

## 🎯 **CORRECTED DATABASE SCHEMA**

### **1. Inventory Table (Corrected)**
```sql
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_name TEXT,
    vendor_name TEXT,
    item_code TEXT,                     -- XtraChef ID
    item_description TEXT,              -- Vendor specific name
    product_name TEXT UNIQUE,           -- Product(s) - STANDARDIZED KEY
    uom TEXT,                          -- Purchase unit (lb, case, gallon)
    pack DECIMAL,                      -- Package count
    size DECIMAL,                      -- Package size  
    unit TEXT,                         -- Individual unit
    contracted_price DECIMAL(10,2),    -- Price per UOM
    last_purchased_price DECIMAL(10,2),
    last_purchased_date DATE
);
```

### **2. Recipe Ingredients Table (Corrected)**
```sql
CREATE TABLE recipe_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_name TEXT,                   -- FK to recipes.recipe_name
    ingredient_name TEXT,               -- FK to inventory.product_name
    ingredient_type TEXT,               -- Product or PrepRecipe
    quantity DECIMAL(10,3),             -- Numeric amount only
    unit TEXT,                         -- Unit of measure only
    yield_percentage DECIMAL(5,2),      -- Usable percentage
    extended_cost DECIMAL(10,2),        -- Calculated cost
    FOREIGN KEY (recipe_name) REFERENCES recipes (recipe_name),
    FOREIGN KEY (ingredient_name) REFERENCES inventory (product_name)
);
```

### **3. Unit Conversion Table (NEW)**
```sql
CREATE TABLE unit_conversions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_unit TEXT,
    to_unit TEXT,
    conversion_factor DECIMAL(10,6)     -- Multiply by this to convert
);

-- Examples:
-- oz to lb: 0.0625 (1 oz = 0.0625 lb)
-- cup to gallon: 0.0625 (1 cup = 0.0625 gallon)
```

---

## 🚨 **IMMEDIATE CORRECTION REQUIREMENTS**

1. **Split Measurement Field**: Separate quantity and unit in all recipe CSVs
2. **Use Product(s) as PK**: Change inventory primary key from Item Code to Product(s)
3. **Implement Unit Conversions**: Build conversion table for recipe calculations
4. **Financial Field Formatting**: Round all costs to 2 decimal places
5. **Validate Pack/Size Logic**: Ensure UOM calculations account for packaging
6. **Recipe Type Handling**: Distinguish between Products and PrepRecipes in calculations

---

## 💡 **UNDERSTANDING XTRACHEF WORKFLOW**

**XtraChef Purpose**: Inventory management system that standardizes product names across vendors
- **Vendor A**: "4 | 10#av CHICKEN WING BUFFALO 1812 JNT" 
- **Vendor B**: "20lb Case Buffalo Wings Premium"
- **XtraChef Standardizes To**: "Protein, Chicken, Wing"

**Menu Creation Process**:
1. **Recipes** use standardized ingredient names from XtraChef
2. **Inventory** links vendor-specific products to standardized names  
3. **Cost Calculations** use vendor pricing with standardized naming
4. **Menu Engineering** analyzes profitability using consistent data

This standardization allows restaurants to:
- Compare vendor pricing for same ingredients
- Maintain consistent recipes regardless of supplier changes
- Calculate accurate costs despite different packaging/naming