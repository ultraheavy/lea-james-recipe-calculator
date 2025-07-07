# Data Relationship Diagram - Restaurant Calculator

## Core Relationships

```
MENU ITEMS (what customers see)
    ├── item_name (e.g., "Nashville Hot Chicken Sandwich")
    ├── recipe_id → RECIPES
    └── version_id → MENU_VERSIONS

RECIPES (how to make items)
    ├── recipe_name (e.g., "Nashville Hot Chicken Recipe")
    ├── recipe_group (category)
    └── has many → RECIPE_INGREDIENTS

RECIPE_INGREDIENTS (what goes into recipes)
    ├── recipe_id → RECIPES
    ├── ingredient_id → INVENTORY (this is the KEY connection!)
    ├── ingredient_name (should match inventory.item_description)
    └── quantity & unit

INVENTORY (raw ingredients/items)
    ├── id (referenced by recipe_ingredients.ingredient_id)
    ├── item_code (internal code like "CHK-001")
    ├── item_description (THE ACTUAL INGREDIENT NAME like "Chicken Breast")
    └── vendor info, pricing, etc.

VENDOR_PRODUCTS (supplier info)
    ├── inventory_id → INVENTORY
    ├── vendor_id → VENDORS
    └── vendor-specific pricing/codes
```

## Key Points:

1. **INVENTORY.item_description** = The ingredient name used in recipes (e.g., "Chicken Breast", "Hot Sauce")
2. **INVENTORY.item_code** = Internal tracking code (e.g., "CHK-001", "SAU-023")
3. **RECIPE_INGREDIENTS.ingredient_name** should match **INVENTORY.item_description**
4. The connection: RECIPE_INGREDIENTS.ingredient_id → INVENTORY.id

## Inventory Table Display Requirements:

The inventory table should show:
1. **Item Name**: `item_description` (THE INGREDIENT NAME - "Chicken Breast")
2. **Vendor Description**: Vendor's description of the item
3. **Vendor**: `vendor_name` 
4. **Vendor Code**: `vendor_item_code`
5. **Last Purchased Date**: `last_purchased_date`
6. **Price**: `current_price`
7. **Pack Size**: `pack_size`

## Why This Matters:

- When a chef looks for "Chicken Breast" in inventory, they need to see "Chicken Breast" (item_description), NOT "CHK-001" (item_code)
- The item_description is what connects to recipes through recipe_ingredients
- This is the whole point of the system - connecting recipes to actual inventory items