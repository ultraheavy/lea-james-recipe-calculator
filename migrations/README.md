# Database Migration Guide

## Menu System Unification Migration

This migration unifies the dual menu system (menu_versions + menus tables) into a single `menus_actual` table.

### Prerequisites
1. **BACKUP YOUR DATABASE FIRST!**
2. Ensure you have SQLite3 installed
3. Have access to your production database

### Migration Steps

#### 1. Backup Production Database
```bash
# For SQLite
sqlite3 restaurant_calculator.db ".backup restaurant_calculator_backup_$(date +%Y%m%d).db"

# Or copy the file
cp restaurant_calculator.db restaurant_calculator_backup_$(date +%Y%m%d).db
```

#### 2. Run Migration Script
```bash
# Run the migration
sqlite3 restaurant_calculator.db < migrations/unify_menu_system.sql

# Check the output for any errors
```

#### 3. Deploy Code Changes
The following code changes need to be deployed:
- Updated `app.py` with unified menu routes
- Updated templates (removed Recipe Assignment links)
- Updated CSS for better dropdown styling

```bash
# Pull latest changes
git pull origin main

# Restart your application
# (depends on your deployment method)
```

#### 4. Verify Migration
```bash
# Check the new table structure
sqlite3 restaurant_calculator.db "SELECT * FROM menus_actual;"

# Verify menu items
sqlite3 restaurant_calculator.db "SELECT COUNT(*) FROM menu_menu_items_actual;"
```

### Rollback Plan
If something goes wrong:

1. Stop the application
2. Restore from backup:
```bash
mv restaurant_calculator_backup_[date].db restaurant_calculator.db
```
3. Revert code changes:
```bash
git checkout 62e92f5  # commit before menu unification
```
4. Restart application

### What Changed

1. **Database Changes:**
   - New primary table: `menus_actual`
   - New relationship table: `menu_menu_items_actual`
   - Old tables kept but deprecated: `menu_versions`, `menu_items`

2. **Route Changes:**
   - `/menu_items` now redirects to `/menus_mgmt`
   - Pricing analysis uses `menus_actual` instead of `menu_versions`

3. **UI Improvements:**
   - Fixed dropdown styling (smaller fonts, better scaling)
   - View switcher works on all inventory pages
   - Removed redundant "Recipe Assignment" navigation links

### Post-Migration Checklist

- [ ] Database backup created
- [ ] Migration script executed successfully
- [ ] No errors in migration output
- [ ] Application restarted
- [ ] Menu management page loads correctly
- [ ] Can create/edit menus
- [ ] Pricing analysis works with new menu system
- [ ] Inventory dropdowns display correctly
- [ ] View switcher (table/card/list) works

### Support

If you encounter issues:
1. Check the application logs
2. Verify all tables exist with `.tables` command in SQLite
3. Ensure foreign key constraints are satisfied
4. The old tables are preserved - you can query them if needed