# Restaurant Recipe Cost Calculator - Web App Version

This is a Flask web application that replicates the functionality of your Excel restaurant recipe cost calculator (`LJ_recipe_cost_calculator_withoutmacros.xlsx`).

## Features

✅ **Inventory Management** - Replaces "Inventory Master" sheet
- Add/edit ingredients with costs, units, and yields
- Track purchase units vs recipe units
- Calculate yield percentages

✅ **Recipe Cost Calculator** - Replaces Recipe_1, Recipe_2, etc. sheets
- Create recipes with multiple ingredients
- Automatic cost calculations
- Track yield amounts and shelf life
- Station and equipment requirements

✅ **Menu Item Management** - Replaces "Menu Item List" sheets
- Link recipes to menu items
- Calculate food cost percentages
- Track menu pricing and profitability

✅ **Unit Conversions** - Replaces "Conversion Calculator" sheet
- Convert between cooking measurements
- Automatic calculations for recipe scaling

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (file-based, no server required)
- **Frontend**: HTML/CSS/JavaScript
- **Deployment**: Can run locally or on any server

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip3 install flask
   ```

2. **Run the Application**:
   ```bash
   python3 app.py
   ```

3. **Access the App**:
   Open your browser to: `http://localhost:8888`

## File Structure

```
LJ_Test_Doca/
├── app.py                          # Main Flask application
├── templates/                      # HTML templates
│   ├── base.html                  # Base template with navigation
│   ├── index.html                 # Dashboard
│   ├── inventory.html             # Inventory management
│   └── recipes.html               # Recipe management
├── restaurant_calculator.db       # SQLite database (auto-created)
└── README.md                      # This file
```

## Database Schema

The app uses SQLite with these tables:

- **inventory** - Ingredient master data
- **recipes** - Recipe information
- **recipe_ingredients** - Links recipes to ingredients with quantities
- **menu_items** - Menu items linked to recipes

## Advantages over Excel

1. **Multi-user Access** - Multiple people can use it simultaneously
2. **Web-based** - Access from any device with a browser
3. **Data Integrity** - Prevents formula corruption
4. **Backup & Sync** - Easy to backup the database file
5. **Scalability** - Can handle thousands of recipes/ingredients
6. **Mobile Friendly** - Works on phones and tablets
7. **Security** - No macro security concerns

## Next Steps to Expand

- Add user authentication
- Import existing Excel data
- Export to PDF reports
- Recipe photo uploads
- Nutritional information
- Supplier management
- Cost trend analysis
- Menu engineering analytics

## Original Excel Structure Analyzed

The original Excel file contained:
- 36 worksheets total
- Inventory Master with 995+ data strings
- 15 Recipe calculation sheets
- 15 Menu Cost Group sheets
- Instructions and conversion tools
- Batch recipe management
