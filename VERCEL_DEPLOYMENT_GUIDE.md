# Vercel Deployment Guide - Hybrid Next.js + Python Serverless

## Overview

This guide covers deploying the Multi-Agent Portfolio Analysis System as a hybrid Next.js frontend with Python serverless functions on Vercel.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Vercel Platform                     │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Next.js)           │  Backend (Python 3.12)    │
│  ├── Static Assets            │  ├── /api/agents/         │
│  ├── Server Components        │  ├── /api/notifications/  │
│  ├── Client Components        │  ├── /api/scheduler/      │
│  └── Routing                  │  ├── /api/database/       │
│                                │  └── /api/supervisor.py   │
├─────────────────────────────────────────────────────────────┤
│                    External Services                        │
│  ├── PostgreSQL (Database)    │  ├── Redis (Cache)       │
│  ├── SMTP Email Service       │  ├── GitHub Actions      │
│  └── External Cron Service    │  └── Monitoring Tools    │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Node.js 18+**: For frontend development
3. **Python 3.12**: For serverless functions
4. **Git Repository**: Connected to GitHub
5. **Environment Variables**: See setup section below

## 1. Environment Variables Setup

### Required Variables

```bash
# Core Configuration
XAI_API_KEY=your_xai_api_key_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your_app_password
TO_EMAIL=recipient@example.com

# Optional (Production)
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://user:pass@host:port
CRON_SECRET=your_secure_random_string
API_SECRET_KEY=your_api_secret_key

# Configuration
ENVIRONMENT=production
DEFAULT_PORTFOLIO=AAPL,GOOGL,MSFT,AMZN,TSLA
HIGH_VOLATILITY_THRESHOLD=0.05
```

### Automated Setup

```bash
# Run the setup script
chmod +x setup-env.sh
./setup-env.sh

# Set up Vercel environment variables
./setup-vercel-env.sh
```

### Manual Vercel Setup

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to Settings → Environment Variables
4. Add each variable with appropriate scope:
   - **Production**: Live deployment
   - **Preview**: Pull request previews
   - **Development**: Local development

## 2. Project Structure

```
multi-agent-port-analysis/
├── frontend/                 # Next.js frontend
│   ├── src/
│   │   ├── pages/           # Next.js pages
│   │   ├── components/      # React components
│   │   ├── hooks/          # Custom hooks
│   │   ├── utils/          # Utility functions
│   │   └── types/          # TypeScript types
│   ├── public/             # Static assets
│   ├── package.json        # Frontend dependencies
│   └── next.config.js      # Next.js configuration
├── api/                    # Python serverless functions
│   ├── agents/             # AI agent functions
│   ├── notifications/      # Email handling
│   ├── scheduler/          # Cron management
│   ├── database/           # Storage management
│   └── supervisor.py       # Orchestration
├── vercel.json             # Vercel configuration
├── requirements.txt        # Python dependencies
├── .vercelignore          # Deployment exclusions
└── .github/workflows/     # GitHub Actions
```

## 3. Vercel Configuration

### vercel.json

```json
{
  "version": 2,
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
      "dest": "/api/agents/risk_agent.py"
    },
    {
      "src": "/_next/static/(.*)",
      "dest": "/frontend/_next/static/$1",
      "headers": {
        "Cache-Control": "public, max-age=31536000, immutable"
      }
    },
    {
      "src": "/",
      "dest": "/frontend/index.html"
    }
  ]
}
```

## 4. Deployment Process

### Option A: GitHub Integration (Recommended)

1. **Connect Repository**
   ```bash
   # Push to GitHub
   git add .
   git commit -m "Deploy hybrid Next.js + Python app"
   git push origin main
   ```

2. **Import to Vercel**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Configure build settings:
     - **Framework Preset**: Next.js
     - **Root Directory**: `./`
     - **Build Command**: `cd frontend && npm run build`
     - **Output Directory**: `frontend/.next`
     - **Install Command**: `cd frontend && npm install`

