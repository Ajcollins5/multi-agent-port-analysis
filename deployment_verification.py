#!/usr/bin/env python3
"""
Deployment Verification Script
Quick verification that the Vercel deployment is working correctly
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
BASE_URL = os.environ.get("VERCEL_DEPLOYMENT_URL", "https://multi-agent-port-analysis.vercel.app")
CRON_SECRET = os.environ.get("CRON_SECRET", "test_secret")
TIMEOUT = 30

def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_step(step: str, success: bool = True):
    """Print a formatted step result"""
    status = "✅" if success else "❌"
    print(f"{status} {step}")

def check_frontend():
    """Check frontend accessibility"""
    print_header("Frontend Verification")
    
    try:
        # Test main page
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        print_step(f"Main page: {response.status_code}", response.status_code == 200)
        
        # Test key routes
        routes = ["/analysis", "/knowledge", "/events", "/scheduler", "/settings"]
        for route in routes:
            try:
                response = requests.get(f"{BASE_URL}{route}", timeout=TIMEOUT)
                print_step(f"Route {route}: {response.status_code}", response.status_code in [200, 404])
            except requests.exceptions.RequestException as e:
                print_step(f"Route {route}: Error - {e}", False)
                
    except requests.exceptions.RequestException as e:
        print_step(f"Frontend check failed: {e}", False)

def check_api_endpoints():
    """Check API endpoints"""
    print_header("API Endpoints Verification")
    
    endpoints = [
        "/api/agents/risk",
        "/api/agents/news", 
        "/api/agents/events",
        "/api/agents/knowledge",
        "/api/supervisor",
        "/api/storage",
        "/api/notifications/email",
        "/api/scheduler/cron"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=TIMEOUT)
            print_step(f"{endpoint}: {response.status_code}", response.status_code == 200)
        except requests.exceptions.RequestException as e:
            print_step(f"{endpoint}: Error - {e}", False)

def test_portfolio_analysis():
    """Test portfolio analysis functionality"""
    print_header("Portfolio Analysis Test")
    
    try:
        # Test single ticker analysis
        payload = {
            "action": "analyze_ticker",
            "ticker": "AAPL",
            "analysis_type": "focused"
        }
        
        response = requests.post(f"{BASE_URL}/api/supervisor", json=payload, timeout=TIMEOUT)
        print_step(f"Single ticker analysis: {response.status_code}", response.status_code == 200)
        
        if response.status_code == 200:
            result = response.json()
            has_required_fields = all(field in result for field in ["ticker", "agent_results", "synthesis"])
            print_step(f"Response structure valid: {has_required_fields}", has_required_fields)
        
        # Test portfolio analysis
        payload = {
            "action": "analyze_portfolio",
            "portfolio": ["AAPL", "GOOGL", "MSFT"]
        }
        
        response = requests.post(f"{BASE_URL}/api/supervisor", json=payload, timeout=TIMEOUT)
        print_step(f"Portfolio analysis: {response.status_code}", response.status_code == 200)
        
    except requests.exceptions.RequestException as e:
        print_step(f"Portfolio analysis failed: {e}", False)

def test_email_system():
    """Test email notification system"""
    print_header("Email System Test")
    
    try:
        # Test email configuration
        payload = {"action": "test_config"}
        response = requests.post(f"{BASE_URL}/api/notifications/email", json=payload, timeout=TIMEOUT)
        print_step(f"Email config test: {response.status_code}", response.status_code == 200)
        
        if response.status_code == 200:
            result = response.json()
            config_valid = result.get("success", False)
            print_step(f"Email configuration valid: {config_valid}", config_valid)
        
    except requests.exceptions.RequestException as e:
        print_step(f"Email system test failed: {e}", False)

def test_storage_system():
    """Test storage system"""
    print_header("Storage System Test")
    
    try:
        # Test storage status
        payload = {"action": "status"}
        response = requests.post(f"{BASE_URL}/api/storage", json=payload, timeout=TIMEOUT)
        print_step(f"Storage status: {response.status_code}", response.status_code == 200)
        
        if response.status_code == 200:
            result = response.json()
            storage_active = "primary_storage" in result
            print_step(f"Storage system active: {storage_active}", storage_active)
        
        # Test storing a test insight
        payload = {
            "action": "store_insight",
            "ticker": "TEST",
            "insight": "Test insight from verification script",
            "agent": "VerificationAgent",
            "metadata": {"test": True, "timestamp": datetime.now().isoformat()}
        }
        
        response = requests.post(f"{BASE_URL}/api/storage", json=payload, timeout=TIMEOUT)
        print_step(f"Store test insight: {response.status_code}", response.status_code == 200)
        
        # Test retrieving insights
        payload = {"action": "get_insights", "limit": 5}
        response = requests.post(f"{BASE_URL}/api/storage", json=payload, timeout=TIMEOUT)
        print_step(f"Retrieve insights: {response.status_code}", response.status_code == 200)
        
    except requests.exceptions.RequestException as e:
        print_step(f"Storage system test failed: {e}", False)

def test_scheduler_system():
    """Test scheduler system"""
    print_header("Scheduler System Test")
    
    try:
        # Test getting scheduled jobs
        payload = {"action": "get_jobs", "secret": CRON_SECRET}
        response = requests.post(f"{BASE_URL}/api/scheduler/cron", json=payload, timeout=TIMEOUT)
        print_step(f"Get scheduled jobs: {response.status_code}", response.status_code == 200)
        
        if response.status_code == 200:
            result = response.json()
            has_jobs_data = "scheduled_jobs" in result
            print_step(f"Jobs data present: {has_jobs_data}", has_jobs_data)
        
    except requests.exceptions.RequestException as e:
        print_step(f"Scheduler system test failed: {e}", False)

def test_performance():
    """Test performance metrics"""
    print_header("Performance Test")
    
    endpoints_to_test = [
        "/api/agents/risk",
        "/api/supervisor",
        "/api/storage"
    ]
    
    response_times = []
    
    for endpoint in endpoints_to_test:
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=TIMEOUT)
            end_time = time.time()
            response_time = end_time - start_time
            
            response_times.append(response_time)
            fast_response = response_time < 5.0
            print_step(f"{endpoint}: {response_time:.2f}s", fast_response)
            
        except requests.exceptions.RequestException as e:
            print_step(f"{endpoint}: Error - {e}", False)
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        print_step(f"Average response time: {avg_time:.2f}s", avg_time < 10.0)

def test_complete_workflow():
    """Test complete end-to-end workflow"""
    print_header("Complete Workflow Test")
    
    try:
        # Step 1: Analyze a stock
        print("  Step 1: Stock Analysis")
        payload = {
            "action": "analyze_ticker",
            "ticker": "AAPL",
            "analysis_type": "comprehensive"
        }
        
        response = requests.post(f"{BASE_URL}/api/supervisor", json=payload, timeout=TIMEOUT)
        analysis_success = response.status_code == 200
        print_step(f"    Stock analysis: {response.status_code}", analysis_success)
        
        # Step 2: Check data persistence
        print("  Step 2: Data Persistence")
        payload = {"action": "get_insights", "ticker": "AAPL", "limit": 5}
        response = requests.post(f"{BASE_URL}/api/storage", json=payload, timeout=TIMEOUT)
        storage_success = response.status_code == 200
        print_step(f"    Data retrieval: {response.status_code}", storage_success)
        
        # Step 3: Test notification system
        print("  Step 3: Notification System")
        payload = {"action": "test_config"}
        response = requests.post(f"{BASE_URL}/api/notifications/email", json=payload, timeout=TIMEOUT)
        notification_success = response.status_code == 200
        print_step(f"    Email config: {response.status_code}", notification_success)
        
        # Overall workflow success
        workflow_success = all([analysis_success, storage_success, notification_success])
        print_step(f"Complete workflow: {'SUCCESS' if workflow_success else 'PARTIAL'}", workflow_success)
        
    except requests.exceptions.RequestException as e:
        print_step(f"Complete workflow failed: {e}", False)

def main():
    """Main verification function"""
    print_header("Vercel Deployment Verification")
    print(f"🎯 Target URL: {BASE_URL}")
    print(f"⏰ Timeout: {TIMEOUT}s")
    print(f"📅 Verification time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all verification checks
    check_frontend()
    check_api_endpoints()
    test_portfolio_analysis()
    test_email_system()
    test_storage_system()
    test_scheduler_system()
    test_performance()
    test_complete_workflow()
    
    # Summary
    print_header("Verification Summary")
    print("✅ Deployment verification completed!")
    print("📊 Review the results above to ensure all systems are operational")
    print("🔍 For detailed testing, run: python3 -m pytest test_vercel.py -v")
    print("📖 For deployment guide, see: VERCEL_PRODUCTION_DEPLOYMENT.md")

if __name__ == "__main__":
    main() 