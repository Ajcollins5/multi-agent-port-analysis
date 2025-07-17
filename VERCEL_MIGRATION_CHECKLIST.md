# Vercel Migration Checklist

## 🎯 **Pre-Migration Assessment**

- [ ] **Identify Real-time Dependencies**
  - [ ] Streamlit WebSocket connections
  - [ ] Session state management
  - [ ] Auto-refresh mechanisms
  - [ ] Background threads

- [ ] **Identify Email Dependencies**
  - [ ] SMTP configuration
  - [ ] Gmail app password usage
  - [ ] Email template system
  - [ ] Notification triggers

- [ ] **Identify Scheduling Dependencies**
  - [ ] APScheduler background jobs
  - [ ] Continuous processes
  - [ ] Cron-like functionality
  - [ ] Periodic tasks

- [ ] **Identify Database Dependencies**
  - [ ] SQLite file storage
  - [ ] Persistent connections
  - [ ] Data migration needs
  - [ ] Schema requirements

---

## 📧 **Email System Migration**

### **Phase 1: Provider Setup**
- [ ] **Configure SendGrid**
  - [ ] Sign up for SendGrid account
  - [ ] Generate API key
  - [ ] Set `SENDGRID_API_KEY` environment variable
  - [ ] Set `SENDGRID_FROM_EMAIL` environment variable
  - [ ] Verify domain (if using custom domain)

- [ ] **Configure Resend (Alternative)**
  - [ ] Sign up for Resend account
  - [ ] Generate API key
  - [ ] Set `RESEND_API_KEY` environment variable
  - [ ] Set `RESEND_FROM_EMAIL` environment variable

- [ ] **Configure SMTP Fallback**
  - [ ] Generate Gmail app password
  - [ ] Set `SMTP_SERVER=smtp.gmail.com`
  - [ ] Set `SMTP_PORT=587`
  - [ ] Set `SENDER_EMAIL` and `SENDER_PASSWORD`

### **Phase 2: Implementation**
- [ ] **Install Enhanced Email Service**
  - [ ] Deploy `api/notifications/enhanced_email_service.py`
  - [ ] Install required dependencies: `sendgrid`, `requests`
  - [ ] Test configuration endpoint

- [ ] **Update Email Templates**
  - [ ] High impact alert template
  - [ ] Portfolio summary template
  - [ ] System alert template
  - [ ] Test templated emails

- [ ] **Test Email Fallback**
  - [ ] Test SendGrid primary
  - [ ] Test Resend fallback
  - [ ] Test SMTP fallback
  - [ ] Verify error handling

### **Phase 3: Validation**
- [ ] **Test Email Delivery**
  ```bash
  curl -X POST "https://your-app.vercel.app/api/notifications/enhanced_email_service" \
    -H "Content-Type: application/json" \
    -d '{"action": "test_config"}'
  ```

- [ ] **Monitor Email Logs**
  - [ ] Check Vercel function logs
  - [ ] Monitor SendGrid delivery
  - [ ] Track bounce rates

---

## 🔄 **Real-time Features Migration**

### **Phase 1: Polling Setup**
- [ ] **Install React Query**
  ```bash
  cd frontend
  npm install @tanstack/react-query
  ```

- [ ] **Deploy Real-time Hooks**
  - [ ] Deploy `frontend/src/hooks/useRealTimePolling.ts`
  - [ ] Configure polling intervals
  - [ ] Set up error handling

- [ ] **Update Components**
  - [ ] Replace Streamlit session state with React Query
  - [ ] Implement polling controls
  - [ ] Add loading states

### **Phase 2: Advanced Real-time (Optional)**
- [ ] **Configure Pusher (Optional)**
  - [ ] Sign up for Pusher account
  - [ ] Set Pusher environment variables
  - [ ] Implement WebSocket alternative

- [ ] **Set up Server-Sent Events**
  - [ ] Create SSE endpoint
  - [ ] Implement event streaming
  - [ ] Test browser compatibility

