import os
import json
import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Environment variables with defensive checks
XAI_API_KEY = os.environ.get("XAI_API_KEY")
if not XAI_API_KEY:
    raise ValueError("XAI_API_KEY environment variable is required for NewsAgent. Set it in Vercel dashboard or local .env.")

SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
TO_EMAIL = os.environ.get("TO_EMAIL")

# Defensive checks for email configuration (required for notifications)
if not SENDER_EMAIL:
    raise ValueError("SENDER_EMAIL environment variable is required for email notifications. Set it in Vercel dashboard or local .env.")
if not SENDER_PASSWORD:
    raise ValueError("SENDER_PASSWORD environment variable is required for email notifications. Set it in Vercel dashboard or local .env.")
if not TO_EMAIL:
    raise ValueError("TO_EMAIL environment variable is required for email notifications. Set it in Vercel dashboard or local .env.")

# In-memory storage for insights
INSIGHTS_STORAGE = []

def analyze_news_sentiment(ticker: str) -> Dict[str, Any]:
    """Analyze news sentiment and estimate market impact"""
    try:
        # Get stock info for company name
        stock = yf.Ticker(ticker)
        info = stock.info
        company_name = info.get('longName', ticker)
        
        # Simulate news sentiment analysis (in production, integrate with news API)
        # This is a placeholder implementation
        current_price = info.get('currentPrice', 0)
        market_cap = info.get('marketCap', 0)
        
        # Basic sentiment analysis based on stock performance
        data = yf.download(ticker, period="1d", progress=False)
        if not data.empty:
            price_change = data['Close'].iloc[-1] - data['Close'].iloc[0]
            price_change_pct = price_change / data['Close'].iloc[0] * 100
            
            # Determine sentiment based on price movement
            if price_change_pct > 2:
                sentiment = "POSITIVE"
                impact_level = "HIGH"
            elif price_change_pct > 0.5:
                sentiment = "POSITIVE"
                impact_level = "MEDIUM"
            elif price_change_pct < -2:
                sentiment = "NEGATIVE"
                impact_level = "HIGH"
            elif price_change_pct < -0.5:
                sentiment = "NEGATIVE"
                impact_level = "MEDIUM"
            else:
                sentiment = "NEUTRAL"
                impact_level = "LOW"
        else:
            sentiment = "NEUTRAL"
            impact_level = "LOW"
            price_change_pct = 0
        
        # Create news analysis result
        result = {
            "ticker": ticker,
            "company_name": company_name,
            "sentiment": sentiment,
            "impact_level": impact_level,
            "price_change_pct": float(price_change_pct),
            "current_price": current_price,
            "market_cap": market_cap,
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "news_sentiment",
            "confidence": 0.85  # Placeholder confidence score
        }
        
        # Store insight
        insight = {
            "ticker": ticker,
            "insight": f"News Sentiment: {company_name} shows {sentiment} sentiment with {impact_level} impact",
            "timestamp": datetime.now().isoformat(),
            "agent": "NewsAgent",
            "metrics": {
                "sentiment": sentiment,
                "impact_level": impact_level,
                "price_change_pct": float(price_change_pct)
            }
        }
        INSIGHTS_STORAGE.append(insight)
        
        return result
        
    except Exception as e:
        return {"error": str(e), "ticker": ticker}

def get_market_news_impact(tickers: List[str]) -> Dict[str, Any]:
    """Analyze news impact across multiple tickers"""
    try:
        news_results = []
        high_impact_count = 0
        sentiment_summary = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
        
        for ticker in tickers:
            news_analysis = analyze_news_sentiment(ticker)
            if "error" not in news_analysis:
                news_results.append(news_analysis)
                sentiment_summary[news_analysis["sentiment"]] += 1
                if news_analysis["impact_level"] == "HIGH":
                    high_impact_count += 1
        
        # Overall market sentiment
        if sentiment_summary["POSITIVE"] > sentiment_summary["NEGATIVE"]:
            overall_sentiment = "POSITIVE"
        elif sentiment_summary["NEGATIVE"] > sentiment_summary["POSITIVE"]:
            overall_sentiment = "NEGATIVE"
        else:
            overall_sentiment = "NEUTRAL"
        
        return {
            "analyzed_tickers": len(news_results),
            "high_impact_count": high_impact_count,
            "overall_sentiment": overall_sentiment,
            "sentiment_breakdown": sentiment_summary,
            "timestamp": datetime.now().isoformat(),
            "results": news_results,
            "agent": "NewsAgent"
        }
        
    except Exception as e:
        return {"error": str(e), "agent": "NewsAgent"}

def estimate_news_impact(ticker: str, news_keywords: Optional[List[str]] = None) -> Dict[str, Any]:
    """Estimate potential market impact of news events"""
    try:
        # Get basic stock info
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Analyze recent price movements as proxy for news impact
        data = yf.download(ticker, period="5d", progress=False)
        if data.empty:
            return {"error": f"No data found for {ticker}"}
        
        # Calculate impact metrics
        volatility = data['Close'].pct_change().std()
        volume_avg = data['Volume'].mean()
        recent_volume = data['Volume'].iloc[-1]
        volume_spike = recent_volume / volume_avg if volume_avg > 0 else 1
        
        # Determine news impact level
        if volatility > 0.05 and volume_spike > 1.5:
            impact_estimate = "HIGH"
            confidence = 0.9
        elif volatility > 0.02 or volume_spike > 1.2:
            impact_estimate = "MEDIUM"
            confidence = 0.7
        else:
            impact_estimate = "LOW"
            confidence = 0.5
        
        return {
            "ticker": ticker,
            "impact_estimate": impact_estimate,
            "confidence": confidence,
            "volatility": float(volatility),
            "volume_spike": float(volume_spike),
            "recent_volume": int(recent_volume),
            "average_volume": int(volume_avg),
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "news_impact_estimation"
        }
        
    except Exception as e:
        return {"error": str(e), "ticker": ticker}

def handler(request):
    """Vercel serverless function handler for NewsAgent"""
    try:
        if request.method == "POST":
            body = request.get_json() or {}
            action = body.get("action", "analyze_sentiment")
            
            if action == "analyze_sentiment":
                ticker = body.get("ticker", "AAPL")
                return json.dumps(analyze_news_sentiment(ticker))
            
            elif action == "market_impact":
                tickers = body.get("tickers", ["AAPL"])
                return json.dumps(get_market_news_impact(tickers))
            
            elif action == "impact_estimate":
                ticker = body.get("ticker", "AAPL")
                keywords = body.get("keywords", [])
                return json.dumps(estimate_news_impact(ticker, keywords))
            
            else:
                return json.dumps({"error": "Invalid action", "available_actions": ["analyze_sentiment", "market_impact", "impact_estimate"]})
        
        else:
            return json.dumps({
                "agent": "NewsAgent",
                "description": "Analyzes news sentiment and market impact",
                "endpoints": [
                    "POST - analyze_sentiment: Analyze news sentiment for a ticker",
                    "POST - market_impact: Analyze news impact across multiple tickers",
                    "POST - impact_estimate: Estimate potential news impact"
                ],
                "status": "active"
            })
            
    except Exception as e:
        return json.dumps({"error": str(e), "agent": "NewsAgent"}) 