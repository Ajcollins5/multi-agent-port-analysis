# Enhanced Vercel Serverless Setup

## Overview

The Multi-Agent Portfolio Analysis System has been enhanced with a comprehensive serverless architecture designed for Vercel deployment. This setup wraps all multi-agent logic in individual serverless functions, implements proper email notifications, handles database operations with fallbacks, and provides cron-compatible scheduling.

## Architecture

### Serverless Functions

#### 1. Agent Functions (`/api/agents/`)

**Risk Agent** (`/api/agents/risk_agent.py`)
- Analyzes stock volatility and risk metrics
- Triggers email alerts for high-impact events (>5% volatility)
- Endpoints: `analyze_stock`, `impact_level`, `portfolio_risk`

**News Agent** (`/api/agents/news_agent.py`)
- Performs sentiment analysis and news impact assessment
- Simulates news sentiment based on price movements
- Endpoints: `analyze_sentiment`, `market_impact`, `impact_estimate`

**Event Sentinel** (`/api/agents/event_sentinel.py`)
- Monitors portfolio-wide events and correlations
- Detects volume spikes and cross-ticker patterns
- Endpoints: `detect_events`, `event_summary`, `correlations`

**Knowledge Curator** (`/api/agents/knowledge_curator.py`)
- Manages knowledge base quality and identifies gaps
- Refines insights and tracks evolution patterns
- Endpoints: `quality_assessment`, `identify_gaps`, `refine_insight`

#### 2. Support Services (`/api/`)

**Email Handler** (`/api/notifications/email_handler.py`)
- Handles all email notifications with templated messages
- Supports high-impact alerts, portfolio risks, daily summaries
- Uses environment variables for SMTP configuration

**Cron Handler** (`/api/scheduler/cron_handler.py`)
- Manages background scheduling compatible with Vercel
- Supports portfolio analysis, risk assessment, event monitoring
- Includes job history and execution tracking

**Storage Manager** (`/api/database/storage_manager.py`)
- Handles data persistence with fallback hierarchy
- Primary: External DB (PostgreSQL) → Cache (Redis) → In-memory
- Manages insights, events, and knowledge evolution data

**Supervisor** (`/api/supervisor.py`)
- Orchestrates multi-agent analysis workflows
- Synthesizes results from multiple agents
- Coordinates notifications and storage operations

## Database Strategy

### Vercel Ephemeral Environment Handling

The system uses a three-tier storage approach:

1. **External Database** (Production): PostgreSQL with connection pooling
2. **Redis Cache** (Optional): For fast data retrieval and session storage
3. **In-Memory Fallback** (Always): Thread-safe storage for development/fallback

### Schema Design

```sql
-- Insights table
CREATE TABLE insights (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    insight TEXT NOT NULL,
    agent VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Events table
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    ticker VARCHAR(10),
    message TEXT,
    severity VARCHAR(20),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Knowledge evolution table
CREATE TABLE knowledge_evolution (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    evolution_type VARCHAR(50),
    previous_insight TEXT,
    refined_insight TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
```

## Email Notification System

### Templates

- **High Impact Alert**: Triggered by >5% volatility
- **Portfolio Risk Alert**: Portfolio-wide risk assessments
- **Daily Summary**: Analysis completion reports
- **System Alert**: Error notifications and system status

### Configuration

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your_app_password
TO_EMAIL=recipient@example.com
```

## Scheduling & Cron

### Vercel-Compatible Scheduling

Since Vercel doesn't support traditional cron jobs, the system uses:

1. **External Cron Services**: GitHub Actions, Render Cron, or Cron-job.org
2. **Webhook Triggers**: External services call `/api/scheduler/cron`
3. **Manual Triggers**: Dashboard-based job execution

### Example Cron Configuration

```yaml
# GitHub Actions (.github/workflows/cron.yml)
name: Portfolio Analysis Cron
on:
  schedule:
    - cron: '0 */1 * * *'  # Every hour
jobs:
  trigger-analysis:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Analysis
        run: |
          curl -X POST https://your-app.vercel.app/api/scheduler/cron \
            -H "Content-Type: application/json" \
            -H "X-Cron-Secret: ${{ secrets.CRON_SECRET }}" \
            -d '{"action": "check_jobs", "secret": "${{ secrets.CRON_SECRET }}"}'
```

## Environment Variables

### Required Variables

```bash
# Core Configuration
XAI_API_KEY=your_xai_api_key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your_app_password
TO_EMAIL=recipient@example.com

# Optional (for production scaling)
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://user:pass@host:port
CRON_SECRET=your_secure_secret
```

### Vercel Environment Setup

1. Go to Vercel Dashboard → Project Settings → Environment Variables
2. Add all required variables
3. Set environment to "Production", "Preview", or "Development"

## API Endpoints

### Agent Endpoints

```bash
# Risk Agent
POST /api/agents/risk
{
  "action": "analyze_stock",
  "ticker": "AAPL"
}