### **Phase 3: Performance Optimization**
- [ ] **Implement Adaptive Polling**
  - [ ] User activity detection
  - [ ] Interval adjustment
  - [ ] Background optimization

- [ ] **Add Batch Polling**
  - [ ] Multiple query batching
  - [ ] Coordinated refresh
  - [ ] Error isolation

### **Phase 4: Testing**
- [ ] **Test Polling Mechanisms**
  - [ ] Portfolio data polling
  - [ ] Event stream polling
  - [ ] System status polling
  - [ ] Performance under load

---

## ⏰ **Scheduling System Migration**

### **Phase 1: Service Setup**
- [ ] **Configure Vercel Cron Jobs**
  - [ ] Update `vercel.json` with cron configuration
  - [ ] Set `CRON_SECRET` environment variable
  - [ ] Deploy cron endpoints

- [ ] **Setup External Cron Services**
  - [ ] Sign up for cron-job.org
  - [ ] Get API key: `CRON_JOB_ORG_API_KEY`
  - [ ] Alternative: EasyCron setup

- [ ] **Configure GitHub Actions**
  - [ ] Set GitHub token: `GITHUB_TOKEN`
  - [ ] Set repository: `GITHUB_REPOSITORY`
  - [ ] Test workflow creation

### **Phase 2: Implementation**
- [ ] **Deploy Cron Manager**
  - [ ] Deploy `api/scheduler/vercel_cron_jobs.py`
  - [ ] Test service detection
  - [ ] Verify authentication

- [ ] **Create Scheduled Jobs**
  - [ ] Portfolio analysis job (hourly)
  - [ ] Risk assessment job (15 min)
  - [ ] Event monitoring job (5 min)
  - [ ] System health check (daily)

### **Phase 3: Testing**
- [ ] **Test Job Creation**
  ```bash
  curl -X POST "https://your-app.vercel.app/api/scheduler/vercel_cron_jobs" \
    -H "Content-Type: application/json" \
    -d '{
      "action": "create_job",
      "job_config": {
        "name": "Portfolio Analysis",
        "path": "/api/cron/portfolio-analysis",
        "schedule": "0 */1 * * *",
        "job_type": "portfolio_analysis"
      },
      "service": "external",
      "secret": "your_cron_secret"
    }'
  ```

- [ ] **Verify Job Execution**
  - [ ] Check job history
  - [ ] Monitor execution logs
  - [ ] Test error handling

---

## 💾 **Database Migration**

### **Phase 1: Service Selection**
- [ ] **Choose Database Provider**
  - [ ] Option A: Supabase (PostgreSQL)
  - [ ] Option B: Vercel KV (Redis)
  - [ ] Option C: External PostgreSQL
  - [ ] Option D: In-memory (development only)

### **Phase 2: Supabase Setup (Recommended)**
- [ ] **Create Supabase Project**
  - [ ] Sign up for Supabase
  - [ ] Create new project
  - [ ] Get connection details

- [ ] **Configure Environment Variables**
  - [ ] Set `SUPABASE_URL`
  - [ ] Set `SUPABASE_ANON_KEY`
  - [ ] Set `SUPABASE_SERVICE_ROLE_KEY`

- [ ] **Create Database Schema**
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

### **Phase 3: Data Migration**
- [ ] **Export Existing Data**
  - [ ] Export SQLite insights
  - [ ] Export knowledge evolution
  - [ ] Export events

- [ ] **Import to New Database**
  - [ ] Create migration script
  - [ ] Test data integrity
  - [ ] Verify all data migrated

### **Phase 4: Testing**
- [ ] **Test Database Operations**
  - [ ] Insert operations
  - [ ] Query operations
  - [ ] Update operations
  - [ ] Delete operations

---

## 🔧 **Feature Detection & Fallbacks**

