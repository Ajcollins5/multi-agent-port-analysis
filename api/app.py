import os
import json
import sqlite3
from datetime import datetime, timedelta
from api.main import fetch_stock_data, determine_impact_level, analyze_portfolio, send_email, PORTFOLIO

# In-memory database for Vercel (since SQLite files don't persist)
# In production, you'd use a proper database like PostgreSQL
def get_mock_insights():
    """Get mock insights for demonstration"""
    return [
        {
            "ticker": "AAPL",
            "insight": "Strong technical indicators showing bullish momentum",
            "timestamp": "2024-01-01 10:00:00"
        },
        {
            "ticker": "AAPL", 
            "insight": "REFINED: Market sentiment remains positive with institutional buying",
            "timestamp": "2024-01-01 11:00:00"
        },
        {
            "ticker": "TSLA",
            "insight": "High volatility detected, monitor for trend reversal",
            "timestamp": "2024-01-01 12:00:00"
        }
    ]

def get_portfolio_summary():
    """Get portfolio summary for dashboard"""
    try:
        results = []
        for ticker in PORTFOLIO:
            stock_data = fetch_stock_data(ticker)
            if not stock_data.get("error"):
                # Map to portfolio summary format
                volatility = float(stock_data["volatility"]) if stock_data["volatility"] else 0.0
                impact_level = "High" if volatility > 0.05 else "Medium" if volatility > 0.02 else "Low"
                
                results.append({
                    "ticker": ticker,
                    "volatility": volatility,
                    "impact_level": impact_level,
                    "insights": 3  # Mock insight count
                })
        
        return {
            "portfolio_data": results,
            "total_stocks": len(PORTFOLIO),
            "high_impact_count": len([r for r in results if r["impact_level"] == "High"]),
            "total_insights": sum([r["insights"] for r in results])
        }
        
    except Exception as e:
        return {"error": str(e)}

def get_recent_insights(limit=10):
    """Get recent insights for dashboard"""
    insights = get_mock_insights()
    return {
        "insights": insights[:limit],
        "total_count": len(insights)
    }

def get_event_summary():
    """Get event summary for dashboard"""
    try:
        portfolio_analysis = analyze_portfolio()
        
        events = []
        for result in portfolio_analysis.get("results", []):
            if isinstance(result, dict) and result.get("high_impact"):
                events.append({
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "type": "HIGH_IMPACT",
                    "ticker": result.get("ticker", "UNKNOWN"),
                    "message": f"High volatility detected: {result.get('volatility', 0.0):.4f}"
                })
        
        return {
            "events": events,
            "portfolio_risk": portfolio_analysis.get("portfolio_risk", "LOW"),
            "event_count": len(events)
        }
        
    except Exception as e:
        return {"error": str(e)}

def get_knowledge_evolution(ticker):
    """Get knowledge evolution data for a ticker"""
    insights = get_mock_insights()
    ticker_insights = [i for i in insights if i["ticker"] == ticker]
    
    refined_count = len([i for i in ticker_insights if i["insight"].startswith("REFINED:")])
    
    return {
        "ticker": ticker,
        "total_insights": len(ticker_insights),
        "refined_insights": refined_count,
        "evolution_rate": refined_count / len(ticker_insights) * 100 if ticker_insights else 0,
        "insights": ticker_insights
    }

def handler(request):
    """Main Vercel serverless function handler"""
    try:
        # Parse request
        if request.method == "POST":
            body = request.get_json()
            action = body.get("action")
            
            if action == "dashboard":
                return json.dumps({
                    "portfolio_summary": get_portfolio_summary(),
                    "recent_insights": get_recent_insights(5),
                    "event_summary": get_event_summary()
                })
            
            elif action == "analyze_ticker":
                ticker = body.get("ticker", "AAPL")
                return json.dumps({
                    "stock_data": fetch_stock_data(ticker),
                    "impact_level": determine_impact_level(ticker),
                    "knowledge_evolution": get_knowledge_evolution(ticker)
                })
            
            elif action == "portfolio_analysis":
                return json.dumps(analyze_portfolio())
            
            elif action == "insights":
                limit = body.get("limit", 10)
                return json.dumps(get_recent_insights(limit))
            
            elif action == "events":
                return json.dumps(get_event_summary())
            
            elif action == "knowledge_evolution":
                ticker = body.get("ticker", "AAPL")
                return json.dumps(get_knowledge_evolution(ticker))
            
            else:
                return json.dumps({"error": "Invalid action"})
        
        else:
            # GET request - return dashboard data
            return json.dumps({
                "status": "Multi-Agent Portfolio Analysis Dashboard API",
                "version": "1.0.0",
                "powered_by": "Grok 4 with Knowledge Evolution",
                "portfolio": PORTFOLIO,
                "endpoints": [
                    "POST /api/app - dashboard (complete dashboard data)",
                    "POST /api/app - analyze_ticker",
                    "POST /api/app - portfolio_analysis",
                    "POST /api/app - insights",
                    "POST /api/app - events",
                    "POST /api/app - knowledge_evolution"
                ],
                "dashboard_data": {
                    "portfolio_summary": get_portfolio_summary(),
                    "recent_insights": get_recent_insights(5),
                    "event_summary": get_event_summary()
                }
            })
            
    except Exception as e:
        return json.dumps({"error": str(e)})

# Vercel handler
def main(request):
    """Vercel entry point"""
    return handler(request) 