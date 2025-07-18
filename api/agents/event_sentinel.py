import os
import json
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Environment variables with defensive checks
XAI_API_KEY = os.environ.get("XAI_API_KEY")
# Environment validation moved to runtime functions

SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
TO_EMAIL = os.environ.get("TO_EMAIL")

# In-memory storage for events and insights
EVENTS_STORAGE = []
INSIGHTS_STORAGE = []

def send_email(subject: str, body: str, to_email: Optional[str] = None) -> Dict[str, Any]:
    """Send email notifications for critical events"""
    if not to_email:
        to_email = TO_EMAIL
    
    try:
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

def detect_portfolio_events(portfolio: List[str]) -> Dict[str, Any]:
    """Detect significant events across the entire portfolio"""
    try:
        events = []
        high_volatility_count = 0
        total_volume_spike = 0
        portfolio_metrics = {}
        
        for ticker in portfolio:
            try:
                data = yf.download(ticker, period="5d", progress=False)
                if not data.empty:
                    volatility = data['Close'].pct_change().std()
                    current_price = float(data['Close'].iloc[-1])
                    volume_avg = data['Volume'].mean()
                    recent_volume = data['Volume'].iloc[-1]
                    volume_spike = recent_volume / volume_avg if volume_avg > 0 else 1
                    
                    # Store metrics
                    portfolio_metrics[ticker] = {
                        "volatility": float(volatility),
                        "current_price": current_price,
                        "volume_spike": float(volume_spike),
                        "recent_volume": int(recent_volume)
                    }
                    
                    # Detect events
                    if volatility > 0.05:
                        high_volatility_count += 1
                        events.append({
                            "type": "HIGH_VOLATILITY",
                            "ticker": ticker,
                            "message": f"HIGH VOLATILITY: {ticker} ({volatility:.4f})",
                            "volatility": float(volatility),
                            "timestamp": datetime.now().isoformat()
                        })
                    elif volatility > 0.02:
                        events.append({
                            "type": "MEDIUM_VOLATILITY",
                            "ticker": ticker,
                            "message": f"MEDIUM VOLATILITY: {ticker} ({volatility:.4f})",
                            "volatility": float(volatility),
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    # Volume spike detection
                    if volume_spike > 2.0:
                        total_volume_spike += 1
                        events.append({
                            "type": "VOLUME_SPIKE",
                            "ticker": ticker,
                            "message": f"VOLUME SPIKE: {ticker} ({volume_spike:.2f}x average)",
                            "volume_spike": float(volume_spike),
                            "timestamp": datetime.now().isoformat()
                        })
                        
            except Exception as e:
                events.append({
                    "type": "ERROR",
                    "ticker": ticker,
                    "message": f"ERROR: {ticker} - {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Portfolio-wide risk assessment
        portfolio_risk = "HIGH" if high_volatility_count > len(portfolio) * 0.5 else "MEDIUM" if high_volatility_count > 0 else "LOW"
        
        # Create event summary
        event_summary = {
            "portfolio_size": len(portfolio),
            "portfolio_risk": portfolio_risk,
            "high_volatility_count": high_volatility_count,
            "volume_spike_count": total_volume_spike,
            "total_events": len(events),
            "timestamp": datetime.now().isoformat(),
            "events": events,
            "portfolio_metrics": portfolio_metrics,
            "agent": "EventSentinel"
        }
        
        # Store events
        EVENTS_STORAGE.extend(events)
        
        # Send email for critical portfolio events
        if portfolio_risk == "HIGH":
            subject = f"🚨 PORTFOLIO ALERT: High Risk Detected ({high_volatility_count} stocks)"
            body = f"""PORTFOLIO-WIDE HIGH RISK EVENT DETECTED

Portfolio Risk Level: {portfolio_risk}
High Volatility Stocks: {high_volatility_count}/{len(portfolio)}
Volume Spikes: {total_volume_spike}
Total Events: {len(events)}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DETECTED EVENTS:
{chr(10).join(f'• {event["message"]}' for event in events[:10])}

This is a critical portfolio alert from EventSentinel.
Multiple high-impact events detected requiring immediate attention.

---
Multi-Agent Portfolio Analysis System
EventSentinel - Portfolio Monitoring"""
            
            email_result = send_email(subject, body)
            event_summary["email_sent"] = email_result["success"]
            if not email_result["success"]:
                event_summary["email_error"] = email_result.get("error")
        
        return event_summary
        
    except Exception as e:
        return {"error": str(e), "agent": "EventSentinel"}

def generate_event_summary(time_window_hours: int = 24) -> Dict[str, Any]:
    """Generate comprehensive event summary for specified time window"""
    try:
        # Calculate time window
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        # Filter recent events
        recent_events = [
            event for event in EVENTS_STORAGE 
            if datetime.fromisoformat(event["timestamp"]) > cutoff_time
        ]
        
        # Analyze event patterns
        event_types = {}
        ticker_activity = {}
        
        for event in recent_events:
            # Count event types
            event_type = event["type"]
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
            # Track ticker activity
            ticker = event["ticker"]
            if ticker not in ticker_activity:
                ticker_activity[ticker] = []
            ticker_activity[ticker].append(event)
        
        # Generate summary
        summary = {
            "time_window_hours": time_window_hours,
            "total_events": len(recent_events),
            "event_types": event_types,
            "active_tickers": len(ticker_activity),
            "ticker_activity": ticker_activity,
            "timestamp": datetime.now().isoformat(),
            "agent": "EventSentinel"
        }
        
        # Add analysis insights
        if recent_events:
            most_active_ticker = max(ticker_activity.keys(), key=lambda x: len(ticker_activity[x]))
            most_common_event = max(event_types.keys(), key=lambda x: event_types[x])
            
            summary["insights"] = {
                "most_active_ticker": most_active_ticker,
                "most_common_event": most_common_event,
                "activity_level": "HIGH" if len(recent_events) > 10 else "MEDIUM" if len(recent_events) > 5 else "LOW"
            }
        else:
            summary["insights"] = {
                "activity_level": "NONE",
                "message": "No events detected in the specified time window"
            }
        
        return summary
        
    except Exception as e:
        return {"error": str(e), "agent": "EventSentinel"}

def detect_correlations(portfolio: List[str]) -> Dict[str, Any]:
    """Detect correlations and patterns across portfolio"""
    try:
        correlations = {}
        ticker_data = {}
        
        # Collect data for all tickers
        for ticker in portfolio:
            try:
                data = yf.download(ticker, period="30d", progress=False)
                if not data.empty:
                    ticker_data[ticker] = {
                        "returns": data['Close'].pct_change().dropna(),
                        "volatility": data['Close'].pct_change().std(),
                        "volume": data['Volume'].mean()
                    }
            except Exception as e:
                continue
        
        # Calculate correlations
        correlation_pairs = []
        tickers = list(ticker_data.keys())
        
        for i in range(len(tickers)):
            for j in range(i + 1, len(tickers)):
                ticker1, ticker2 = tickers[i], tickers[j]
                
                # Calculate correlation coefficient
                returns1 = ticker_data[ticker1]["returns"]
                returns2 = ticker_data[ticker2]["returns"]
                
                # Align data
                aligned_data = returns1.align(returns2, join='inner')
                if len(aligned_data[0]) > 5:  # Minimum data points
                    correlation = aligned_data[0].corr(aligned_data[1])
                    
                    correlation_pairs.append({
                        "ticker1": ticker1,
                        "ticker2": ticker2,
                        "correlation": float(correlation),
                        "strength": "HIGH" if abs(correlation) > 0.7 else "MEDIUM" if abs(correlation) > 0.5 else "LOW"
                    })
        
        # Sort by correlation strength
        correlation_pairs.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        
        return {
            "analyzed_tickers": len(ticker_data),
            "correlation_pairs": correlation_pairs[:10],  # Top 10 correlations
            "timestamp": datetime.now().isoformat(),
            "agent": "EventSentinel"
        }
        
    except Exception as e:
        return {"error": str(e), "agent": "EventSentinel"}

def handler(request):
    """Vercel serverless function handler for EventSentinel"""
    try:
        if request.method == "POST":
            body = request.get_json() or {}
            action = body.get("action", "detect_events")
            
            if action == "detect_events":
                portfolio = body.get("portfolio", ["AAPL"])
                return json.dumps(detect_portfolio_events(portfolio))
            
            elif action == "event_summary":
                time_window = body.get("time_window_hours", 24)
                return json.dumps(generate_event_summary(time_window))
            
            elif action == "correlations":
                portfolio = body.get("portfolio", ["AAPL"])
                return json.dumps(detect_correlations(portfolio))
            
            else:
                return json.dumps({"error": "Invalid action", "available_actions": ["detect_events", "event_summary", "correlations"]})
        
        else:
            return json.dumps({
                "agent": "EventSentinel",
                "description": "Monitors portfolio-wide events and detects correlations",
                "endpoints": [
                    "POST - detect_events: Detect portfolio-wide events",
                    "POST - event_summary: Generate event summary for time window",
                    "POST - correlations: Detect correlations between tickers"
                ],
                "status": "active"
            })
            
    except Exception as e:
        return json.dumps({"error": str(e), "agent": "EventSentinel"}) 