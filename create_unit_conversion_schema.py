#!/usr/bin/env python3
"""
Create unit conversion database schema for accurate recipe costing
Based on Gemini's analysis - canonical units approach
"""

import sqlite3
from backup_database import backup_database

DATABASE = 'restaurant_calculator.db'

def create_unit_conversion_schema():
    """Create tables and fields for unit conversion system"""
    
    print("📦 Creating database backup...")
    backup_database()
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # 1. Create units table
        print("\n🔨 Creating units table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS units (
                unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                symbol TEXT NOT NULL UNIQUE,
                dimension TEXT NOT NULL CHECK(dimension IN ('WEIGHT', 'VOLUME', 'COUNT')),
                to_canonical_factor DECIMAL(20,10) NOT NULL,
                is_precise BOOLEAN DEFAULT 1,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 2. Add density and yield fields to inventory
        print("\n🔧 Adding conversion fields to inventory...")
        
        # Check which columns already exist
        columns = cursor.execute("PRAGMA table_info(inventory)").fetchall()
        existing_columns = [col[1] for col in columns]
        
        # Add density field if not exists
        if 'density_g_per_ml' not in existing_columns:
            cursor.execute('''
                ALTER TABLE inventory ADD COLUMN density_g_per_ml DECIMAL(10,4)
            ''')
            print("  ✓ Added density_g_per_ml")
        
        # Add count to weight field if not exists
        if 'count_to_weight_g' not in existing_columns:
            cursor.execute('''
                ALTER TABLE inventory ADD COLUMN count_to_weight_g DECIMAL(10,2)
            ''')
            print("  ✓ Added count_to_weight_g")
        
        # yield_percent already exists, but let's ensure it has proper default
        cursor.execute('''
            UPDATE inventory SET yield_percent = 100 WHERE yield_percent IS NULL
        ''')
        
        # 3. Create ingredient unit equivalents table for custom conversions
        print("\n🔨 Creating ingredient unit equivalents table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingredient_unit_equivalents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER NOT NULL,
                custom_unit_name TEXT NOT NULL,
                canonical_quantity DECIMAL(10,4) NOT NULL,
                canonical_unit_symbol TEXT NOT NULL,
                notes TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (inventory_id) REFERENCES inventory(id),
                UNIQUE(inventory_id, custom_unit_name)
            )
        ''')
        
        # 4. Create conversion audit log table
        print("\n🔨 Creating conversion audit log...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unit_conversion_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_ingredient_id INTEGER,
                from_quantity DECIMAL(10,4),
                from_unit TEXT,
                to_quantity DECIMAL(10,4),
                to_unit TEXT,
                conversion_method TEXT,
                conversion_status TEXT,
                error_message TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recipe_ingredient_id) REFERENCES recipe_ingredients(id)
            )
        ''')
        
        # 5. Add conversion status fields to recipe_ingredients
        print("\n🔧 Adding conversion tracking to recipe ingredients...")
        
        columns = cursor.execute("PRAGMA table_info(recipe_ingredients)").fetchall()
        existing_columns = [col[1] for col in columns]
        
        if 'canonical_quantity' not in existing_columns:
            cursor.execute('''
                ALTER TABLE recipe_ingredients ADD COLUMN canonical_quantity DECIMAL(10,4)
            ''')
            print("  ✓ Added canonical_quantity")
        
        if 'canonical_unit' not in existing_columns:
            cursor.execute('''
                ALTER TABLE recipe_ingredients ADD COLUMN canonical_unit TEXT
            ''')
            print("  ✓ Added canonical_unit")
        
        if 'conversion_status' not in existing_columns:
            cursor.execute('''
                ALTER TABLE recipe_ingredients ADD COLUMN conversion_status TEXT
            ''')
            print("  ✓ Added conversion_status")
        
        # 6. Create indexes for performance
        print("\n📇 Creating indexes...")
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_units_symbol ON units(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_units_dimension ON units(dimension)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ingredient_equivalents ON ingredient_unit_equivalents(inventory_id)')
        
        conn.commit()
        print("\n✅ Unit conversion schema created successfully!")
        
        # Show summary
        units_count = cursor.execute('SELECT COUNT(*) FROM units').fetchone()[0]
        print(f"\n📊 Schema Summary:")
        print(f"  - Units table created (currently {units_count} units)")
        print(f"  - Inventory enhanced with density and count-to-weight fields")
        print(f"  - Custom unit equivalents table ready")
        print(f"  - Conversion audit log ready")
        print(f"  - Recipe ingredients enhanced with conversion tracking")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def show_schema_info():
    """Display information about the new schema"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    print("\n📋 New Schema Information:")
    
    # Units table
    print("\n1. UNITS table structure:")
    print("   - unit_id: Primary key")
    print("   - name: Full unit name (e.g., 'Pound')")
    print("   - symbol: Unit abbreviation (e.g., 'lb')")
    print("   - dimension: WEIGHT, VOLUME, or COUNT")
    print("   - to_canonical_factor: Multiplier to convert to base unit")
    print("   - is_precise: False for units like 'pinch', 'dash'")
    
    print("\n2. Canonical units:")
    print("   - WEIGHT: grams (g)")
    print("   - VOLUME: milliliters (ml)")
    print("   - COUNT: each (ea)")
    
    print("\n3. Inventory enhancements:")
    print("   - density_g_per_ml: For volume to weight conversions")
    print("   - count_to_weight_g: Weight of one 'each' item")
    print("   - yield_percent: Already exists, used for waste/trim")
    
    print("\n4. Custom conversions:")
    print("   - ingredient_unit_equivalents: For 'slice', 'bunch', etc.")
    print("   - Specific to each inventory item")
    
    conn.close()

if __name__ == "__main__":
    create_unit_conversion_schema()
    show_schema_info()