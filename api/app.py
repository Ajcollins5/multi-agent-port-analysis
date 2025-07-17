#!/usr/bin/env python3
"""
Multi-Agent Portfolio Analysis API - Vercel Serverless
Simple HTTP handler optimized for Vercel deployment
"""

import os
import json
import sqlite3
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from urllib.parse import parse_qs

def get_stock_analysis(ticker: str) -> Dict[str, Any]:
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
        
        volatility = data['Close'].pct_change().std()
        
        # Determine risk level
        if volatility > 0.05:
            risk_level = "high"
        elif volatility > 0.02:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "ticker": ticker,
            "current_price": round(current_price, 2),
            "change": round(change, 2),
            "change_percent": round(change_pct, 2),
            "volatility": round(volatility, 4),
            "risk_level": risk_level,
            "timestamp": datetime.now().isoformat(),
            "data_points": len(data)
        }
        
    except Exception as e:
        return {"error": f"Error analyzing {ticker}: {str(e)}"}

def handler(request, context):
    """Vercel serverless handler - proper format for Vercel Python runtime"""
    try:
        # Handle CORS preflight requests
        if request.method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                },
                'body': ''
            }
        
        # Parse query parameters
        query_params = {}
        if hasattr(request, 'args'):
            query_params = dict(request.args)
        elif hasattr(request, 'url') and '?' in request.url:
            query_string = request.url.split('?', 1)[1]
            query_params = {k: v[0] if isinstance(v, list) else v 
                          for k, v in parse_qs(query_string).items()}
        
        # Parse request body
        body = ''
        if hasattr(request, 'get_data'):
            body = request.get_data(as_text=True)
        elif hasattr(request, 'data'):
            body = request.data.decode('utf-8') if isinstance(request.data, bytes) else str(request.data)
        
        # Parse JSON body
        body_data = {}
        if body and body.strip():
            try:
                body_data = json.loads(body)
            except json.JSONDecodeError:
                pass
        
        # Get parameters
        ticker = query_params.get('ticker') or body_data.get('ticker', 'AAPL')
        action = query_params.get('action') or body_data.get('action', 'analyze')
        
        # Handle different actions
        if action == 'analyze':
            result = get_stock_analysis(ticker)
        elif action == 'health':
            result = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "service": "multi-agent-portfolio-analysis"
            }
        else:
            result = {"error": f"Unknown action: {action}"}
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({"error": f"Internal server error: {str(e)}"})
        }

# For local testing
if __name__ == "__main__":
    # Simple test
    class MockRequest:
        def __init__(self):
            self.method = 'GET'
            self.args = {'ticker': 'AAPL', 'action': 'analyze'}
            
        def get_data(self, as_text=False):
            return '{}'
    
    result = handler(MockRequest(), None)
    print(json.dumps(json.loads(result['body']), indent=2)) 