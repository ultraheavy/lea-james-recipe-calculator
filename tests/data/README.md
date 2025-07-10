# Data Tests - Data Integrity and Import Validation

This directory contains tests for data integrity, import processes, and database validation.

## Test Files:

- `test_schema_validation.py` - Database schema and constraint validation
- `test_csv_imports.py` - CSV import process validation
- `test_data_relationships.py` - Foreign key and relationship integrity
- `test_data_consistency.py` - Data consistency and business rule validation

## Running Data Tests:

```bash
# Run all data tests
python -m pytest tests/data/ -v

# Run schema validation only
python -m pytest tests/data/test_schema_validation.py -v

# Run with database markers
python -m pytest -m database -v
```

## Protected Areas:

⚠️ **CRITICAL**: These tests protect XtraChef integration per DATA_MODEL.md
- XtraChef field mapping must remain intact
- Core database relationships are immutable
- Cost calculation integrity must be maintained

## Coverage Goals:

- Schema validation: 100%
- Import processes: 95%+
- Data relationships: 100%
- Business rules: 90%+