### **Phase 1: Feature Detection**
- [ ] **Deploy Feature Detector**
  - [ ] Deploy feature detection system
  - [ ] Test service detection
  - [ ] Verify fallback mechanisms

- [ ] **Test All Providers**
  - [ ] Email provider detection
  - [ ] Database provider detection
  - [ ] Cron service detection
  - [ ] Real-time feature detection

### **Phase 2: Fallback Testing**
- [ ] **Test Email Fallbacks**
  - [ ] Simulate SendGrid failure
  - [ ] Verify Resend fallback
  - [ ] Test SMTP fallback

- [ ] **Test Database Fallbacks**
  - [ ] Simulate database failure
  - [ ] Verify in-memory fallback
  - [ ] Test data recovery

### **Phase 3: Monitoring**
- [ ] **Set up Monitoring**
  - [ ] Configure Sentry (optional)
  - [ ] Set up error tracking
  - [ ] Monitor service health

---

## 🚀 **Deployment**

### **Phase 1: Environment Setup**
- [ ] **Configure Vercel Environment Variables**
  ```bash
  # Core Configuration
  XAI_API_KEY=your_xai_api_key_here
  CRON_SECRET=your_secure_cron_secret

  # Email Configuration
  SENDGRID_API_KEY=your_sendgrid_api_key
  SENDGRID_FROM_EMAIL=your@domain.com
  RESEND_API_KEY=your_resend_api_key
  RESEND_FROM_EMAIL=your@domain.com
  TO_EMAIL=recipient@example.com

  # Database Configuration
  SUPABASE_URL=https://your-project.supabase.co
  SUPABASE_ANON_KEY=your_anon_key
  DATABASE_URL=postgresql://user:pass@host:port/db

  # External Services
  CRON_JOB_ORG_API_KEY=your_cron_job_org_key
  GITHUB_TOKEN=your_github_token
  GITHUB_REPOSITORY=owner/repo

  # Feature Flags
  ENABLE_REAL_TIME_POLLING=true
  ENABLE_EMAIL_FALLBACK=true
  ENABLE_EXTERNAL_CRON=true
  ```

### **Phase 2: Deployment**
- [ ] **Deploy to Vercel**
  ```bash
  vercel --prod
  ```

- [ ] **Verify Deployment**
  - [ ] Check function logs
  - [ ] Test API endpoints
  - [ ] Monitor error rates

### **Phase 3: Post-Deployment**
- [ ] **Run Integration Tests**
  ```bash
  export VERCEL_DEPLOYMENT_URL=https://your-app.vercel.app
  python -m pytest test_vercel.py -v
  ```

- [ ] **Monitor Performance**
  - [ ] Check response times
  - [ ] Monitor error rates
  - [ ] Verify uptime

---

## ✅ **Testing & Validation**

### **Functionality Testing**
- [ ] **Email System**
  - [ ] Test all providers
  - [ ] Test template rendering
  - [ ] Test fallback mechanisms
  - [ ] Verify delivery

- [ ] **Real-time Features**
  - [ ] Test polling mechanisms
  - [ ] Test error handling
  - [ ] Test performance
  - [ ] Test adaptive polling

- [ ] **Scheduling System**
  - [ ] Test job creation
  - [ ] Test job execution
  - [ ] Test job deletion
  - [ ] Test multiple services

- [ ] **Database Operations**
  - [ ] Test data persistence
  - [ ] Test query performance
  - [ ] Test error handling
  - [ ] Test fallback mechanisms

### **Performance Testing**
- [ ] **Load Testing**
  - [ ] Test concurrent requests
  - [ ] Test database performance
  - [ ] Test email throughput
  - [ ] Test polling performance

- [ ] **Stress Testing**
  - [ ] Test failure scenarios
  - [ ] Test recovery mechanisms
  - [ ] Test error handling
  - [ ] Test resource limits

### **Security Testing**
- [ ] **Authentication**
  - [ ] Test cron secrets
  - [ ] Test API security
  - [ ] Test environment variables
  - [ ] Test error messages

