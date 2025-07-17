#!/usr/bin/env python3
"""
Integration Tests for Vercel Deployment
Tests API endpoints and frontend data fetching for the Multi-Agent Portfolio Analysis System
"""

import pytest
import requests
import json
import time
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

# Test Configuration
BASE_URL = os.environ.get("VERCEL_DEPLOYMENT_URL", "https://multi-agent-port-analysis.vercel.app")
CRON_SECRET = os.environ.get("CRON_SECRET", "test_secret")
TEST_TIMEOUT = 30  # seconds
TEST_PORTFOLIO = ["AAPL", "GOOGL", "MSFT"]

class TestVercelDeployment:
    """Integration tests for Vercel deployment"""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create a requests session for testing"""
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "VercelTestSuite/1.0"
        })
        yield session
        session.close()
    
    def test_frontend_health(self, session):
        """Test frontend accessibility and basic functionality"""
        print("🌐 Testing frontend health...")
        
        # Test main page
        response = session.get(f"{BASE_URL}/", timeout=TEST_TIMEOUT)
        assert response.status_code == 200, f"Frontend main page failed: {response.status_code}"
        
        # Test static assets
        static_assets = [
            "/_next/static/css/app.css",
            "/favicon.ico",
            "/manifest.json"
        ]
        
        for asset in static_assets:
            try:
                response = session.get(f"{BASE_URL}{asset}", timeout=TEST_TIMEOUT)
                print(f"   ✓ {asset}: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"   ⚠️ {asset}: {e}")
        
        # Test frontend routes
        frontend_routes = [
            "/",
            "/analysis",
            "/knowledge", 
            "/events",
            "/scheduler",
            "/settings"
        ]
        
        for route in frontend_routes:
            try:
                response = session.get(f"{BASE_URL}{route}", timeout=TEST_TIMEOUT)
                assert response.status_code in [200, 404], f"Route {route} failed: {response.status_code}"
                print(f"   ✓ Route {route}: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"   ⚠️ Route {route}: {e}")
    
    def test_api_agent_endpoints(self, session):
        """Test all agent API endpoints"""
        print("🤖 Testing agent API endpoints...")
        
        agents = {
            "risk": {
                "endpoint": "/api/agents/risk",
                "test_actions": ["analyze_stock", "impact_level", "portfolio_risk"]
            },
            "news": {
                "endpoint": "/api/agents/news",
                "test_actions": ["analyze_sentiment", "market_impact", "impact_estimate"]
            },
            "events": {
                "endpoint": "/api/agents/events",
                "test_actions": ["detect_events", "event_summary", "correlations"]
            },
            "knowledge": {
                "endpoint": "/api/agents/knowledge",
                "test_actions": ["quality_assessment", "identify_gaps", "refine_insight"]
            }
        }
        
        for agent_name, agent_config in agents.items():
            print(f"   Testing {agent_name} agent...")
            
            # Test GET request (health check)
            response = session.get(f"{BASE_URL}{agent_config['endpoint']}", timeout=TEST_TIMEOUT)
            assert response.status_code == 200, f"{agent_name} agent health check failed: {response.status_code}"
            
            agent_info = response.json()
            assert "agent" in agent_info, f"{agent_name} agent missing agent info"
            assert agent_info["status"] == "active", f"{agent_name} agent not active"
            print(f"      ✓ Health check passed")
            
            # Test POST requests for each action
            for action in agent_config["test_actions"]:
                payload = {"action": action}
                
                # Add specific test data for each action
                if action == "analyze_stock":
                    payload["ticker"] = "AAPL"
                elif action == "portfolio_risk":
                    payload["portfolio"] = TEST_PORTFOLIO
                elif action == "detect_events":
                    payload["portfolio"] = TEST_PORTFOLIO
                elif action == "market_impact":
                    payload["tickers"] = TEST_PORTFOLIO
                elif action == "refine_insight":
                    payload.update({
                        "ticker": "AAPL",
                        "original_insight": "Test insight",
                        "additional_context": "Test context"
                    })
                
                response = session.post(
                    f"{BASE_URL}{agent_config['endpoint']}", 
                    json=payload, 
                    timeout=TEST_TIMEOUT
                )
                
                assert response.status_code == 200, f"{agent_name} {action} failed: {response.status_code}"
                result = response.json()
                assert "error" not in result or result.get("error") is None, f"{agent_name} {action} returned error: {result.get('error')}"
                print(f"      ✓ {action} action passed")
    
    def test_supervisor_orchestration(self, session):
        """Test supervisor agent orchestration"""
        print("🎭 Testing supervisor orchestration...")
        
        # Test single ticker analysis
        payload = {
            "action": "analyze_ticker",
            "ticker": "AAPL",
            "analysis_type": "comprehensive"
        }
        
        response = session.post(f"{BASE_URL}/api/supervisor", json=payload, timeout=TEST_TIMEOUT)
        assert response.status_code == 200, f"Supervisor ticker analysis failed: {response.status_code}"
        
        result = response.json()
        assert "ticker" in result, "Supervisor result missing ticker"
        assert "agent_results" in result, "Supervisor result missing agent results"
        assert "synthesis" in result, "Supervisor result missing synthesis"
        print("   ✓ Single ticker analysis passed")
        
        # Test portfolio analysis
        payload = {
            "action": "analyze_portfolio",
            "portfolio": TEST_PORTFOLIO
        }
        
        response = session.post(f"{BASE_URL}/api/supervisor", json=payload, timeout=TEST_TIMEOUT)
        assert response.status_code == 200, f"Supervisor portfolio analysis failed: {response.status_code}"
        
        result = response.json()
        assert "portfolio" in result, "Supervisor portfolio result missing portfolio"
        assert "individual_results" in result, "Supervisor portfolio result missing individual results"
        assert "portfolio_synthesis" in result, "Supervisor portfolio result missing portfolio synthesis"
        print("   ✓ Portfolio analysis passed")
    
    def test_notification_system(self, session):
        """Test email notification system"""
        print("📧 Testing notification system...")
        
        # Test email configuration
        payload = {"action": "test_config"}
        response = session.post(f"{BASE_URL}/api/notifications/email", json=payload, timeout=TEST_TIMEOUT)
        
        assert response.status_code == 200, f"Email test config failed: {response.status_code}"
        result = response.json()
        print(f"   Email config test: {result.get('success', 'Unknown')}")
        
        # Test templated email
        payload = {
            "action": "send_templated",
            "template_name": "high_impact_alert",
            "template_data": {
                "ticker": "AAPL",
                "current_price": "150.00",
                "volatility": "0.06",
                "threshold": "0.05",
                "impact_level": "HIGH",
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "additional_info": "Test alert from integration tests"
            }
        }
        
        response = session.post(f"{BASE_URL}/api/notifications/email", json=payload, timeout=TEST_TIMEOUT)
        assert response.status_code == 200, f"Templated email failed: {response.status_code}"
        result = response.json()
        print(f"   Templated email test: {result.get('success', 'Unknown')}")
    
    def test_storage_system(self, session):
        """Test storage system"""
        print("💾 Testing storage system...")
        
        # Test storage status
        payload = {"action": "status"}
        response = session.post(f"{BASE_URL}/api/storage", json=payload, timeout=TEST_TIMEOUT)
        
        assert response.status_code == 200, f"Storage status failed: {response.status_code}"
        result = response.json()
        assert "primary_storage" in result, "Storage status missing primary storage info"
        print(f"   Storage status: {result.get('primary_storage', 'Unknown')}")
        
        # Test storing insight
        payload = {
            "action": "store_insight",
            "ticker": "AAPL",
            "insight": "Test insight from integration tests",
            "agent": "TestAgent",
            "metadata": {"test": True, "timestamp": datetime.now().isoformat()}
        }
        
        response = session.post(f"{BASE_URL}/api/storage", json=payload, timeout=TEST_TIMEOUT)
        assert response.status_code == 200, f"Store insight failed: {response.status_code}"
        result = response.json()
        assert result.get("success", False), f"Store insight unsuccessful: {result}"
        print("   ✓ Store insight passed")
        
        # Test retrieving insights
        payload = {
            "action": "get_insights",
            "ticker": "AAPL",
            "limit": 5
        }
        
        response = session.post(f"{BASE_URL}/api/storage", json=payload, timeout=TEST_TIMEOUT)
        assert response.status_code == 200, f"Get insights failed: {response.status_code}"
        result = response.json()
        assert result.get("success", False), f"Get insights unsuccessful: {result}"
        assert "insights" in result, "Get insights missing insights data"
        print("   ✓ Get insights passed")
    
    def test_scheduler_system(self, session):
        """Test scheduler system"""
        print("⏰ Testing scheduler system...")
        
        # Test cron job creation
        payload = {
            "action": "create_job",
            "job_type": "portfolio_analysis",
            "interval_minutes": 60,
            "secret": CRON_SECRET
        }
        
        response = session.post(f"{BASE_URL}/api/scheduler/cron", json=payload, timeout=TEST_TIMEOUT)
        assert response.status_code == 200, f"Create cron job failed: {response.status_code}"
        result = response.json()
        assert result.get("success", False), f"Create cron job unsuccessful: {result}"
        print("   ✓ Create cron job passed")
        
        # Test getting scheduled jobs
        payload = {
            "action": "get_jobs",
            "secret": CRON_SECRET
        }
        
        response = session.post(f"{BASE_URL}/api/scheduler/cron", json=payload, timeout=TEST_TIMEOUT)
        assert response.status_code == 200, f"Get scheduled jobs failed: {response.status_code}"
        result = response.json()
        assert "scheduled_jobs" in result, "Get scheduled jobs missing jobs data"
        print("   ✓ Get scheduled jobs passed")
    
    def test_portfolio_analysis_workflow(self, session):
        """Test complete portfolio analysis workflow"""
        print("🔄 Testing complete portfolio analysis workflow...")
        
        workflow_results = {}
        
        # Step 1: Analyze individual stocks
        print("   Step 1: Analyzing individual stocks...")
        for ticker in TEST_PORTFOLIO:
            payload = {
                "action": "analyze_ticker",
                "ticker": ticker,
                "analysis_type": "focused"
            }
            
            response = session.post(f"{BASE_URL}/api/supervisor", json=payload, timeout=TEST_TIMEOUT)
            assert response.status_code == 200, f"Individual analysis failed for {ticker}: {response.status_code}"
            
            result = response.json()
            workflow_results[ticker] = result
            print(f"      ✓ {ticker} analysis completed")
        
        # Step 2: Portfolio-wide analysis
        print("   Step 2: Portfolio-wide analysis...")
        payload = {
            "action": "analyze_portfolio",
            "portfolio": TEST_PORTFOLIO
        }
        
        response = session.post(f"{BASE_URL}/api/supervisor", json=payload, timeout=TEST_TIMEOUT)
        assert response.status_code == 200, f"Portfolio analysis failed: {response.status_code}"
        
        portfolio_result = response.json()
        workflow_results["portfolio"] = portfolio_result
        print("      ✓ Portfolio analysis completed")
        
        # Step 3: Check for high-risk events
        print("   Step 3: Checking for high-risk events...")
        high_risk_stocks = []
        
        for ticker, result in workflow_results.items():
            if ticker == "portfolio":
                continue
            
            synthesis = result.get("synthesis", {})
            if synthesis.get("overall_risk") == "HIGH":
                high_risk_stocks.append(ticker)
        
        if high_risk_stocks:
            print(f"      ⚠️ High risk detected in: {', '.join(high_risk_stocks)}")
        else:
            print("      ✓ No high-risk events detected")
        
        # Step 4: Verify data persistence
        print("   Step 4: Verifying data persistence...")
        payload = {
            "action": "get_insights",
            "limit": 10
        }
        
        response = session.post(f"{BASE_URL}/api/storage", json=payload, timeout=TEST_TIMEOUT)
        assert response.status_code == 200, f"Data persistence check failed: {response.status_code}"
        
        result = response.json()
        insights_count = len(result.get("insights", []))
        print(f"      ✓ {insights_count} insights stored")
        
        # Step 5: Test notification system
        print("   Step 5: Testing notification system...")
        if high_risk_stocks:
            payload = {
                "action": "high_impact_alert",
                "data": {
                    "ticker": high_risk_stocks[0],
                    "current_price": 150.00,
                    "volatility": 0.06,
                    "impact_level": "HIGH",
                    "additional_info": "High risk detected in workflow test"
                }
            }
            
            response = session.post(f"{BASE_URL}/api/notifications/email", json=payload, timeout=TEST_TIMEOUT)
            assert response.status_code == 200, f"High impact notification failed: {response.status_code}"
            print("      ✓ High impact notification sent")
        else:
            print("      ✓ No high impact notifications needed")
        
        print("   ✅ Complete portfolio analysis workflow passed")
        return workflow_results
    
    def test_error_handling(self, session):
        """Test error handling and edge cases"""
        print("🛡️ Testing error handling...")
        
        # Test invalid API endpoints
        invalid_endpoints = [
            "/api/invalid",
            "/api/agents/invalid",
            "/api/agents/risk/invalid"
        ]
        
        for endpoint in invalid_endpoints:
            response = session.get(f"{BASE_URL}{endpoint}", timeout=TEST_TIMEOUT)
            # Should either return 404 or redirect to fallback
            assert response.status_code in [404, 200], f"Invalid endpoint {endpoint} returned unexpected status: {response.status_code}"
            print(f"   ✓ {endpoint}: {response.status_code}")
        
        # Test invalid JSON payload
        invalid_payload = "invalid json"
        response = session.post(
            f"{BASE_URL}/api/agents/risk",
            data=invalid_payload,
            headers={"Content-Type": "application/json"},
            timeout=TEST_TIMEOUT
        )
        assert response.status_code in [400, 500], f"Invalid JSON should return 400 or 500, got: {response.status_code}"
        print("   ✓ Invalid JSON handled correctly")
        
        # Test missing required parameters
        payload = {"action": "analyze_stock"}  # Missing ticker
        response = session.post(f"{BASE_URL}/api/agents/risk", json=payload, timeout=TEST_TIMEOUT)
        assert response.status_code == 200, f"Missing parameter test failed: {response.status_code}"
        # Should handle gracefully with default values
        print("   ✓ Missing parameters handled gracefully")
        
        # Test rate limiting (if implemented)
        print("   ⏭️ Rate limiting test skipped (not implemented)")
    
    def test_performance_benchmarks(self, session):
        """Test performance benchmarks"""
        print("⚡ Testing performance benchmarks...")
        
        # Test API response times
        endpoints_to_test = [
            "/api/agents/risk",
            "/api/agents/news",
            "/api/agents/events",
            "/api/agents/knowledge",
            "/api/supervisor",
            "/api/storage",
            "/api/notifications/email"
        ]
        
        response_times = {}
        
        for endpoint in endpoints_to_test:
            start_time = time.time()
            
            try:
                response = session.get(f"{BASE_URL}{endpoint}", timeout=TEST_TIMEOUT)
                end_time = time.time()
                response_time = end_time - start_time
                
                response_times[endpoint] = response_time
                status = "✓" if response_time < 5.0 else "⚠️"
                print(f"   {status} {endpoint}: {response_time:.2f}s")
                
            except requests.exceptions.RequestException as e:
                print(f"   ❌ {endpoint}: {e}")
        
        # Calculate average response time
        if response_times:
            avg_response_time = sum(response_times.values()) / len(response_times)
            print(f"   📊 Average response time: {avg_response_time:.2f}s")
            
            # Assert performance requirements
            assert avg_response_time < 10.0, f"Average response time too high: {avg_response_time:.2f}s"
            assert all(t < 30.0 for t in response_times.values()), "Some endpoints exceed 30s timeout"
        
        print("   ✅ Performance benchmarks completed")

class TestFrontendDataFetching:
    """Test frontend data fetching patterns"""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create a requests session for testing"""
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "VercelTestSuite/1.0"
        })
        yield session
        session.close()
    
    def test_api_endpoints_for_frontend(self, session):
        """Test API endpoints used by frontend"""
        print("🌐 Testing frontend API endpoints...")
        
        # Test portfolio data endpoint
        response = session.get(f"{BASE_URL}/api/app", timeout=TEST_TIMEOUT)
        assert response.status_code == 200, f"Portfolio data endpoint failed: {response.status_code}"
        print("   ✓ Portfolio data endpoint accessible")
        
        # Test main API endpoint
        response = session.get(f"{BASE_URL}/api/main", timeout=TEST_TIMEOUT)
        assert response.status_code == 200, f"Main API endpoint failed: {response.status_code}"
        print("   ✓ Main API endpoint accessible")
        
        # Test API endpoints that frontend would call
        frontend_api_calls = [
            {
                "endpoint": "/api/supervisor",
                "method": "POST",
                "payload": {"action": "analyze_ticker", "ticker": "AAPL"}
            },
            {
                "endpoint": "/api/storage",
                "method": "POST", 
                "payload": {"action": "get_insights", "limit": 5}
            },
            {
                "endpoint": "/api/scheduler/cron",
                "method": "POST",
                "payload": {"action": "get_jobs", "secret": CRON_SECRET}
            }
        ]
        
        for api_call in frontend_api_calls:
            if api_call["method"] == "POST":
                response = session.post(
                    f"{BASE_URL}{api_call['endpoint']}", 
                    json=api_call["payload"], 
                    timeout=TEST_TIMEOUT
                )
            else:
                response = session.get(f"{BASE_URL}{api_call['endpoint']}", timeout=TEST_TIMEOUT)
            
            assert response.status_code == 200, f"Frontend API call failed: {api_call['endpoint']}"
            print(f"   ✓ {api_call['endpoint']} - {api_call['method']}")
    
    def test_cors_configuration(self, session):
        """Test CORS configuration for frontend"""
        print("🔗 Testing CORS configuration...")
        
        # Test preflight request
        headers = {
            "Origin": "https://your-frontend-domain.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        response = session.options(f"{BASE_URL}/api/agents/risk", headers=headers, timeout=TEST_TIMEOUT)
        print(f"   CORS preflight response: {response.status_code}")
        
        # Test actual CORS headers in response
        response = session.get(f"{BASE_URL}/api/agents/risk", timeout=TEST_TIMEOUT)
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
        }
        
        print(f"   CORS headers: {cors_headers}")
        print("   ✓ CORS configuration tested")

