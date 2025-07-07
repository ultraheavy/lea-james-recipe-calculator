# CLAUDE.md - AI Development Guidelines for Restaurant Management System

## 🚨 CRITICAL: READ BEFORE ANY CODE CHANGES

### **GOLDEN RULES - NEVER VIOLATE**

1. **NO DESTRUCTIVE CHANGES WITHOUT EXPLICIT PERMISSION**
   - Do NOT rename database columns
   - Do NOT change existing table relationships
   - Do NOT modify working CSV import processes
   - Do NOT alter established data flows

2. **MANDATORY BACKUP BEFORE ANY CHANGES**
   ```bash
   # ALWAYS run before making changes:
   cp restaurant_calculator.db restaurant_calculator_backup_$(date +%Y%m%d_%H%M%S).db
   git add . && git commit -m "Backup before [CHANGE_DESCRIPTION]"
   ```

3. **RESPECT ESTABLISHED DATA MODEL**
   - XtraChef CSV import structure is SACRED
   - Product naming conventions are FIXED
   - Vendor relationships are ESTABLISHED

---

## 📊 **ESTABLISHED DATA MODEL - DO NOT CHANGE**

### **XtraChef Integration (PROTECTED)**
```sql
-- NEVER CHANGE THESE COLUMN NAMES OR RELATIONSHIPS
inventory Table:
- item_code (XtraChef: Invoice Item Code)
- item_description (XtraChef: Product Name) 
- vendor_name (XtraChef: Vendor Name)
- current_price (XtraChef: Latest Price)
- last_purchased_date (XtraChef: Invoice Date)
```

### **Vendor Relationship Rules (FIXED)**
- `vendor_name` = Company that sells the product
- `item_description` = Product name (what you buy)
- `vendor_item_code` = Vendor's SKU/product code
- **DO NOT USE vendor_code as item_description**
- **DO NOT DUPLICATE vendor information across columns**

### **Recipe Integration (ESTABLISHED)**
```sql
recipe_ingredients Table:
- ingredient_id → inventory.id (FIXED RELATIONSHIP)
- recipe_id → recipes.id (FIXED RELATIONSHIP)
- quantity, unit, cost (CALCULATION FIELDS)
```

---

## 🔒 **PROTECTED COMPONENTS - DO NOT MODIFY**

### **1. CSV Import System**
- `import_toast_data.py` - **PRODUCTION CRITICAL**
- `import_xtrachef_data.py` - **PRODUCTION CRITICAL**
- Column mapping logic - **ESTABLISHED**

### **2. Cost Calculation Engine**
- Recipe cost calculations - **WORKING & TESTED**
- Vendor pricing relationships - **ESTABLISHED**
- Menu profit calculations - **PRODUCTION READY**

### **3. Database Schema Core**
- Primary key relationships - **NEVER CHANGE**
- Foreign key constraints - **ESTABLISHED**
- Index structure - **OPTIMIZED**

---

## 📋 **CHANGE REQUEST PROTOCOL**

### **Before Making ANY Changes:**

1. **Identify Change Type:**
   - 🟢 **ADDITIVE**: Adding new features without touching existing code
   - 🟡 **ENHANCEMENT**: Improving existing features (requires approval)
   - 🔴 **STRUCTURAL**: Changing database/relationships (FORBIDDEN without explicit permission)

2. **Required Documentation:**
   ```markdown
   ## Change Request
   - **Type**: [ADDITIVE/ENHANCEMENT/STRUCTURAL]
   - **Files Affected**: [list all files]
   - **Database Changes**: [list any schema changes]
   - **Risk Assessment**: [what could break]
   - **Rollback Plan**: [how to undo]
   ```

3. **Mandatory Testing Checklist:**
   - [ ] XtraChef CSV import still works
   - [ ] Recipe cost calculations unchanged
   - [ ] Menu pricing calculations intact
   - [ ] All existing data relationships preserved

---

## 🎯 **CURRENT PROJECT FOCUS**

