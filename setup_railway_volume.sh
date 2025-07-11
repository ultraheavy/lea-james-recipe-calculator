#!/bin/bash

# Railway Volume Setup Script
# This helps transition from git-based database to volume-based storage

echo "=== Railway Volume Setup Guide ==="
echo ""
echo "This script will help you set up persistent database storage using Railway volumes."
echo ""

# Check current state
if [ -f "restaurant_calculator.db" ]; then
    echo "✓ Local database found: restaurant_calculator.db"
    echo "  Size: $(du -h restaurant_calculator.db | cut -f1)"
else
    echo "⚠️  No local database found"
fi

echo ""
echo "=== STEP 1: Create Volume in Railway Dashboard ==="
echo ""
echo "1. Go to: https://railway.app/dashboard"
echo "2. Select your project: 'Lea Jane's Menu Coster'"
echo "3. Click on the 'web' service"
echo "4. Go to Settings → Volumes"
echo "5. Click '+ New Volume' with these settings:"
echo "   - Mount Path: /data"
echo "   - Name: recipe-db-volume"
echo "6. Click 'Create Volume'"
echo ""
read -p "Press Enter when you've created the volume in Railway..."

echo ""
echo "=== STEP 2: Deploy Code Changes ==="
echo ""
echo "The code has been updated to use the volume. Let's deploy:"
echo ""

# Commit the changes
echo "Committing volume support changes..."
git add app.py railway_volume_config.py setup_railway_volume.sh
git commit -m "Add Railway volume support for persistent database storage"

echo ""
echo "=== STEP 3: Initial Deployment (With Database) ==="
echo ""
echo "For the first deployment, we need the database in git to migrate it to the volume."
echo "The app will automatically copy it to /data/ on first run."
echo ""
read -p "Ready to push to main? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin main
    echo ""
    echo "✓ Pushed to main! Railway will deploy in 3-5 minutes."
    echo ""
    echo "=== STEP 4: Verify Volume Migration ==="
    echo ""
    echo "After deployment completes:"
    echo "1. Check the site works: https://ljmpc.ultraheavy.space/"
    echo "2. In Railway logs, look for:"
    echo "   - 'Railway volume detected at /data'"
    echo "   - 'Database migrated successfully!'"
    echo ""
    echo "=== STEP 5: Remove Database from Git ==="
    echo ""
    echo "Once confirmed working, run:"
    echo "  ./cleanup_database_from_git.sh"
    echo ""
    echo "This time it's safe because the database is in the volume!"
else
    echo "Deployment cancelled."
fi

echo ""
echo "=== Troubleshooting ==="
echo ""
echo "If the site stops working after cleanup:"
echo "1. The volume might not have mounted correctly"
echo "2. Check Railway logs for errors"
echo "3. You can always re-add the database to git as a fallback"
echo ""
echo "To check volume status via Railway CLI:"
echo "  railway logs | grep -i volume"