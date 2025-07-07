import sqlite3

# Check if we have actual price data
conn = sqlite3.connect('restaurant_calculator.db')
cursor = conn.cursor()

# Check for non-zero prices
cursor.execute('SELECT COUNT(*) FROM inventory WHERE current_price IS NOT NULL AND current_price > 0')
price_count = cursor.fetchone()[0]
print(f'Items with current_price > 0: {price_count}')

cursor.execute('SELECT COUNT(*) FROM inventory WHERE last_purchased_price IS NOT NULL AND last_purchased_price > 0')
last_price_count = cursor.fetchone()[0]
print(f'Items with last_purchased_price > 0: {last_price_count}')

# Check for recipe costs
cursor.execute('SELECT COUNT(*) FROM recipes WHERE food_cost IS NOT NULL AND food_cost > 0')
recipe_cost_count = cursor.fetchone()[0]
print(f'Recipes with food_cost > 0: {recipe_cost_count}')

# Show some actual data
cursor.execute('SELECT item_description, current_price, last_purchased_price FROM inventory WHERE last_purchased_price > 0 LIMIT 5')
items = cursor.fetchall()
print('\nItems with last_purchased_price:')
for item in items:
    print(f'  {item[0]}: current=${item[1] or 0:.2f}, last=${item[2] or 0:.2f}')

# Check recipe ingredients
cursor.execute('SELECT COUNT(*) FROM recipe_ingredients WHERE cost > 0')
ingredient_cost_count = cursor.fetchone()[0]
print(f'\nRecipe ingredients with cost > 0: {ingredient_cost_count}')

# Show some recipe ingredients
cursor.execute('SELECT ingredient_name, quantity, unit_of_measure, cost FROM recipe_ingredients WHERE cost > 0 LIMIT 5')
ingredients = cursor.fetchall()
print('\nRecipe ingredients with costs:')
for ing in ingredients:
    print(f'  {ing[0]}: {ing[1]} {ing[2]} - ${ing[3]:.2f}')

conn.close()
