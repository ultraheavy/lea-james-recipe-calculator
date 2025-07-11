#!/bin/bash

# Database Deployment Script
# Uploads local database to production

echo "=== Database Deployment Script ==="
echo "This will upload your local database to production"
echo ""

# Configuration
LOCAL_DB="restaurant_calculator.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="restaurant_calculator_backup_${TIMESTAMP}.db"

# Check if local database exists
if [ ! -f "$LOCAL_DB" ]; then
    echo "Error: Local database $LOCAL_DB not found!"
    exit 1
fi

echo "1. Creating backup of local database..."
cp "$LOCAL_DB" "${BACKUP_NAME}"
echo "   Backup created: ${BACKUP_NAME}"

echo ""
echo "2. Database statistics:"
echo "   Size: $(du -h $LOCAL_DB | cut -f1)"
echo "   Tables: $(sqlite3 $LOCAL_DB "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" 2>/dev/null)"
echo "   Menus: $(sqlite3 $LOCAL_DB "SELECT COUNT(*) FROM menus_actual;" 2>/dev/null)"
echo "   Recipes: $(sqlite3 $LOCAL_DB "SELECT COUNT(*) FROM recipes_actual;" 2>/dev/null)"
echo "   Inventory: $(sqlite3 $LOCAL_DB "SELECT COUNT(*) FROM inventory;" 2>/dev/null)"

echo ""
echo "=== DEPLOYMENT OPTIONS ==="
echo ""
echo "Choose your deployment method:"
echo ""
echo "OPTION 1: Direct File Upload (Recommended for small deployments)"
echo "  - Use SFTP/SCP to upload the database file"
echo "  - Example: scp $LOCAL_DB user@server:/path/to/app/"
echo ""
echo "OPTION 2: Git-based deployment (if database is in repo)"
echo "  - Add to git: git add $LOCAL_DB"
echo "  - Commit: git commit -m 'Update production database'"
echo "  - Push: git push origin main"
echo ""
echo "OPTION 3: Cloud hosting (Heroku, AWS, etc.)"
echo "  - Each platform has specific database upload methods"
echo "  - Usually involves database dump/restore commands"
echo ""

# Create a compressed version for easier upload
echo "3. Creating compressed version for upload..."
cp "$LOCAL_DB" "${LOCAL_DB}.upload"
gzip -9 "${LOCAL_DB}.upload"
echo "   Compressed file created: ${LOCAL_DB}.upload.gz"
echo "   Compressed size: $(du -h ${LOCAL_DB}.upload.gz | cut -f1)"

echo ""
echo "=== MANUAL UPLOAD INSTRUCTIONS ==="
echo ""
echo "For manual upload via SCP:"
echo "  scp ${LOCAL_DB}.upload.gz user@yourserver:/path/to/app/"
echo ""
echo "Then on the server:"
echo "  1. Backup existing: mv restaurant_calculator.db restaurant_calculator.db.old"
echo "  2. Decompress: gunzip restaurant_calculator.db.upload.gz"
echo "  3. Rename: mv restaurant_calculator.db.upload restaurant_calculator.db"
echo "  4. Set permissions: chmod 644 restaurant_calculator.db"
echo "  5. Restart app: [your restart command]"
echo ""

# Clean up
rm -f "${LOCAL_DB}.upload.gz"