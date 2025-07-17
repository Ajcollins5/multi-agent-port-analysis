# Multi-Agent Portfolio Analysis System

A comprehensive multi-agent system for portfolio analysis powered by Grok 4 AI with knowledge evolution capabilities.

## Features

### 🚀 **Multi-Agent Analysis**
- **RiskAgent**: Analyzes stock volatility, beta, and risk metrics
- **NewsAgent**: Performs news sentiment analysis with impact estimation
- **Supervisor**: Orchestrates agents and synthesizes insights
- **EventSentinel**: Monitors portfolio-wide events and cross-ticker correlations
- **KnowledgeCurator**: Manages knowledge base quality and identifies analysis gaps
- **Powered by Grok 4**: Advanced reasoning with xAI's Grok model

### 🧠 **Knowledge Evolution**
- **Persistent Learning**: Agents learn from previous analyses
- **Historical Context**: Past insights inform new analysis
- **Pattern Recognition**: Identifies trends and evolution in understanding
- **Refined Insights**: Uses Grok's reasoning to improve insights over time

### 📊 **Web Dashboard (Streamlit)**
- **Portfolio Overview**: Real-time portfolio metrics and volatility tracking
- **Ad-hoc Analysis**: Analyze any ticker with Grok agents
- **Knowledge Evolution**: Visualize how understanding evolves over time
- **Event Monitoring**: Real-time alerts and event tracking
- **Background Scheduling**: Automated portfolio analysis

### 💾 **Data Management**
- **SQLite Database**: Persistent storage for insights and knowledge
- **Event Detection**: Automatic alerts for high volatility events (>5%)
- **Export Capabilities**: Download insights as CSV files

### 📧 **Email Notifications**
- **High Impact Alerts**: Automatic email notifications for volatility >5%
- **Analysis Completion**: Email summaries after Grok analysis
- **Daily Reports**: Portfolio analysis completion notifications
- **Configurable Recipients**: Hardcoded email addresses for alerts

### 🧪 **Comprehensive Testing**
- **Tool Testing**: Unit tests for all agent tools (fetch_stock_data, etc.)
- **Integration Testing**: End-to-end analysis workflow testing
- **Mock Data Testing**: Comprehensive mock scenarios for reliability
- **Agent Testing**: Tests for EventSentinel and KnowledgeCurator tools
- **Email Testing**: SMTP notification testing with mocks

### 🚀 **Production Deployment**
- **Vercel Ready**: Configured for serverless deployment
- **Environment Variables**: Secure API key and email configuration
- **Serverless Functions**: Optimized for scalability and performance
- **Static Frontend**: Interactive HTML dashboard with real-time updates
- **API Endpoints**: RESTful API for programmatic access

## Installation

### Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd multi-agent-port-analysis
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up xAI API Key**
- Get your API key from [x.ai/api](https://x.ai/api)
- Update the `XAI_API_KEY` in `main.py` (line 9)

4. **Configure Email Notifications**
- Update email settings in `main.py` (lines 22-29)
- For Gmail: Use App Password (not regular password)
- Go to: Google Account > Security > 2-Step Verification > App passwords
- Update `sender_email`, `sender_password`, and `to_email` variables

### Vercel Deployment

1. **Prepare for Vercel**
- Ensure all files are in the repository root
- The `vercel.json` configuration file is already included
- The `api/` directory contains serverless functions

2. **Deploy to Vercel**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

3. **Set Environment Variables in Vercel Dashboard**
- Go to your Vercel project dashboard
- Navigate to Settings > Environment Variables
- Add the following variables:

```
XAI_API_KEY=your_xai_api_key_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
TO_EMAIL=recipient@example.com
```

4. **Verify Deployment**
- Your app will be available at: `https://your-project.vercel.app`
- Test the API endpoints: `https://your-project.vercel.app/api/main`
- Access the dashboard: `https://your-project.vercel.app/`

## Usage

### Local Development

#### CLI Interface
```bash
python main.py
```

#### Web Dashboard (Streamlit)
```bash
streamlit run app.py
```

Then navigate to `http://localhost:8501` in your browser.

#### Run Tests
```bash
python run_tests.py
```

Or run specific test classes:
```bash
python run_tests.py TestStockDataTools
python run_tests.py TestEventSentinelTools
python run_tests.py TestKnowledgeCuratorTools
```

### Production Deployment (Vercel)

#### Web Dashboard
- Visit: `https://your-project.vercel.app`
- Interactive HTML dashboard with real-time portfolio analysis
- Analyze individual tickers or entire portfolio
- View portfolio metrics and high-impact events

#### API Endpoints
- **Main API**: `https://your-project.vercel.app/api/main`
- **Dashboard API**: `https://your-project.vercel.app/api/app`

#### API Usage Examples

**Analyze a ticker:**
```bash
curl -X POST https://your-project.vercel.app/api/main \
  -H "Content-Type: application/json" \
  -d '{"action": "analyze_ticker", "ticker": "AAPL"}'
```

**Get portfolio analysis:**
```bash
curl -X POST https://your-project.vercel.app/api/main \
  -H "Content-Type: application/json" \
  -d '{"action": "analyze_portfolio"}'
```

**Get dashboard data:**
```bash
curl -X POST https://your-project.vercel.app/api/app \
  -H "Content-Type: application/json" \
  -d '{"action": "dashboard"}'
```

## Dashboard Features

### 📈 **Portfolio Dashboard**
- Real-time portfolio metrics
- Volatility tracking and impact levels
- Recent insights display
- Interactive charts and visualizations

### 🔍 **Ad-hoc Analysis**
- Analyze any ticker symbol
- Grok-powered multi-agent analysis
- Add tickers to portfolio
- Quick analysis buttons for popular stocks

### 🧠 **Knowledge Evolution**
- Historical insight tracking
- Evolution pattern analysis
- Knowledge timeline visualization
- Refined insight monitoring

### ⚡ **Events & Alerts**
- Real-time event monitoring
- High volatility alerts
- System status updates
- Auto-refresh capabilities

### ⚙️ **Settings**
- Portfolio management
- Database export/import
- System configuration
- Background scheduling controls

## Impact Levels

- **🔴 High Impact**: Volatility > 5%
- **🟡 Medium Impact**: Volatility 2-5%
- **🟢 Low Impact**: Volatility < 2%

## Background Scheduling

The system supports automated analysis with configurable intervals:
- **Default**: Hourly analysis
- **Customizable**: Modify scheduling in settings
- **Event-driven**: Automatic alerts for significant events

## Agent Tools

### EventSentinel Tools
- **detect_portfolio_events**: Monitors portfolio-wide risk and correlations
- **generate_event_summary**: Creates comprehensive event analysis reports

### KnowledgeCurator Tools
- **curate_knowledge_quality**: Assesses knowledge base quality and coverage
- **identify_knowledge_gaps**: Finds analysis gaps and recommends improvements

### Core Agent Tools
- **fetch_stock_data**: Retrieves market data with volatility detection
- **determine_impact_level**: Classifies risk levels (low/medium/high)
- **store_insight**: Manages knowledge base storage
- **refine_insight**: Evolves insights using Grok reasoning

## Database Schema

```sql
CREATE TABLE insights (
    ticker TEXT,
    insight TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RiskAgent     │    │   NewsAgent     │    │   Supervisor    │
│                 │    │                 │    │                 │
│ • Volatility    │    │ • Sentiment     │    │ • Orchestration │
│ • Beta Analysis │    │ • Impact Levels │    │ • Synthesis     │
│ • Risk Metrics  │    │ • News Analysis │    │ • Coordination  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  EventSentinel  │    │KnowledgeCurator │    │  Grok 4 Model   │
│                 │    │                 │    │                 │
│ • Event Monitor │    │ • Knowledge QA  │    │ • Advanced AI   │
│ • Correlations  │    │ • Gap Analysis  │    │ • Reasoning     │
│ • Portfolio Risk│    │ • Curation      │    │ • Synthesis     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ SQLite Database │
                    │                 │
                    │ • Insights      │
                    │ • Knowledge     │
                    │ • Evolution     │
                    └─────────────────┘
```

## Deployment Structure

### Vercel Files
- **vercel.json**: Vercel configuration with Python runtime
- **api/main.py**: Serverless functions for core analysis
- **api/app.py**: Dashboard API endpoints
- **index.html**: Frontend dashboard interface
- **environment.config.example**: Environment variables template

### Local Development Files
- **main.py**: Full multi-agent system with CLI
- **app.py**: Streamlit web dashboard
- **test_tools.py**: Comprehensive test suite
- **run_tests.py**: Test runner script

### Configuration Files
- **requirements.txt**: Python dependencies
- **vercel.json**: Vercel deployment configuration
- **environment.config.example**: Environment variables template

## Environment Variables

### Required for Vercel Deployment
```
XAI_API_KEY=your_xai_api_key_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
TO_EMAIL=recipient@example.com
```

### Optional Configuration
```
DATABASE_URL=postgresql://... (for production database)
ENVIRONMENT=production
DEBUG=false
```

## Vercel Deployment Setup

### Step-by-Step Environment Variable Configuration

⚠️ **Critical Warning**: Missing environment variables will cause runtime failures in the multi-agent system. All required variables must be properly configured.

#### 1. Access Vercel Dashboard
1. Log into your [Vercel Dashboard](https://vercel.com/dashboard)
2. Navigate to your project
3. Click on **Settings** tab
4. Select **Environment Variables** from the left sidebar

#### 2. Add XAI_API_KEY (Required)
1. Click **Add New** environment variable
2. **Key**: `XAI_API_KEY`
3. **Value**: Your Grok API key value (e.g., `xai-aBJmxv3MlpQOUfnjamcRs2VOB3kGpJBlEHY2QstvR7SP9CP2BZWYzFVcOxvaGLlBf6OQX4g0J6g72IBD`)
4. **Environments**: Select all (Production, Preview, Development)
5. ✅ **Check "Sensitive"** to encrypt the value
6. Click **Save**

#### 3. Add Email Configuration (Required)
Add each of these variables following the same process:

**SMTP Server Configuration:**
- **Key**: `SMTP_SERVER`
- **Value**: `smtp.gmail.com` (or your email provider's SMTP server)
- **Environments**: All
- **Sensitive**: ✅ Recommended

**SMTP Port:**
- **Key**: `SMTP_PORT`
- **Value**: `587` (or your provider's port)
- **Environments**: All
- **Sensitive**: No

**Sender Email:**
- **Key**: `SENDER_EMAIL`
- **Value**: Your email address (e.g., `your-email@gmail.com`)
- **Environments**: All
- **Sensitive**: ✅ Recommended

**Email Password:**
- **Key**: `SENDER_PASSWORD`
- **Value**: Your app password (not regular password)
- **Environments**: All
- **Sensitive**: ✅ **Required**

**Recipient Email:**
- **Key**: `TO_EMAIL`
- **Value**: Alert recipient email (e.g., `recipient@example.com`)
- **Environments**: All
- **Sensitive**: ✅ Recommended

#### 4. Add Optional Configuration Variables
Based on your requirements from `api/environment.example`:

**Database Configuration (Optional):**
- **Key**: `DATABASE_URL`
- **Value**: `postgresql://user:password@host:port/database`
- **Sensitive**: ✅ **Required**

- **Key**: `REDIS_URL`
- **Value**: `redis://user:password@host:port`
- **Sensitive**: ✅ **Required**

**System Configuration:**
- **Key**: `VERCEL_URL`
- **Value**: `https://your-project.vercel.app`
- **Sensitive**: No

- **Key**: `CRON_SECRET`
- **Value**: Generate a secure random string
- **Sensitive**: ✅ **Required**

- **Key**: `ENVIRONMENT`
- **Value**: `production`
- **Sensitive**: No

**Portfolio Configuration:**
- **Key**: `DEFAULT_PORTFOLIO`
- **Value**: `AAPL,GOOGL,MSFT,AMZN,TSLA`
- **Sensitive**: No

**Threshold Configuration:**
- **Key**: `HIGH_VOLATILITY_THRESHOLD`
- **Value**: `0.05`
- **Sensitive**: No

- **Key**: `API_SECRET_KEY`
- **Value**: Generate a secure random string
- **Sensitive**: ✅ **Required**

#### 5. Alternative: CLI Method for Legacy Secrets
If you prefer using the Vercel CLI (not recommended for new projects):

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Add secrets (legacy method)
vercel secrets add xai-api-key "your_xai_api_key_value"
vercel secrets add smtp-server "smtp.gmail.com"
vercel secrets add sender-email "your-email@gmail.com"
vercel secrets add sender-password "your_app_password"
```

**Note**: The dashboard method is preferred as it's more secure and easier to manage.

#### 6. Verification Steps
1. **Check All Variables**: Ensure all required variables are added
2. **Test Deployment**: Deploy your project and test functionality
3. **Monitor Logs**: Check Vercel function logs for any missing variable errors
4. **Test Email Alerts**: Verify email notifications work correctly
5. **Test API Endpoints**: Ensure all multi-agent system features work

#### 7. Common Issues and Solutions

**Missing XAI_API_KEY:**
- **Error**: `No API key configured`
- **Solution**: Add `XAI_API_KEY` with your Grok API key

**Email Configuration Issues:**
- **Error**: `SMTP authentication failed`
- **Solution**: Use app password for Gmail, not regular password

**Database Connection Issues:**
- **Error**: `Database connection failed`
- **Solution**: Verify `DATABASE_URL` format and credentials

**Runtime Failures:**
- **Error**: `Environment variable not found`
- **Solution**: Ensure all variables are added to all environments (Production, Preview, Development)

### Gmail App Password Setup
For Gmail SMTP configuration:
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to **Security** > **2-Step Verification**
3. Scroll down to **App passwords**
4. Generate a new app password for "Mail"
5. Use this app password (not your regular password) for `SENDER_PASSWORD`

### Security Best Practices
- ✅ Always mark sensitive variables as "Sensitive" in Vercel
- ✅ Use strong, unique passwords for all credentials
- ✅ Never commit environment variables to version control
- ✅ Regularly rotate API keys and passwords
- ✅ Use database connection strings with proper authentication
- ✅ Monitor Vercel function logs for security issues

**⚠️ Critical**: The multi-agent system requires all environment variables to be properly configured. Missing or incorrect variables will cause runtime failures, broken email notifications, and analysis errors.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions, please open an issue in the GitHub repository.

