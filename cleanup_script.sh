#!/bin/bash

# Safe File Reorganization Script for Restaurant Management System
# Run this from the LJ_Test_Doca directory

set -e  # Exit on any error

echo "🧹 RESTAURANT MANAGEMENT SYSTEM - SAFE FILE CLEANUP"
echo "=================================================="

# Check we're in the right directory
if [ ! -f "app.py" ] || [ ! -f "restaurant_calculator.db" ]; then
    echo "❌ ERROR: Not in the correct directory. Please run from LJ_Test_Doca/"
    exit 1
fi

echo "✅ Confirmed: In correct project directory"

# Create backup before any changes
BACKUP_DIR="LJ_Test_Doca_BACKUP_$(date +%Y%m%d_%H%M%S)"
PARENT_DIR=$(dirname "$(pwd)")
echo "📦 Creating safety backup: $PARENT_DIR/$BACKUP_DIR"
cp -r "$(pwd)" "$PARENT_DIR/$BACKUP_DIR"

# Git commit current state
echo "💾 Creating git backup commit..."
git add .
git commit -m "PRE-CLEANUP: Backup before file reorganization $(date)" || echo "  - Working tree clean, no commit needed"

echo ""
echo "🗂️  PHASE 1: CREATE NEW DIRECTORY STRUCTURE"
echo "============================================"

# Create new directory structure
mkdir -p app
mkdir -p data/{imports,exports,sources}
mkdir -p scripts/{backup,utilities,data_cleanup}
mkdir -p migrations/{completed,archive}
mkdir -p docs/{user,technical,ai_safety}
mkdir -p logs
mkdir -p archive/{old_apps,old_databases,old_scripts,temp_files}
mkdir -p deployment

echo "✅ Created new directory structure"

echo ""
echo "🗂️  PHASE 2: MOVE CORE APPLICATION FILES"
echo "========================================"

# Move core app files (keeping copies for safety)
echo "Moving core application files..."
cp cost_utils.py app/ 2>/dev/null || echo "  - cost_utils.py not found, skipping"
cp unit_converter.py app/ 2>/dev/null || echo "  - unit_converter.py not found, skipping"

# Note: We'll keep app.py and restaurant_calculator.db in root for now to avoid breaking imports

echo ""
echo "🗂️  PHASE 3: ORGANIZE DATA MANAGEMENT FILES"
echo "=========================================="

# Move import/export scripts
echo "Moving data import/export scripts..."
mv import_toast_data*.py data/imports/ 2>/dev/null || echo "  - No import_toast_data files found"
mv import_xtrachef_data.py data/imports/ 2>/dev/null || echo "  - import_xtrachef_data.py not found"
mv import_recipe_system.py data/imports/ 2>/dev/null || echo "  - import_recipe_system.py not found"
mv import_database.py data/imports/ 2>/dev/null || echo "  - import_database.py not found"
mv import_recipe_ingredients.py data/imports/ 2>/dev/null || echo "  - import_recipe_ingredients.py not found"

mv export_data.py data/exports/ 2>/dev/null || echo "  - export_data.py not found"
mv export_database.py data/exports/ 2>/dev/null || echo "  - export_database.py not found"

# Move original data sources
mv data_sources_from_toast data/sources/ 2>/dev/null || echo "  - data_sources_from_toast not found"
mv *.csv data/sources/ 2>/dev/null || echo "  - No CSV files found in root"

echo ""
echo "🗂️  PHASE 4: ORGANIZE UTILITY SCRIPTS"
echo "===================================="

# Move backup and utility scripts
echo "Moving utility scripts..."
mv backup_automation.py scripts/backup/ 2>/dev/null || echo "  - backup_automation.py not found"
mv backup_database.py scripts/backup/ 2>/dev/null || echo "  - backup_database.py not found"

mv recalculate_*.py scripts/utilities/ 2>/dev/null || echo "  - No recalculate scripts found"
mv *_quality.py scripts/utilities/ 2>/dev/null || echo "  - No quality scripts found"
mv unit_converter.py scripts/utilities/ 2>/dev/null || echo "  - unit_converter.py already moved or not found"

# Move one-time cleanup scripts
echo "Moving completed migration scripts..."
mv fix_*.py scripts/data_cleanup/ 2>/dev/null || echo "  - No fix scripts found"
mv cleanup_*.py scripts/data_cleanup/ 2>/dev/null || echo "  - No cleanup scripts found"
mv add_*.py scripts/data_cleanup/ 2>/dev/null || echo "  - No add scripts found"
mv populate_*.py scripts/data_cleanup/ 2>/dev/null || echo "  - No populate scripts found"

