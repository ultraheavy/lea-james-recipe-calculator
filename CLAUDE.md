# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Application Overview

This is a Flask-based restaurant management web application designed for recipe costing and menu management. It replaces an Excel-based system with a modern web interface integrated with Toast POS data.

## Commands

### Starting the Application
```bash
./start_app.sh              # Start Flask app on port 8888
# OR manually:
python3 app.py              # Runs in debug mode on port 8888
```

### Stopping the Application
```bash
./stop_app.sh               # Stop the running Flask app
# OR manually:
pkill -f 'python3 app.py'
```

### Database Operations
```bash
python3 add_sample_data.py      # Add sample data to database
python3 import_toast_data.py    # Import data from Toast CSV files
python3 backup_database.py      # Create timestamped database backup
sqlite3 restaurant_calculator.db ".schema"  # View database schema
```

### Git Operations with Auto-commit
The application includes an auto-commit system that tracks database changes:
```bash
python3 auto_commit.py          # Manually trigger database commit check
```

## Architecture

### Core Application Structure
- **app.py**: Main Flask application (741 lines) with all routes and database operations
- **auto_commit.py**: Git integration that automatically commits database changes with descriptive messages
- **restaurant_calculator.db**: SQLite database containing all business data

### Database Schema Overview
The database uses Toast POS-compatible fields:
- **inventory**: 16 fields including item_code, vendor pricing, yield percentages
- **recipes**: 24 fields for comprehensive recipe management
- **recipe_ingredients**: Links recipes to inventory with cost calculations
- **menu_items**: Tracks menu versions (V1/V2/V3) with pricing analysis
- **vendors & vendor_products**: Multi-vendor support per ingredient
- **menu_versions**: Supports menu planning and comparison

### Key Features Architecture
1. **Menu Versioning System**: Allows V1 (current), V2 (planning), V3 (future) menu management
2. **Multi-Vendor Support**: Each ingredient can have multiple vendors with primary/active status
3. **Auto-commit Integration**: Database changes are automatically tracked in git with descriptive commits
4. **Pricing Analysis**: Built-in recommendations based on target food cost percentages

### Template System
All templates extend base.html and expect these database fields:
- Inventory items use: item_code, item_description, vendor_name, current_price
- Recipes use: recipe_name, food_cost, menu_price, recipe_group
- Menu items use: item_name, menu_group, food_cost_percent, version_id

## Known Issues and Solutions

### Critical Template Field Mapping Issue
**Problem**: Templates reference incorrect field names (e.g., item.item_number instead of item.item_code)
**Impact**: Data exists but doesn't display in web interface
**Fix**: Update template field references to match database schema

### Recipe Ingredient Quantities
Some recipe ingredients have zero quantities due to CSV parsing issues. When fixing:
1. Check the original CSV files in data_sources_from_toast/
2. Update parsing logic in import_toast_data.py
3. Re-run the import after backing up the database

## Toast POS Integration

The application is designed to import/export data from Toast POS:
- Item Detail Reports → inventory table
- Recipe exports → recipes and recipe_ingredients tables
- All Toast-specific fields are preserved for compatibility

## Development Workflow

1. Always create a database backup before major changes:
   ```bash
   python3 backup_database.py
   ```

2. The auto_commit.py integration tracks database changes automatically

3. When modifying routes that change the database, they already use the @with_auto_commit decorator

4. Current data status:
   - 233 inventory items with pricing
   - 66 recipes with ingredients
   - ~96% ingredient matching rate
   - Menu versioning system active

## Port and Access
- Development server: http://localhost:8888
- Debug mode is enabled by default
- Accessible from network: host='0.0.0.0'