"""Test fuzzy matching accuracy"""

import pytest
import sqlite3
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from ingredient_matcher import IngredientMatcher

@pytest.fixture
def test_db(tmp_path):
    """Create test database with sample data"""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE inventory (
            id INTEGER PRIMARY KEY,
            item_code TEXT,
            item_description TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE recipes (
            id INTEGER PRIMARY KEY,
            recipe_name TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE recipe_ingredients (
            id INTEGER PRIMARY KEY,
            recipe_id INTEGER,
            ingredient_name TEXT,
            ingredient_id INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE vendor_products (
            id INTEGER PRIMARY KEY,
            inventory_id INTEGER,
            vendor_sku TEXT,
            upc_code TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE fuzzy_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_term TEXT NOT NULL,
            inventory_id INTEGER,
            match_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(search_term, inventory_id)
        )
    """)
    
    # Insert test data
    inventory_items = [
        (1, 'CHK001', 'Dry Goods, Chicken Base, Paste'),
        (2, 'MAY001', 'Dry Goods, Mayonnaise, Heavy'),
        (3, 'SAM001', 'Dry Goods, Sauce, Chile Sambal'),
        (4, 'KET001', 'Dry Goods, Ketchup Packets'),
        (5, 'SHA001', 'Produce, Shallots, Peeled, Fresh'),
    ]
    
    cursor.executemany(
        "INSERT INTO inventory VALUES (?, ?, ?)", 
        inventory_items
    )
    
    cursor.execute("INSERT INTO recipes VALUES (1, 'Test Recipe')")
    
    recipe_ingredients = [
        (1, 1, 'Fried Chicken Tender', None),
        (2, 1, 'Dry Goods, MAYONNAISE HVY PLST SHLF', None),
        (3, 1, 'Dry Goods, Sambal Chill Sauce (wt)', None),
        (4, 1, 'Dry Goods, Sauce, Tomato Ketchup, Jug', None),
        (5, 1, 'Pickled Shallot', None),
    ]
    
    cursor.executemany(
        "INSERT INTO recipe_ingredients VALUES (?, ?, ?, ?)",
        recipe_ingredients
    )
    
    conn.commit()
    conn.close()
    
    return str(db_path)

def test_fuzzy_matching_accuracy(test_db):
    """Test that fuzzy matching achieves >90% accuracy"""
    matcher = IngredientMatcher(test_db)
    
    # Expected matches
    expected_matches = {
        'Fried Chicken Tender': 1,  # Chicken Base
        'Dry Goods, MAYONNAISE HVY PLST SHLF': 2,  # Mayonnaise
        'Dry Goods, Sambal Chill Sauce (wt)': 3,  # Chile Sambal
        'Dry Goods, Sauce, Tomato Ketchup, Jug': 4,  # Ketchup Packets
        'Pickled Shallot': 5,  # Shallots
    }
    
    inventory_items = matcher.get_inventory_items()
    correct_matches = 0
    total_tests = len(expected_matches)
    
    for ingredient, expected_id in expected_matches.items():
        matches = matcher.find_matches(
            ingredient, 
            inventory_items,
            threshold=80.0,
            limit=1
        )
        
        if matches and matches[0][0] == expected_id:
            correct_matches += 1
            print(f"✓ {ingredient} → {matches[0][1]} ({matches[0][2]:.1f}%)")
        else:
            print(f"✗ {ingredient} → {matches[0][1] if matches else 'NO MATCH'}")
    
    accuracy = correct_matches / total_tests
    assert accuracy >= 0.9, f"Accuracy {accuracy:.1%} is below 90%"

def test_cache_functionality(test_db):
    """Test that caching works correctly"""
    matcher = IngredientMatcher(test_db)
    inventory_items = matcher.get_inventory_items()
    
    # First call - should hit database
    matches1 = matcher.find_matches(
        "Mayonnaise Heavy",
        inventory_items,
        threshold=80.0,
        use_cache=True
    )
    
    # Second call - should hit cache
    matches2 = matcher.find_matches(
        "Mayonnaise Heavy", 
        inventory_items,
        threshold=80.0,
        use_cache=True
    )
    
    assert matches1 == matches2
    
    # Verify cache was populated
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cache_count = cursor.execute(
        "SELECT COUNT(*) FROM fuzzy_cache"
    ).fetchone()[0]
    conn.close()
    
    assert cache_count > 0

def test_threshold_filtering(test_db):
    """Test that threshold properly filters results"""
    matcher = IngredientMatcher(test_db)
    inventory_items = matcher.get_inventory_items()
    
    # High threshold - should get fewer matches
    high_threshold_matches = matcher.find_matches(
        "Chicken",
        inventory_items,
        threshold=90.0,
        limit=10
    )
    
    # Low threshold - should get more matches
    low_threshold_matches = matcher.find_matches(
        "Chicken",
        inventory_items,
        threshold=50.0,
        limit=10
    )
    
    assert len(low_threshold_matches) >= len(high_threshold_matches)