# PROJECT_DOCUMENTATION_INDEX.md
## Restaurant Management System - Complete Documentation Framework

**Purpose**: Master index for all project documentation and AI guardrails  
**Status**: MASTER REFERENCE - Keep Updated  
**Last Updated**: January 2025

---

## 📚 **DOCUMENTATION HIERARCHY**

### **🚨 TIER 1: CRITICAL - READ FIRST**
These documents prevent catastrophic system damage:

#### **1. CLAUDE.md** - AI Development Guidelines
- **Purpose**: Golden rules for AI interaction
- **When to Use**: BEFORE every AI request
- **Key Section**: Protected Components, Change Protocol
- **Status**: MANDATORY READING

#### **2. DATA_MODEL.md** - Sacred Database Structure  
- **Purpose**: Immutable database relationships
- **When to Use**: Any database-related work
- **Key Section**: XtraChef mapping, relationship flows
- **Status**: NEVER MODIFY WITHOUT PERMISSION

#### **3. AI_PROMPTING_GUIDE.md** - How to Work with Claude
- **Purpose**: Specific prompting strategies
- **When to Use**: Every AI interaction session
- **Key Section**: Constraint-first prompting, forbidden patterns
- **Status**: OPERATIONAL MANUAL

---

### **🟡 TIER 2: STRATEGIC - BUSINESS CONTEXT**
These documents define what the system should do:

#### **4. PRD.md** - Product Requirements
- **Purpose**: What the system is supposed to accomplish
- **When to Use**: Planning new features or changes
- **Key Section**: Protected features, forbidden modifications
- **Status**: BUSINESS AUTHORITY

#### **5. BRD.md** - Business Requirements
- **Purpose**: Why the system exists and business context
- **When to Use**: Understanding business impact of changes
- **Key Section**: User roles, business processes, ROI metrics
- **Status**: BUSINESS CONTEXT

#### **6. FRD.md** - Functional Requirements
- **Purpose**: Technical specifications and implementation details
- **When to Use**: Technical planning and architecture decisions
- **Key Section**: System architecture, API endpoints, testing
- **Status**: TECHNICAL AUTHORITY

---

## 🎯 **DOCUMENT USAGE MATRIX**

| Task Type | Primary Docs | Secondary Docs | Key Checkpoints |
|-----------|-------------|----------------|-----------------|
| **AI Coding Session** | CLAUDE.md<br>AI_PROMPTING_GUIDE.md | DATA_MODEL.md<br>FRD.md | Protected components<br>Constraint prompting |
| **New Feature Planning** | PRD.md<br>BRD.md | FRD.md<br>CLAUDE.md | Business alignment<br>Technical feasibility |
| **Database Work** | DATA_MODEL.md<br>CLAUDE.md | FRD.md<br>BRD.md | Schema protection<br>Relationship integrity |
| **UI/UX Changes** | CLAUDE.md<br>AI_PROMPTING_GUIDE.md | PRD.md<br>BRD.md | Visual changes only<br>User requirements |
| **Bug Fixes** | CLAUDE.md<br>AI_PROMPTING_GUIDE.md | DATA_MODEL.md<br>FRD.md | Minimal changes<br>Root cause analysis |

---

## 🔄 **WORKFLOW INTEGRATION**

### **Before Starting ANY Work:**
1. **Identify Task Type** (UI, Feature, Database, Bug)
2. **Read Relevant Tier 1 Docs** (Always CLAUDE.md)
3. **Check Business Context** (PRD/BRD for feature changes)
4. **Review Technical Specs** (FRD for implementation)
5. **Plan Constraints** (Use AI_PROMPTING_GUIDE.md)

### **During Work:**
1. **Reference CLAUDE.md** for boundaries
2. **Check DATA_MODEL.md** for database concerns
3. **Verify against PRD.md** for scope creep
4. **Use AI_PROMPTING_GUIDE.md** for AI interactions

### **After Work:**
1. **Test against FRD.md** requirements
2. **Verify BRD.md** business objectives met
3. **Update documentation** if needed
4. **Document lessons learned**

---

## 🏗️ **SYSTEM GUARDRAILS SUMMARY**

### **IMMUTABLE COMPONENTS (NEVER CHANGE)**
From DATA_MODEL.md:
- XtraChef CSV import mapping
- Core database relationships
- Cost calculation algorithms
- inventory/recipes/recipe_ingredients schema

### **PROTECTED FEATURES (APPROVAL REQUIRED)**
From PRD.md:
- XtraChef integration functionality
- Recipe cost calculation engine  
- Menu management system
- Mobile-responsive interface

