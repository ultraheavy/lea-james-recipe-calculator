# AI_PROMPTING_GUIDE.md
## How to Work with Claude Code on Restaurant Management System

**Purpose**: Prevent destructive changes, maintain focus, ensure proper version control  
**Audience**: Developers working with AI assistance  
**Status**: MANDATORY READING

---

## 🎯 **PROMPTING STRATEGY: CONSTRAINT-FIRST APPROACH**

### **ALWAYS Start Prompts With Constraints**

#### **Template for ALL Requests:**
```
CONSTRAINTS:
- DO NOT modify database schema or column names
- DO NOT change XtraChef import functionality  
- DO NOT alter cost calculation logic
- DO NOT break existing recipe-ingredient relationships
- BACKUP database before any changes
- Use git commits before and after changes

TASK: [Your specific request]

SCOPE: [Exactly what should change]

FILES TO MODIFY: [Specific files only]

FILES TO NEVER TOUCH: [Protected files]
```

#### **Example Good Prompt:**
```
CONSTRAINTS:
- DO NOT modify inventory table schema
- DO NOT change existing recipe cost calculations
- ONLY modify CSS files for styling
- BACKUP before changes: cp restaurant_calculator.db backup_$(date +%Y%m%d).db
- Git commit: git add . && git commit -m "Add mobile menu styling"

TASK: Improve mobile menu appearance

SCOPE: Update CSS only to make mobile hamburger menu more visually appealing

FILES TO MODIFY: 
- static/css/responsive-navigation.css
- static/css/mobile-buttons.css

FILES TO NEVER TOUCH:
- app.py (route handlers)
- templates/*_modern.html (structure)
- Any database-related files
```

#### **Example Bad Prompt (NEVER DO THIS):**
```
❌ "Make the inventory system better"
❌ "Fix the database relationships"
❌ "Improve the cost calculations"
❌ "Optimize the menu system"
```

---

## 🔒 **TASK-SPECIFIC PROMPTING PATTERNS**

### **1. UI/Visual Changes (SAFE)**
```
CONSTRAINTS:
- ONLY modify CSS and static assets
- DO NOT change HTML structure in templates
- DO NOT modify JavaScript functionality
- Test on mobile devices after changes
- Maintain existing responsive breakpoints

TASK: [Specific visual change]
SCOPE: [Exact styling modification]
FILES: static/css/[specific-file.css]
```

### **2. New Feature Addition (CAREFUL)**
```
CONSTRAINTS:
- DO NOT modify existing database tables
- DO NOT change existing route handlers
- ADD new functionality only, don't modify existing
- CREATE new templates, don't modify existing ones
- MAINTAIN all existing relationships

TASK: [New feature description]
SCOPE: [Additive functionality only]
NEW FILES: [List new files to create]
EXISTING FILES: [Files that must remain unchanged]
```

### **3. Bug Fixes (VERY CAREFUL)**
```
CONSTRAINTS:
- IDENTIFY root cause before making changes
- DO NOT modify working code to fix unrelated issues
- MINIMAL changes only to address specific bug
- PRESERVE all existing functionality
- TEST extensively after fix

BUG: [Specific error description]
EXPECTED: [What should happen]
ACTUAL: [What is happening]
SCOPE: [Minimal fix only]
```

### **4. Database-Related Tasks (EXTREME CAUTION)**
```
CONSTRAINTS:
- NEVER DROP or ALTER existing tables
- NEVER RENAME existing columns
- NEVER CHANGE existing relationships
- BACKUP database BEFORE any changes
- ONLY ADD new tables/columns if absolutely necessary
- VERIFY data integrity after changes

TASK: [Database modification]
BACKUP COMMAND: cp restaurant_calculator.db backup_$(date +%Y%m%d_%H%M%S).db
SCOPE: [Minimal database change]
ROLLBACK PLAN: [How to undo changes]
```

---

## 🚫 **FORBIDDEN PROMPTING PATTERNS**

### **NEVER Use These Phrases:**
- ❌ "Optimize the database"
- ❌ "Improve the relationships"  
- ❌ "Fix the naming conventions"
- ❌ "Standardize the columns"
- ❌ "Refactor the code"
- ❌ "Update the schema"
- ❌ "Modernize the structure"

### **NEVER Give Open-Ended Requests:**
- ❌ "Make the system better"
- ❌ "Clean up the code"
- ❌ "Improve performance"
- ❌ "Add more features"
- ❌ "Fix any issues you see"

### **NEVER Allow Scope Creep:**
- ❌ "While you're at it, also..."
- ❌ "This would be a good time to..."
- ❌ "You should also fix..."
- ❌ "Since we're changing this..."

---

## 📋 **PRE-TASK CHECKLIST**

### **Before EVERY AI Request:**
- [ ] **Clear Objective**: Exactly what needs to change?
- [ ] **Scope Definition**: What should NOT change?
- [ ] **File List**: Which files are involved?
- [ ] **Backup Plan**: How to undo if needed?
- [ ] **Testing Plan**: How to verify changes work?
- [ ] **Git Status**: Is repository clean?

### **During AI Interaction:**
- [ ] **Monitor Scope**: Is AI staying within bounds?
- [ ] **Check Files**: Are only allowed files being modified?
- [ ] **Verify Logic**: Do changes make sense?
- [ ] **Question Changes**: Why is AI making each change?
- [ ] **Stop Early**: Halt if scope expands unexpectedly

