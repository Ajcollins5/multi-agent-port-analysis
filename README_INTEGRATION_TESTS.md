# Integration Tests Documentation

## Overview

The `test_vercel.py` file contains comprehensive integration tests for the Vercel deployment of the Multi-Agent Portfolio Analysis System. These tests validate both API endpoints and frontend data fetching capabilities.

## Test Structure

### TestVercelDeployment

**Purpose**: Tests the complete Vercel deployment functionality

**Test Methods**:
- `test_frontend_health()` - Tests frontend accessibility and routing
- `test_api_agent_endpoints()` - Tests all agent API endpoints (risk, news, events, knowledge)
- `test_supervisor_orchestration()` - Tests supervisor agent coordination
- `test_notification_system()` - Tests email notification functionality
- `test_storage_system()` - Tests data persistence and retrieval
- `test_scheduler_system()` - Tests cron job scheduling
- `test_portfolio_analysis_workflow()` - Tests complete end-to-end workflow
- `test_error_handling()` - Tests error handling and edge cases
- `test_performance_benchmarks()` - Tests response times and performance

### TestFrontendDataFetching

**Purpose**: Tests frontend-specific API integrations

**Test Methods**:
- `test_api_endpoints_for_frontend()` - Tests API endpoints used by frontend
- `test_cors_configuration()` - Tests CORS configuration for frontend

## Configuration

### Environment Variables

```bash
# Required for testing
VERCEL_DEPLOYMENT_URL=https://your-deployment.vercel.app
CRON_SECRET=your_cron_secret_here

# Optional for local testing
XAI_API_KEY=your_api_key_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your@email.com
SENDER_PASSWORD=your_app_password
```

### Test Configuration

```python
# Default configuration in test_vercel.py
BASE_URL = os.environ.get("VERCEL_DEPLOYMENT_URL", "https://multi-agent-port-analysis.vercel.app")
CRON_SECRET = os.environ.get("CRON_SECRET", "test_secret")
TEST_TIMEOUT = 30  # seconds
TEST_PORTFOLIO = ["AAPL", "GOOGL", "MSFT"]
```

## Running the Tests

### Prerequisites

```bash
# Install dependencies
pip install pytest requests

# Set environment variables
export VERCEL_DEPLOYMENT_URL=https://your-deployment.vercel.app
export CRON_SECRET=your_actual_cron_secret
```

### Running Tests

```bash
# Run all tests
python3 -m pytest test_vercel.py -v

# Run specific test class
python3 -m pytest test_vercel.py::TestVercelDeployment -v

# Run specific test method
python3 -m pytest test_vercel.py::TestVercelDeployment::test_frontend_health -v

# Run with detailed output
python3 -m pytest test_vercel.py --tb=long -v -s

# Run in parallel (if pytest-xdist is installed)
python3 -m pytest test_vercel.py -n auto
```

### Running as Script

```bash
# Run the integrated test runner
python3 test_vercel.py
```

## Test Scenarios

### 1. Frontend Health Tests

- **Main page accessibility**: Tests homepage loading
- **Static assets**: Tests CSS, favicon, manifest loading
- **Frontend routes**: Tests all application routes
- **Mobile responsiveness**: Verifies responsive design

### 2. API Agent Tests

Each agent is tested for:
- **Health check**: GET request to verify agent status
- **Action endpoints**: POST requests with specific actions
- **Data validation**: Response structure and error handling
- **Performance**: Response time monitoring

### 3. Supervisor Orchestration Tests

- **Single ticker analysis**: Tests individual stock analysis
- **Portfolio analysis**: Tests multi-stock portfolio analysis
- **Agent coordination**: Verifies proper agent communication
- **Result synthesis**: Tests result aggregation and processing

### 4. Notification System Tests

- **Email configuration**: Tests SMTP settings
- **Template rendering**: Tests email template system
- **Delivery verification**: Tests email sending capability
- **Error handling**: Tests notification failure scenarios

### 5. Storage System Tests

- **Data persistence**: Tests insight storage
- **Data retrieval**: Tests insight querying
- **Data integrity**: Verifies stored data accuracy
- **Storage status**: Tests storage system health

### 6. Scheduler System Tests

- **Cron job creation**: Tests scheduled job creation
- **Job listing**: Tests retrieving scheduled jobs
- **Job execution**: Tests job execution capability
- **Security**: Tests cron secret authentication

