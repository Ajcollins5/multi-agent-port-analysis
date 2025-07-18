#!/usr/bin/env python3
"""
Test script to verify Vercel function endpoints are working correctly
Run this after deploying the fixes to check if the function failures are resolved.
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, Any

# Configuration
VERCEL_URL = os.environ.get("VERCEL_URL", "https://your-project.vercel.app")
CRON_SECRET = os.environ.get("CRON_SECRET", "your_cron_secret")

def test_main_api_health():
    """Test the main API health endpoint"""
    print("🔍 Testing main API health endpoint...")
    
    try:
        response = requests.get(f"{VERCEL_URL}/api/app", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   Exception: {e}")
        return False

def test_cron_handler_info():
    """Test the cron handler info endpoint (no auth required)"""
    print("\n🔍 Testing cron handler info endpoint...")
    
    try:
        response = requests.get(f"{VERCEL_URL}/api/scheduler/cron_handler", timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   Exception: {e}")
        return False

def test_cron_handler_authenticated():
    """Test the cron handler with authentication"""
    print("\n🔍 Testing cron handler with authentication...")
    
    try:
        headers = {"X-Cron-Secret": CRON_SECRET}
        payload = {"action": "get_jobs"}
        
        response = requests.post(
            f"{VERCEL_URL}/api/scheduler/cron_handler", 
            headers=headers, 
            json=payload, 
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   Exception: {e}")
        return False

def test_cors_headers():
    """Test CORS headers are properly set"""
    print("\n🔍 Testing CORS headers...")
    
    try:
        # Test OPTIONS request
        response = requests.options(f"{VERCEL_URL}/api/scheduler/cron_handler", timeout=30)
        print(f"   OPTIONS Status Code: {response.status_code}")
        
        headers = response.headers
        print(f"   CORS Headers:")
        print(f"     Access-Control-Allow-Origin: {headers.get('Access-Control-Allow-Origin', 'Not Set')}")
        print(f"     Access-Control-Allow-Methods: {headers.get('Access-Control-Allow-Methods', 'Not Set')}")
        print(f"     Access-Control-Allow-Headers: {headers.get('Access-Control-Allow-Headers', 'Not Set')}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"   Exception: {e}")
        return False

def test_main_api_actions():
    """Test main API actions"""
    print("\n🔍 Testing main API actions...")
    
    try:
        # Test health check
        payload = {"action": "health"}
        response = requests.post(f"{VERCEL_URL}/api/app", json=payload, timeout=30)
        
        print(f"   Health Check Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Health Check Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   Exception: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide a summary"""
    print("🚀 Starting comprehensive Vercel function test...")
    print(f"   Target URL: {VERCEL_URL}")
    print(f"   Test Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    results = {}
    
    # Run all tests
    results["main_api_health"] = test_main_api_health()
    results["cron_handler_info"] = test_cron_handler_info()
    results["cron_handler_authenticated"] = test_cron_handler_authenticated()
    results["cors_headers"] = test_cors_headers()
    results["main_api_actions"] = test_main_api_actions()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Vercel functions are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    # Check if environment variables are set
    if VERCEL_URL == "https://your-project.vercel.app":
        print("⚠️  Please set VERCEL_URL environment variable to your actual Vercel deployment URL")
        print("   Example: export VERCEL_URL=https://your-project.vercel.app")
    
    if CRON_SECRET == "your_cron_secret":
        print("⚠️  Please set CRON_SECRET environment variable to your actual cron secret")
        print("   Example: export CRON_SECRET=your_actual_secret")
    
    print()
    
    # Run the tests
    success = run_comprehensive_test()
    
    if success:
        print("\n🚀 Next Steps:")
        print("   1. Check your Vercel dashboard to confirm error rates have dropped")
        print("   2. Monitor the functions for a few minutes to ensure stability")
        print("   3. Test the frontend to ensure all features are working")
    else:
        print("\n🔧 Troubleshooting:")
        print("   1. Check Vercel function logs for detailed error messages")
        print("   2. Verify all environment variables are set in Vercel dashboard")
        print("   3. Ensure the deployment completed successfully")
        print("   4. Check that all dependencies are properly installed") 