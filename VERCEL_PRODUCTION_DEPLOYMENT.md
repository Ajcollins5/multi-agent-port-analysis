# Vercel Production Deployment Guide

## 🚀 Complete Step-by-Step Production Deployment

This guide walks you through deploying the Multi-Agent Portfolio Analysis System to Vercel production with full configuration, monitoring, and verification.

---

## Prerequisites Checklist

- [ ] GitHub repository with the migrated code
- [ ] Vercel account (free or pro)
- [ ] Domain name (optional, for custom domain)
- [ ] Email credentials (Gmail app password recommended)
- [ ] API keys (xAI API key)
- [ ] Database URLs (PostgreSQL, Redis - optional)

---

## Step 1: Repository Preparation

### 1.1 Verify Repository Structure

```bash
# Ensure your repository has the correct structure
ls -la
```

Expected structure:
```
multi-agent-port-analysis/
├── frontend/                 # Next.js frontend
├── api/                     # Python serverless functions
├── vercel.json              # Vercel configuration
├── requirements.txt         # Python dependencies
├── .vercelignore           # Deployment exclusions
├── .github/workflows/      # GitHub Actions
└── README.md
```

### 1.2 Test Local Setup

```bash
# Run the environment setup script
./setup-env.sh

# Test the application locally
cd frontend
npm install
npm run dev

# Test API endpoints
python -m pytest test_vercel.py -v
```

---

## Step 2: Vercel Project Setup

### 2.1 Create New Vercel Project

