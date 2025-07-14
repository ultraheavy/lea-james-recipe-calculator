#!/usr/bin/env python3
"""Test exclusion rules in detail"""

import csv
from datetime import datetime, timedelta

# Check the CSV for items that should be excluded
csv_path = "reference/LJ_DATA_Ref/Lea_Janes_Items_list_latest.csv"

stats = {
    'total': 0,
    'no_product': 0,
    'old_purchase': 0,
    'both': 0,
    'should_load': 0
}

nine_months_ago = datetime.now() - timedelta(days=270)
print(f"Nine months ago cutoff: {nine_months_ago.strftime('%Y-%m-%d')}")
print(f"Today: {datetime.now().strftime('%Y-%m-%d')}\n")

with open(csv_path, 'r') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        stats['total'] += 1
        
        product = row.get('Product(s)', '').strip()
        last_date_str = row.get('Last Purchased Date', '').strip()
        
        no_product = not product
        old_purchase = False
        
        if last_date_str:
            for fmt in ['%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d']:
                try:
                    last_date = datetime.strptime(last_date_str, fmt)
                    if last_date < nine_months_ago:
                        old_purchase = True
                    break
                except ValueError:
                    continue
        
        if no_product and old_purchase:
            stats['both'] += 1
        elif no_product:
            stats['no_product'] += 1
        elif old_purchase:
            stats['old_purchase'] += 1
        else:
            stats['should_load'] += 1
            
        # Show some examples
        if stats['total'] <= 10:
            print(f"Row {stats['total']}:")
            print(f"  Product: '{product}' {'[EMPTY]' if no_product else ''}")
            print(f"  Last Date: {last_date_str} {'[OLD]' if old_purchase else ''}")

print(f"\nSummary:")
print(f"Total rows: {stats['total']}")
print(f"No product name: {stats['no_product']}")
print(f"Old purchase (>9 months): {stats['old_purchase']}")
print(f"Both issues: {stats['both']}")
print(f"Should load: {stats['should_load']}")
print(f"\nExpected to exclude: {stats['no_product'] + stats['old_purchase'] + stats['both']}")