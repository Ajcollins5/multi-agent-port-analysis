# Vercel Deployment Guide with Debugging

## Overview
This guide provides step-by-step instructions for deploying the multi-agent portfolio analysis app to Vercel, including debugging steps and troubleshooting.

## ✅ Configuration Updates Applied

### 1. vercel.json Updates
- ✅ Added `"ignoreCommand": "exit 0"` to bypass build checks
- ✅ Configured Python 3.12 runtime for all functions
- ✅ Set up proper routing for API endpoints
- ✅ Environment variable references configured

### 2. requirements.txt Updates
- ✅ Enabled `pyautogen==0.1.15` for multi-agent framework
- ✅ Enabled `redis==5.0.1` for enhanced storage
- ✅ All critical dependencies (flask, yfinance, pandas, numpy, requests) present

### 3. Removed Legacy Files
- ✅ Deleted `ignore-build.sh` (replaced by direct `exit 0` command)
- ✅ Repository is clean and ready for deployment

## 🚀 Deployment Steps

### Phase 1: Environment Setup
1. **Log into Vercel Dashboard**
   - Go to https://vercel.com/dashboard
   - Connect your GitHub account if not already connected

2. **Import Project**
   - Click "Add New..." → "Project"
   - Select "Import Git Repository"
   - Choose your GitHub repository: `multi-agent-port-analysis`

### Phase 2: Configuration
3. **Configure Environment Variables**
   ```bash
   # Required variables (set these in Vercel dashboard)
   XAI_API_KEY=your_xai_api_key_here
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_app_password
   TO_EMAIL=recipient@email.com
   
   # Optional but recommended
   DATABASE_URL=your_database_url
   REDIS_URL=your_redis_url
   CRON_SECRET=your_cron_secret
   API_SECRET_KEY=your_api_secret
   DEFAULT_PORTFOLIO=AAPL,GOOGL,MSFT,TSLA,AMZN
   HIGH_VOLATILITY_THRESHOLD=0.05
   ENVIRONMENT=production
   ```

4. **Build Settings**
   - Framework Preset: `Other`
   - Build Command: `cd frontend && npm install && npm run build`
   - Output Directory: `frontend/.next`
   - Install Command: `cd frontend && npm install`

### Phase 3: Deployment
5. **Deploy Project**
   - Click "Deploy"
   - Monitor build logs for any errors
   - Wait for deployment to complete

6. **Test Deployment**
   - Run the debug script with your deployed URL:
   ```bash
   python3 deploy_debug.py --url https://your-app.vercel.app
   ```

## 🔧 Debugging and Troubleshooting

### Common Issues and Solutions

#### 1. Build Failures
**Issue**: Build process fails during npm install or build
**Solution**: 
- Check that `frontend/package.json` exists and has correct dependencies
- Verify Node.js version compatibility (should be 18.x)
- Review build logs in Vercel dashboard for specific errors

#### 2. Function Timeout Errors
**Issue**: Serverless functions timeout after 10 seconds
**Solution**:
- Increase `maxDuration` in `vercel.json` for heavy functions
- Optimize API endpoint code for faster response times
- Consider breaking down large operations into smaller chunks

#### 3. Environment Variable Issues
**Issue**: Missing environment variables causing 403 errors
**Solution**:
- Double-check all required environment variables are set in Vercel dashboard
- Verify variable names match exactly (case-sensitive)
- Test locally with `.env` file first

#### 4. API Endpoint Not Found (404)
**Issue**: API routes return 404 errors
**Solution**:
- Verify `vercel.json` routing configuration
- Check that API files exist in correct paths
- Ensure proper file structure in `api/` directory

#### 5. Python Import Errors
**Issue**: Missing Python dependencies
**Solution**:
- Verify `requirements.txt` has all necessary dependencies
- Check Python version compatibility (using 3.12)
- Review function logs in Vercel dashboard

## 📊 Debug Script Usage

### Local Testing
```bash
# Test current configuration
python3 deploy_debug.py

# Test specific URL
python3 deploy_debug.py --url https://your-app.vercel.app

# Verbose output
python3 deploy_debug.py --verbose
```

### Debug Script Checks
The debug script verifies:
- ✅ Vercel configuration validity
- ✅ Python requirements completeness
- ✅ Git repository status
- ✅ Environment variable presence
- ✅ API endpoint accessibility

## 🚨 Error Response Actions

### If Deployment Fails
1. **Capture Full Error Output**
   - Copy complete build logs from Vercel dashboard
   - Save to `deployment_error_log.txt`
   - Include timestamp and specific error messages

2. **Run Debug Script**
   ```bash
   python3 deploy_debug.py > debug_output.txt 2>&1
   ```

3. **Check Configuration**
   - Verify `vercel.json` syntax with JSON validator
   - Confirm all files referenced in config exist
   - Review environment variables

4. **Incremental Debugging**
   - Try deploying with minimal configuration first
   - Gradually add functions and routes
   - Test each component individually

### If Runtime Errors Occur
1. **Check Function Logs**
   - Go to Vercel dashboard → Functions tab
   - Review real-time logs for errors
   - Look for Python traceback messages

2. **Test API Endpoints**
   - Use browser or curl to test endpoints directly
   - Check response status codes and messages
   - Verify proper CORS headers

3. **Monitor Performance**
   - Check function execution times
   - Monitor memory usage
   - Review concurrent request handling

## 📝 Deployment Checklist

### Pre-Deployment
- [ ] Repository is clean (no uncommitted changes)
- [ ] All environment variables configured
- [ ] `vercel.json` configured with `ignoreCommand: "exit 0"`
- [ ] `requirements.txt` has all dependencies
- [ ] Debug script passes all tests

### During Deployment
- [ ] Monitor build logs for errors
- [ ] Verify all functions deploy successfully
- [ ] Check routing configuration
- [ ] Test environment variable access

### Post-Deployment
- [ ] Run debug script against deployed URL
- [ ] Test all API endpoints
- [ ] Verify email functionality
- [ ] Check real-time features
- [ ] Monitor function performance

## 🎯 Success Criteria

### Deployment Success Indicators
- ✅ Build completes without errors
- ✅ All functions deploy successfully
- ✅ API endpoints return 200 status codes
- ✅ Environment variables accessible
- ✅ No runtime errors in function logs

### Performance Benchmarks
- Response time < 2 seconds for API calls
- Function cold start < 5 seconds
- Memory usage < 512MB per function
- Zero timeout errors

## 📞 Support and Resources

### Vercel Documentation
- [Vercel Functions Guide](https://vercel.com/docs/functions)
- [Python Runtime](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Environment Variables](https://vercel.com/docs/projects/environment-variables)

### Debug Resources
- Use `deploy_debug.py` for comprehensive testing
- Check `deployment_debug_report.json` for detailed results
- Review Vercel function logs for runtime issues

### Emergency Rollback
If deployment fails catastrophically:
1. Go to Vercel dashboard → Deployments
2. Find last working deployment
3. Click "Promote to Production"
4. Investigate issues in staging environment

---

**Note**: The `ignoreCommand: "exit 0"` configuration will bypass Vercel's build checks, ensuring deployment proceeds regardless of detected changes. This is useful for troubleshooting deployment issues but should be used carefully in production environments. 