1. **Go to Vercel Dashboard**
   - Visit [vercel.com](https://vercel.com)
   - Sign in or create account
   - Click "New Project"

2. **Import Repository**
   - Click "Import Git Repository"
   - Select your GitHub repository
   - Click "Import"

3. **Configure Project Settings**
   ```
   Project Name: multi-agent-portfolio-analysis
   Framework Preset: Next.js
   Root Directory: ./
   Build Command: cd frontend && npm run build
   Output Directory: frontend/.next
   Install Command: cd frontend && npm install
   ```

4. **Advanced Build Settings**
   ```
   Node.js Version: 18.x
   Environment Variables: (will add in next step)
   ```

### 2.2 Link to GitHub Repository

1. **Enable GitHub Integration**
   - Go to Project Settings → Git
   - Ensure "Connected Git Repository" shows your repo
   - Enable "Automatic Deployments"

2. **Configure Branch Settings**
   ```
   Production Branch: main
   Preview Branches: develop, feature/*
   ```

---

## Step 3: Environment Variables Configuration

### 3.1 Secure Environment Variable Setup

**⚠️ CRITICAL: Never commit secrets to version control**

1. **Go to Project Settings → Environment Variables**

2. **Add Core Configuration Variables**

   ```bash
   # Core API Configuration
   XAI_API_KEY=your_xai_api_key_here
   # Get from: https://x.ai/api
   
   # Email Configuration (SMTP)
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your_gmail_app_password
   TO_EMAIL=recipient@example.com
   
   # Security
   CRON_SECRET=your_secure_random_32_char_string
   API_SECRET_KEY=your_api_secret_key_here
   
   # Configuration
   ENVIRONMENT=production
   DEFAULT_PORTFOLIO=AAPL,GOOGL,MSFT,AMZN,TSLA
   HIGH_VOLATILITY_THRESHOLD=0.05
   ```

3. **Add Optional Production Variables**

   ```bash
   # Database (Optional - for scaling)
   DATABASE_URL=postgresql://user:password@host:port/database
   REDIS_URL=redis://user:password@host:port
   
   # Vercel Configuration
   VERCEL_URL=https://your-project-name.vercel.app
   ```

4. **Set Variable Scopes**
   - **Production**: Live deployment
   - **Preview**: Pull request previews  
   - **Development**: Local development

### 3.2 Gmail App Password Setup

1. **Enable 2-Factor Authentication**
   - Go to Google Account settings
   - Security → 2-Step Verification
   - Enable if not already enabled

2. **Generate App Password**
   - Go to Security → App passwords
   - Select "Mail" and your device
   - Copy the 16-character password
   - Use this as `SENDER_PASSWORD`

### 3.3 Generate Secure Secrets

```bash
# Generate secure random strings
openssl rand -hex 32  # For CRON_SECRET
openssl rand -hex 32  # For API_SECRET_KEY
```

---

## Step 4: Custom Domain Configuration (Optional)

### 4.1 Add Custom Domain

1. **Go to Project Settings → Domains**
2. **Add Domain**
   ```
   Domain: your-domain.com
   Redirect: www.your-domain.com → your-domain.com
   ```

3. **Configure DNS**
   - Add CNAME record: `your-domain.com` → `cname.vercel-dns.com`
   - Add A record: `your-domain.com` → `76.76.19.19`

### 4.2 SSL Certificate

- Vercel automatically provides SSL certificates
- Certificate will be issued within minutes
- Verify HTTPS is working: `https://your-domain.com`

---

## Step 5: Deployment Configuration

### 5.1 Verify vercel.json Configuration

```json
{
  "version": 2,
  "name": "multi-agent-portfolio-analysis",
  "functions": {
    "api/agents/risk_agent.py": {
      "runtime": "python3.12",
      "maxDuration": 30
    },
    "api/supervisor.py": {
      "runtime": "python3.12", 
      "maxDuration": 60
    }
  },
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/api/agents/risk",
      "dest": "/api/agents/risk_agent.py",
      "methods": ["GET", "POST"]
    },
    {
      "src": "/_next/static/(.*)",
      "dest": "/frontend/_next/static/$1",
      "headers": {
        "Cache-Control": "public, max-age=31536000, immutable"
      }
    }
  ]
}
```

### 5.2 Deploy to Production

1. **Manual Deployment**
   ```bash
   # Install Vercel CLI
   npm install -g vercel@latest
   
   # Login to Vercel
   vercel login
   
   # Deploy to production
   vercel --prod
   ```

2. **Automatic Deployment**
   ```bash
   # Push to main branch
   git add .
   git commit -m "Deploy to production"
   git push origin main
   ```

---

## Step 6: GitHub Actions Integration

### 6.1 Configure GitHub Secrets

Go to GitHub Repository → Settings → Secrets and Variables → Actions

Add the following secrets:

```bash
VERCEL_TOKEN=your_vercel_token_here
VERCEL_ORG_ID=your_vercel_org_id
VERCEL_PROJECT_ID=your_vercel_project_id
VERCEL_DEPLOYMENT_URL=https://your-project.vercel.app
CRON_SECRET=your_cron_secret_here
```

### 6.2 Get Vercel IDs

```bash
# Get Vercel token
vercel login
vercel whoami

# Get organization ID
vercel teams list

# Get project ID  
vercel projects list

# Get deployment URL
vercel ls
```

### 6.3 Enable Automatic Deployments

The GitHub Actions workflows will automatically:
- Run tests on pull requests
- Deploy to preview on PR
- Deploy to production on main branch
- Run scheduled portfolio analysis

---

## Step 7: Monitoring and Logging Setup

### 7.1 Enable Vercel Analytics

1. **Go to Project Dashboard**
2. **Analytics Tab**
3. **Enable Analytics**
4. **Configure Metrics**
   - Function invocations
   - Error rates
   - Response times
   - Traffic patterns

### 7.2 Function Logs Monitoring

1. **Real-time Logs**
   ```bash
   # View live logs
   vercel logs --follow
   
   # View specific function logs
   vercel logs api/supervisor.py --since 1h
   
   # View error logs
   vercel logs --since 1h | grep ERROR
   ```

2. **Log Retention**
   - Free: 1 day retention
   - Pro: 7 days retention
   - Enterprise: 30 days retention

### 7.3 Error Monitoring Setup

1. **Built-in Error Tracking**
   - Automatic error collection
   - Error rate monitoring
   - Performance metrics

2. **Custom Error Monitoring** (Optional)
   ```bash
   # Install Sentry (optional)
   npm install @sentry/nextjs
   
   # Add to environment variables
   SENTRY_DSN=your_sentry_dsn_here
   ```

---

## Step 8: Performance Optimization

### 8.1 Function Optimization

1. **Cold Start Optimization**
   - Keep functions warm with scheduled calls
   - Optimize import statements
   - Use connection pooling

2. **Caching Strategy**
   ```json
   {
     "headers": [
       {
         "source": "/_next/static/(.*)",
         "headers": [
           {
             "key": "Cache-Control",
             "value": "public, max-age=31536000, immutable"
           }
         ]
       }
     ]
   }
   ```

### 8.2 Database Optimization

1. **Connection Pooling**
   - Use PostgreSQL connection pooling
   - Implement Redis for caching
   - Optimize query performance

2. **Scaling Considerations**
   - Read replicas for heavy queries
   - Data archiving strategies
   - Query optimization

---

## Step 9: Security Configuration

### 9.1 API Security

1. **Rate Limiting**
   ```python
   # Implement in Python functions
   from functools import wraps
   import time
   
   def rate_limit(max_calls=100, window=3600):
       # Rate limiting implementation
       pass
   ```

2. **Input Validation**
   ```python
   # Validate all inputs
   def validate_ticker(ticker):
       if not ticker or len(ticker) > 10:
           raise ValueError("Invalid ticker")
       return ticker.upper()
   ```

### 9.2 Environment Security

1. **Secret Rotation**
   - Rotate API keys regularly
   - Update email passwords
   - Regenerate CRON_SECRET

2. **Access Control**
   - Limit GitHub Actions permissions
   - Use principle of least privilege
   - Monitor access logs

---

## Step 10: Post-Deployment Verification

### 10.1 Automated Testing

```bash
# Run integration tests
export VERCEL_DEPLOYMENT_URL=https://your-project.vercel.app
python -m pytest test_vercel.py -v

# Test specific workflows
python test_vercel.py
```

### 10.2 Manual Verification Checklist

- [ ] **Frontend Accessibility**
  - [ ] Main page loads: `https://your-domain.com`
  - [ ] All routes work: `/analysis`, `/knowledge`, `/events`, `/scheduler`, `/settings`
  - [ ] Static assets load correctly
  - [ ] Mobile responsiveness

- [ ] **API Endpoints**
  - [ ] Risk agent: `GET/POST /api/agents/risk`
  - [ ] News agent: `GET/POST /api/agents/news`
  - [ ] Event sentinel: `GET/POST /api/agents/events`
  - [ ] Knowledge curator: `GET/POST /api/agents/knowledge`
  - [ ] Supervisor: `GET/POST /api/supervisor`
  - [ ] Storage: `GET/POST /api/storage`
  - [ ] Notifications: `GET/POST /api/notifications/email`
  - [ ] Scheduler: `GET/POST /api/scheduler/cron`

- [ ] **Email System**
  - [ ] Configuration test passes
  - [ ] Test emails are received
  - [ ] Templates render correctly

- [ ] **Storage System**
  - [ ] Data persistence works
  - [ ] Insights are stored and retrieved
  - [ ] Fallback mechanisms work

### 10.3 Performance Verification

```bash
# Test response times
curl -w "%{time_total}\n" https://your-domain.com/api/agents/risk

# Test function execution
vercel logs --since 1h | grep duration

# Monitor error rates
vercel logs --since 1h | grep error
```

---

## Step 11: Portfolio Analysis Workflow Simulation

### 11.1 Complete Workflow Test

```python
# Test script for complete workflow
import requests
import json

BASE_URL = "https://your-domain.com"
TEST_PORTFOLIO = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]

def test_complete_workflow():
    # Step 1: Individual stock analysis
    print("🔍 Step 1: Analyzing individual stocks...")
    for ticker in TEST_PORTFOLIO:
        response = requests.post(f"{BASE_URL}/api/supervisor", json={
            "action": "analyze_ticker",
            "ticker": ticker,
            "analysis_type": "comprehensive"
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ {ticker}: {result.get('synthesis', {}).get('overall_risk', 'UNKNOWN')}")
        else:
            print(f"   ❌ {ticker}: {response.status_code}")
    
    # Step 2: Portfolio analysis
    print("📊 Step 2: Portfolio-wide analysis...")
    response = requests.post(f"{BASE_URL}/api/supervisor", json={
        "action": "analyze_portfolio", 
        "portfolio": TEST_PORTFOLIO
    })
    
    if response.status_code == 200:
        result = response.json()
        portfolio_risk = result.get('portfolio_synthesis', {}).get('portfolio_risk', 'UNKNOWN')
        print(f"   ✓ Portfolio risk: {portfolio_risk}")
    else:
        print(f"   ❌ Portfolio analysis failed: {response.status_code}")
    
    # Step 3: Check notifications
    print("📧 Step 3: Testing notifications...")
    response = requests.post(f"{BASE_URL}/api/notifications/email", json={
        "action": "test_config"
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✓ Email system: {result.get('success', 'UNKNOWN')}")
    else:
        print(f"   ❌ Email test failed: {response.status_code}")
    
    # Step 4: Verify data persistence
    print("💾 Step 4: Checking data persistence...")
    response = requests.post(f"{BASE_URL}/api/storage", json={
        "action": "get_insights",
        "limit": 10
    })
    
    if response.status_code == 200:
        result = response.json()
        insight_count = len(result.get('insights', []))
        print(f"   ✓ Insights stored: {insight_count}")
    else:
        print(f"   ❌ Storage check failed: {response.status_code}")
    
    print("🎉 Workflow simulation completed!")

if __name__ == "__main__":
    test_complete_workflow()
```

### 11.2 Cron Job Verification

```bash
# Test cron endpoint
curl -X POST https://your-domain.com/api/scheduler/cron \
  -H "Content-Type: application/json" \
  -H "X-Cron-Secret: your_cron_secret" \
  -d '{"action": "check_jobs", "secret": "your_cron_secret"}'

# Verify GitHub Actions cron is working
# Check: Repository → Actions → Portfolio Analysis Cron
```

---

## Step 12: Production Maintenance

### 12.1 Regular Health Checks

Create a monitoring script:

```python
# health_check.py
import requests
import time
from datetime import datetime

def health_check():
    endpoints = [
        "/api/agents/risk",
        "/api/agents/news", 
        "/api/agents/events",
        "/api/agents/knowledge",
        "/api/supervisor",
        "/api/storage",
        "/api/notifications/email"
    ]
    
    base_url = "https://your-domain.com"
    
    for endpoint in endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}{endpoint}", timeout=30)
            end_time = time.time()
            
            status = "✓" if response.status_code == 200 else "❌"
            duration = end_time - start_time
            
            print(f"{status} {endpoint}: {response.status_code} ({duration:.2f}s)")
            
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    print(f"Health check completed at {datetime.now()}")

if __name__ == "__main__":
    health_check()
```

### 12.2 Backup and Recovery

1. **Environment Variable Backup**
   ```bash
   # Export environment variables
   vercel env pull .env.production.backup
   
   # Store securely (not in version control)
   ```

2. **Database Backups**
   ```bash
   # If using PostgreSQL
   pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
   
   # If using Redis
   redis-cli --rdb dump_$(date +%Y%m%d).rdb
   ```

### 12.3 Scaling Monitoring

```bash
# Monitor usage
vercel usage

# Check function performance
vercel logs --since 24h | grep "Duration:"

# Monitor costs
vercel billing
```

---

## Step 13: Troubleshooting Guide

### 13.1 Common Issues

1. **Build Failures**
   ```bash
   # Check build logs
   vercel logs --since 1h
   
   # Test locally
   cd frontend && npm run build
   python -m py_compile api/supervisor.py
   ```

2. **Function Timeouts**
   ```bash
   # Increase timeout in vercel.json
   "maxDuration": 60
   
   # Optimize function performance
   ```

3. **Environment Variable Issues**
   ```bash
   # List all environment variables
   vercel env ls
   
   # Pull current environment
   vercel env pull .env.current
   ```

4. **Database Connection Issues**
   ```bash
   # Test database connection
   curl -X POST https://your-domain.com/api/storage \
     -H "Content-Type: application/json" \
     -d '{"action": "status"}'
   ```

### 13.2 Performance Issues

1. **Slow Response Times**
   - Check function logs for bottlenecks
   - Optimize database queries
   - Implement caching

2. **High Error Rates**
   - Review error logs
   - Check API rate limits
   - Verify environment variables

### 13.3 Support Resources

- **Vercel Documentation**: https://vercel.com/docs
- **Vercel Discord**: https://discord.gg/vercel
- **GitHub Issues**: Your repository issues
- **Vercel Support**: support@vercel.com (Pro/Enterprise)

---

## ✅ Production Deployment Checklist

- [ ] Repository structure verified
- [ ] Vercel project created and configured
- [ ] Environment variables securely added
- [ ] Custom domain configured (if applicable)
- [ ] GitHub Actions secrets configured
- [ ] Monitoring and logging enabled
- [ ] Performance optimization implemented
- [ ] Security measures in place
- [ ] Post-deployment verification completed
- [ ] Portfolio analysis workflow tested
- [ ] Cron jobs verified
- [ ] Health checks implemented
- [ ] Backup procedures established
- [ ] Troubleshooting guide reviewed

---

## 🎉 Congratulations!

Your Multi-Agent Portfolio Analysis System is now deployed to Vercel production with:

- ✅ **Hybrid Next.js + Python serverless architecture**
- ✅ **Automated deployments via GitHub Actions**
- ✅ **Comprehensive monitoring and logging**
- ✅ **Production-grade security**
- ✅ **Scalable infrastructure**
- ✅ **Automated portfolio analysis**

**Your deployment is live at**: `https://your-domain.com`

**Monitor your deployment**: 
- Dashboard: https://vercel.com/dashboard
- Logs: `vercel logs --follow`
- Analytics: Project dashboard → Analytics

**Need help?** Refer to the troubleshooting guide or contact support. 