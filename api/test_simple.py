#!/usr/bin/env python3
"""
Simple test function to verify Vercel deployment works
"""

import json
from datetime import datetime


def handler(event, context):
    """Simple Vercel function handler for testing"""
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
        
        # Simple response
        response_data = {
            "success": True,
            "message": "Simple test function working",
            "timestamp": datetime.now().isoformat(),
            "method": event.get("httpMethod", "GET"),
            "path": event.get("path", "/"),
            "user_agent": event.get("headers", {}).get("user-agent", "unknown")
        }
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": json.dumps(response_data)
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"success": False, "error": str(e)})
        } 