#!/usr/bin/env python3

"""
Multi-Agent Portfolio Analysis API - Vercel Serverless
Simple HTTP handler optimized for Vercel deployment
"""

import json
import yfinance as yf
from datetime import datetime, timedelta
from urllib.parse import parse_qs

def get_stock_analysis(ticker: str):
    """Get basic stock analysis for a ticker"""
    try:
        # Fetch stock data
        stock = yf.Ticker(ticker)
        data = stock.history(period="5d")
        
        if data.empty:
            return {"error": f"No data found for {ticker}"}
        
        # Calculate basic metrics
        current_price = data['Close'].iloc[-1]
        previous_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
        change = current_price - previous_price
        change_pct = (change / previous_price) * 100 if previous_price != 0 else 0
        
        # Calculate volatility
        volatility = data['Close'].pct_change().std() * 100
        
        # Determine impact level
        if volatility > 5:
            impact_level = "high"
        elif volatility > 2:
            impact_level = "medium"
        else:
            impact_level = "low"
        
        return {
            "ticker": ticker,
            "current_price": round(current_price, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "volatility": round(volatility, 2),
            "impact_level": impact_level,
            "timestamp": datetime.now().isoformat(),
            "data_points": len(data)
        }
    
    except Exception as e:
        return {"error": f"Error analyzing {ticker}: {str(e)}"}

def get_health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Multi-Agent Portfolio Analysis API",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/app?action=health",
            "analysis": "/api/app?ticker=SYMBOL&action=analyze"
        }
    }

def handler(request):
    """
    Vercel serverless function handler
    
    This function handles HTTP requests for the portfolio analysis API.
    It processes different actions and returns JSON responses.
    """
    try:
        # Get request method and query parameters
        method = getattr(request, 'method', 'GET')
        
        # Parse query parameters
        if hasattr(request, 'args'):
            # Flask-style request
            params = request.args
        elif hasattr(request, 'query'):
            # Raw query string
            params = parse_qs(request.query)
            # Convert lists to single values
            params = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in params.items()}
        else:
            # Fallback - no parameters
            params = {}
        
        # Get action parameter
        action = params.get('action', 'health')
        
        # Route based on action
        if action == 'health':
            result = get_health_check()
        elif action == 'analyze':
            ticker = params.get('ticker', 'AAPL')
            result = get_stock_analysis(ticker)
        else:
            result = {
                "error": "Invalid action",
                "valid_actions": ["health", "analyze"],
                "example": "/api/app?action=health"
            }
        
        # Return JSON response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            },
            'body': json.dumps(result, indent=2)
        }
    
    except Exception as e:
        # Error response
        error_response = {
            "error": "Internal server error",
            "details": str(e),
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps(error_response, indent=2)
        }

# Export handler for Vercel
app = handler 