3. **Set Environment Variables**
   - Add all required environment variables
   - Set appropriate scopes (Production, Preview, Development)

### Option B: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

## 5. GitHub Actions Setup

### Required Secrets

Add these secrets to your GitHub repository:

```
Settings → Secrets and variables → Actions → New repository secret
```

**Required Secrets:**
- `VERCEL_TOKEN`: Vercel API token
- `VERCEL_ORG_ID`: Your Vercel organization ID
- `VERCEL_PROJECT_ID`: Your project ID
- `VERCEL_DEPLOYMENT_URL`: Your production URL
- `CRON_SECRET`: Secret for cron job authentication

**Optional Secrets:**
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `XAI_API_KEY`: xAI API key
- `SENDER_EMAIL`: Email sender address
- `SENDER_PASSWORD`: Email app password

### Get Vercel IDs

```bash
# Get organization ID
vercel teams list

# Get project ID
vercel projects list

# Get deployment URL
vercel domains list
```

## 6. Database Setup

### PostgreSQL (Production)

```bash
# Example using Railway
# 1. Sign up at railway.app
# 2. Create PostgreSQL database
# 3. Get connection string
# 4. Add to Vercel environment variables

DATABASE_URL=postgresql://user:pass@containers-us-west-xxx.railway.app:5432/railway
```

### Redis (Optional)

```bash
# Example using Redis Cloud
# 1. Sign up at redis.com
# 2. Create Redis database
# 3. Get connection string
# 4. Add to Vercel environment variables

REDIS_URL=redis://user:pass@redis-xxx.redislabs.com:12345
```

## 7. Cron Job Setup

### Option A: GitHub Actions (Recommended)

The cron workflow runs automatically every hour:

```yaml
# .github/workflows/cron.yml
on:
  schedule:
    - cron: '0 * * * *'  # Every hour
```

### Option B: External Cron Service

```bash
# Example using cron-job.org
curl -X POST "https://api.cron-job.org/jobs" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "job": {
      "url": "https://your-app.vercel.app/api/scheduler/cron",
      "schedule": {"hours": [-1], "minutes": [0]},
      "requestMethod": "POST",
      "requestBody": "{\"action\": \"check_jobs\", \"secret\": \"YOUR_CRON_SECRET\"}",
      "requestHeaders": [
        {"name": "Content-Type", "value": "application/json"},
        {"name": "X-Cron-Secret", "value": "YOUR_CRON_SECRET"}
      ]
    }
  }'
```

## 8. Testing Deployment

### Health Checks

```bash
# Test API endpoints
curl https://your-app.vercel.app/api/agents/risk
curl https://your-app.vercel.app/api/supervisor

# Test frontend
curl https://your-app.vercel.app/

# Test email notifications
curl -X POST https://your-app.vercel.app/api/notifications/email \
  -H "Content-Type: application/json" \
  -d '{"action": "test_config"}'
```

### Manual Testing

1. **Frontend**: Visit your deployment URL
2. **API Endpoints**: Test each agent endpoint
3. **Email System**: Send test notifications
4. **Cron Jobs**: Trigger manual analysis
5. **Storage**: Check data persistence

## 9. Monitoring and Maintenance

### Vercel Analytics

1. Go to your project dashboard
2. Enable Analytics
3. Monitor:
   - Function execution times
   - Error rates
   - Traffic patterns
   - Performance metrics

### Logging

```bash
# View function logs
vercel logs

# View real-time logs
vercel logs --follow

# View specific function logs
vercel logs --since 1h api/supervisor.py
```

### Performance Monitoring

```bash
# Check function performance
vercel inspect

# Monitor cold starts
vercel ls --meta

# Check deployment status
vercel ls
```

