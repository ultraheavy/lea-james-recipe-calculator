#!/usr/bin/env python3
"""
Fix ingredient mapping between recipes and inventory
"""

import sqlite3
import re

DATABASE = 'restaurant_calculator.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def normalize_ingredient_name(name):
    """Normalize ingredient name for better matching"""
    # Remove category prefixes like "Dry Goods, " 
    name = re.sub(r'^(Dry Goods|Protein|Dairy|Produce|Non Con|Sauces),?\s*', '', name, flags=re.I)
    
    # Normalize common variations
    replacements = {
        'DIll': 'Dill',
        'Chicken  Breading': 'Chicken Breading',
        'Oil, Canola, Clear, Frying': 'Canola Oil',
        'Shortening, Pork Lard': 'Lard',
        'Salt, Kosher': 'Kosher Salt',
        'Pickle, Dill, Slices': 'Dill Pickle Slices',
        'Bread, Texas Toast': 'Texas Toast',
        'Chicken, Tenders': 'Chicken Tenders',
        'Chicken, Wing': 'Chicken Wings',
    }
    
    for old, new in replacements.items():
        if old.lower() in name.lower():
            name = name.replace(old, new)
    
    return name.strip()

def create_ingredient_mappings():
    """Create mappings between recipe ingredients and inventory"""
    print("🔗 Creating ingredient mappings...")
    
    mappings_created = 0
    
    with get_db() as conn:
        # Get all unmatched ingredients
        unmatched = conn.execute('''
            SELECT DISTINCT ingredient_name 
            FROM recipe_ingredients 
            WHERE ingredient_id IS NULL
            ORDER BY ingredient_name
        ''').fetchall()
        
        print(f"Found {len(unmatched)} unique unmatched ingredients")
        
        for row in unmatched:
            ingredient_name = row['ingredient_name']
            normalized_name = normalize_ingredient_name(ingredient_name)
            
            # Try multiple matching strategies
            matches = []
            
            # 1. Exact match on normalized name
            exact = conn.execute('''
                SELECT id, item_description, current_price 
                FROM inventory 
                WHERE LOWER(item_description) = LOWER(?)
            ''', (normalized_name,)).fetchone()
            
            if exact:
                matches.append(exact)
            else:
                # 2. Contains match
                contains = conn.execute('''
                    SELECT id, item_description, current_price 
                    FROM inventory 
                    WHERE LOWER(item_description) LIKE LOWER(?)
                    ORDER BY LENGTH(item_description)
                    LIMIT 5
                ''', (f'%{normalized_name}%',)).fetchall()
                
                matches.extend(contains)
                
                # 3. Try key words
                key_words = normalized_name.split()
                if len(key_words) > 1:
                    for word in key_words:
                        if len(word) > 3:  # Skip short words
                            word_matches = conn.execute('''
                                SELECT id, item_description, current_price 
                                FROM inventory 
                                WHERE LOWER(item_description) LIKE LOWER(?)
                                LIMIT 3
                            ''', (f'%{word}%',)).fetchall()
                            matches.extend(word_matches)
            
            # Find best match
            best_match = None
            if matches:
                # Prefer matches with similar word count
                target_words = set(normalized_name.lower().split())
                best_score = 0
                
                for match in matches:
                    match_words = set(match['item_description'].lower().split())
                    common_words = target_words.intersection(match_words)
                    score = len(common_words) / max(len(target_words), 1)
                    
                    if score > best_score:
                        best_score = score
                        best_match = match
            
            if best_match and best_score > 0.3:  # At least 30% word match
                # Update all recipe ingredients with this name
                conn.execute('''
                    UPDATE recipe_ingredients 
                    SET ingredient_id = ?, 
                        cost = quantity * ?
                    WHERE ingredient_name = ? AND ingredient_id IS NULL
                ''', (best_match['id'], best_match['current_price'] or 0, ingredient_name))
                
                mappings_created += 1
                print(f"  ✓ Mapped: {ingredient_name} → {best_match['item_description']}")
            else:
                print(f"  ✗ No match: {ingredient_name}")
        
        # Recalculate recipe costs
        conn.execute('''
            UPDATE recipes 
            SET food_cost = (
                SELECT COALESCE(SUM(cost), 0) 
                FROM recipe_ingredients 
                WHERE recipe_id = recipes.id
            ),
            updated_date = CURRENT_TIMESTAMP
        ''')
        
        conn.commit()
    
    return mappings_created

def show_mapping_summary():
    """Show summary of ingredient mappings"""
    print("\n📊 Mapping Summary:")
    
    with get_db() as conn:
        total = conn.execute('SELECT COUNT(*) FROM recipe_ingredients').fetchone()[0]
        matched = conn.execute('SELECT COUNT(*) FROM recipe_ingredients WHERE ingredient_id IS NOT NULL').fetchone()[0]
        unmatched = total - matched
        
        print(f"\nTotal recipe ingredients: {total}")
        print(f"Matched to inventory: {matched} ({matched/total*100:.1f}%)")
        print(f"Unmatched: {unmatched} ({unmatched/total*100:.1f}%)")
        
        if unmatched > 0:
            print("\n❌ Top unmatched ingredients:")
            unmatched_list = conn.execute('''
                SELECT ingredient_name, COUNT(*) as count 
                FROM recipe_ingredients 
                WHERE ingredient_id IS NULL 
                GROUP BY ingredient_name 
                ORDER BY count DESC 
                LIMIT 10
            ''').fetchall()
            
            for item in unmatched_list:
                print(f"  - {item['ingredient_name']} ({item['count']} uses)")

def main():
    print("🔧 Fixing ingredient mappings...")
    
    # Create mappings
    mappings = create_ingredient_mappings()
    print(f"\n✅ Created {mappings} new mappings")
    
    # Show summary
    show_mapping_summary()

if __name__ == "__main__":
    main()