- [ ] **Input Validation**
  - [ ] Test malformed requests
  - [ ] Test SQL injection
  - [ ] Test XSS prevention
  - [ ] Test rate limiting

---

## 🎉 **Migration Complete**

### **Final Verification**
- [ ] **All Services Operational**
  - [ ] Email notifications working
  - [ ] Real-time polling active
  - [ ] Scheduled jobs running
  - [ ] Database operations working

- [ ] **Performance Metrics**
  - [ ] Response times < 5 seconds
  - [ ] Error rates < 1%
  - [ ] Uptime > 99%
  - [ ] Email delivery > 95%

- [ ] **Monitoring Active**
  - [ ] Error tracking configured
  - [ ] Performance monitoring
  - [ ] Uptime monitoring
  - [ ] Cost monitoring

### **Documentation Updated**
- [ ] **Update README**
  - [ ] New architecture description
  - [ ] Environment variable guide
  - [ ] Deployment instructions
  - [ ] Troubleshooting guide

- [ ] **Update API Documentation**
  - [ ] New endpoints documented
  - [ ] Authentication methods
  - [ ] Error codes
  - [ ] Examples updated

### **Team Handoff**
- [ ] **Knowledge Transfer**
  - [ ] Architecture review
  - [ ] Operations guide
  - [ ] Troubleshooting procedures
  - [ ] Monitoring setup

- [ ] **Support Documentation**
  - [ ] Runbook creation
  - [ ] Emergency procedures
  - [ ] Contact information
  - [ ] Escalation procedures

---

## 🆘 **Rollback Plan**

### **If Migration Fails**
- [ ] **Immediate Actions**
  - [ ] Stop new deployments
  - [ ] Assess impact
  - [ ] Notify stakeholders
  - [ ] Document issues

- [ ] **Data Recovery**
  - [ ] Restore from backup
  - [ ] Verify data integrity
  - [ ] Test functionality
  - [ ] Notify users

- [ ] **System Restoration**
  - [ ] Revert to previous version
  - [ ] Restore configurations
  - [ ] Test all systems
  - [ ] Monitor stability

### **Post-Rollback**
- [ ] **Issue Analysis**
  - [ ] Root cause analysis
  - [ ] Document lessons learned
  - [ ] Update migration plan
  - [ ] Plan retry strategy

---

## 📊 **Success Metrics**

### **Technical Metrics**
- [ ] **System Performance**
  - Response time: < 5 seconds
  - Error rate: < 1%
  - Uptime: > 99.9%
  - Function cold start: < 2 seconds

- [ ] **Feature Metrics**
  - Email delivery rate: > 95%
  - Polling accuracy: > 99%
  - Job execution success: > 95%
  - Database query time: < 1 second

### **Business Metrics**
- [ ] **Cost Efficiency**
  - Reduced infrastructure costs
  - Lower maintenance overhead
  - Improved scalability
  - Better resource utilization

- [ ] **User Experience**
  - Faster load times
  - More reliable notifications
  - Better real-time updates
  - Improved availability

---

## 🔗 **Resources**

### **Documentation**
- [Vercel Cron Jobs](https://vercel.com/docs/cron-jobs)
- [SendGrid API](https://docs.sendgrid.com/api-reference)
- [Resend API](https://resend.com/docs)
- [React Query](https://tanstack.com/query/latest)

### **External Services**
- [cron-job.org](https://cron-job.org/)
- [EasyCron](https://www.easycron.com/)
- [Supabase](https://supabase.com/)
- [Pusher](https://pusher.com/)

### **Monitoring**
- [Sentry](https://sentry.io/)
- [Datadog](https://www.datadoghq.com/)
- [Vercel Analytics](https://vercel.com/analytics)

---

**✅ Migration Complete! Your application is now fully compatible with Vercel's serverless architecture.** 