#!/bin/bash

# Multi-Agent Portfolio Analysis - Environment Setup Script
# This script helps set up environment variables for local development and Vercel deployment

set -e

COLOR_RED='\033[0;31m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[0;34m'
COLOR_NC='\033[0m' # No Color

echo -e "${COLOR_BLUE}🚀 Multi-Agent Portfolio Analysis - Environment Setup${COLOR_NC}"
echo "============================================================="

# Function to prompt for input with default value
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    
    echo -e "${COLOR_YELLOW}$prompt${COLOR_NC}"
    if [ -n "$default" ]; then
        echo -e "${COLOR_BLUE}Default: $default${COLOR_NC}"
    fi
    read -p "Enter value: " input
    
    if [ -z "$input" ] && [ -n "$default" ]; then
        input="$default"
    fi
    
    declare -g "$var_name"="$input"
}

# Function to generate random string
generate_random() {
    openssl rand -hex 16
}

echo "Setting up environment variables..."
echo ""

# Core Configuration
echo -e "${COLOR_GREEN}1. Core Configuration${COLOR_NC}"
prompt_with_default "XAI API Key (get from x.ai/api):" "" "XAI_API_KEY"

# Email Configuration
echo ""
echo -e "${COLOR_GREEN}2. Email Configuration${COLOR_NC}"
prompt_with_default "SMTP Server:" "smtp.gmail.com" "SMTP_SERVER"
prompt_with_default "SMTP Port:" "587" "SMTP_PORT"
prompt_with_default "Sender Email:" "" "SENDER_EMAIL"
prompt_with_default "Sender Password (App Password for Gmail):" "" "SENDER_PASSWORD"
prompt_with_default "Recipient Email:" "" "TO_EMAIL"

# Database Configuration (Optional)
echo ""
echo -e "${COLOR_GREEN}3. Database Configuration (Optional)${COLOR_NC}"
prompt_with_default "Database URL (PostgreSQL):" "" "DATABASE_URL"
prompt_with_default "Redis URL:" "" "REDIS_URL"

# Vercel Configuration
echo ""
echo -e "${COLOR_GREEN}4. Vercel Configuration${COLOR_NC}"
prompt_with_default "Vercel URL:" "https://your-project.vercel.app" "VERCEL_URL"
prompt_with_default "Cron Secret:" "$(generate_random)" "CRON_SECRET"

# Security Configuration
echo ""
echo -e "${COLOR_GREEN}5. Security Configuration${COLOR_NC}"
prompt_with_default "API Secret Key:" "$(generate_random)" "API_SECRET_KEY"
prompt_with_default "Environment:" "development" "ENVIRONMENT"

# Portfolio Configuration
echo ""
echo -e "${COLOR_GREEN}6. Portfolio Configuration${COLOR_NC}"
prompt_with_default "Default Portfolio (comma-separated):" "AAPL,GOOGL,MSFT,AMZN,TSLA" "DEFAULT_PORTFOLIO"
prompt_with_default "High Volatility Threshold:" "0.05" "HIGH_VOLATILITY_THRESHOLD"

# Create .env file
echo ""
echo -e "${COLOR_BLUE}Creating .env file...${COLOR_NC}"

cat > .env << EOF
# Multi-Agent Portfolio Analysis - Environment Configuration
# Generated on: $(date)

# AI/ML Configuration
XAI_API_KEY=$XAI_API_KEY

# Email Configuration (SMTP)
SMTP_SERVER=$SMTP_SERVER
SMTP_PORT=$SMTP_PORT
SENDER_EMAIL=$SENDER_EMAIL
SENDER_PASSWORD=$SENDER_PASSWORD
TO_EMAIL=$TO_EMAIL

# Database Configuration (Optional)
DATABASE_URL=$DATABASE_URL
REDIS_URL=$REDIS_URL

# Vercel Configuration
VERCEL_URL=$VERCEL_URL
CRON_SECRET=$CRON_SECRET

# Security Configuration
API_SECRET_KEY=$API_SECRET_KEY
ENVIRONMENT=$ENVIRONMENT

# Portfolio Configuration
DEFAULT_PORTFOLIO=$DEFAULT_PORTFOLIO
HIGH_VOLATILITY_THRESHOLD=$HIGH_VOLATILITY_THRESHOLD

