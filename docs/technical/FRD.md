# FRD - Functional Requirements Document
## Restaurant Cost Management System

**Version**: 2.0  
**Date**: January 2025  
**Technical Lead**: Development Team  
**Status**: PRODUCTION SYSTEM - CORE FUNCTIONS LOCKED

---

## 🏗️ **SYSTEM ARCHITECTURE (ESTABLISHED)**

### **Technology Stack (IMMUTABLE)**
- **Backend**: Flask (Python 3.8+)
- **Database**: SQLite with WAL mode
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **CSS Framework**: Custom responsive system
- **Version Control**: Git with automated backups
- **Deployment**: Local/cloud compatible

### **Core Dependencies (LOCKED)**
```python
# requirements.txt - DO NOT MODIFY WITHOUT APPROVAL
Flask==2.3.3
sqlite3 (built-in)
csv (built-in)  
datetime (built-in)
os (built-in)
```

---

## 📊 **DATABASE SCHEMA (PROTECTED)**

### **Core Tables (IMMUTABLE STRUCTURE)**

#### **inventory** - Primary Product Catalog
```sql
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,           -- Internal key
    item_code TEXT UNIQUE,                          -- XtraChef ID (NEVER CHANGE)
    item_description TEXT NOT NULL,                 -- Product name (NEVER CHANGE)
    vendor_name TEXT,                               -- Vendor company (NEVER CHANGE)
    current_price REAL DEFAULT 0,                   -- Current cost
    last_purchased_price REAL,                      -- Previous cost
    last_purchased_date TEXT,                       -- Purchase date
    unit_measure TEXT,                              -- Purchase unit
    purchase_unit TEXT,                             -- Purchase unit
    recipe_cost_unit TEXT,                          -- Recipe unit  
    pack_size TEXT,                                 -- Package size
    yield_percent REAL DEFAULT 100,                 -- Usable percentage
    product_categories TEXT,                        -- Food categories
    vendor_item_code TEXT,                          -- Vendor SKU
    notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
#### **recipes** - Recipe Definitions
```sql
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_name TEXT NOT NULL,                      -- Display name
    recipe_group TEXT,                              -- Category
    recipe_type TEXT DEFAULT 'Recipe',              -- Type
    status TEXT DEFAULT 'Draft',                    -- Status
    food_cost REAL DEFAULT 0,                       -- Calculated cost
    labor_cost REAL DEFAULT 0,                      -- Labor cost
    menu_price REAL DEFAULT 0,                      -- Selling price
    gross_margin REAL,                              -- Profit margin
    prime_cost REAL,                                -- Food + Labor
    shelf_life TEXT,                                -- Shelf life
    shelf_life_uom TEXT,                            -- Units
    prep_recipe_yield REAL,                         -- Recipe yield
    serving_size TEXT,                              -- Portion size
    station TEXT,                                   -- Prep station
    procedure TEXT,                                 -- Instructions
    notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **recipe_ingredients** - Recipe-Inventory Links
```sql
CREATE TABLE recipe_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,                     -- FK to recipes
    ingredient_id INTEGER NOT NULL,                 -- FK to inventory
    quantity REAL NOT NULL,                         -- Amount needed
    unit TEXT,                                      -- Unit of measure
    cost REAL DEFAULT 0,                            -- Calculated cost
    notes TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES inventory (id) ON DELETE CASCADE
);
```

---

## 🔧 **CORE FUNCTIONAL REQUIREMENTS**

### **FR-001: XtraChef Integration (CRITICAL)**
**Status**: PRODUCTION - DO NOT MODIFY

**Requirements**:
- Import CSV exports from XtraChef system
- Map Invoice Item Code → item_code
- Map Product Name → item_description  
- Map Vendor → vendor_name
- Map Price → current_price
- Update existing records, insert new ones
- Maintain data integrity during import

**Technical Implementation**:
```python
# PROTECTED FUNCTION - DO NOT MODIFY
def import_xtrachef_csv(file_path):
    """Import XtraChef CSV data - PRODUCTION CRITICAL"""
    # Implementation locked - changes require approval
```

**Acceptance Criteria**:
- ✅ 99.9% data import accuracy
- ✅ Handle 1000+ inventory items
- ✅ Complete import in <30 seconds
- ✅ Maintain existing relationships
- ✅ Error handling for malformed data

### **FR-002: Cost Calculation Engine (CRITICAL)**
**Status**: PRODUCTION - MODIFICATIONS REQUIRE APPROVAL

**Requirements**:
- Calculate recipe costs from ingredient prices
- Update recipe costs when ingredient prices change
- Calculate food cost percentages
- Calculate profit margins
- Handle unit conversions