# Test runner
if __name__ == "__main__":
    print("🚀 Starting Vercel Integration Tests")
    print(f"📍 Target URL: {BASE_URL}")
    print(f"🕐 Timeout: {TEST_TIMEOUT}s")
    print(f"💼 Test Portfolio: {TEST_PORTFOLIO}")
    print("=" * 60)
    
    # Run tests
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "User-Agent": "VercelTestSuite/1.0"
    })
    
    try:
        # Initialize test classes
        vercel_tests = TestVercelDeployment()
        frontend_tests = TestFrontendDataFetching()
        
        # Run deployment tests
        vercel_tests.test_frontend_health(session)
        vercel_tests.test_api_agent_endpoints(session)
        vercel_tests.test_supervisor_orchestration(session)
        vercel_tests.test_notification_system(session)
        vercel_tests.test_storage_system(session)
        vercel_tests.test_scheduler_system(session)
        vercel_tests.test_portfolio_analysis_workflow(session)
        vercel_tests.test_error_handling(session)
        vercel_tests.test_performance_benchmarks(session)
        
        # Run frontend tests
        frontend_tests.test_api_endpoints_for_frontend(session)
        frontend_tests.test_cors_configuration(session)
        
        print("\n" + "=" * 60)
        print("🎉 All integration tests passed!")
        print("✅ Vercel deployment is working correctly")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
    finally:
        session.close() 