# Additional Configuration
MEDIUM_VOLATILITY_THRESHOLD=0.02
EMAIL_ALERT_THRESHOLD=0.05
DEFAULT_ANALYSIS_INTERVAL=60
BACKGROUND_PROCESSING=true
LOG_LEVEL=INFO
ENABLE_LOG_FILE=false
EOF

echo -e "${COLOR_GREEN}✅ .env file created successfully!${COLOR_NC}"

# Create Vercel environment variables script
echo ""
echo -e "${COLOR_BLUE}Creating Vercel environment setup script...${COLOR_NC}"

cat > setup-vercel-env.sh << 'EOF'
#!/bin/bash

# Vercel Environment Variables Setup Script
# Run this script to set up environment variables in Vercel

set -e

COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_NC='\033[0m'

echo -e "${COLOR_YELLOW}🔧 Setting up Vercel environment variables...${COLOR_NC}"

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Installing Vercel CLI..."
    npm install -g vercel
fi

# Source the .env file to get variables
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found. Run setup-env.sh first."
    exit 1
fi

# Set environment variables in Vercel
echo "Setting environment variables in Vercel..."

vercel env add XAI_API_KEY production <<< "$XAI_API_KEY"
vercel env add SMTP_SERVER production <<< "$SMTP_SERVER"
vercel env add SMTP_PORT production <<< "$SMTP_PORT"
vercel env add SENDER_EMAIL production <<< "$SENDER_EMAIL"
vercel env add SENDER_PASSWORD production <<< "$SENDER_PASSWORD"
vercel env add TO_EMAIL production <<< "$TO_EMAIL"

if [ -n "$DATABASE_URL" ]; then
    vercel env add DATABASE_URL production <<< "$DATABASE_URL"
fi

if [ -n "$REDIS_URL" ]; then
    vercel env add REDIS_URL production <<< "$REDIS_URL"
fi

vercel env add VERCEL_URL production <<< "$VERCEL_URL"
vercel env add CRON_SECRET production <<< "$CRON_SECRET"
vercel env add API_SECRET_KEY production <<< "$API_SECRET_KEY"
vercel env add ENVIRONMENT production <<< "production"
vercel env add DEFAULT_PORTFOLIO production <<< "$DEFAULT_PORTFOLIO"
vercel env add HIGH_VOLATILITY_THRESHOLD production <<< "$HIGH_VOLATILITY_THRESHOLD"

echo -e "${COLOR_GREEN}✅ Vercel environment variables set successfully!${COLOR_NC}"
echo "🚀 You can now deploy to Vercel with: vercel --prod"
EOF

chmod +x setup-vercel-env.sh

echo -e "${COLOR_GREEN}✅ Vercel setup script created: setup-vercel-env.sh${COLOR_NC}"

# Create frontend .env file
echo ""
echo -e "${COLOR_BLUE}Creating frontend .env file...${COLOR_NC}"

cat > frontend/.env.local << EOF
# Frontend Environment Variables
NEXT_PUBLIC_API_URL=$VERCEL_URL
NEXT_PUBLIC_ENVIRONMENT=$ENVIRONMENT
EOF

echo -e "${COLOR_GREEN}✅ Frontend .env.local file created!${COLOR_NC}"

# Security reminder
echo ""
echo -e "${COLOR_YELLOW}🔐 Security Reminders:${COLOR_NC}"
echo "1. Never commit .env files to version control"
echo "2. Use App Passwords for Gmail (not your regular password)"
echo "3. Keep your API keys secure and rotate them regularly"
echo "4. Set up proper CORS origins in production"
echo "5. Use strong secrets for CRON_SECRET and API_SECRET_KEY"

# Next steps
echo ""
echo -e "${COLOR_BLUE}📋 Next Steps:${COLOR_NC}"
echo "1. Review the generated .env file"
echo "2. Test email configuration: python -c \"from api.notifications.email_handler import test_email_configuration; print(test_email_configuration())\""
echo "3. Set up Vercel environment variables: ./setup-vercel-env.sh"
echo "4. Deploy to Vercel: vercel --prod"
echo "5. Set up GitHub Actions secrets for automated deployment"

echo ""
echo -e "${COLOR_GREEN}🎉 Environment setup completed successfully!${COLOR_NC}"
echo "📁 Files created:"
echo "   - .env (local development)"
echo "   - setup-vercel-env.sh (Vercel deployment)"
echo "   - frontend/.env.local (frontend configuration)" 