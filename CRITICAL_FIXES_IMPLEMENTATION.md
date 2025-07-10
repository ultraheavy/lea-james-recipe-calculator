# 🚨 CRITICAL ISSUES FIXES - Implementation Plan

**Generated:** 2025-07-09
**Status:** URGENT - Production System Health

## 📊 CURRENT STATUS
✅ **Core System Health: EXCELLENT**
- Recipe costing engine: **WORKING** 
- Profit margins: **78-86% verified**
- XtraChef integration: **INTACT**
- Database: **250 items, 66 recipes, 107 menu items**

❌ **Infrastructure Issues: CRITICAL**
- Test framework failures (pytest configuration)
- Database schema mismatch in tests
- Zero-price menu items
- UOM mapping errors

---

## 🎯 **IMMEDIATE FIXES REQUIRED**

### 1. **TEST FRAMEWORK REPAIR** (Critical)
**Problem:** Test runner using unsupported `--json-report` flags
**Impact:** Cannot run automated testing
**Solution:** Update pytest configuration and install missing plugins

### 2. **DATABASE SCHEMA VALIDATION** (High)
**Problem:** Tests expect different column names than actual schema
**Impact:** False test failures masking real issues
**Solution:** Align test schemas with production database

### 3. **ZERO-PRICE MENU ITEMS** (High)
**Problem:** Some menu items have $0 prices
**Impact:** Revenue calculations will be incorrect
**Solution:** Identify and fix pricing issues

### 4. **UOM MAPPING ERRORS** (Medium)
**Problem:** Unit conversion failures
**Impact:** Recipe cost accuracy
**Solution:** Fix UOM alias configuration

---

## 🔧 **IMPLEMENTATION SEQUENCE**

### Phase 1: Test Framework Fix (30 minutes)
1. Update requirements.txt with missing packages
2. Fix pytest configuration
3. Update test runner to use correct flags
4. Validate test execution

### Phase 2: Database Schema Alignment (20 minutes)
1. Verify actual database schema
2. Update test schemas to match production
3. Fix column name mismatches
4. Validate schema consistency

### Phase 3: Data Quality Fixes (45 minutes)
1. Identify zero-price menu items
2. Fix pricing issues
3. Validate UOM mappings
4. Test price propagation

### Phase 4: ETL Module Validation (15 minutes)
1. Verify ETL import paths
2. Test pack size parsing
3. Validate UOM alias functionality
4. Confirm data import capability

---

## 🎖️ **SUCCESS CRITERIA**
- [ ] All pytest tests run without configuration errors
- [ ] Database schema tests pass
- [ ] No menu items with $0 prices
- [ ] UOM conversions working correctly
- [ ] ETL module fully functional
- [ ] Price change propagation working

---

## 🚀 **EXPECTED OUTCOME**
- **Test Suite**: 95%+ pass rate
- **Data Integrity**: 100% validated
- **Business Logic**: Fully operational
- **Profit Margins**: Maintained at 78-86%
- **System Reliability**: Production-ready

---

**Next Steps:** Implement fixes in sequence, validate each phase before proceeding.
