#!/bin/bash

# Deploy Vercel Function Fixes Script
# This script deploys the fixes for the failing Vercel functions

set -e  # Exit on any error

echo "🚀 Deploying Vercel Function Fixes"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "vercel.json" ]; then
    echo "❌ Error: vercel.json not found. Please run this script from the project root directory."
    exit 1
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Error: Vercel CLI is not installed."
    echo "Install it with: npm install -g vercel"
    exit 1
fi

# Check if user is logged in to Vercel
if ! vercel whoami &> /dev/null; then
    echo "🔐 Please log in to Vercel first:"
    vercel login
fi

# Show current configuration
echo "📋 Current Vercel Configuration:"
echo "   Functions configured:"
grep -A 10 '"functions"' vercel.json | head -8

echo "   Routing rules:"
grep -A 10 '"rewrites"' vercel.json | head -8

echo ""
echo "🔧 What we've fixed:"
echo "   ✅ Added proper routing for /api/scheduler/* endpoints"
echo "   ✅ Updated cron handler to use Vercel serverless format"
echo "   ✅ Added CORS headers for cross-origin requests"
echo "   ✅ Added authentication and error handling"
echo ""

# Ask for confirmation
read -p "📤 Ready to deploy? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled."
    exit 1
fi

echo "🔄 Starting deployment..."

# Deploy to Vercel
echo "   Deploying to production..."
vercel deploy --prod

# Get the deployment URL
VERCEL_URL=$(vercel ls --meta | grep -E "https://.*\.vercel\.app" | head -1 | awk '{print $1}')

if [ -z "$VERCEL_URL" ]; then
    echo "⚠️  Could not automatically detect Vercel URL."
    echo "   Please check your Vercel dashboard for the deployment URL."
    VERCEL_URL="https://your-project.vercel.app"
fi

echo "✅ Deployment completed!"
echo "   URL: $VERCEL_URL"

# Ask if user wants to run tests
echo ""
read -p "🧪 Run tests to verify the fixes? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔍 Running test script..."
    
    # Check if the test script exists
    if [ -f "scripts/test_vercel_endpoints.py" ]; then
        # Export the URL for the test script
        export VERCEL_URL="$VERCEL_URL"
        
        # Run the tests
        python3 scripts/test_vercel_endpoints.py
    else
        echo "❌ Test script not found at scripts/test_vercel_endpoints.py"
        echo "   Please run it manually with:"
        echo "   VERCEL_URL=$VERCEL_URL python3 scripts/test_vercel_endpoints.py"
    fi
else
    echo "⏩ Skipping tests."
    echo "   You can run them later with:"
    echo "   VERCEL_URL=$VERCEL_URL python3 scripts/test_vercel_endpoints.py"
fi

echo ""
echo "🎯 Next Steps:"
echo "   1. Check your Vercel dashboard to confirm error rates have dropped"
echo "   2. Monitor the functions for a few minutes to ensure stability"
echo "   3. Test the frontend to ensure all features are working"
echo "   4. Set up environment variables if not already done:"
echo "      - CRON_SECRET: Secret for cron job authentication"
echo "      - SUPABASE_URL: Your Supabase project URL"
echo "      - SUPABASE_SERVICE_ROLE_KEY: Your Supabase service role key"
echo "      - XAI_API_KEY: Your xAI API key"
echo ""
echo "✨ Deployment complete! Your Vercel functions should now be working correctly." 