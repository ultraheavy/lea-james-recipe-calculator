#!/usr/bin/env python3
"""Test the PDF staging table data."""

import sqlite3

conn = sqlite3.connect('recipe_cost_app.db')
cursor = conn.cursor()

# Sample some data
cursor.execute("""
    SELECT recipe_name, ingredient_name, quantity, unit, cost, needs_review
    FROM stg_pdf_recipes
    LIMIT 10
""")

print("Sample data from staging table:")
print("-" * 80)
for row in cursor.fetchall():
    qty = row[2] or '-'
    unit = row[3] or '-'
    cost = row[4] or '0'
    print(f"{row[0]:30} | {row[1]:25} | {qty:5} {unit:5} | ${cost:6} | Review: {row[5]}")

# Get summary
cursor.execute("SELECT COUNT(*) FROM stg_pdf_recipes WHERE needs_review = 1")
needs_review = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM stg_pdf_recipes WHERE cost IS NULL OR cost = '' OR cost = '0' OR cost = '0.00'")
missing_costs = cursor.fetchone()[0]

print("\nSummary:")
print(f"Rows needing review: {needs_review}")
print(f"Missing/zero costs: {missing_costs}")

conn.close()