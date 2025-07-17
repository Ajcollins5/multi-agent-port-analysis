# Vercel Configuration Documentation

## Overview
This document explains the `vercel.json` configuration for the Multi-Agent Portfolio Analysis System, including the migration from the legacy `routes` array to the modern `rewrites` configuration.

## Configuration Structure

### 1. Serverless Function Configuration
```json
"functions": {
  "api/app.py": {
    "runtime": "python3.12",
    "memory": 1024,
    "maxDuration": 60
  },
  // ... other functions
}
```

**Purpose**: Defines Python serverless functions with runtime configuration. Each function corresponds to a Python file in the `api/` directory.

**Key Points**:
- All API functions use Python 3.12 runtime
- Main Flask app (`api/app.py`) gets more memory (1024MB) and longer timeout (60s)
- Agent functions have shorter timeouts (30s) for optimal performance

### 2. Modern Routing Configuration (Rewrites)

#### Migration from Routes to Rewrites
**IMPORTANT**: Previously used `routes` array which conflicts with modern Vercel configuration. Migrated to `rewrites` for compatibility with `redirects` and `headers` as per Vercel documentation.

#### API Routing
```json
{
  "source": "/api/(.*)",
  "destination": "/api/app.py"
}
```
- **Central API routing**: All `/api/*` requests go to the main Flask app
- The Flask app acts as a central routing hub for the multi-agent system
- Individual agent functions are called internally by the Flask app

#### Static Asset Routing
```json
{
  "source": "/_next/static/(.*)",
  "destination": "/frontend/_next/static/$1"
},
{
  "source": "/_next/image(.*)",
  "destination": "/frontend/_next/image$1"
}
```
- **Next.js static assets**: Optimized routing for built Next.js assets
- **Image optimization**: Handles Next.js image optimization API

#### Static File Routing
```json
{
  "source": "/favicon.ico",
  "destination": "/favicon.ico"
}
```
- **Corrected routing**: Static files route to root level (no `/frontend/public/` needed)
- Handles: `favicon.ico`, `robots.txt`, `sitemap.xml`, `manifest.json`

#### Frontend Page Routing
```json
{
  "source": "/dashboard/(.*)",
  "destination": "/frontend/dashboard/$1"
}
```
- **Next.js application pages**: Routes frontend pages to Next.js build output
- Covers: dashboard, analysis, knowledge, events, scheduler, settings

#### Fallback Routing
```json
{
  "source": "/",
  "destination": "/index.html"
},
{
  "source": "/(.*)",
  "destination": "/frontend/$1"
}
```
- **Root path**: Serves the main landing page (`index.html`)
- **Fallback**: All other requests route to frontend build output

### 3. Redirect Configuration
```json
"redirects": [
  {
    "source": "/app",
    "destination": "/",
    "permanent": false
  },
  {
    "source": "/streamlit",
    "destination": "/",
    "permanent": true
  }
]
```
- **Legacy route handling**: Manages URL migrations from old application structure
- **Streamlit migration**: Permanent redirect from old Streamlit-based interface

### 4. Headers Configuration
```json
"headers": [
  {
    "source": "/api/(.*)",
    "headers": [
      {
        "key": "Access-Control-Allow-Origin",
        "value": "*"
      }
    ]
  }
]
```
- **CORS headers**: Enables cross-origin requests for API endpoints
- **Cache optimization**: Long-term caching for static assets (`max-age=31536000`)
- **Security headers**: Proper handling of authentication tokens (`X-Cron-Secret`)

### 5. Environment Variables
```json
"env": {
  "XAI_API_KEY": "@xai_api_key",
  "SMTP_SERVER": "@smtp_server",
  // ... other secrets
}
```
- **Vercel secrets**: References to encrypted environment variables
- **Runtime configuration**: Used by serverless functions at runtime
- **Security**: Sensitive data stored as Vercel secrets, not in code

### 6. Build Configuration
```json
"build": {
  "env": {
    "PYTHON_VERSION": "3.12",
    "NODE_VERSION": "18"
  }
},
"installCommand": "cd frontend && npm install",
"buildCommand": "cd frontend && npm run build",
"outputDirectory": "frontend/.next"
```
- **Runtime versions**: Python 3.12 for API, Node 18 for frontend
- **Build process**: Builds Next.js frontend, outputs to `.next` directory
- **Installation**: Installs frontend dependencies only

### 7. Deployment Settings
```json
"regions": ["iad1", "sfo1"],
"github": {
  "enabled": true,
  "silent": true
}
```
- **Multi-region deployment**: East Coast (iad1) and West Coast (sfo1)
- **GitHub integration**: Automatic deployments from repository
- **Silent mode**: Reduces GitHub commit noise

## Compliance with Vercel Documentation

### ✅ What We Follow
1. **No conflicting keys**: Removed `routes` array to avoid conflicts with `rewrites`, `redirects`, and `headers`
2. **Modern routing**: Uses `rewrites` for URL rewriting, `redirects` for permanent/temporary redirects
3. **Proper function configuration**: Each serverless function properly configured with runtime and limits
4. **Environment security**: All sensitive data stored as Vercel secrets

### ❌ What We Avoid
1. **Legacy routes array**: Conflicts with modern configuration
2. **Inline comments**: JSON doesn't support comments (documentation kept separate)
3. **Hardcoded secrets**: All sensitive data properly referenced as secrets

## File Cross-Reference

### API Files
- `api/app.py`: Main Flask application (verified exists, 580 lines)
- `api/agents/`: Individual agent modules (all verified to exist)
- `api/notifications/`: Email handling (exists)
- `api/scheduler/`: Cron job handling (exists)
- `api/database/`: Storage management (exists)

### Frontend Files
- `frontend/`: Next.js application directory (verified)
- `frontend/.next/`: Build output directory (verified)
- `index.html`: Root landing page (verified, 235 lines)

### Static Files
- Static files route to root level (no `/frontend/public/` structure found)
- Corrected routing to avoid 404 errors

## Testing Status
- **Configuration validation**: JSON syntax validated ✅
- **Route simulation**: All key paths tested ✅
- **File existence**: All referenced files verified ✅
- **Compliance check**: No conflicting keys found ✅

## Deployment Ready
The configuration is now fully compliant with Vercel documentation and ready for production deployment. 