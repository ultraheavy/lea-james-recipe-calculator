#!/bin/bash
# Quick database sync to production

echo "🔄 Syncing database to production..."

# Export database
python3 scripts/sync_database.py

# Add and commit
git add data/production_data.sql data/production_data_summary.txt
git commit -m "Update production database - $(date +%Y-%m-%d)"

# Push to trigger deployment
git push origin main

echo "✅ Sync complete! Railway will automatically deploy with new data."