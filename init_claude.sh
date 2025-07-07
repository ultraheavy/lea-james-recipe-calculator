#!/bin/bash

# Claude Session Initialization Script
# Run this before starting any Claude Code session

echo "🚀 INITIALIZING CLAUDE SESSION FOR RESTAURANT MANAGEMENT SYSTEM"
echo "================================================================"

# Set project directory
PROJECT_DIR="/Users/ndrfn/Dropbox/001-Projects/Claude_projects/python_we4b_recipe_app/LJ_Test_Doca"

# Check if we're in the right directory
if [ ! -f "$PROJECT_DIR/CLAUDE.md" ]; then
    echo "❌ ERROR: Cannot find CLAUDE.md in project directory"
    echo "Please ensure you're in: $PROJECT_DIR"
    exit 1
fi

echo "✅ Project directory confirmed: $PROJECT_DIR"
echo ""

# Display critical files that Claude must read
echo "📚 CRITICAL DOCUMENTATION FILES:"
echo "================================"
echo "1. CLAUDE.md - AI Development Guidelines (MANDATORY)"
echo "2. DATA_MODEL.md - Sacred Database Structure (PROTECTED)"  
echo "3. AI_PROMPTING_GUIDE.md - Constraint-First Prompting (REQUIRED)"
echo "4. PRD.md - Product Requirements (BUSINESS AUTHORITY)"
echo "5. BRD.md - Business Requirements (CONTEXT)"
echo "6. FRD.md - Functional Requirements (TECHNICAL SPECS)"
echo ""

# Show current git status
echo "📝 GIT STATUS:"
echo "=============="
cd "$PROJECT_DIR"
git status --porcelain
echo ""

# Show database backup status
echo "💾 DATABASE BACKUP CHECK:"
echo "========================="
if [ -f "restaurant_calculator.db" ]; then
    echo "✅ Main database found: restaurant_calculator.db"
    ls -la restaurant_calculator_backup_*.db 2>/dev/null | tail -3
    echo "Last 3 backups shown above"
else
    echo "⚠️  Main database not found - check if server is running"
fi
echo ""

# Create the initialization prompt for Claude
echo "🤖 CLAUDE INITIALIZATION PROMPT:"
echo "================================="
echo ""
echo "COPY THIS PROMPT TO START YOUR CLAUDE SESSION:"
echo "----------------------------------------------"
echo ""
cat << 'EOF'
INITIALIZATION REQUEST - READ FIRST:

Before any work, please use desktop-commander to read these files:
1. CLAUDE.md (AI Guidelines - MANDATORY)
2. DATA_MODEL.md (Database Structure - PROTECTED) 
3. AI_PROMPTING_GUIDE.md (Prompting Rules - REQUIRED)

After reading, confirm you understand:
❌ Protected: Database schema, XtraChef import, cost calculations
✅ Allowed: CSS changes, new features (with approval)
🔒 Required: Backup database before ANY changes
📋 Mandatory: Use constraint-first prompting

STATE: "I have read the documentation and understand the constraints."

THEN provide your actual task using the template from AI_PROMPTING_GUIDE.md.
EOF

echo ""
echo "🎯 READY FOR CLAUDE SESSION!"
echo "Copy the prompt above to initialize Claude properly."
