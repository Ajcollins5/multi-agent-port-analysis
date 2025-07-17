#!/bin/bash

# Build ignore script for Vercel
# This script determines whether to skip the build based on the changes

# Get the list of changed files
CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD)

# Define patterns for files that should NOT trigger a build
IGNORE_PATTERNS=(
    "README.md"
    "*.md"
    "DEPLOYMENT.md"
    "PROJECT_REVIEW.md"
    "COST_ANALYSIS.md"
    "ENHANCED_VERCEL_SETUP.md"
    "NEXTJS_MIGRATION.md"
    "LICENSE"
    ".gitignore"
    ".vercelignore"
    "test_tools.py"
    "run_tests.py"
    "*_test.py"
    "migrate_to_beta.py"
    "optimizations.py"
    "worker.py"
    "cloud_config.py"
    "*.log"
    ".DS_Store"
    "Thumbs.db"
    "environment.config.example"
    "api/environment.example"
)

# Check if only ignored files were changed
SIGNIFICANT_CHANGES=false

for file in $CHANGED_FILES; do
    SHOULD_IGNORE=false
    
    # Check if file matches any ignore pattern
    for pattern in "${IGNORE_PATTERNS[@]}"; do
        if [[ $file == $pattern ]]; then
            SHOULD_IGNORE=true
            break
        fi
    done
    
    # If file doesn't match ignore patterns, it's a significant change
    if [ "$SHOULD_IGNORE" = false ]; then
        SIGNIFICANT_CHANGES=true
        break
    fi
done

# Skip build if only non-significant files changed
if [ "$SIGNIFICANT_CHANGES" = false ]; then
    echo "🚀 Only documentation or test files changed. Skipping build."
    exit 0
else
    echo "✅ Significant changes detected. Proceeding with build."
    exit 1
fi 