### **APPROVED WORK ONLY:**
- UI/UX improvements (visual only)
- New feature additions (non-destructive)
- Performance optimizations (no schema changes)
- Documentation and testing

### **FORBIDDEN WORK:**
- Database schema "improvements"
- Column renaming for "consistency"
- Changing working import processes
- "Optimizing" established relationships

---

## 📁 **FILE MODIFICATION PERMISSIONS**

### **✅ FREELY MODIFIABLE:**
- `static/css/*` - Styling changes
- `templates/*` - UI improvements
- New files for new features
- Documentation files

### **⚠️ MODIFY WITH CAUTION:**
- `app.py` - Only add routes, don't change existing
- Route handlers - Add new, don't modify working ones

### **🚨 NEVER MODIFY WITHOUT PERMISSION:**
- `import_*.py` - Data import scripts
- Database schema in `app.py`
- Working calculation functions
- Established relationships

---

## 🔄 **VERSION CONTROL REQUIREMENTS**

### **Every Change Must:**
1. Create feature branch: `git checkout -b feature/[description]`
2. Commit frequently with descriptive messages
3. Test thoroughly before merging
4. Tag stable versions: `git tag v1.x.x`

### **Commit Message Format:**
```
[TYPE]: Brief description

- Specific change 1
- Specific change 2

Files: list changed files
Tests: what was tested
Risk: assessment of impact
```

---

## 🧪 **TESTING REQUIREMENTS**

### **Before ANY Code Change:**
1. **Data Integrity Test**:
   ```bash
   python3 -c "
   import sqlite3
   conn = sqlite3.connect('restaurant_calculator.db')
   print('Inventory count:', conn.execute('SELECT COUNT(*) FROM inventory').fetchone()[0])
   print('Recipe count:', conn.execute('SELECT COUNT(*) FROM recipes').fetchone()[0])
   print('Ingredient links:', conn.execute('SELECT COUNT(*) FROM recipe_ingredients').fetchone()[0])
   "
   ```

2. **Import Test**:
   ```bash
   # Test with sample XtraChef data
   python3 import_xtrachef_data.py --test-mode
   ```

3. **Calculation Test**:
   ```bash
   # Verify recipe costs haven't changed
   python3 test_cost_calculations.py
   ```

---

## 📈 **PROJECT STATUS TRACKING**

### **COMPLETED & PROTECTED:**
- ✅ XtraChef CSV integration
- ✅ Recipe cost calculations  
- ✅ Vendor management system
- ✅ Menu pricing analysis
- ✅ Mobile-responsive UI
- ✅ Multi-theme system

### **IN PROGRESS:**
- 🔄 [Current sprint items only]

### **BACKLOG:**
- 📋 [Future enhancements only]

---

## 🚨 **EMERGENCY ROLLBACK**

### **If Something Breaks:**
1. **Immediate Action:**
   ```bash
   git reset --hard HEAD~1  # Undo last commit
   cp restaurant_calculator_backup_*.db restaurant_calculator.db  # Restore DB
   ```

2. **Verify System:**
   ```bash
   python3 app.py  # Test server starts
   # Test key functionality in browser
   ```

3. **Document Issue:**
   - What changed
   - What broke
   - How it was fixed
   - Prevention for future

---

## 📞 **ESCALATION PROCESS**

### **When to Stop and Ask:**
- Any database schema questions
- Column naming conflicts
- XtraChef integration issues
- Performance degradation
- Broken calculations

### **Required Information for Help:**
- Exact error message
- Steps to reproduce
- Files modified
- Expected vs actual behavior
- Current git status

---

## 🎪 **DEVELOPMENT PHILOSOPHY**

**"First, do no harm"** - Medical Hippocratic Oath applied to code

1. **Preserve Working Systems**
2. **Add Value, Don't Replace Value**
3. **Document Everything**
4. **Test Relentlessly**
5. **Version Control Religiously**

---

**Remember: This is a PRODUCTION restaurant management system. Breaking it impacts real business operations.**