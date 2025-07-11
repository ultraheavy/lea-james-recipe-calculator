#!/bin/bash
echo "Removing database from git..."
git rm --cached restaurant_calculator.db
echo "restaurant_calculator.db" >> .gitignore
git add .gitignore
git commit -m "Remove database from git tracking"
git push origin main
echo "✓ Database removed from git"
echo "✓ Added to .gitignore"
