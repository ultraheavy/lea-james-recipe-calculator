# 🧪 Lea Jane's Hot Chicken - Automated Testing Framework

## 📋 **Testing Strategy Overview**

This comprehensive testing suite ensures the reliability and accuracy of the Lea Jane's Hot Chicken recipe cost management system. All tests follow the project's **CLAUDE.md** guidelines and protect critical XtraChef integration points.

## 🏗️ **Directory Structure**

```
tests/
├── unit/                    # Individual function testing
├── integration/             # System component integration  
├── business/               # Business logic validation
├── data/                   # Data integrity and import tests
├── automation/             # Hooks and continuous monitoring
├── run_tests.py            # Main test runner
└── pytest.ini             # Test configuration
```

## 🎯 **Critical Test Areas**

### **1. Recipe Costing Engine** (business/)
- **File:** `test_recipe_costing.py`
- **Purpose:** Validates core cost calculations that drive business profitability
- **Coverage:** Recipe cost flows, ingredient cost propagation, yield calculations

### **2. XtraChef Integration** (integration/)
- **File:** `test_xtrachef_integration.py`  
- **Purpose:** Protects sacred XtraChef data mapping (per DATA_MODEL.md)
- **Coverage:** CSV import, field mapping, data integrity

### **3. Database Integrity** (data/)
- **Purpose:** Ensures schema compliance and relationship integrity
- **Coverage:** Foreign keys, constraints, data validation

### **4. Unit Functions** (unit/)
- **Purpose:** Individual function validation
- **Coverage:** Utility functions, calculations, data transformations

### **5. Health Monitoring** (automation/)
- **File:** `health_monitor.py`
- **Purpose:** Continuous system health checks
- **Coverage:** Performance benchmarks, automated reporting

## 🚀 **Running Tests**

### **Run All Tests:**
```bash
python tests/run_tests.py
```

### **Run Specific Test Category:**
```bash
# Business logic tests only
python -m pytest tests/business/ -v

# XtraChef integration tests only  
python -m pytest tests/integration/ -v

# Data integrity tests only
python -m pytest tests/data/ -v
```

### **Run with Coverage Report:**
```bash
python -m pytest --cov=app --cov-report=html
```

## 📊 **Success Criteria**

### **Coverage Goals:**
- ✅ **90%+ Coverage** of critical business functions
- ✅ **100% Coverage** of XtraChef integration (PROTECTED)
- ✅ **85%+ Coverage** of database operations
- ✅ **Automated Execution** via hooks

### **Performance Benchmarks:**
- ✅ **Recipe Cost Calculation:** < 100ms per recipe
- ✅ **XtraChef CSV Import:** < 30 seconds for 1000 items
- ✅ **Database Queries:** < 500ms for complex joins
- ✅ **Health Check Cycle:** < 5 minutes complete system scan

## ⚠️ **Protected Components**

### **IMMUTABLE (Per DATA_MODEL.md):**
- XtraChef field mapping
- Core database relationships  
- Cost calculation algorithms
- inventory/recipes/recipe_ingredients schema

### **Tests MUST:**
- Verify XtraChef integration remains intact
- Validate cost calculations are accurate
- Ensure no data corruption during operations
- Confirm performance benchmarks are met

## 🔧 **Test Configuration**

### **Environment Variables:**
```bash
TESTING=true                 # Enables test mode
TEST_DATABASE=test.db        # Separate test database
FORCE_DB_INIT=true          # Force database initialization
```

### **Dependencies:**
- pytest
- pytest-cov (coverage reporting)
- pytest-mock (mocking support)
- sqlite3 (database testing)

## 📈 **Continuous Integration**

Tests run automatically on:
- Code commits (pre-commit hooks)
- Pull requests (GitHub Actions)
- Daily health checks (cron jobs)
- Deployment pipelines (production safety)

## 🆘 **Emergency Procedures**

If tests fail:
1. **STOP** any deployment or changes
2. Review failed test output
3. Check CLAUDE.md for guidance
4. Consult DATA_MODEL.md for schema rules
5. Contact system owner if XtraChef integration affected

---

**Last Updated:** 2025-07-09  
**Framework Version:** 1.0  
**Compliance:** CLAUDE.md + DATA_MODEL.md + PRD.md