echo ""
echo "🗂️  PHASE 5: ARCHIVE OLD FILES"
echo "============================="

# Archive old application versions
echo "Archiving old application files..."
mv app_*.py archive/old_apps/ 2>/dev/null || echo "  - No old app files found"

# Archive old databases
echo "Archiving old database files..."
mv *_old.db archive/old_databases/ 2>/dev/null || echo "  - No old database files found"
mv toast_recipes.db archive/old_databases/ 2>/dev/null || echo "  - toast_recipes.db not found"
mv restaurant_manager.db archive/old_databases/ 2>/dev/null || echo "  - restaurant_manager.db not found"

# Archive temporary files
echo "Archiving temporary files..."
mv debug_*.py archive/temp_files/ 2>/dev/null || echo "  - No debug files found"
mv sanity.py archive/temp_files/ 2>/dev/null || echo "  - sanity.py not found"
mv *.log logs/ 2>/dev/null || echo "  - No log files found in root"

echo ""
echo "🗂️  PHASE 6: ORGANIZE DOCUMENTATION"
echo "=================================="

# Move documentation files
echo "Moving documentation files..."
mv AI_*.md docs/ai_safety/ 2>/dev/null || echo "  - No AI documentation found"
mv BRD.md docs/technical/ 2>/dev/null || echo "  - BRD.md not found"
mv PRD.md docs/technical/ 2>/dev/null || echo "  - PRD.md not found"
mv FRD.md docs/technical/ 2>/dev/null || echo "  - FRD.md not found"
mv DATA_MODEL.md docs/technical/ 2>/dev/null || echo "  - DATA_MODEL.md not found"
mv CLAUDE*.md docs/ai_safety/ 2>/dev/null || echo "  - No CLAUDE documentation found"

mv DEPLOYMENT.md docs/user/ 2>/dev/null || echo "  - DEPLOYMENT.md not found"
mv DEVELOPMENT.md docs/user/ 2>/dev/null || echo "  - DEVELOPMENT.md not found"
mv PROJECT_*.md docs/technical/ 2>/dev/null || echo "  - No PROJECT documentation found"

echo ""
echo "🗂️  PHASE 7: ORGANIZE DEPLOYMENT FILES"
echo "====================================="

# Move deployment-related files
echo "Moving deployment files..."
mv Procfile deployment/ 2>/dev/null || echo "  - Procfile not found"
mv railway.json deployment/ 2>/dev/null || echo "  - railway.json not found"
cp requirements.txt deployment/ 2>/dev/null || echo "  - requirements.txt not found"

echo ""
echo "🗂️  PHASE 8: MOVE EXISTING FOLDERS"
echo "================================="

# Move existing organized folders
mv backups/* logs/ 2>/dev/null || echo "  - No existing backups folder"
mv migrations/* migrations/archive/ 2>/dev/null || echo "  - migrations folder empty or doesn't exist"

echo ""
echo "🧹 PHASE 9: CLEANUP EMPTY DIRECTORIES AND HIDDEN FILES"
echo "======================================================"

# Remove empty directories
find . -maxdepth 1 -type d -empty -delete 2>/dev/null || true

# Clean up hidden files (be careful with .git)
find . -name ".DS_Store" -delete 2>/dev/null || true
rm -rf __pycache__ 2>/dev/null || true

echo ""
echo "✅ CLEANUP COMPLETE!"
echo "==================="
echo ""
echo "📊 SUMMARY OF CHANGES:"
echo "- ✅ Created organized directory structure"
echo "- ✅ Moved data import/export scripts to data/"
echo "- ✅ Moved utility scripts to scripts/"
echo "- ✅ Archived old files to archive/"
echo "- ✅ Organized documentation in docs/"
echo "- ✅ Moved deployment files to deployment/"
echo ""
echo "📁 NEW STRUCTURE:"
find . -type d -maxdepth 2 | sort
echo ""
echo "🚨 IMPORTANT NEXT STEPS:"
echo "1. Test the application: python3 app.py"
echo "2. Visit http://localhost:8888 to verify it works"
echo "3. Test import scripts from their new locations"
echo "4. Update any hardcoded paths in configuration files"
echo "5. Commit changes: git add . && git commit -m 'Reorganize project structure'"
echo ""
echo "💾 BACKUP LOCATION: $PARENT_DIR/$BACKUP_DIR"
echo "🔄 ROLLBACK: If anything breaks, restore from backup"
echo ""
echo "✅ CLEANUP COMPLETED SUCCESSFULLY!"