# 🚀 Vercel Production Deployment Guide

## 📋 Prerequisites

1. **Vercel CLI installed**:
   ```bash
   npm install -g vercel
   ```

2. **Python 3.9+** available locally (for pre-deployment validation)

3. **Required API Keys**:
   - Grok 4 API key from xAI
   - Email credentials for notifications

## 🔧 Environment Variables Setup

### Required Variables (Must be set in Vercel dashboard)

1. **Go to your Vercel project dashboard**
2. **Navigate to Settings → Environment Variables**
3. **Add the following variables**:

```bash
# AI Configuration
XAI_API_KEY=xai-xxxxxxxxxxxxxxxxxxxxxxxxxx

# Email Configuration
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
TO_EMAIL=alerts@yourdomain.com

# Optional (will use defaults if not set)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
ENVIRONMENT=production
HIGH_VOLATILITY_THRESHOLD=0.05
DEFAULT_PORTFOLIO=AAPL,GOOGL,MSFT,AMZN,TSLA
```

### 📧 Email Setup Instructions

1. **For Gmail**:
   - Enable 2-factor authentication
   - Generate an "App Password" for your email
   - Use the app password as `SENDER_PASSWORD`

2. **For other providers**:
   - Update `SMTP_SERVER` and `SMTP_PORT` accordingly
   - Use appropriate credentials

## 🚀 Deployment Steps

### Method 1: Using the Deployment Script (Recommended)

1. **Make the script executable**:
   ```bash
   chmod +x scripts/deploy.sh
   ```

2. **Run the deployment script**:
   ```bash
   ./scripts/deploy.sh
   ```

3. **Follow the prompts** and confirm deployment

### Method 2: Manual Deployment

1. **Login to Vercel**:
   ```bash
   vercel login
   ```

2. **Deploy to production**:
   ```bash
   vercel --prod
   ```

## 🔍 Post-Deployment Verification

### 1. Test API Endpoints

```bash
# Test system status
curl https://your-domain.vercel.app/api/app

# Test portfolio analysis
curl -X POST https://your-domain.vercel.app/api/app \
  -H "Content-Type: application/json" \
  -d '{"action": "portfolio_analysis"}'

# Test ticker analysis
curl -X POST https://your-domain.vercel.app/api/app \
  -H "Content-Type: application/json" \
  -d '{"action": "analyze_ticker", "ticker": "AAPL"}'
```

### 2. Check Function Logs

1. Go to Vercel dashboard
2. Navigate to Functions tab
3. Check for any errors in the logs

### 3. Test Email Notifications

```bash
curl -X POST https://your-domain.vercel.app/api/app \
  -H "Content-Type: application/json" \
  -d '{"action": "send_test_email", "subject": "Test", "message": "Deployment successful!"}'
```

## 🏗️ Architecture Overview

Your deployment includes:

- **🧠 Multi-Agent System**: RiskAgent, NewsAgent, EventSentinel, KnowledgeCurator, Supervisor
- **🤖 AI Integration**: Grok 4 for intelligent synthesis
- **💾 Data Storage**: SQLite with Redis caching
- **📧 Notifications**: Email alerts for high-risk events
- **⏰ Scheduled Tasks**: Automated portfolio monitoring
- **🔒 Security**: Environment validation and error handling

## 🛠️ Configuration Files

### vercel.json
- Defines serverless functions
- Sets up API routing
- Configures cron jobs
- Sets memory and timeout limits

### requirements.txt
- Python dependencies
- Automatically installed by Vercel

### Environment Variables
- Validated on startup
- Secure handling of sensitive data

## 🔧 Troubleshooting

### Common Issues:

1. **"XAI_API_KEY not found"**:
   - Ensure the API key is set in Vercel dashboard
   - Check the key format (should start with "xai-")

2. **Email sending fails**:
   - Verify email credentials
   - Check if 2FA is enabled and app password is used

3. **Function timeout**:
   - Check function logs in Vercel dashboard
   - Verify API limits aren't exceeded

4. **Database errors**:
   - SQLite is ephemeral on Vercel
   - Consider upgrading to PostgreSQL for persistence

### Getting Help:

1. **Check function logs** in Vercel dashboard
2. **Test locally** with the same environment variables
3. **Use the environment validator**:
   ```bash
   python3 api/config/env_validator.py
   ```

## 🎯 Next Steps

1. **Monitor Performance**: Check function execution times
2. **Set up Alerts**: Configure Vercel notifications
3. **Scale if Needed**: Upgrade plan for higher limits
4. **Add Database**: Consider PostgreSQL for production
5. **Custom Domain**: Set up your own domain

## 📊 Expected Performance

- **Function Cold Start**: ~2-3 seconds
- **Warm Function**: ~200-500ms
- **API Response Time**: ~1-2 seconds
- **Memory Usage**: 256MB - 1GB per function
- **Concurrent Users**: Depends on Vercel plan

Your multi-agent portfolio analysis system is now ready for production! 🎉 