# News Agent
POST /api/agents/news
{
  "action": "analyze_sentiment",
  "ticker": "AAPL"
}

# Event Sentinel
POST /api/agents/events
{
  "action": "detect_events",
  "portfolio": ["AAPL", "GOOGL"]
}

# Knowledge Curator
POST /api/agents/knowledge
{
  "action": "quality_assessment"
}
```

### Service Endpoints

```bash
# Email Notifications
POST /api/notifications/email
{
  "action": "high_impact_alert",
  "data": {
    "ticker": "AAPL",
    "current_price": 150.00,
    "volatility": 0.06,
    "impact_level": "HIGH"
  }
}

# Cron Scheduler
POST /api/scheduler/cron
{
  "action": "schedule_portfolio",
  "interval_minutes": 60,
  "secret": "your_cron_secret"
}

# Storage Manager
POST /api/storage
{
  "action": "store_insight",
  "ticker": "AAPL",
  "insight": "Risk analysis shows high volatility",
  "agent": "RiskAgent"
}
```

## Deployment

### 1. Vercel Deployment

```bash
# Deploy to Vercel
vercel --prod

# Set environment variables
vercel env add XAI_API_KEY
vercel env add SMTP_SERVER
vercel env add SENDER_EMAIL
vercel env add SENDER_PASSWORD
vercel env add TO_EMAIL
```

### 2. Database Setup (Production)

```bash
# PostgreSQL (recommended)
# Set DATABASE_URL environment variable

# Redis (optional)
# Set REDIS_URL environment variable
```

### 3. Cron Setup

```bash
# Option 1: GitHub Actions
# Add .github/workflows/cron.yml

# Option 2: External Service
# Configure webhook to call /api/scheduler/cron

# Option 3: Vercel Cron (when available)
# Use vercel.json cron configuration
```

## Usage Examples

### Analyze Single Stock

```bash
curl -X POST https://your-app.vercel.app/api/supervisor \
  -H "Content-Type: application/json" \
  -d '{
    "action": "analyze_ticker",
    "ticker": "AAPL",
    "analysis_type": "comprehensive"
  }'
```

### Analyze Portfolio

```bash
curl -X POST https://your-app.vercel.app/api/supervisor \
  -H "Content-Type: application/json" \
  -d '{
    "action": "analyze_portfolio",
    "portfolio": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
  }'
```

### Test Email Configuration

```bash
curl -X POST https://your-app.vercel.app/api/notifications/email \
  -H "Content-Type: application/json" \
  -d '{
    "action": "test_config"
  }'
```

## Monitoring & Maintenance

### Health Checks

```bash
# Check all agents
GET /api/agents/risk
GET /api/agents/news
GET /api/agents/events
GET /api/agents/knowledge

# Check services
GET /api/notifications/email
GET /api/scheduler/cron
GET /api/storage
```

### Storage Management

```bash
# View storage status
POST /api/storage
{
  "action": "status"
}

# Clear storage (maintenance)
POST /api/storage
{
  "action": "clear_storage",
  "storage_type": "insights"
}
```

## Performance Optimizations

### Database Optimization

1. **Connection Pooling**: Use PostgreSQL connection pooling
2. **Query Optimization**: Index on ticker and timestamp columns
3. **Data Retention**: Implement automatic cleanup for old data

### Caching Strategy

1. **Redis Caching**: Cache frequent queries and results
2. **Function Caching**: Cache expensive calculations
3. **CDN Integration**: Use Vercel's CDN for static assets

### Scaling Considerations

1. **Database Scaling**: Use read replicas for heavy queries
2. **External Services**: Consider dedicated email service (SendGrid, Mailgun)
3. **Message Queues**: Use Redis or cloud messaging for async processing

## Security

### API Security

```bash
# Use environment variables
XAI_API_KEY=secret_key
CRON_SECRET=secure_random_string

# Validate webhook signatures
# Rate limiting (Vercel automatic)
# CORS configuration
```

### Data Security

```bash
# Encrypt sensitive data
# Use HTTPS only
# Validate all inputs
# Sanitize database queries
```

## Troubleshooting

### Common Issues

1. **Email Failures**: Check SMTP configuration and app passwords
2. **Database Timeouts**: Verify connection strings and network access
3. **Cron Jobs Not Running**: Check webhook URLs and secrets
4. **Memory Limits**: Optimize functions for Vercel's limits

### Debug Endpoints

```bash
# Check agent status
GET /api/agents/risk

# Test storage
POST /api/storage {"action": "status"}

# Test email
POST /api/notifications/email {"action": "test_config"}
```

This enhanced setup provides a production-ready, scalable serverless architecture for the Multi-Agent Portfolio Analysis System, with proper error handling, notifications, and database management suitable for Vercel deployment. 