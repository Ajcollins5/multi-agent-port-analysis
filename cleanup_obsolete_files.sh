#!/bin/bash

# Cleanup Script for Multi-Agent Portfolio Analysis
# Removes obsolete files after successful Vercel deployment

echo "🧹 Starting cleanup of obsolete files..."
echo "This will remove migration docs, test files, and duplicate code"
echo

# Confirmation
read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 1
fi

echo "Starting cleanup..."

# 1. Remove duplicate application files
echo "📁 Removing duplicate application files..."
rm -f main.py
rm -f render.yaml
rm -f cloud_config.py
rm -f setup-env.sh
echo "✅ Removed duplicate application files"

# 2. Remove migration documentation
echo "📚 Removing migration documentation..."
rm -f VERCEL_*.md
rm -f DEPLOYMENT*.md
rm -f ENHANCED_VERCEL_SETUP.md
rm -f NEXTJS_MIGRATION.md
rm -f STREAMLIT_CLOUD_DEPLOYMENT.md
rm -f PROJECT_REVIEW.md
rm -f COST_ANALYSIS.md
rm -f README_INTEGRATION_TESTS.md
echo "✅ Removed migration documentation"

# 3. Remove test and debug files
echo "🔧 Removing test and debug files..."
rm -f test_*.py
rm -f run_tests.py
rm -rf .pytest_cache/
rm -f deploy_debug.py
rm -f deployment_debug_report.json
rm -f deployment_verification.py
rm -f vercel_setup_check.py
echo "✅ Removed test and debug files"

# 4. Remove migration scripts
echo "🔄 Removing migration scripts..."
rm -f migrate_to_beta.py
rm -f optimizations.py
echo "✅ Removed migration scripts"

# 5. Remove build artifacts
echo "🗂️ Removing build artifacts..."
rm -rf Werkzeug-1.0.1.dist-info/
rm -rf werkzeug/
rm -f .DS_Store
echo "✅ Removed build artifacts"

# 6. Check scripts directory
if [ -d "scripts/" ]; then
    echo "⚠️  Found scripts/ directory. Please review contents before removing:"
    ls -la scripts/
    read -p "Remove scripts/ directory? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf scripts/
        echo "✅ Removed scripts directory"
    else
        echo "⏭️  Skipped scripts directory"
    fi
fi

# 7. Check for alternative frontend files
echo "🌐 Checking frontend configuration..."
if [ -f "index.html" ] && [ -d "frontend/" ]; then
    echo "⚠️  Found both index.html and frontend/ directory"
    echo "   - index.html: Static landing page"
    echo "   - frontend/: Next.js application"
    echo "   - Current deployment uses Next.js frontend"
    read -p "Remove static index.html and sw.js? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f index.html
        rm -f sw.js
        echo "✅ Removed static frontend files"
    else
        echo "⏭️  Kept static frontend files"
    fi
fi

# 8. Optional: Remove .streamlit directory (if exists)
if [ -d ".streamlit/" ]; then
    echo "🔧 Found .streamlit/ directory (no longer needed)"
    read -p "Remove .streamlit/ directory? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf .streamlit/
        echo "✅ Removed .streamlit directory"
    else
        echo "⏭️  Kept .streamlit directory"
    fi
fi

echo
echo "🎉 Cleanup completed!"
echo
echo "📊 Summary of removed files:"
echo "   - Migration documentation: ~200KB"
echo "   - Test files: ~75KB"
echo "   - Debug files: ~50KB"
echo "   - Duplicate code: ~40KB"
echo "   - Build artifacts: ~30KB"
echo "   - Total space saved: ~400KB+"
echo
echo "✅ Essential files preserved:"
echo "   - api/ directory (all files)"
echo "   - frontend/ directory (Next.js app)"
echo "   - vercel.json"
echo "   - requirements.txt"
echo "   - README.md"
echo "   - LICENSE"
echo "   - .gitignore"
echo
echo "🚀 Your deployment is now cleaner and ready for production!" 