### **BUSINESS CRITICAL PROCESSES (UNDERSTAND BEFORE CHANGING)**
From BRD.md:
- Daily cost monitoring workflow
- Weekly menu engineering process
- Monthly business review requirements
- XtraChef sync process

### **TECHNICAL BOUNDARIES (RESPECT ARCHITECTURE)**
From FRD.md:
- Flask application structure
- SQLite database with WAL mode
- Mobile-first CSS framework
- Git version control requirements

---

## 🚨 **EMERGENCY PROCEDURES**

### **If System is Broken:**
1. **STOP**: Don't make more changes
2. **BACKUP**: Copy database immediately
3. **ROLLBACK**: Use git to revert changes
4. **ASSESS**: Check against DATA_MODEL.md
5. **RESTORE**: Follow CLAUDE.md emergency procedures

### **If AI Goes Off-Track:**
1. **HALT**: Stop the AI session immediately
2. **REVIEW**: Check what changes were made
3. **ASSESS**: Verify against CLAUDE.md guardrails
4. **REVERT**: Undo unauthorized changes
5. **RESTART**: Begin new session with better constraints

### **If Requirements Are Unclear:**
1. **REFERENCE**: Check PRD.md and BRD.md
2. **CLARIFY**: Define specific business need
3. **SCOPE**: Use FRD.md to understand technical impact
4. **PLAN**: Create constrained approach using AI_PROMPTING_GUIDE.md

---

## 📋 **MAINTENANCE SCHEDULE**

### **Monthly Reviews:**
- **Update PROJECT_STATUS.md** with completed work
- **Review CLAUDE.md** for new lessons learned
- **Check DATA_MODEL.md** for any schema drift
- **Verify PRD.md** alignment with business needs

### **Quarterly Reviews:**
- **Assess BRD.md** against actual business outcomes
- **Update FRD.md** with architecture changes
- **Review AI_PROMPTING_GUIDE.md** effectiveness
- **Plan documentation improvements

### **Annual Reviews:**
- **Complete documentation audit**
- **Business requirements realignment**
- **Technical architecture review**
- **Process improvement assessment**

---

## 🎯 **QUICK REFERENCE CARDS**

### **Pre-AI Session Checklist:**
- [ ] Read CLAUDE.md golden rules
- [ ] Identify which components are protected (DATA_MODEL.md)
- [ ] Define constraints using AI_PROMPTING_GUIDE.md
- [ ] Backup database and git commit
- [ ] Write specific, bounded prompt

### **During AI Session Monitoring:**
- [ ] Is AI staying within defined scope?
- [ ] Are only approved files being modified?
- [ ] Is AI respecting database schema (DATA_MODEL.md)?
- [ ] Are changes aligned with business needs (PRD.md)?
- [ ] Is AI explaining each change clearly?

### **Post-AI Session Verification:**
- [ ] Test all functionality works
- [ ] Verify XtraChef import still functions
- [ ] Check recipe cost calculations are accurate
- [ ] Confirm mobile interface works
- [ ] Git commit with clear message
- [ ] Update relevant documentation

---

## 🏆 **SUCCESS METRICS**

### **Documentation Effectiveness:**
- **Zero Unauthorized Schema Changes**: Protect data integrity
- **Reduced Scope Creep**: AI stays within defined boundaries
- **Faster Development**: Clear requirements reduce iteration
- **Fewer Rollbacks**: Better planning prevents errors
- **Improved Quality**: Systematic approach improves outcomes

### **Project Health Indicators:**
- **Database Integrity**: No corruption or relationship breaks
- **Feature Stability**: Working features remain working
- **Business Alignment**: Changes support operational needs
- **Technical Debt**: Minimal accumulation through planned changes
- **Team Understanding**: Clear documentation enables knowledge transfer

---

## 📞 **DOCUMENT OWNERS & CONTACTS**

| Document | Primary Owner | Update Authority | Review Frequency |
|----------|---------------|------------------|------------------|
| CLAUDE.md | Tech Lead | Team Lead | After each AI issue |
| DATA_MODEL.md | Database Admin | CTO + Business | Never (unless emergency) |
| PRD.md | Product Manager | Business Owner | Quarterly |
| BRD.md | Business Owner | Executive Team | Quarterly |
| FRD.md | Tech Lead | Senior Developer | Monthly |
| AI_PROMPTING_GUIDE.md | Development Team | Tech Lead | Monthly |

---

**CRITICAL REMINDER: These documents are your safety net. They prevent AI from making destructive changes that could break a production restaurant management system. When in doubt, refer to the documentation rather than experimenting.**