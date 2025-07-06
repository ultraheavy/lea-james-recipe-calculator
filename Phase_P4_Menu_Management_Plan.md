# Phase P4: Menu Management & UX Enhancement Plan

## Primary Goal
Enable restaurant to create and manage multiple menus with shared menu items, while improving mobile UX.

## Core Functionality Requirements

### 1. Menu Management System
- **Create/Edit/Delete Menus**
  - Menu name, description, active status
  - Menu versions (seasonal, special events)
  - Menu categories/sections
  
- **Menu Item Assignment**
  - Assign items to multiple menus
  - Set item-specific pricing per menu
  - Control item visibility/availability
  - Bulk operations (add/remove multiple items)

### 2. Recipe Editing
- **Full CRUD for Recipes**
  - Edit recipe details and metadata
  - Add/remove/modify ingredients
  - Adjust quantities and yields
  - Maintain cost calculations in real-time
  
### 3. Data Fixes
- Add missing ingredients to recipes 97, 100, 102, 105
- Fix recipes 81 & 87 with >100% food cost

## UX Improvements

### 1. Table Enhancements
- **Restore Column Sorting**
  - Click headers to sort asc/desc
  - Visual indicators for sort direction
  - Multi-column sort capability

### 2. View Switcher
- **Three Display Modes:**
  - Table View (current)
  - List View (compact, mobile-friendly)
  - Card View (visual, swipeable on mobile)
  
### 3. Mobile Optimizations
- Fix hamburger menu functionality
- Responsive card layout for inventory
- Touch-friendly controls (min 44x44px)
- Swipe gestures for navigation
- Bottom tab bar for key actions

## Database Schema Additions

```sql
-- New menus table
CREATE TABLE menus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Menu to menu_item mapping
CREATE TABLE menu_menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_id INTEGER NOT NULL,
    menu_item_id INTEGER NOT NULL,
    category TEXT,
    sort_order INTEGER DEFAULT 0,
    is_available BOOLEAN DEFAULT 1,
    override_price DECIMAL(10,2),
    FOREIGN KEY (menu_id) REFERENCES menus(id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id),
    UNIQUE(menu_id, menu_item_id)
);

-- Menu categories
CREATE TABLE menu_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    menu_id INTEGER NOT NULL,
    category_name TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0,
    FOREIGN KEY (menu_id) REFERENCES menus(id)
);
```

## Implementation Phases

### Phase 4A: Core Menu Features (Priority: HIGH)
1. Database schema updates
2. Menu CRUD operations
3. Menu item assignment interface
4. Basic menu builder UI

### Phase 4B: Recipe Editing (Priority: HIGH)
1. Recipe edit forms
2. Ingredient management
3. Real-time cost updates
4. Validation and error handling

### Phase 4C: UX Enhancements (Priority: MEDIUM)
1. Column sorting restoration
2. View switcher implementation
3. Card view for inventory
4. Mobile navigation fixes

### Phase 4D: Advanced Features (Priority: LOW)
1. Menu analytics/comparison
2. Seasonal menu management
3. Print-friendly menu layouts
4. Menu item recommendations

## Success Metrics
- Users can create multiple menus and assign items
- All tables have sortable columns
- Mobile users can navigate efficiently
- Recipe costs update accurately when edited
- Zero critical data errors remain

## Technical Considerations
- Use Flask-WTF for forms
- HTMX for dynamic updates
- CSS Grid/Flexbox for responsive layouts
- LocalStorage for view preferences
- Progressive enhancement approach