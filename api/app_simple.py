#!/usr/bin/env python3
"""
Simplified API handler for testing Vercel deployment
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handler(event, context):
    """
    Simplified Vercel serverless function handler
    """
    try:
        # Handle OPTIONS requests for CORS
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                },
                "body": ""
            }
        
        # Extract request data
        http_method = event.get("httpMethod", "GET")
        query_params = event.get("queryStringParameters") or {}
        body = event.get("body", "{}")
        
        # Parse request data
        if http_method == "POST":
            try:
                request_data = json.loads(body) if body else {}
            except json.JSONDecodeError:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"success": False, "error": "Invalid JSON in request body"})
                }
        else:
            request_data = dict(query_params)
        
        # Set default action if not provided
        if "action" not in request_data:
            request_data["action"] = "health"
        
        # Process the request
        result = process_request(request_data)
        
        # Return response
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"success": False, "error": str(e)})
        }


def process_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process API request with simplified logic"""
    try:
        action = request_data.get("action", "health")
        
        if action == "health":
            return {
                "success": True,
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "message": "Simplified API is working",
                "environment": {
                    "python_version": "3.9+",
                    "environment_vars": {
                        "VERCEL_URL": bool(os.environ.get("VERCEL_URL")),
                        "SUPABASE_URL": bool(os.environ.get("SUPABASE_URL")),
                        "XAI_API_KEY": bool(os.environ.get("XAI_API_KEY"))
                    }
                }
            }
        
        elif action == "analyze_portfolio":
            portfolio = request_data.get("portfolio", [])
            if not portfolio:
                return {"success": False, "error": "Portfolio is required"}
            
            # Simplified portfolio analysis
            return {
                "success": True,
                "portfolio_size": len(portfolio),
                "analyzed_stocks": len(portfolio),
                "portfolio_risk": "MEDIUM",
                "high_risk_count": 1,
                "timestamp": datetime.now().isoformat(),
                "message": "Simplified portfolio analysis completed"
            }
        
        elif action == "analyze_ticker":
            ticker = request_data.get("ticker", "").upper()
            if not ticker:
                return {"success": False, "error": "Ticker is required"}
            
            # Simplified ticker analysis
            return {
                "success": True,
                "ticker": ticker,
                "risk_level": "MEDIUM",
                "confidence": 0.75,
                "timestamp": datetime.now().isoformat(),
                "message": f"Simplified analysis for {ticker} completed"
            }
        
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
            
    except Exception as e:
        logger.error(f"Request processing error: {e}")
        return {"success": False, "error": str(e)}


# For local testing
if __name__ == "__main__":
    # Test the API locally
    test_event = {
        "httpMethod": "POST",
        "body": json.dumps({"action": "health"})
    }
    
    result = handler(test_event, {})
    print(json.dumps(result, indent=2)) 