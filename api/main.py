import os
import json
import sqlite3
import yfinance as yf
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Vercel environment variables
XAI_API_KEY = os.environ.get("XAI_API_KEY", "")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "")
TO_EMAIL = os.environ.get("TO_EMAIL", "austin@example.com")

# Portfolio configuration
PORTFOLIO = ['AAPL']

def send_email(subject, body, to_email=None):
    """Send email notifications for high impact events and system alerts"""
    if not to_email:
        to_email = TO_EMAIL
    
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = to_email
        message["Subject"] = subject
        
        # Add body to email
        message.attach(MIMEText(body, "plain"))
        
        # Create SMTP session
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Enable TLS encryption
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        # Send email
        text = message.as_string()
        server.sendmail(SENDER_EMAIL, to_email, text)
        server.quit()
        
        return {"success": True, "message": f"Email sent to {to_email}"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def fetch_stock_data(ticker):
    """Fetch stock data and detect high impact events"""
    try:
        # Download stock data for the past 5 days
        data = yf.download(ticker, period="5d", progress=False)
        
        if data.empty:
            return {"error": f"No data found for {ticker}"}
        
        volatility = data['Close'].pct_change().std()
        
        # Event detection: Check if volatility exceeds threshold
        result = {
            "ticker": ticker,
            "volatility": float(volatility),
            "data": f"Data for {ticker}: Volatility {volatility:.2f}",
            "high_impact": volatility > 0.05
        }
        
        if volatility > 0.05:
            # Send email notification for high impact event
            subject = f"🚨 HIGH IMPACT EVENT: {ticker} Stock Alert"
            body = f"""HIGH IMPACT EVENT DETECTED

Ticker: {ticker}
Volatility: {volatility:.4f} (>0.05 threshold)
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is an automated alert from the Multi-Agent Portfolio Analysis System.
High volatility detected requiring immediate attention.

---
Multi-Agent Portfolio Analysis System
Powered by Grok 4 with Knowledge Evolution"""
            
            email_result = send_email(subject, body)
            result["email_sent"] = email_result["success"]
            result["email_error"] = email_result.get("error")
        
        return result
        
    except Exception as e:
        return {"error": str(e)}

def determine_impact_level(ticker):
    """Determine impact level based on volatility"""
    try:
        # Fetch stock data to calculate volatility
        data = yf.download(ticker, period="5d", progress=False)
        
        if data.empty:
            return {"error": f"No data found for {ticker}"}
        
        volatility = data['Close'].pct_change().std()
        
        # Determine impact level based on volatility thresholds
        if volatility > 0.05:
            impact_level = "high"
        elif volatility > 0.02:
            impact_level = "medium"
        else:
            impact_level = "low"
        
        return {
            "ticker": ticker,
            "impact_level": impact_level,
            "volatility": float(volatility),
            "message": f"Impact level for {ticker}: {impact_level} (volatility: {volatility:.4f})"
        }
        
    except Exception as e:
        return {"error": str(e)}

def analyze_portfolio():
    """Analyze the entire portfolio"""
    try:
        results = []
        high_impact_count = 0
        
        for ticker in PORTFOLIO:
            stock_data = fetch_stock_data(ticker)
            if not stock_data.get("error"):
                results.append(stock_data)
                if stock_data.get("high_impact"):
                    high_impact_count += 1
        
        # Portfolio summary
        portfolio_risk = "HIGH" if high_impact_count > len(PORTFOLIO) * 0.5 else "MEDIUM" if high_impact_count > 0 else "LOW"
        
        summary = {
            "portfolio_size": len(PORTFOLIO),
            "analyzed_stocks": len(results),
            "high_impact_count": high_impact_count,
            "portfolio_risk": portfolio_risk,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "results": results
        }
        
        return summary
        
    except Exception as e:
        return {"error": str(e)}

def handler(request):
    """Main Vercel serverless function handler"""
    try:
        # Parse request
        if request.method == "POST":
            body = request.get_json()
            action = body.get("action")
            
            if action == "analyze_ticker":
                ticker = body.get("ticker", "AAPL")
                return json.dumps(fetch_stock_data(ticker))
            
            elif action == "impact_level":
                ticker = body.get("ticker", "AAPL")
                return json.dumps(determine_impact_level(ticker))
            
            elif action == "analyze_portfolio":
                return json.dumps(analyze_portfolio())
            
            elif action == "send_test_email":
                subject = body.get("subject", "Test Email")
                message = body.get("message", "Test message from Multi-Agent Portfolio Analysis")
                return json.dumps(send_email(subject, message))
            
            else:
                return json.dumps({"error": "Invalid action"})
        
        else:
            # GET request - return system status
            return json.dumps({
                "status": "Multi-Agent Portfolio Analysis System",
                "version": "1.0.0",
                "powered_by": "Grok 4 with Knowledge Evolution",
                "portfolio": PORTFOLIO,
                "endpoints": [
                    "POST /api/main - analyze_ticker",
                    "POST /api/main - impact_level", 
                    "POST /api/main - analyze_portfolio",
                    "POST /api/main - send_test_email"
                ]
            })
            
    except Exception as e:
        return json.dumps({"error": str(e)})

# Vercel handler
def main(request):
    """Vercel entry point"""
    return handler(request) 