### **After AI Changes:**
- [ ] **Test Immediately**: Verify functionality works
- [ ] **Check Database**: Ensure data integrity
- [ ] **Review Code**: Understand all changes made
- [ ] **Git Commit**: Commit changes with clear message
- [ ] **Document**: Update relevant documentation

---

## 🔄 **VERSION CONTROL INTEGRATION**

### **Mandatory Git Workflow:**
```bash
# BEFORE starting AI work
git status                           # Ensure clean state
git add . && git commit -m "Backup before AI changes: [description]"

# DURING AI work (frequent commits)
git add -A
git commit -m "AI Progress: [specific change made]"

# AFTER AI work  
git add -A
git commit -m "Complete: [task description] - verified working"
git tag -a v2.1.[increment] -m "Release: [description]"
```

### **Branch Strategy for AI Work:**
```bash
# Create feature branch for AI work
git checkout -b ai/[task-description]

# Work with AI on branch
[AI makes changes]

# Test thoroughly
[Verify everything works]

# Merge back to main only if successful
git checkout main
git merge ai/[task-description]
git branch -d ai/[task-description]
```

---

## 🧪 **TESTING PROTOCOLS**

### **Immediate Testing After AI Changes:**
```bash
# 1. Database integrity check
python3 -c "
import sqlite3
conn = sqlite3.connect('restaurant_calculator.db')
print('Tables:', [r[0] for r in conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()])
print('Inventory count:', conn.execute('SELECT COUNT(*) FROM inventory').fetchone()[0])
print('Recipe count:', conn.execute('SELECT COUNT(*) FROM recipes').fetchone()[0])
"

# 2. Application starts
python3 app.py &
sleep 3
curl -f http://localhost:8888/health || echo "FAILED: App not responding"
pkill -f "python3 app.py"

# 3. Key functionality test
python3 -c "
# Test XtraChef import
# Test recipe cost calculation  
# Test menu calculations
print('All tests passed')
"
```

### **Manual Testing Checklist:**
- [ ] **Dashboard loads**: All stats display correctly
- [ ] **Inventory page**: Items display with correct data
- [ ] **Recipe page**: Recipes show with ingredients
- [ ] **Menu page**: Menu items show with costs
- [ ] **Mobile view**: Interface works on tablet
- [ ] **Navigation**: All menu items work
- [ ] **Forms**: Add/edit functionality works

---

## 📞 **ESCALATION PROCEDURES**

### **When to Stop AI Work Immediately:**
1. **AI suggests schema changes** without explicit permission
2. **AI wants to rename columns** for "consistency"
3. **AI proposes to "optimize" working code**
4. **AI starts modifying multiple unrelated files**
5. **AI cannot explain why a change is necessary**

### **Error Recovery Process:**
```bash
# IMMEDIATE ACTION if something breaks
git reset --hard HEAD~1                    # Undo last commit
cp backup_*.db restaurant_calculator.db    # Restore database
python3 app.py                             # Test if fixed

# If still broken
git log --oneline -10                      # Find last working commit
git reset --hard [working-commit-hash]     # Reset to working state

# Report issue with:
# - What prompt was used
# - What changes were made
# - What broke
# - Current git status
```

---

## 🎪 **PSYCHOLOGY OF AI INTERACTION**

### **Keep Claude Focused:**
- **One Task**: Single, specific objective per conversation
- **Clear Boundaries**: Explicit list of what NOT to touch
- **Frequent Verification**: Check progress regularly
- **Narrow Scope**: Smaller changes are safer
- **Question Everything**: Ask Claude to explain each change

### **Prevent AI Overreach:**
- **No Optimization Requests**: Don't ask AI to "improve" working code
- **Specific File Lists**: Tell AI exactly which files to modify
- **Explicit Permissions**: Only allow what you specifically request
- **Regular Checkpoints**: Review changes before continuing
- **Stop Early**: Better to do multiple small sessions

### **Maintain Control:**
- **You Decide**: AI suggests, you approve
- **Understand Changes**: Don't accept code you don't understand
- **Test Everything**: Verify each change works
- **Document Decisions**: Record why changes were made
- **Version Everything**: Git commits are your safety net

---

## 🏆 **SUCCESS PATTERNS**

### **Effective AI Collaboration:**
1. **Clear Requirements**: Specific, bounded requests
2. **Incremental Changes**: Small steps with testing
3. **Constant Verification**: Check each modification
4. **Good Documentation**: Update docs as you go
5. **Version Control**: Commit early and often

### **Example Successful Session:**
```
1. "Add a simple search box to inventory page header"
   - Claude adds search input to template
   - Test: search box appears, doesn't break layout
   - Commit: "Add inventory search input"

2. "Make search box filter inventory table on keyup"
   - Claude adds JavaScript filter function
   - Test: typing filters table correctly
   - Commit: "Add inventory search functionality"

3. "Style search box to match existing buttons"
   - Claude updates CSS for consistency
   - Test: search box looks good on mobile/desktop
   - Commit: "Style inventory search box"

Result: Working search feature with clear change history
```

---

**REMEMBER: AI is a powerful tool, but YOU are the architect. Maintain control, verify everything, and never let AI modify systems you don't fully understand.**