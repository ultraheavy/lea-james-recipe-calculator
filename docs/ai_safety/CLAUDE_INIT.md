# CLAUDE_INIT.md - Quick Initialization for AI Sessions

## 🚀 REQUIRED: START EVERY CLAUDE SESSION WITH THIS

**COPY AND PASTE THIS PROMPT:**

---

**INITIALIZATION - READ DOCUMENTATION FIRST:**

Please use desktop-commander to read these critical files before any work:

```
/docs/ai_safety/CLAUDE.md
docs/technical/DATA_MODEL.md
docs/ai_safety/AI_PROMPTING_GUIDE.md
```

**After reading, confirm you understand:**
- ❌ PROTECTED: Database schema, XtraChef import, cost calculations  
- ✅ ALLOWED: CSS styling, new features (with approval)
- 🔒 MANDATORY: Backup database before changes
- 📋 REQUIRED: Use constraint-first prompting templates

**ACKNOWLEDGMENT:** "I have read the project documentation and understand the constraints. I will follow the constraint-first prompting approach."

---

**THEN** provide your actual task request using this template:

```
CONSTRAINTS:
- DO NOT modify database schema or column names
- DO NOT change XtraChef import functionality  
- DO NOT alter cost calculation logic
- BACKUP before changes: cp restaurant_calculator.db backup_$(date +%Y%m%d).db

TASK: [Your specific request]
SCOPE: [Exactly what should change]
FILES TO MODIFY: [Specific files only]
FILES TO NEVER TOUCH: [Protected files]
```

---

## 🎯 QUICK CHECKLIST:

### Before AI Session:
- [ ] Run `./init_claude.sh` to check project status
- [ ] Have Claude read CLAUDE.md, DATA_MODEL.md, AI_PROMPTING_GUIDE.md
- [ ] Wait for Claude's acknowledgment
- [ ] Use constraint-first prompting template

### During AI Session:
- [ ] Monitor that AI stays within scope
- [ ] Verify only approved files are modified
- [ ] Question any unexpected changes
- [ ] Stop if AI suggests schema changes

### After AI Session:
- [ ] Test all functionality works
- [ ] Verify XtraChef import still functions
- [ ] Check database integrity
- [ ] Git commit with clear message

---

**REMEMBER: The documentation protects your production restaurant system. Always initialize Claude properly!**