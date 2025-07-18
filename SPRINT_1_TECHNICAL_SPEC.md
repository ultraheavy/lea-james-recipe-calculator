# Sprint 1: Technical Specification
## Critical Fixes & Recipe Editing Implementation

### Overview
Sprint 1 focuses on fixing critical data issues and implementing the recipe editing interface - the most requested missing feature.

## Task 1: Fix Critical Data Issues

### 1.1 Fix Recipes with >100% Food Cost
**Problem**: Recipes 81 and 87 show impossible food cost percentages

**Investigation Steps**:
```sql
-- Analyze the problematic recipes
SELECT r.id, r.name, r.recipe_cost, r.selling_price, 
       r.food_cost_percentage, r.profit_margin
FROM recipes r
WHERE r.id IN (81, 87);

-- Check their ingredients
SELECT ri.*, i.name, i.unit_price, i.purchase_unit
FROM recipe_ingredients ri
JOIN inventory i ON ri.inventory_id = i.id
WHERE ri.recipe_id IN (81, 87);
```

**Solution Approach**:
1. Check if selling prices are incorrectly low
2. Verify ingredient quantities and unit conversions
3. Look for missing yield percentages
4. Recalculate costs after fixes

### 1.2 Add Missing Ingredients
**Affected Recipes**: 97, 100, 102, 105

**Implementation**:
```python
# Create script: fix_missing_ingredients.py
def add_missing_ingredients():
    missing_data = {
        97: [  # 24 Hour Chili Brined Chicken Thigh
            {"name": "Chicken Thigh", "quantity": 1, "unit": "lb"},
            {"name": "Chili Brine", "quantity": 0.5, "unit": "cup"}
        ],
        100: [  # Comeback Sauce - Updated 2025
            {"name": "Mayonnaise", "quantity": 1, "unit": "cup"},
            {"name": "Ketchup", "quantity": 0.25, "unit": "cup"}
        ],
        # ... etc
    }
```

## Task 2: Recipe Editing Interface

### 2.1 Backend Routes
**File**: `app.py` (later refactored to `routes/recipes.py`)

```python
@app.route('/recipes/<int:recipe_id>/edit', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    """Edit recipe details and ingredients"""
    if request.method == 'GET':
        # Load recipe and ingredients
        # Return edit form
    else:
        # Validate form data
        # Update recipe
        # Handle ingredients (add/update/delete)
        # Recalculate costs
        # Log activity
```

### 2.2 Frontend Templates
**Files to Create**:
- `templates/edit_recipe_full.html`
- `templates/partials/ingredient_row.html`
- `static/js/recipe-editor.js`

**Key Features**:
```html
<!-- Real-time cost calculation -->
<div class="cost-calculator">
    <span>Total Cost: $<span id="total-cost">0.00</span></span>
    <span>Food Cost %: <span id="food-cost-pct">0%</span></span>
</div>

<!-- Dynamic ingredient management -->
<button onclick="addIngredientRow()">Add Ingredient</button>
```

### 2.3 JavaScript Implementation
```javascript
// recipe-editor.js
class RecipeEditor {
    constructor() {
        this.ingredients = [];
        this.bindEvents();
    }
    
    addIngredient() {
        // Clone template row
        // Add to DOM
        // Initialize autocomplete
    }
    
    calculateCosts() {
        // Sum ingredient costs
        // Calculate percentages
        // Update UI in real-time
    }
    
    saveRecipe() {
        // Validate all fields
        // Submit via AJAX
        // Handle response
    }
}
```

### 2.4 Database Operations
```python
def update_recipe_with_ingredients(recipe_id, recipe_data, ingredients_data):
    """Transactional update of recipe and ingredients"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            # Update recipe
            cursor.execute("""
                UPDATE recipes 
                SET name=?, description=?, selling_price=?, 
                    recipe_yield=?, yield_unit=?, category=?
                WHERE id=?
            """, (...))
            
            # Delete removed ingredients
            # Update existing ingredients
            # Insert new ingredients
            
            # Recalculate costs
            calculate_recipe_cost(recipe_id)
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
```

## Task 3: Security Update

### 3.1 Production SECRET_KEY
**File**: `.env` (create if not exists)
```bash
SECRET_KEY=your-generated-secret-key-here
```

**Update app.py**:
```python
from dotenv import load_dotenv
load_dotenv()

app.secret_key = os.environ.get('SECRET_KEY')
if not app.secret_key:
    raise ValueError("No SECRET_KEY set for Flask application")
```

## Testing Plan

### Unit Tests
```python
# test_recipe_editing.py
def test_update_recipe():
    # Test recipe update
    # Test ingredient additions
    # Test ingredient deletions
    # Test cost recalculation

def test_validation():
    # Test required fields
    # Test numeric validation
    # Test unit conversions
```

### Integration Tests
1. Create recipe with multiple ingredients
2. Edit all fields and save
3. Add/remove ingredients dynamically
4. Verify cost calculations
5. Test with all three themes

### Manual Testing Checklist
- [ ] Form loads with current data
- [ ] All fields are editable
- [ ] Ingredients can be added/removed
- [ ] Autocomplete works for inventory items
- [ ] Real-time calculation updates
- [ ] Form validation prevents bad data
- [ ] Success/error messages display
- [ ] Mobile responsive design
- [ ] No JavaScript errors

## Rollback Plan
1. Database backup before deployment
2. Feature flag for new editing interface
3. Keep old view-only pages active
4. Git tags for quick reversion
5. Monitor error logs closely

## Success Criteria
- [ ] All recipes have <100% food cost
- [ ] Missing ingredients added successfully
- [ ] Recipe editing works without errors
- [ ] Real-time calculations are accurate
- [ ] Mobile interface is usable
- [ ] No security vulnerabilities
- [ ] Page loads in <2 seconds

---
*Sprint 1 Start Date: TBD*  
*Estimated Completion: 3-4 days*