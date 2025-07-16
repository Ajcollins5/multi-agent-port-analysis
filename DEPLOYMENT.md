# Vercel Deployment Guide

## 🚀 Multi-Agent Portfolio Analysis System - Vercel Deployment

This guide walks you through deploying the Multi-Agent Portfolio Analysis System to Vercel.

## Prerequisites

- [Vercel account](https://vercel.com)
- [xAI API key](https://x.ai/api)
- Gmail account with App Password (for email notifications)
- Git repository with the project

## 📋 Pre-Deployment Checklist

### 1. **Verify File Structure**
```
multi-agent-port-analysis/
├── vercel.json                    ✓ Vercel configuration
├── index.html                     ✓ Frontend dashboard
├── api/
│   ├── main.py                   ✓ Main API functions
│   └── app.py                    ✓ Dashboard API
├── requirements.txt               ✓ Python dependencies
├── environment.config.example     ✓ Environment variables template
└── README.md                     ✓ Documentation
```

### 2. **Environment Variables Setup**
Prepare the following environment variables:

```bash
# xAI Grok API
XAI_API_KEY=your_xai_api_key_here

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_gmail_app_password
TO_EMAIL=recipient@example.com
```

### 3. **Gmail App Password Setup**
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification
3. Go to App passwords
4. Generate password for "Mail"
5. Use this password as `SENDER_PASSWORD`

## 🛠️ Deployment Steps

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```

### Step 3: Deploy the Project
```bash
# From your project directory
vercel

# Follow the prompts:
# ? Set up and deploy "multi-agent-port-analysis"? [Y/n] Y
# ? Which scope do you want to deploy to? [Select your account]
# ? Link to existing project? [Y/n] n
# ? What's your project's name? multi-agent-portfolio-analysis
# ? In which directory is your code located? ./
```

### Step 4: Set Environment Variables
In your Vercel dashboard:

1. Go to your project
2. Navigate to **Settings** > **Environment Variables**
3. Add each variable:

| Variable | Value | Environment |
|----------|-------|-------------|
| `XAI_API_KEY` | your_xai_api_key_here | Production |
| `SMTP_SERVER` | smtp.gmail.com | Production |
| `SMTP_PORT` | 587 | Production |
| `SENDER_EMAIL` | your_email@gmail.com | Production |
| `SENDER_PASSWORD` | your_gmail_app_password | Production |
| `TO_EMAIL` | recipient@example.com | Production |

### Step 5: Redeploy with Environment Variables
```bash
vercel --prod
```

## 🧪 Testing Your Deployment

### 1. **Test the Dashboard**
Visit: `https://your-project.vercel.app`

Expected: Interactive dashboard with portfolio metrics

### 2. **Test API Endpoints**

**Main API Status:**
```bash
curl https://your-project.vercel.app/api/main
```

**Dashboard API Status:**
```bash
curl https://your-project.vercel.app/api/app
```

**Analyze a ticker:**
```bash
curl -X POST https://your-project.vercel.app/api/main \
  -H "Content-Type: application/json" \
  -d '{"action": "analyze_ticker", "ticker": "AAPL"}'
```

**Portfolio analysis:**
```bash
curl -X POST https://your-project.vercel.app/api/main \
  -H "Content-Type: application/json" \
  -d '{"action": "analyze_portfolio"}'
```

### 3. **Test Email Notifications**
```bash
curl -X POST https://your-project.vercel.app/api/main \
  -H "Content-Type: application/json" \
  -d '{"action": "send_test_email", "subject": "Test", "message": "Test message"}'
```

## 🔧 Troubleshooting

### Common Issues

#### 1. **Environment Variables Not Working**
- **Problem**: API returns errors about missing configuration
- **Solution**: 
  - Verify environment variables are set in Vercel dashboard
  - Redeploy with `vercel --prod`
  - Check variable names match exactly

#### 2. **Email Notifications Failing**
- **Problem**: Email sending returns errors
- **Solution**:
  - Verify Gmail App Password is correct
  - Check SMTP settings
  - Ensure 2-Step Verification is enabled

#### 3. **API Timeout Errors**
- **Problem**: Functions timeout after 10 seconds
- **Solution**: 
  - Reduce analysis complexity
  - Optimize yfinance requests
  - Consider upgrading Vercel plan

#### 4. **Import Errors**
- **Problem**: Python packages not found
- **Solution**:
  - Verify `requirements.txt` is complete
  - Check for typos in package names
  - Ensure compatible versions

#### 5. **CORS Issues**
- **Problem**: Frontend can't access API
- **Solution**:
  - Verify API routes in `vercel.json`
  - Check frontend API calls use correct paths
  - Ensure proper request methods

### Debug Mode

Enable debug logging by adding to environment variables:
```
DEBUG=true
```

Then check function logs in Vercel dashboard.

## 📊 Performance Optimization

### 1. **Function Optimization**
- Use `progress=False` in yfinance calls
- Implement caching for repeated requests
- Optimize database queries

### 2. **Frontend Optimization**
- Minimize API calls
- Implement loading states
- Use efficient data structures

### 3. **Email Optimization**
- Batch notifications
- Use templates for consistent formatting
- Implement rate limiting

## 🔐 Security Best Practices

### 1. **Environment Variables**
- Never commit API keys to git
- Use different keys for development/production
- Rotate keys regularly

### 2. **API Security**
- Validate all input parameters
- Implement rate limiting
- Use HTTPS only

### 3. **Email Security**
- Use App Passwords instead of regular passwords
- Validate email addresses
- Implement spam protection

## 📈 Monitoring & Maintenance

### 1. **Vercel Dashboard**
- Monitor function invocations
- Check error rates
- Review performance metrics

### 2. **Email Notifications**
- Monitor email delivery rates
- Check spam folders
- Verify recipient addresses

### 3. **API Usage**
- Monitor xAI API usage
- Track request patterns
- Optimize for cost efficiency

## 🚀 Production Readiness

### Checklist Before Going Live:

- [ ] All environment variables configured
- [ ] Email notifications tested
- [ ] API endpoints respond correctly
- [ ] Frontend dashboard loads properly
- [ ] Error handling implemented
- [ ] Performance optimized
- [ ] Security measures in place
- [ ] Monitoring configured
- [ ] Documentation updated
- [ ] Team access configured

## 📞 Support

For deployment issues:
1. Check Vercel function logs
2. Review environment variable configuration
3. Test API endpoints individually
4. Verify email settings
5. Check GitHub issues for similar problems

## 📚 Additional Resources

- [Vercel Python Documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [xAI API Documentation](https://x.ai/api)
- [Gmail App Passwords Guide](https://support.google.com/accounts/answer/185833)

---

**Deployment Complete!** Your Multi-Agent Portfolio Analysis System is now live on Vercel. 🎉 