**Technical Implementation**:
```python
# PROTECTED FUNCTIONS - MODIFY WITH EXTREME CAUTION
def calculate_recipe_cost(recipe_id):
    """Calculate total recipe cost - BUSINESS CRITICAL"""
    
def update_all_recipe_costs():
    """Recalculate all recipe costs - PERFORMANCE CRITICAL"""
    
def calculate_food_cost_percentage(recipe_id, menu_price):
    """Calculate food cost % - FINANCIAL CRITICAL"""
```

**Acceptance Criteria**:
- ✅ Recipe costs update within 1 second of ingredient price change
- ✅ Calculations accurate to 2 decimal places
- ✅ Handle missing ingredients gracefully
- ✅ Support 20+ ingredients per recipe
- ✅ Performance: <500ms for single recipe calculation
### **FR-003: Recipe Management (ESTABLISHED)**
**Status**: STABLE - ENHANCEMENTS ALLOWED

**Requirements**:
- Create, read, update, delete recipes
- Link ingredients to recipes with quantities
- Support recipe versioning
- Recipe search and filtering
- Bulk operations on recipes

**Technical Implementation**:
```python
# STABLE FUNCTIONS - CAN BE ENHANCED
@app.route('/recipes', methods=['GET'])
def recipes():
    """List all recipes with filtering"""
    
@app.route('/recipes/<int:recipe_id>', methods=['GET'])  
def view_recipe(recipe_id):
    """View recipe details"""
    
@app.route('/recipes/add', methods=['GET', 'POST'])
def add_recipe():
    """Add new recipe"""
```

**Acceptance Criteria**:
- ✅ Support 500+ recipes
- ✅ Recipe search by name/ingredient
- ✅ Mobile-optimized forms
- ✅ Real-time cost updates
- ✅ Recipe duplication functionality

### **FR-004: Menu Management (COMPLETE)**
**Status**: PRODUCTION - VISUAL IMPROVEMENTS ONLY

**Requirements**:
- Manage menu versions (Current, Future, Seasonal)
- Link recipes to menu items
- Calculate menu item profitability
- Compare menu versions
- Export menu data

**Technical Implementation**:
```python
# PRODUCTION FUNCTIONS - VISUAL CHANGES ONLY
@app.route('/menu')
def menu():
    """Menu management with versioning"""
    
@app.route('/menu/compare')
def menu_compare():
    """Compare menu versions"""
```

**Acceptance Criteria**:
- ✅ Support multiple menu versions
- ✅ Menu comparison functionality
- ✅ Profit margin calculations
- ✅ Export to PDF/CSV
- ✅ Mobile menu viewing

### **FR-005: Mobile Interface (COMPLETE)**
**Status**: PRODUCTION - REFINEMENTS ONLY

**Requirements**:
- Responsive design for tablets/phones
- Touch-optimized interface (44px minimum)
- Offline recipe access
- Fast loading on 3G connections
- Kitchen-friendly design

**Technical Implementation**:
```css
/* PRODUCTION CSS - REFINEMENTS ONLY */
/* responsive-navigation.css - 1000+ lines COMPLETE */
/* mobile-buttons.css - Touch optimization COMPLETE */
/* modern-ui.css - Theme system COMPLETE */
```

**Acceptance Criteria**:
- ✅ Works on iOS/Android tablets
- ✅ <3 second load times on 3G
- ✅ Touch targets >44px
- ✅ Offline recipe viewing
- ✅ Kitchen-safe interface

---

## 🔗 **API ENDPOINTS (ESTABLISHED)**

### **Core Routes (PROTECTED)**
```python
# PRODUCTION ROUTES - DO NOT MODIFY
@app.route('/')                           # Dashboard
@app.route('/inventory')                  # Inventory list
@app.route('/recipes')                    # Recipe list  
@app.route('/menu')                       # Menu management
@app.route('/health')                     # System health
```

### **Data Routes (STABLE)**
```python
# CAN BE ENHANCED - NO BREAKING CHANGES
@app.route('/inventory/add', methods=['GET', 'POST'])
@app.route('/inventory/edit/<int:item_id>', methods=['GET', 'POST'])
@app.route('/recipes/add', methods=['GET', 'POST'])
@app.route('/recipes/<int:recipe_id>')
```

### **API Response Format (STANDARDIZED)**
```json
{
  "status": "success|error",
  "data": {},
  "message": "string",
  "timestamp": "ISO-8601",
  "version": "2.0"
}
```
---

## 🎯 **NON-FUNCTIONAL REQUIREMENTS**

