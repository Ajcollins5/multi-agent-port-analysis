# Streamlit Cloud Deployment Guide

## 🚀 **Multi-Agent Portfolio Analysis - Streamlit Native Deployment**

This guide covers deploying your Streamlit application to both **Render** and **Streamlit Community Cloud**, which natively support Streamlit applications.

---

## 📋 **Prerequisites**

1. **GitHub Repository**: Your code must be in a public GitHub repository
2. **API Keys**: 
   - xAI API key from [x.ai/api](https://x.ai/api)
   - Gmail App Password for email notifications
3. **Database** (Optional): PostgreSQL for production persistence
4. **Redis** (Optional): For caching and performance

---

## 🎯 **Option 1: Streamlit Community Cloud (RECOMMENDED)**

### **Advantages:**
- ✅ **Native Streamlit support** - No configuration needed
- ✅ **Free tier available** - Perfect for prototyping
- ✅ **Automatic deployments** - GitHub integration
- ✅ **Built-in secrets management** - Secure environment variables
- ✅ **Zero configuration** - Works out of the box

### **Step-by-Step Deployment:**

#### **1. Prepare Your Repository**

Ensure your repository has these files:
```
multi-agent-port-analysis/
├── app.py                     # Main Streamlit application
├── main.py                    # Core analysis logic
├── requirements.txt           # Dependencies
├── .streamlit/
│   ├── config.toml           # Streamlit configuration
│   └── secrets.toml          # Environment variables template
├── README.md                 # Documentation
└── LICENSE                   # License file
```

#### **2. Sign Up for Streamlit Community Cloud**

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"

#### **3. Configure Your App**

1. **Repository**: Select your GitHub repository
2. **Branch**: Choose `main` (or your default branch)
3. **Main file path**: `app.py`
4. **App URL**: Choose your custom URL (e.g., `portfolio-analysis`)

#### **4. Set Up Secrets**

In your Streamlit Cloud dashboard:

1. Go to **Settings** > **Secrets**
2. Add the following secrets:

```toml
# xAI Configuration
XAI_API_KEY = "your_xai_api_key_here"

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_gmail_app_password"
TO_EMAIL = "recipient@example.com"

# Optional: Database Configuration
DATABASE_URL = "postgresql://user:password@host:port/database"

# Feature Flags
ENABLE_BACKGROUND_ANALYSIS = "true"
ENABLE_EMAIL_NOTIFICATIONS = "true"
```

#### **5. Deploy**

1. Click **Deploy**
2. Wait for deployment to complete (2-5 minutes)
3. Your app will be available at `https://your-app-name.streamlit.app`

#### **6. Verify Deployment**

Test these features:
- ✅ Portfolio dashboard loads
- ✅ Stock analysis works
- ✅ Email notifications function
- ✅ Background scheduling operates

---

## 🔧 **Option 2: Render Deployment**

### **Advantages:**
- ✅ **Full control** - Custom build and start commands
- ✅ **Persistent storage** - Disk mounting for databases
- ✅ **Background workers** - Separate processes for scheduling
- ✅ **Custom domains** - Professional URLs
- ✅ **Database services** - Managed PostgreSQL and Redis

### **Step-by-Step Deployment:**

#### **1. Prepare Render Configuration**

Your repository should have:
```
multi-agent-port-analysis/
├── render.yaml              # Render service configuration
├── app.py                   # Main Streamlit application
├── requirements.txt         # Dependencies
├── .streamlit/config.toml   # Streamlit configuration
└── worker.py               # Background worker (optional)
```

#### **2. Sign Up for Render**

1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account
3. Connect your repository

#### **3. Configure Services**

The `render.yaml` file defines:

- **Web Service**: Streamlit application
- **Redis Service**: Caching layer
- **PostgreSQL Service**: Database
- **Worker Service**: Background processing (optional)

#### **4. Set Environment Variables**

In your Render dashboard:

1. Go to **Environment**
2. Add these variables:

```bash
XAI_API_KEY=your_xai_api_key_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_gmail_app_password
TO_EMAIL=recipient@example.com
PYTHONUNBUFFERED=1
```

#### **5. Deploy Services**

1. **Deploy from GitHub**: Connect your repository
2. **Auto-deploy**: Enable automatic deployments
3. **Monitor**: Check deployment logs

#### **6. Access Your Application**

- **Web Service**: `https://your-app-name.onrender.com`
- **Database**: Accessible via `DATABASE_URL` environment variable
- **Redis**: Available at `REDIS_URL`

---

## 🔄 **Code Adjustments for Cloud Deployment**

### **1. Update Environment Variable Access**

```python
# cloud_config.py
import os
import streamlit as st

def get_config(key, default=None):
    """Get configuration from environment variables or Streamlit secrets"""
    # Try Streamlit secrets first (for Streamlit Cloud)
    try:
        return st.secrets.get(key, default)
    except:
        # Fall back to environment variables (for Render)
        return os.environ.get(key, default)

# Usage in your app
XAI_API_KEY = get_config("XAI_API_KEY")
SMTP_SERVER = get_config("SMTP_SERVER", "smtp.gmail.com")
SENDER_EMAIL = get_config("SENDER_EMAIL")
```

### **2. Database Connection for Cloud**

```python
# database_cloud.py
import os
import sqlite3
import psycopg2
from urllib.parse import urlparse
import streamlit as st

def get_database_connection():
    """Get database connection for cloud deployment"""
    database_url = get_config("DATABASE_URL")
    
    if database_url and database_url.startswith("postgresql://"):
        # Use PostgreSQL for production
        parsed = urlparse(database_url)
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password
        )
        return conn, "postgresql"
    else:
        # Use SQLite for development
        conn = sqlite3.connect('knowledge.db')
        return conn, "sqlite"

# Usage in your app
conn, db_type = get_database_connection()
```

### **3. Caching for Performance**

```python
# caching.py
import streamlit as st
import redis
import json
from datetime import datetime, timedelta

@st.cache_data
def get_stock_data_cached(ticker):
    """Cached stock data retrieval"""
    return fetch_stock_data(ticker)

def setup_redis_cache():
    """Set up Redis caching for cloud deployment"""
    redis_url = get_config("REDIS_URL")
    if redis_url:
        try:
            return redis.from_url(redis_url, decode_responses=True)
        except:
            st.warning("Redis connection failed, using in-memory cache")
            return None
    return None

# Usage
redis_client = setup_redis_cache()
```

### **4. Error Handling and Logging**

```python
# error_handling.py
import streamlit as st
import logging
from datetime import datetime

# Configure logging for cloud deployment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def handle_error(error, context=""):
    """Handle errors gracefully in cloud deployment"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    error_msg = f"Error at {timestamp}: {str(error)}"
    
    # Log error
    logging.error(f"{context}: {error_msg}")
    
    # Display user-friendly error
    st.error(f"An error occurred: {context}")
    st.error(f"Details: {str(error)}")
    
    # Optional: Send error notification
    if get_config("ENABLE_ERROR_NOTIFICATIONS") == "true":
        send_error_notification(error_msg, context)

def send_error_notification(error_msg, context):
    """Send error notification via email"""
    try:
        send_email(
            subject=f"🚨 Application Error: {context}",
            body=f"Error occurred in Multi-Agent Portfolio Analysis:\n\n{error_msg}",
            to_email=get_config("TO_EMAIL")
        )
    except:
        logging.error("Failed to send error notification")
```

---

## 📊 **Performance Optimization for Cloud**

### **1. Streamlit Performance Settings**

```python
# Add to your app.py
import streamlit as st

# Configure Streamlit for cloud deployment
st.set_page_config(
    page_title="Multi-Agent Portfolio Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-username/multi-agent-port-analysis',
        'Report a bug': "https://github.com/your-username/multi-agent-port-analysis/issues",
        'About': "Multi-Agent Portfolio Analysis System powered by Grok 4"
    }
)

# Enable caching for better performance
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_portfolio_data():
    """Load portfolio data with caching"""
    return get_portfolio_summary()

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def analyze_ticker_cached(ticker):
    """Analyze ticker with caching"""
    return analyze_ticker(ticker)
```

### **2. Background Processing**

```python
# worker.py - Optional background worker for Render
import time
import schedule
from main import daily_analysis
from cloud_config import get_config

def run_background_worker():
    """Run background analysis worker"""
    interval = int(get_config("ANALYSIS_INTERVAL", "3600"))  # Default 1 hour
    
    schedule.every(interval).seconds.do(daily_analysis)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    run_background_worker()
```

---

## 🔒 **Security Best Practices**

### **1. Environment Variables**

```python
# Never hardcode secrets
XAI_API_KEY = get_config("XAI_API_KEY")  # ✅ Good
# XAI_API_KEY = "xai-xxxxx"             # ❌ Bad

# Use secure defaults
SMTP_PORT = int(get_config("SMTP_PORT", "587"))
ENABLE_DEBUG = get_config("DEBUG", "false").lower() == "true"
```

### **2. Input Validation**

```python
def validate_ticker(ticker):
    """Validate ticker input"""
    if not ticker or len(ticker) > 10:
        raise ValueError("Invalid ticker symbol")
    return ticker.upper().strip()

def validate_email(email):
    """Validate email address"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError("Invalid email address")
    return email
```

---

## 🚀 **Deployment Comparison**

| Feature | Streamlit Community Cloud | Render |
|---------|---------------------------|---------|
| **Cost** | Free (with limits) | $7/month starter |
| **Setup Time** | 5 minutes | 15 minutes |
| **Custom Domain** | ❌ No | ✅ Yes |
| **Database** | ❌ No | ✅ PostgreSQL |
| **Background Workers** | ❌ No | ✅ Yes |
| **Persistent Storage** | ❌ No | ✅ Yes |
| **Scaling** | Auto | Manual |
| **Monitoring** | Basic | Advanced |

---

## 📈 **Monitoring and Maintenance**

### **1. Health Checks**

```python
# Add to your app.py
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        conn, db_type = get_database_connection()
        conn.close()
        
        # Test API availability
        test_ticker = "AAPL"
        data = yf.download(test_ticker, period="1d", progress=False)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": db_type,
            "api_access": not data.empty
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
```

### **2. Usage Analytics**

```python
# Add to your app.py
def track_usage(action, ticker=None):
    """Track application usage"""
    usage_data = {
        "action": action,
        "ticker": ticker,
        "timestamp": datetime.now().isoformat(),
        "user_agent": st.context.headers.get("User-Agent", ""),
        "ip": st.context.remote_ip if hasattr(st.context, 'remote_ip') else "unknown"
    }
    
    # Log usage
    logging.info(f"Usage: {json.dumps(usage_data)}")
    
    # Optional: Send to analytics service
    if get_config("ENABLE_ANALYTICS") == "true":
        send_analytics(usage_data)
```

---

## 🎯 **Final Recommendations**

### **For Beginners:**
1. **Start with Streamlit Community Cloud** - Easy setup and free
2. **Use basic features** - Portfolio analysis and email notifications
3. **Upgrade later** - Move to Render when you need more features

### **For Production:**
1. **Use Render** - Better performance and features
2. **Set up PostgreSQL** - Persistent data storage
3. **Enable monitoring** - Health checks and logging
4. **Configure custom domain** - Professional appearance

### **For Enterprise:**
1. **Consider dedicated hosting** - Better control and security
2. **Implement authentication** - User management
3. **Add load balancing** - Handle high traffic
4. **Use external databases** - Scalable data storage

---

## 📞 **Support and Troubleshooting**

### **Common Issues:**

1. **Import Errors**: Update `requirements.txt` with correct versions
2. **Memory Issues**: Use caching and optimize data processing
3. **Timeout Errors**: Increase timeout settings in cloud configuration
4. **Database Connection**: Check DATABASE_URL and credentials

### **Getting Help:**

- **Streamlit Community**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **Render Support**: [render.com/docs](https://render.com/docs)
- **GitHub Issues**: Create issues in your repository

---

Your multi-agent portfolio analysis system is now ready for cloud deployment! 🚀 