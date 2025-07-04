# Git Quick Reference for Restaurant Calculator Project

## Daily Development Commands

```bash
# Check what has changed
git status

# See specific changes
git diff

# Add changes to staging
git add filename.py        # Add specific file
git add .                  # Add all changes

# Commit changes
git commit -m "Description of what you changed"

# View commit history
git log --oneline
```

## Project Management

```bash
# Start the app
./start_app.sh

# Stop the app  
./stop_app.sh

# Add sample data (first time setup)
python3 add_sample_data.py

# Manual start
python3 app.py
```

## Useful Scenarios

### Made a mistake and want to undo uncommitted changes
```bash
git checkout -- filename.py    # Undo changes to specific file
git checkout -- .              # Undo all uncommitted changes
```

### See what changed in last commit
```bash
git show
```

### Create a backup branch before major changes
```bash
git checkout -b backup-before-changes
git checkout main  # Go back to main branch
```

### Compare with previous version
```bash
git diff HEAD~1    # Compare with previous commit
```

## Current Repository Status

- **Branch**: main
- **Commits**: 3 (initial app, utilities, documentation)
- **Tracked**: 16 files (code, templates, docs)
- **Ignored**: Database files, logs, Excel files, Python cache

## Files NOT in Version Control
- `restaurant_calculator.db` - Your data
- `app.log` - Application logs  
- `__pycache__/` - Python cache
- `*.xlsx` - Original Excel files

These are ignored because they contain runtime data or are generated files.
