# Unit Tests - Individual Function Validation

This directory contains unit tests for individual functions and utilities in the Lea James Hot Chicken system.

## Test Files:

- `test_cost_utils.py` - Cost calculation utility functions
- `test_data_validation.py` - Data validation and cleaning functions  
- `test_uom_conversions.py` - Unit of measure conversion functions
- `test_menu_calculations.py` - Menu pricing and margin calculations

## Running Unit Tests:

```bash
# Run all unit tests
python -m pytest tests/unit/ -v

# Run specific test file
python -m pytest tests/unit/test_cost_utils.py -v

# Run with coverage
python -m pytest tests/unit/ --cov=app.cost_utils --cov-report=term-missing
```

## Coverage Goals:

- Individual function testing: 95%+
- Edge case validation: 90%+
- Error handling: 85%+