### **NFR-001: Performance Requirements**
- **Page Load Time**: <2 seconds on desktop, <3 seconds mobile
- **Database Queries**: <500ms for standard operations
- **Bulk Operations**: Progress indicators for >5 second operations
- **Memory Usage**: <512MB for full application
- **Storage**: Support 10MB+ database with 2+ years data

### **NFR-002: Reliability Requirements**
- **Uptime**: 99.5% availability during business hours (6am-11pm)
- **Data Integrity**: Zero data corruption tolerance
- **Backup**: Automated daily backups with 30-day retention
- **Recovery**: <4 hour recovery time from backup
- **Error Handling**: Graceful degradation for all failures

### **NFR-003: Security Requirements**
- **Data Protection**: All cost data treated as confidential
- **Input Validation**: SQL injection prevention
- **Access Logging**: Audit trail for all data modifications
- **Session Management**: Secure session handling
- **Data Export**: Audit trail for information export

### **NFR-004: Usability Requirements**
- **Learning Curve**: 1-2 hours maximum training for new users
- **Mobile Usability**: One-handed operation on tablets
- **Accessibility**: WCAG 2.1 AA compliance for text/contrast
- **Error Messages**: Clear, actionable error descriptions
- **Help System**: Context-sensitive help for all functions

---

## 🧪 **TESTING REQUIREMENTS**

### **Unit Testing (MANDATORY)**
```python
# Required test coverage
def test_recipe_cost_calculation():
    """Test recipe cost calculation accuracy"""
    
def test_xtrachef_import():
    """Test CSV import functionality"""
    
def test_menu_profit_calculation():
    """Test menu profit margin calculations"""
```

**Coverage Requirements**:
- **Cost Calculations**: 100% test coverage
- **Data Import**: 100% test coverage  
- **CRUD Operations**: 90% test coverage
- **API Endpoints**: 85% test coverage

### **Integration Testing (REQUIRED)**
- **XtraChef Import**: Full CSV import workflow
- **Cost Propagation**: Ingredient price → Recipe cost → Menu profit
- **Mobile Interface**: Touch interaction testing
- **Database Operations**: Concurrent user testing

### **Performance Testing (REQUIRED)**
- **Load Testing**: 10 concurrent users
- **Data Volume**: 1000+ inventory items, 500+ recipes
- **Import Performance**: Large CSV file processing
- **Mobile Performance**: 3G connection simulation

---

## 📋 **DEPLOYMENT REQUIREMENTS**

### **Production Environment**
- **Server**: Linux/Windows compatible
- **Python**: 3.8+ with Flask
- **Database**: SQLite with WAL mode enabled
- **Backup**: Automated daily database backup
- **Monitoring**: Application health monitoring

### **Development Environment**
- **Git**: Version control with feature branches
- **Testing**: Local SQLite for development
- **Documentation**: Updated with all changes
- **Code Review**: All changes require review

---

## 🔄 **CHANGE CONTROL PROCESS**

### **Functional Change Categories**

#### **Category 1: FORBIDDEN (Owner Permission Only)**
- Database schema modifications
- XtraChef import logic changes
- Cost calculation algorithm changes
- Core API endpoint modifications
- Production data transformations

#### **Category 2: RESTRICTED (Technical Lead Approval)**
- New functional features
- Performance optimizations
- Security enhancements
- Integration additions
- Database query optimizations

#### **Category 3: ALLOWED (Standard Process)**
- UI/UX improvements
- New report features
- Documentation updates
- Test coverage improvements
- Bug fixes (non-core functions)

### **Change Implementation Process**
1. **Functional Analysis**: Impact on business operations
2. **Technical Review**: Architecture and performance impact
3. **Testing Plan**: Comprehensive test strategy
4. **Rollback Plan**: How to revert if needed
5. **Documentation**: Update all relevant docs

---

## 🚨 **CRITICAL SYSTEM DEPENDENCIES**

### **External Dependencies (MONITOR CLOSELY)**
- **XtraChef CSV Format**: Changes break import process
- **Toast POS Integration**: Future dependency for sales data
- **Browser Compatibility**: Chrome, Safari, Firefox support
- **Mobile OS**: iOS 12+, Android 8+ compatibility

### **Internal Dependencies (PROTECT CAREFULLY)**
- **Database Relationships**: Foreign key integrity critical
- **Cost Calculation Chain**: Inventory → Recipe → Menu
- **File System**: CSV import/export functionality
- **Session Management**: User state persistence

---

**FUNCTIONAL RULE: Any change that modifies data flow, calculations, or core business logic requires comprehensive testing and business approval before implementation.**