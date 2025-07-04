# Restaurant Calculator - Development Guide

## Git Repository Setup

This project uses Git for version control. The repository structure follows standard Python/Flask conventions.

### Repository Structure

```
├── .git/                   # Git repository data
├── .gitignore             # Files to ignore in version control
├── README.md              # Main project documentation
├── DEVELOPMENT.md         # This file - development guide
├── requirements.txt       # Python dependencies
├── app.py                 # Main Flask application
├── add_sample_data.py     # Utility to add sample data
├── start_app.sh          # Start application script
├── stop_app.sh           # Stop application script
└── templates/            # HTML templates
    ├── base.html         # Base template
    ├── index.html        # Dashboard
    ├── inventory.html    # Inventory management
    ├── add_inventory.html # Add inventory form
    ├── recipes.html      # Recipe management
    ├── add_recipe.html   # Add recipe form
    ├── view_recipe.html  # Recipe details
    └── menu.html         # Menu management
```

### Files Not Tracked by Git

- `*.db` - Database files (created at runtime)
- `*.log` - Log files
- `__pycache__/` - Python cache files
- `*.xlsx`, `*.xlsm` - Original Excel files (reference only)
- Environment and IDE files

### Development Workflow

1. **Make changes to code**
2. **Test changes locally**:
   ```bash
   ./start_app.sh
   # Test at http://localhost:8888
   ./stop_app.sh
   ```
3. **Stage changes**:
   ```bash
   git add filename.py
   # or add all changes:
   git add .
   ```
4. **Commit changes**:
   ```bash
   git commit -m "Brief description of changes"
   ```
5. **View commit history**:
   ```bash
   git log --oneline
   ```

### Branching Strategy

- `main` - Production-ready code
- Create feature branches for new features:
  ```bash
  git checkout -b feature/ingredient-photos
  # make changes
  git commit -m "Add photo upload for ingredients"
  git checkout main
  git merge feature/ingredient-photos
  ```

### Useful Git Commands

```bash
# Check repository status
git status

# View changes
git diff

# View commit history
git log --oneline

# Create new branch
git checkout -b branch-name

# Switch branches
git checkout main

# Reset uncommitted changes
git checkout -- filename.py

# Reset to last commit (careful!)
git reset --hard HEAD
```

### Database Management

The SQLite database (`restaurant_calculator.db`) is NOT tracked in Git because:
- It contains user data that changes frequently
- Database files are binary and don't work well with version control
- Each environment should have its own database

To share database structure changes:
1. Modify the schema in `app.py` (in `init_database()` function)
2. Update `add_sample_data.py` if needed
3. Commit these Python files to Git

### Deployment Notes

When deploying to a new environment:
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `python3 app.py`
4. The database will be created automatically
5. Add sample data: `python3 add_sample_data.py`