### 7. Portfolio Analysis Workflow Tests

Complete end-to-end workflow testing:
1. **Individual stock analysis** for each ticker
2. **Portfolio-wide analysis** with cross-correlations
3. **Risk assessment** and high-risk detection
4. **Data persistence** verification
5. **Notification system** integration

### 8. Error Handling Tests

- **Invalid endpoints**: Tests 404 handling
- **Invalid JSON**: Tests malformed request handling
- **Missing parameters**: Tests parameter validation
- **Rate limiting**: Tests rate limiting behavior (if implemented)

### 9. Performance Tests

- **Response time monitoring**: Tests API response times
- **Throughput testing**: Tests concurrent request handling
- **Performance benchmarks**: Establishes baseline performance
- **Timeout handling**: Tests long-running request management

## Expected Results

### Successful Test Run

When all tests pass, you should see:
- ✅ Frontend accessible and routes working
- ✅ All API endpoints responding correctly
- ✅ Agent orchestration functioning properly
- ✅ Email notifications working
- ✅ Data persistence operational
- ✅ Scheduled jobs configured
- ✅ Complete workflow executing successfully
- ✅ Error handling working as expected
- ✅ Performance within acceptable limits

### Test Failures

Common failure scenarios:
- **404 errors**: Deployment not accessible or routes misconfigured
- **500 errors**: Server-side errors in API endpoints
- **Timeout errors**: Functions taking too long to respond
- **Authentication errors**: Invalid API keys or credentials
- **Configuration errors**: Missing environment variables

## Debugging

### Verbose Testing

```bash
# Run with maximum verbosity
python3 -m pytest test_vercel.py -vvv -s --tb=long

# Run with logging
python3 -m pytest test_vercel.py -v -s --log-cli-level=DEBUG
```

### Individual Test Debugging

```bash
# Test specific functionality
python3 -m pytest test_vercel.py::TestVercelDeployment::test_frontend_health -v -s

# Test with custom URL
VERCEL_DEPLOYMENT_URL=https://your-test-url.vercel.app python3 -m pytest test_vercel.py -v
```

### Manual Verification

```bash
# Test API endpoints manually
curl -X GET https://your-deployment.vercel.app/api/agents/risk
curl -X POST https://your-deployment.vercel.app/api/supervisor \
  -H "Content-Type: application/json" \
  -d '{"action": "analyze_ticker", "ticker": "AAPL"}'
```

## Continuous Integration

### GitHub Actions Integration

The tests can be integrated into GitHub Actions workflows:

```yaml
name: Integration Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install pytest requests
    - name: Run integration tests
      env:
        VERCEL_DEPLOYMENT_URL: ${{ secrets.VERCEL_DEPLOYMENT_URL }}
        CRON_SECRET: ${{ secrets.CRON_SECRET }}
      run: |
        python3 -m pytest test_vercel.py -v
```

## Best Practices

### Test Data Management

- Use deterministic test data
- Clean up test data after tests
- Avoid testing with production data
- Use separate test environments

### Test Isolation

- Each test should be independent
- Use session fixtures for shared resources
- Clean up resources after tests
- Handle test failures gracefully

### Performance Considerations

- Set appropriate timeouts
- Use connection pooling
- Monitor test execution time
- Optimize test parallelization

### Security

- Never commit secrets to version control
- Use environment variables for sensitive data
- Validate test authentication
- Use secure test endpoints

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Check network connectivity
   - Verify deployment URL
   - Check firewall settings

2. **Authentication Errors**
   - Verify environment variables
   - Check API key validity
   - Validate CRON_SECRET

3. **Timeout Errors**
   - Increase TEST_TIMEOUT value
   - Check server response time
   - Verify function performance

4. **Import Errors**
   - Install missing dependencies
   - Check Python version compatibility
   - Verify package versions

### Getting Help

- Check test output for detailed error messages
- Review Vercel function logs
- Use debugging tools (pdb, logging)
- Consult deployment documentation

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Add appropriate docstrings
3. Include error handling
4. Test both success and failure cases
5. Update this documentation

## Conclusion

The integration tests provide comprehensive validation of the Vercel deployment, ensuring all components work together correctly in a production environment. Regular execution of these tests helps maintain system reliability and catches deployment issues early. 