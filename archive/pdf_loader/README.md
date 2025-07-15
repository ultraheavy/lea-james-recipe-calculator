# PDF Loader - Archived

This folder contains the archived PDF recipe loading functionality that was removed from the main application.

## Archived Date
January 14, 2025

## Reason for Archival
The PDF loader functionality was removed to simplify the application and reduce the number of staging interfaces.

## Archived Files

### Python Files
- `pdf_recipe_parser.py` - Original PDF parser implementation
- `pdf_recipe_parser_v2.py` - Updated PDF parser version
- `recipe_pdf_staging_admin.py` - Flask blueprint for PDF staging admin interface
- `pdf_recipe_loader.py` - PDF recipe loading functionality
- `pdf_recipe_extractor.py` - PDF data extraction utility
- `test_pdf_staging.py` - Tests for PDF staging functionality

### Templates
- `recipe_pdf_staging.html` - HTML template for PDF staging interface

### Database Migrations
- `create_stg_pdf_recipes.sql` - SQL migration for PDF staging tables

## Changes Made to Main Application

1. **app.py**
   - Removed PDF blueprint registration (lines 32-40)
   - Replaced with comment: "# PDF recipe staging blueprint removed - functionality archived"

2. **templates/base_modern.html**
   - Removed PDF Recipe Staging navigation link from admin dropdown

3. **csv_import_diagnostics.py**
   - Commented out PDF extractor import and functionality
   - PDF validation now returns False with warning message

4. **fix_calculation_accuracy.py**
   - Commented out Phase 1 PDF extraction
   - Added skip message for archived functionality

5. **calculation_rebuilder.py**
   - Set PDF_SUPPORT = False
   - PDF validation methods remain but are effectively disabled

## Database Impact
The `stg_pdf_recipes` table may still exist in the database but is no longer used by the application.

## Restoration
To restore this functionality:
1. Move files back to their original locations
2. Uncomment the blueprint registration in app.py
3. Restore the navigation link in base_modern.html
4. Uncomment PDF imports in affected files