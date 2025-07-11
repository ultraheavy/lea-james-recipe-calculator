#!/bin/bash

# Upload Local Database to Railway Production
# This script prepares and guides you through uploading your local database

echo "=== Upload Local Database to Railway ==="
echo ""

# Check if database exists
if [ ! -f "restaurant_calculator.db" ]; then
    echo "Error: restaurant_calculator.db not found!"
    exit 1
fi

# Create backup with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="restaurant_calculator_local_backup_${TIMESTAMP}.db"
UPLOAD_FILE="restaurant_calculator_upload.db"

echo "1. Creating local backup..."
cp restaurant_calculator.db "$BACKUP_FILE"
echo "   ✓ Backup created: $BACKUP_FILE"

echo ""
echo "2. Preparing upload file..."
cp restaurant_calculator.db "$UPLOAD_FILE"
echo "   ✓ Upload file created: $UPLOAD_FILE"
echo "   ✓ Size: $(du -h $UPLOAD_FILE | cut -f1)"

echo ""
echo "3. Creating compressed version for faster upload..."
gzip -c "$UPLOAD_FILE" > "${UPLOAD_FILE}.gz"
echo "   ✓ Compressed file: ${UPLOAD_FILE}.gz"
echo "   ✓ Compressed size: $(du -h ${UPLOAD_FILE}.gz | cut -f1)"

echo ""
echo "=== RAILWAY UPLOAD INSTRUCTIONS ==="
echo ""
echo "METHOD 1: Using Railway CLI (if installed)"
echo "------------------------------------------"
echo "1. Install Railway CLI if needed:"
echo "   curl -fsSL https://railway.app/install.sh | sh"
echo ""
echo "2. Login to Railway:"
echo "   railway login"
echo ""
echo "3. Link to your project:"
echo "   railway link"
echo ""
echo "4. Upload the database:"
echo "   railway up ${UPLOAD_FILE}.gz"
echo ""
echo "5. In Railway dashboard, set up a volume mount:"
echo "   - Go to your service settings"
echo "   - Add a volume mount at /app/data"
echo "   - Move database to mounted volume"
echo ""

echo "METHOD 2: Using GitHub (Recommended)"
echo "------------------------------------"
echo "1. Add database to git (temporarily):"
echo "   git add -f restaurant_calculator.db"
echo "   git commit -m 'Add production database'"
echo "   git push origin main"
echo ""
echo "2. Railway will automatically deploy with the database"
echo ""
echo "3. IMPORTANT: Remove database from git after deployment:"
echo "   git rm --cached restaurant_calculator.db"
echo "   git commit -m 'Remove database from git'"
echo "   git push origin main"
echo ""

echo "METHOD 3: Manual Upload via Railway Dashboard"
echo "--------------------------------------------"
echo "1. Go to https://railway.app/dashboard"
echo "2. Select your project"
echo "3. Go to 'Variables' or 'Volumes'"
echo "4. Upload the database file"
echo ""

echo "=== POST-UPLOAD STEPS ==="
echo "1. Verify the site works: https://ljmpc.ultraheavy.space/"
echo "2. Check dashboard: https://ljmpc.ultraheavy.space/pricing-analysis"
echo "3. Remove temporary files:"
echo "   rm -f ${UPLOAD_FILE} ${UPLOAD_FILE}.gz"
echo ""

# Create a git-based upload option
echo "=== QUICK OPTION: Git-based Upload ==="
echo "Would you like to use the Git method? (y/n)"
read -r response

if [[ "$response" == "y" ]]; then
    echo ""
    echo "Adding database to git..."
    git add -f restaurant_calculator.db
    
    echo "Creating commit..."
    git commit -m "Add production database - temporary upload"
    
    echo "Pushing to GitHub (this will trigger Railway deployment)..."
    git push origin main
    
    echo ""
    echo "✓ Database pushed to GitHub!"
    echo "✓ Railway should start deploying automatically"
    echo ""
    echo "IMPORTANT: After deployment succeeds (5-10 minutes), run:"
    echo "  ./cleanup_database_from_git.sh"
    echo ""
    
    # Create cleanup script
    cat > cleanup_database_from_git.sh << 'CLEANUP'
#!/bin/bash
echo "Removing database from git..."
git rm --cached restaurant_calculator.db
echo "restaurant_calculator.db" >> .gitignore
git add .gitignore
git commit -m "Remove database from git tracking"
git push origin main
echo "✓ Database removed from git"
echo "✓ Added to .gitignore"
CLEANUP
    
    chmod +x cleanup_database_from_git.sh
    echo "Created cleanup script: cleanup_database_from_git.sh"
fi

# Clean up temporary upload file
rm -f "$UPLOAD_FILE"