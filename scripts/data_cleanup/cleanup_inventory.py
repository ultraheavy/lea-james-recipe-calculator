#!/usr/bin/env python3
"""
Clean up inventory based on business rules:
1. Remove items last purchased in 2023 or 2024 (outdated)
2. Keep only current/active items (2025 purchases)
3. Remove non-food items (office supplies, rent, etc.)
"""

import sqlite3
import re
from datetime import datetime

DATABASE = 'restaurant_calculator.db'

def analyze_current_inventory():
    """Analyze current inventory by purchase date"""
    print("🔍 Analyzing current inventory...")
    
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        
        # Check dates in last_purchased_date
        items = conn.execute('''
            SELECT item_description, last_purchased_date, vendor_name, current_price
            FROM inventory 
            WHERE last_purchased_date IS NOT NULL AND last_purchased_date != ''
            ORDER BY last_purchased_date DESC
        ''').fetchall()
        
        print(f"Total items with purchase dates: {len(items)}")
        
        # Categorize by year
        year_counts = {'2025': 0, '2024': 0, '2023': 0, 'other': 0}
        items_2025 = []
        items_2024 = []
        items_2023 = []
        
        for item in items:
            date_str = item['last_purchased_date']
            
            if '2025' in date_str:
                year_counts['2025'] += 1
                items_2025.append(item)
            elif '2024' in date_str:
                year_counts['2024'] += 1
                items_2024.append(item)
            elif '2023' in date_str:
                year_counts['2023'] += 1
                items_2023.append(item)
            else:
                year_counts['other'] += 1
        
        print("\n📊 INVENTORY BY YEAR:")
        for year, count in year_counts.items():
            print(f"  {year}: {count} items")
        
        print(f"\n📋 SAMPLE 2025 ITEMS (keeping these):")
        for item in items_2025[:5]:
            print(f"  - {item['item_description']}: ${item['current_price']:.2f} ({item['vendor_name']})")
        
        print(f"\n🗑️ SAMPLE 2023-2024 ITEMS (removing these):")
        old_items = items_2023 + items_2024
        for item in old_items[:5]:
            print(f"  - {item['item_description']}: ${item['current_price']:.2f} ({item['vendor_name']})")
        
        return year_counts

def remove_old_items():
    """Remove items last purchased in 2023 or 2024"""
    print("\n🗑️ Removing outdated inventory items...")
    
    with sqlite3.connect(DATABASE) as conn:
        # Remove items from 2023 and 2024
        removed_2023 = conn.execute('''
            DELETE FROM inventory 
            WHERE last_purchased_date LIKE '%2023%'
        ''').rowcount
        
        removed_2024 = conn.execute('''
            DELETE FROM inventory 
            WHERE last_purchased_date LIKE '%2024%'
        ''').rowcount
        
        conn.commit()
        
        print(f"✅ Removed {removed_2023} items from 2023")
        print(f"✅ Removed {removed_2024} items from 2024")
        print(f"📦 Total removed: {removed_2023 + removed_2024} items")

def remove_non_food_items():
    """Remove obvious non-food items"""
    print("\n🧹 Removing non-food items...")
    
    non_food_keywords = [
        'RENT', 'PAYABLE', 'PURCHASE SUMMARY', 'OTHER', 'FAM',
        'GLOVE', 'NITRILE', 'BAG', 'DEGREASER', 'BLEACH', 
        'TO GO', 'THANK YOU', 'SMILE', 'PLASTIC', 'PAPER',
        'BOWL', 'CUP', 'LID', 'NAPKIN', 'TISSUE', 'CONTAINER'
    ]
    
    total_removed = 0
    
    with sqlite3.connect(DATABASE) as conn:
        for keyword in non_food_keywords:
            removed = conn.execute(f'''
                DELETE FROM inventory 
                WHERE UPPER(item_description) LIKE '%{keyword}%'
                OR UPPER(product_categories) LIKE '%NON CON%'
                OR UPPER(product_categories) LIKE '%NON COM%'
                OR UPPER(product_categories) LIKE '%CHEMICALS%'
            ''').rowcount
            
            if removed > 0:
                print(f"  - Removed {removed} items containing '{keyword}'")
                total_removed += removed
        
        conn.commit()
    
    print(f"✅ Total non-food items removed: {total_removed}")

def final_inventory_summary():
    """Show final cleaned inventory summary"""
    print("\n📊 FINAL CLEANED INVENTORY SUMMARY:")
    
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        
        # Total count
        total = conn.execute('SELECT COUNT(*) as count FROM inventory').fetchone()['count']
        
        # By vendor
        vendors = conn.execute('''
            SELECT vendor_name, COUNT(*) as count
            FROM inventory 
            GROUP BY vendor_name 
            ORDER BY count DESC
        ''').fetchall()
        
        # By category
        categories = conn.execute('''
            SELECT 
                CASE 
                    WHEN UPPER(product_categories) LIKE '%PROTEIN%' THEN 'Protein'
                    WHEN UPPER(product_categories) LIKE '%PRODUCE%' THEN 'Produce'  
                    WHEN UPPER(product_categories) LIKE '%DAIRY%' THEN 'Dairy'
                    WHEN UPPER(product_categories) LIKE '%DRY GOODS%' THEN 'Dry Goods'
                    WHEN UPPER(product_categories) LIKE '%FROZEN%' THEN 'Frozen'
                    ELSE 'Other'
                END as category,
                COUNT(*) as count
            FROM inventory 
            WHERE product_categories IS NOT NULL AND product_categories != ''
            GROUP BY category
            ORDER BY count DESC
        ''').fetchall()
        
        print(f"📦 Total Active Items: {total}")
        
        print(f"\n🏢 TOP VENDORS:")
        for vendor in vendors[:5]:
            print(f"  - {vendor['vendor_name']}: {vendor['count']} items")
        
        print(f"\n🥘 FOOD CATEGORIES:")
        for cat in categories:
            print(f"  - {cat['category']}: {cat['count']} items")

def cleanup_inventory():
    """Run complete inventory cleanup"""
    print("🚀 Starting inventory cleanup process...")
    print("=" * 60)
    
    # Analyze current state
    year_counts = analyze_current_inventory()
    
    # Remove old items
    remove_old_items()
    
    # Remove non-food items
    remove_non_food_items()
    
    # Show final summary
    final_inventory_summary()
    
    print("=" * 60)
    print("✅ Inventory cleanup completed!")
    print("💡 Inventory now contains only current, food-related items from 2025")

if __name__ == '__main__':
    cleanup_inventory()
