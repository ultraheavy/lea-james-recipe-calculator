#!/usr/bin/env python3
"""
Add vendor_products table to support multiple vendors per inventory item
"""

import sqlite3
from backup_database import backup_database

def add_vendor_products_table():
    """Create vendor_products table and migrate data"""
    
    # First, backup the database
    print("📦 Creating database backup...")
    backup_database()
    
    conn = sqlite3.connect('restaurant_calculator.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Create vendor_products table
        print("\n🔨 Creating vendor_products table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendor_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER NOT NULL,
                vendor_id INTEGER NOT NULL,
                vendor_item_code TEXT,
                vendor_price REAL,
                last_purchased_date TEXT,
                last_purchased_price REAL,
                pack_size TEXT,
                unit_measure TEXT,
                is_primary BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (inventory_id) REFERENCES inventory(id),
                FOREIGN KEY (vendor_id) REFERENCES vendors(id),
                UNIQUE(inventory_id, vendor_id, vendor_item_code)
            )
        ''')
        
        # Add indexes for performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_vendor_products_inventory 
            ON vendor_products(inventory_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_vendor_products_vendor 
            ON vendor_products(vendor_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_vendor_products_active 
            ON vendor_products(is_active)
        ''')
        
        print("✅ vendor_products table created successfully")
        
        # Migrate existing vendor data from inventory table
        print("\n📋 Migrating existing vendor data...")
        
        # Get all inventory items with vendor info
        items = cursor.execute('''
            SELECT 
                i.id,
                i.item_code,
                i.item_description,
                i.vendor_name,
                i.current_price,
                i.last_purchased_price,
                i.last_purchased_date,
                i.unit_measure,
                i.pack_size
            FROM inventory i
            WHERE i.vendor_name IS NOT NULL
        ''').fetchall()
        
        migrated_count = 0
        for item in items:
            # Find or create vendor
            vendor = cursor.execute('''
                SELECT id FROM vendors WHERE vendor_name = ?
            ''', (item['vendor_name'],)).fetchone()
            
            if not vendor:
                # Create vendor if doesn't exist
                cursor.execute('''
                    INSERT INTO vendors (vendor_name, created_date)
                    VALUES (?, CURRENT_TIMESTAMP)
                ''', (item['vendor_name'],))
                vendor_id = cursor.lastrowid
            else:
                vendor_id = vendor['id']
            
            # Insert into vendor_products
            cursor.execute('''
                INSERT OR IGNORE INTO vendor_products (
                    inventory_id, vendor_id, vendor_item_code,
                    vendor_price, last_purchased_date, last_purchased_price,
                    pack_size, unit_measure, is_primary, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['id'], vendor_id, item['item_code'],
                item['current_price'], item['last_purchased_date'], 
                item['last_purchased_price'], item['pack_size'], 
                item['unit_measure'], True, True
            ))
            
            if cursor.rowcount > 0:
                migrated_count += 1
        
        print(f"✅ Migrated {migrated_count} vendor relationships")
        
        # Add trigger to update inventory's last purchase info
        print("\n🔧 Creating triggers...")
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS update_inventory_last_purchase
            AFTER UPDATE OF last_purchased_date, last_purchased_price 
            ON vendor_products
            WHEN NEW.is_primary = 1
            BEGIN
                UPDATE inventory
                SET 
                    last_purchased_date = NEW.last_purchased_date,
                    last_purchased_price = NEW.last_purchased_price,
                    current_price = NEW.vendor_price,
                    updated_date = CURRENT_TIMESTAMP
                WHERE id = NEW.inventory_id;
            END;
        ''')
        
        print("✅ Triggers created successfully")
        
        conn.commit()
        
        # Show summary
        total_products = cursor.execute('SELECT COUNT(*) FROM vendor_products').fetchone()[0]
        active_products = cursor.execute('SELECT COUNT(*) FROM vendor_products WHERE is_active = 1').fetchone()[0]
        
        print(f"\n📊 Vendor Products Summary:")
        print(f"  - Total vendor products: {total_products}")
        print(f"  - Active vendor products: {active_products}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    add_vendor_products_table()