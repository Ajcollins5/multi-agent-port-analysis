import os
import json
import yfinance as yf
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional

# Environment variables for configuration (with fallback for build time)
XAI_API_KEY = os.environ.get("XAI_API_KEY")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
TO_EMAIL = os.environ.get("TO_EMAIL")

# Validation function for runtime use
def validate_environment():
    """Validate environment variables at runtime"""
    if not XAI_API_KEY:
        raise ValueError("XAI_API_KEY environment variable is required")
    if not SENDER_EMAIL:
        raise ValueError("SENDER_EMAIL environment variable is required")
    if not SENDER_PASSWORD:
        raise ValueError("SENDER_PASSWORD environment variable is required")
    if not TO_EMAIL:
        raise ValueError("TO_EMAIL environment variable is required")

# In-memory storage for Vercel ephemeral environment
INSIGHTS_STORAGE = []

def send_email(subject: str, body: str, to_email: Optional[str] = None) -> Dict[str, Any]:
    """Send email notifications for high impact events"""
    try:
        # Validate email configuration at runtime
        if not SENDER_EMAIL or not SENDER_PASSWORD or not TO_EMAIL:
            return {"success": False, "error": "Email configuration incomplete"}
        
        if not to_email:
            to_email = TO_EMAIL
        
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        text = message.as_string()
        server.sendmail(SENDER_EMAIL, to_email, text)
        server.quit()
        
        return {"success": True, "message": f"Email sent to {to_email}"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def fetch_stock_data(ticker: str) -> Dict[str, Any]:
    """Fetch stock data and analyze risk metrics with volatility detection"""
    try:
        # Download stock data for the past 5 days
        data = yf.download(ticker, period="5d", progress=False)
        
        if data.empty:
            return {"error": f"No data found for {ticker}"}
        
        # Calculate risk metrics
        volatility = data['Close'].pct_change().std()
        current_price = float(data['Close'].iloc[-1])
        price_change = float(data['Close'].iloc[-1] - data['Close'].iloc[-2])
        volume = int(data['Volume'].iloc[-1]) if not data['Volume'].empty else 0
        
        # Determine impact level
        if volatility > 0.05:
            impact_level = "HIGH"
        elif volatility > 0.02:
            impact_level = "MEDIUM"
        else:
            impact_level = "LOW"
        
        # Create result object
        result = {
            "ticker": ticker,
            "current_price": current_price,
            "price_change": price_change,
            "volatility": float(volatility),
            "volume": volume,
            "impact_level": impact_level,
            "high_impact": volatility > 0.05,
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "risk_assessment"
        }
        
        # Store insight in memory
        insight = {
            "ticker": ticker,
            "insight": f"Risk Analysis: {ticker} volatility {volatility:.4f}, impact level {impact_level}",
            "timestamp": datetime.now().isoformat(),
            "agent": "RiskAgent",
            "metrics": {
                "volatility": float(volatility),
                "current_price": current_price,
                "impact_level": impact_level
            }
        }
        INSIGHTS_STORAGE.append(insight)
        
        # Send email notification for high impact events
        if volatility > 0.05:
            subject = f"🚨 HIGH IMPACT EVENT: {ticker} Risk Alert"
            body = f"""HIGH IMPACT RISK EVENT DETECTED

Ticker: {ticker}
Current Price: ${current_price:.2f}
Price Change: ${price_change:.2f}
Volatility: {volatility:.4f} (>0.05 threshold)
Impact Level: {impact_level}
Volume: {volume:,}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

RISK ASSESSMENT:
- Volatility exceeds 5% threshold
- High impact event detected
- Immediate attention required

This is an automated alert from the Multi-Agent Portfolio Analysis System.
Risk analysis performed by RiskAgent with real-time market data.

---
Multi-Agent Portfolio Analysis System
Powered by Vercel Serverless Functions"""
            
            email_result = send_email(subject, body)
            result["email_sent"] = email_result["success"]
            if not email_result["success"]:
                result["email_error"] = email_result.get("error")
        
        return result
        
    except Exception as e:
        return {"error": str(e), "ticker": ticker}

def determine_impact_level(ticker: str) -> Dict[str, Any]:
    """Determine impact level based on volatility analysis"""
    try:
        data = yf.download(ticker, period="5d", progress=False)
        
        if data.empty:
            return {"error": f"No data found for {ticker}"}
        
        volatility = data['Close'].pct_change().std()
        
        if volatility > 0.05:
            impact_level = "HIGH"
            risk_score = 5
        elif volatility > 0.02:
            impact_level = "MEDIUM"
            risk_score = 3
        else:
            impact_level = "LOW"
            risk_score = 1
        
        return {
            "ticker": ticker,
            "impact_level": impact_level,
            "risk_score": risk_score,
            "volatility": float(volatility),
            "timestamp": datetime.now().isoformat(),
            "analysis": f"Impact level for {ticker}: {impact_level} (volatility: {volatility:.4f})"
        }
        
    except Exception as e:
        return {"error": str(e), "ticker": ticker}

def analyze_portfolio_risk(portfolio: list) -> Dict[str, Any]:
    """Analyze risk across entire portfolio"""
    try:
        portfolio_results = []
        high_risk_count = 0
        total_volatility = 0
        
        for ticker in portfolio:
            stock_analysis = fetch_stock_data(ticker)
            if "error" not in stock_analysis:
                portfolio_results.append(stock_analysis)
                total_volatility += stock_analysis["volatility"]
                if stock_analysis["high_impact"]:
                    high_risk_count += 1
        
        # Calculate portfolio risk level
        avg_volatility = total_volatility / len(portfolio_results) if portfolio_results else 0
        portfolio_risk = "HIGH" if high_risk_count > len(portfolio) * 0.5 else "MEDIUM" if high_risk_count > 0 else "LOW"
        
        return {
            "portfolio_size": len(portfolio),
            "analyzed_stocks": len(portfolio_results),
            "high_risk_count": high_risk_count,
            "portfolio_risk": portfolio_risk,
            "average_volatility": avg_volatility,
            "timestamp": datetime.now().isoformat(),
            "results": portfolio_results,
            "agent": "RiskAgent"
        }
        
    except Exception as e:
        return {"error": str(e), "agent": "RiskAgent"}

def handler(request):
    """Vercel serverless function handler for RiskAgent"""
    try:
        if request.method == "POST":
            body = request.get_json() or {}
            action = body.get("action", "analyze_stock")
            
            if action == "analyze_stock":
                ticker = body.get("ticker", "AAPL")
                return json.dumps(fetch_stock_data(ticker))
            
            elif action == "impact_level":
                ticker = body.get("ticker", "AAPL")
                return json.dumps(determine_impact_level(ticker))
            
            elif action == "portfolio_risk":
                portfolio = body.get("portfolio", ["AAPL"])
                return json.dumps(analyze_portfolio_risk(portfolio))
            
            else:
                return json.dumps({"error": "Invalid action", "available_actions": ["analyze_stock", "impact_level", "portfolio_risk"]})
        
        else:
            return json.dumps({
                "agent": "RiskAgent",
                "description": "Analyzes stock risk, volatility, and impact levels",
                "endpoints": [
                    "POST - analyze_stock: Analyze individual stock risk",
                    "POST - impact_level: Determine risk impact level",
                    "POST - portfolio_risk: Analyze portfolio-wide risk"
                ],
                "status": "active"
            })
            
    except Exception as e:
        return json.dumps({"error": str(e), "agent": "RiskAgent"}) 