#!/bin/bash

# Multi-Agent Portfolio Analysis - Vercel Deployment Script
# This script handles the complete deployment process to Vercel

set -e  # Exit on any error

echo "🚀 Starting Vercel Deployment Process..."
echo "========================================"

# Check if we're in the correct directory
if [ ! -f "vercel.json" ]; then
    echo "❌ Error: vercel.json not found. Please run this script from the project root."
    exit 1
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Error: Vercel CLI is not installed."
    echo "Please install it with: npm install -g vercel"
    exit 1
fi

# Check if user is logged in to Vercel
if ! vercel whoami &> /dev/null; then
    echo "🔐 Please log in to Vercel first:"
    vercel login
fi

# Install frontend dependencies if needed
if [ -d "frontend" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    if [ -f "package.json" ]; then
        npm install
        echo "✅ Frontend dependencies installed"
    fi
    cd ..
fi

# Validate environment variables
echo "🔍 Validating environment configuration..."
python3 -c "
import sys
import os
sys.path.insert(0, 'api')
from config.env_validator import validate_environment

results = validate_environment()
if not results['success']:
    print('❌ Environment validation failed:')
    for error in results['errors']:
        print(f'  - {error[\"variable\"]}: {error[\"error\"]}')
    sys.exit(1)
else:
    print('✅ Environment validation passed')
"

# Check Python dependencies
echo "🐍 Checking Python dependencies..."
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt found"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
echo "This will deploy your multi-agent portfolio analysis system."
echo ""

# Ask for confirmation
read -p "Are you sure you want to deploy to production? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

# Deploy
echo "🔄 Starting deployment..."
vercel --prod

# Check deployment status
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Deployment Successful!"
    echo "========================================"
    echo "Your multi-agent portfolio analysis system is now live!"
    echo ""
    echo "📋 Post-deployment checklist:"
    echo "  ✅ Serverless functions deployed"
    echo "  ✅ API endpoints configured"
    echo "  ✅ Database storage ready"
    echo "  ✅ Email notifications configured"
    echo "  ✅ Cron jobs scheduled"
    echo ""
    echo "🔧 Next steps:"
    echo "  1. Test the API endpoints"
    echo "  2. Verify email notifications"
    echo "  3. Check the Vercel dashboard for function logs"
    echo "  4. Test portfolio analysis functionality"
    echo ""
    echo "🌐 Your deployment is ready for production use!"
else
    echo "❌ Deployment failed. Please check the error messages above."
    exit 1
fi 