## 10. Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Check build logs
   vercel logs --since 1h
   
   # Local testing
   cd frontend && npm run build
   python -m py_compile api/supervisor.py
   ```

2. **Environment Variables**
   ```bash
   # List environment variables
   vercel env ls
   
   # Pull environment variables
   vercel env pull
   ```

3. **Function Timeouts**
   ```bash
   # Increase timeout in vercel.json
   "maxDuration": 60
   
   # Optimize function performance
   # Cache expensive operations
   # Use connection pooling
   ```

4. **Database Connection Issues**
   ```bash
   # Test connection
   curl -X POST https://your-app.vercel.app/api/storage \
     -H "Content-Type: application/json" \
     -d '{"action": "status"}'
   ```

5. **Email Configuration**
   ```bash
   # Test email setup
   curl -X POST https://your-app.vercel.app/api/notifications/email \
     -H "Content-Type: application/json" \
     -d '{"action": "test_config"}'
   ```

### Debug Commands

```bash
# Check deployment status
vercel ls --meta

# Inspect specific deployment
vercel inspect DEPLOYMENT_URL

# View function logs
vercel logs --since 1h

# Test local development
vercel dev
```

## 11. Production Optimization

### Performance

1. **Enable Caching**
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

2. **Optimize Images**
   ```javascript
   // next.config.js
   module.exports = {
     images: {
       domains: ['your-domain.com'],
       optimize: true
     }
   }
   ```

3. **Database Optimization**
   ```python
   # Use connection pooling
   # Implement query caching
   # Optimize database queries
   ```

### Security

1. **Environment Variables**
   ```bash
   # Never commit secrets
   echo ".env*" >> .gitignore
   
   # Use strong secrets
   openssl rand -hex 32
   ```

2. **API Security**
   ```python
   # Validate inputs
   # Rate limiting
   # Authentication
   ```

3. **CORS Configuration**
   ```python
   # Set appropriate origins
   CORS_ORIGINS = ["https://your-domain.com"]
   ```

## 12. Cost Optimization

### Function Optimization

```python
# Minimize cold starts
# Use connection pooling
# Cache expensive operations
# Optimize memory usage
```

### Database Costs

```bash
# Use read replicas
# Implement data archiving
# Optimize query performance
# Monitor usage patterns
```

### Monitoring Costs

```bash
# Track function usage
vercel usage

# Monitor bandwidth
vercel analytics

# Optimize function duration
vercel logs --since 1h
```

## 13. Scaling Considerations

### Horizontal Scaling

1. **Load Balancing**: Automatic with Vercel
2. **Edge Caching**: Built-in CDN
3. **Database Scaling**: Read replicas
4. **Queue Systems**: Redis/SQS for async processing

### Vertical Scaling

1. **Function Memory**: Increase if needed
2. **Database Resources**: Scale up connections
3. **Cache Size**: Optimize Redis usage
4. **Storage**: Monitor disk usage

## 14. Backup and Recovery

### Database Backups

```bash
# Automated backups
# Point-in-time recovery
# Cross-region replication
```

### Environment Backups

```bash
# Export environment variables
vercel env pull .env.backup

# Backup configuration
git tag -a v1.0.0 -m "Production release"
```

## 15. Support and Resources

### Documentation

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [Python on Vercel](https://vercel.com/docs/functions/serverless-functions/runtimes/python)

### Community

- [Vercel Discord](https://discord.gg/vercel)
- [Next.js Discord](https://discord.gg/nextjs)
- [GitHub Discussions](https://github.com/vercel/vercel/discussions)

### Support

- Vercel Pro Support
- GitHub Issues
- Community Forums

---

## Quick Start Checklist

- [ ] Clone repository
- [ ] Run `./setup-env.sh`
- [ ] Set up Vercel environment variables
- [ ] Deploy to Vercel
- [ ] Configure GitHub Actions secrets
- [ ] Set up database (optional)
- [ ] Configure cron jobs
- [ ] Test all endpoints
- [ ] Monitor performance
- [ ] Set up alerts

🚀 **Your hybrid Next.js + Python serverless application is now deployed on Vercel!** 