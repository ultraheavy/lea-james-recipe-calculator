#!/usr/bin/env python3
"""
conftest.py - Shared pytest fixtures and configuration
"""

import pytest
import sqlite3
import os
import sys
from decimal import Decimal

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE = 'restaurant_calculator.db'

@pytest.fixture(scope="session")
def database_connection():
    """Shared database connection for all tests"""
    if not os.path.exists(DATABASE):
        pytest.skip(f"Database {DATABASE} not found")
    
    conn = sqlite3.connect(DATABASE)
    yield conn
    conn.close()

@pytest.fixture(scope="function")
def db_cursor(database_connection):
    """Database cursor for individual tests"""
    cursor = database_connection.cursor()
    yield cursor
    # Note: Not closing cursor as connection handles cleanup

@pytest.fixture(scope="session")
def sample_recipe_data(database_connection):
    """Get sample recipe data for testing"""
    cursor = database_connection.cursor()
    
    # Get a recipe with ingredients for testing
    cursor.execute("""
        SELECT r.id, r.recipe_name, r.food_cost
        FROM recipes r
        JOIN recipe_ingredients ri ON r.id = ri.recipe_id
        WHERE r.food_cost > 0
        GROUP BY r.id
        HAVING COUNT(ri.id) > 0
        LIMIT 1
    """)
    
    recipe = cursor.fetchone()
    if not recipe:
        pytest.skip("No suitable recipe found for testing")
    
    return {
        'id': recipe[0],
        'name': recipe[1],
        'cost': recipe[2]
    }

@pytest.fixture(scope="session")
def sample_inventory_data(database_connection):
    """Get sample inventory data for testing"""
    cursor = database_connection.cursor()
    
    cursor.execute("""
        SELECT id, item_code, item_description, current_price
        FROM inventory
        WHERE current_price > 0
        LIMIT 5
    """)
    
    items = cursor.fetchall()
    if not items:
        pytest.skip("No inventory items found for testing")
    
    return [
        {
            'id': item[0],
            'code': item[1],
            'description': item[2],
            'price': item[3]
        }
        for item in items
    ]

@pytest.fixture(scope="session")
def sample_menu_data(database_connection):
    """Get sample menu data for testing"""
    cursor = database_connection.cursor()
    
    cursor.execute("""
        SELECT id, item_name, menu_price, food_cost
        FROM menu_items
        WHERE menu_price > 0 AND food_cost > 0
        LIMIT 5
    """)
    
    items = cursor.fetchall()
    if not items:
        pytest.skip("No menu items found for testing")
    
    return [
        {
            'id': item[0],
            'name': item[1],
            'price': item[2],
            'cost': item[3]
        }
        for item in items
    ]

@pytest.fixture
def cost_calculator():
    """Cost calculator instance for testing"""
    from cost_utils import CostCalculator
    calc = CostCalculator()
    yield calc
    calc.close()

# Custom markers for test categorization
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual functions"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for system components"
    )
    config.addinivalue_line(
        "markers", "business: Business logic tests (CRITICAL for profitability)"
    )
    config.addinivalue_line(
        "markers", "data: Data integrity and validation tests"
    )
    config.addinivalue_line(
        "markers", "xtrachef: XtraChef integration tests (PROTECTED)"
    )
    config.addinivalue_line(
        "markers", "performance: Performance benchmark tests"
    )
    config.addinivalue_line(
        "markers", "automation: Automated monitoring and health checks"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer than 1 second"
    )
    config.addinivalue_line(
        "markers", "database: Tests that require database access"
    )

# Test collection modifiers
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Automatically mark database tests
        if "database" in str(item.fspath) or "db_cursor" in str(item.fixturenames):
            item.add_marker(pytest.mark.database)
        
        # Mark business tests
        if "business" in str(item.fspath):
            item.add_marker(pytest.mark.business)
        
        # Mark unit tests
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Mark integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Mark data tests
        if "data" in str(item.fspath):
            item.add_marker(pytest.mark.data)

# Helper functions for tests
def assert_valid_price(price, item_name="item"):
    """Assert that a price is valid"""
    assert price is not None, f"Price for {item_name} cannot be None"
    assert isinstance(price, (int, float, Decimal)), f"Price for {item_name} must be numeric"
    assert price >= 0, f"Price for {item_name} cannot be negative: {price}"

def assert_valid_cost(cost, item_name="item"):
    """Assert that a cost is valid"""
    assert cost is not None, f"Cost for {item_name} cannot be None"
    assert isinstance(cost, (int, float, Decimal)), f"Cost for {item_name} must be numeric"
    assert cost >= 0, f"Cost for {item_name} cannot be negative: {cost}"

def assert_valid_margin(margin, item_name="item", min_margin=50, max_margin=95):
    """Assert that a profit margin is within business acceptable ranges"""
    assert margin is not None, f"Margin for {item_name} cannot be None"
    assert isinstance(margin, (int, float)), f"Margin for {item_name} must be numeric"
    assert min_margin <= margin <= max_margin, \
        f"Margin for {item_name} outside acceptable range: {margin}% (should be {min_margin}-{max_margin}%)"
