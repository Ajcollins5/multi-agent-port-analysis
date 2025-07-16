from flask import Flask, request, jsonify, render_template_string
import os
import json
import yfinance as yf
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialize Flask app
app = Flask(__name__)

# Vercel environment variables
XAI_API_KEY = os.environ.get("XAI_API_KEY", "")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "")
TO_EMAIL = os.environ.get("TO_EMAIL", "austin@example.com")

# Portfolio configuration
PORTFOLIO = ['AAPL']

# In-memory storage for insights (since SQLite doesn't persist on Vercel)
# In production, use a proper database like PostgreSQL or Redis
INSIGHTS_STORAGE = []

def send_email(subject, body, to_email=None):
    """Send email notifications for high impact events"""
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

def fetch_stock_data(ticker):
    """Fetch stock data and detect high impact events"""
    try:
        # Download stock data for the past 5 days
        data = yf.download(ticker, period="5d", progress=False)
        
        if data.empty:
            return {"error": f"No data found for {ticker}"}
        
        volatility = data['Close'].pct_change().std()
        current_price = float(data['Close'].iloc[-1])
        
        # Event detection: Check if volatility exceeds threshold
        result = {
            "ticker": ticker,
            "current_price": current_price,
            "volatility": float(volatility),
            "high_impact": volatility > 0.05,
            "impact_level": "High" if volatility > 0.05 else "Medium" if volatility > 0.02 else "Low",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Store insight in memory
        insight = f"Analysis for {ticker}: Price ${current_price:.2f}, Volatility {volatility:.4f} ({result['impact_level']} impact)"
        INSIGHTS_STORAGE.append({
            "ticker": ticker,
            "insight": insight,
            "timestamp": result["timestamp"]
        })
        
        # Keep only last 100 insights
        if len(INSIGHTS_STORAGE) > 100:
            INSIGHTS_STORAGE[:] = INSIGHTS_STORAGE[-100:]
        
        if volatility > 0.05:
            # Send email notification for high impact event
            subject = f"🚨 HIGH IMPACT EVENT: {ticker} Stock Alert"
            body = f"""HIGH IMPACT EVENT DETECTED

Ticker: {ticker}
Current Price: ${current_price:.2f}
Volatility: {volatility:.4f} (>0.05 threshold)
Timestamp: {result["timestamp"]}

This is an automated alert from the Multi-Agent Portfolio Analysis System.
High volatility detected requiring immediate attention.

---
Multi-Agent Portfolio Analysis System
Powered by Vercel Serverless Functions"""
            
            email_result = send_email(subject, body)
            result["email_sent"] = email_result["success"]
            if not email_result["success"]:
                result["email_error"] = email_result.get("error")
        
        return result
        
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

# Dashboard HTML template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Multi-Agent Portfolio Analysis</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; margin: 10px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .metric { display: inline-block; margin: 10px; padding: 15px; background: #f8f9fa; border-radius: 5px; }
        .high { color: #dc3545; font-weight: bold; }
        .medium { color: #ffc107; font-weight: bold; }
        .low { color: #28a745; font-weight: bold; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #0056b3; }
        .alert { padding: 15px; margin: 10px 0; border-radius: 5px; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .insight { background: #e9ecef; padding: 10px; margin: 5px 0; border-radius: 5px; }
        .loading { text-align: center; padding: 20px; }
        input[type="text"] { padding: 10px; margin: 5px; border: 1px solid #ddd; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Multi-Agent Portfolio Analysis System</h1>
            <p>Powered by Vercel Serverless Functions</p>
        </div>
        
        <div class="card">
            <h2>Portfolio Dashboard</h2>
            <div id="portfolio-summary">
                <div class="loading">Loading portfolio data...</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Analyze New Ticker</h2>
            <input type="text" id="ticker-input" placeholder="Enter ticker symbol (e.g., TSLA, GOOGL)" />
            <button class="btn" onclick="analyzeStock()">Analyze</button>
            <div id="analysis-result"></div>
        </div>
        
        <div class="card">
            <h2>Recent Insights</h2>
            <div id="insights-list">
                <div class="loading">Loading insights...</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Quick Actions</h2>
            <button class="btn" onclick="analyzePortfolio()">Analyze Portfolio</button>
            <button class="btn" onclick="refreshDashboard()">Refresh Dashboard</button>
        </div>
    </div>

    <script>
        // API calls using fetch
        async function apiCall(endpoint, data = {}) {
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                return await response.json();
            } catch (error) {
                return { error: error.message };
            }
        }

        // Load portfolio summary
        async function loadPortfolioSummary() {
            const result = await apiCall('/api/app', { action: 'portfolio_analysis' });
            const summaryDiv = document.getElementById('portfolio-summary');
            
            if (result.error) {
                summaryDiv.innerHTML = `<div class="alert alert-error">Error: ${result.error}</div>`;
                return;
            }
            
            const html = `
                <div class="metric">
                    <strong>Portfolio Size:</strong> ${result.portfolio_size || 0} stocks
                </div>
                <div class="metric">
                    <strong>Risk Level:</strong> <span class="${result.portfolio_risk?.toLowerCase() || 'low'}">${result.portfolio_risk || 'LOW'}</span>
                </div>
                <div class="metric">
                    <strong>High Impact:</strong> ${result.high_impact_count || 0} stocks
                </div>
                <div class="metric">
                    <strong>Last Analysis:</strong> ${result.timestamp || 'N/A'}
                </div>
            `;
            summaryDiv.innerHTML = html;
        }

        // Load recent insights
        async function loadInsights() {
            const result = await apiCall('/api/app', { action: 'insights' });
            const insightsDiv = document.getElementById('insights-list');
            
            if (result.error) {
                insightsDiv.innerHTML = `<div class="alert alert-error">Error: ${result.error}</div>`;
                return;
            }
            
            if (result.insights && result.insights.length > 0) {
                const html = result.insights.map(insight => `
                    <div class="insight">
                        <strong>${insight.ticker}</strong> - ${insight.timestamp}<br>
                        ${insight.insight}
                    </div>
                `).join('');
                insightsDiv.innerHTML = html;
            } else {
                insightsDiv.innerHTML = '<div class="alert alert-success">No insights available yet.</div>';
            }
        }

        // Analyze individual stock
        async function analyzeStock() {
            const ticker = document.getElementById('ticker-input').value.toUpperCase();
            const resultDiv = document.getElementById('analysis-result');
            
            if (!ticker) {
                resultDiv.innerHTML = '<div class="alert alert-error">Please enter a ticker symbol.</div>';
                return;
            }
            
            resultDiv.innerHTML = '<div class="loading">Analyzing ' + ticker + '...</div>';
            
            const result = await apiCall('/api/app', { action: 'analyze_ticker', ticker: ticker });
            
            if (result.error) {
                resultDiv.innerHTML = `<div class="alert alert-error">Error: ${result.error}</div>`;
                return;
            }
            
            const html = `
                <div class="alert alert-success">
                    <strong>Analysis Complete for ${ticker}</strong><br>
                    <strong>Current Price:</strong> $${result.current_price?.toFixed(2) || 'N/A'}<br>
                    <strong>Volatility:</strong> ${result.volatility?.toFixed(4) || 'N/A'}<br>
                    <strong>Impact Level:</strong> <span class="${result.impact_level?.toLowerCase() || 'low'}">${result.impact_level || 'LOW'}</span><br>
                    ${result.high_impact ? '<strong>🚨 HIGH IMPACT EVENT DETECTED!</strong><br>' : ''}
                    ${result.email_sent ? '✅ Email notification sent' : ''}
                </div>
            `;
            resultDiv.innerHTML = html;
            
            // Refresh insights to show new analysis
            setTimeout(loadInsights, 1000);
        }

        // Analyze entire portfolio
        async function analyzePortfolio() {
            const result = await apiCall('/api/app', { action: 'portfolio_analysis' });
            
            if (result.error) {
                alert('Error analyzing portfolio: ' + result.error);
                return;
            }
            
            alert(`Portfolio analysis complete!\\n\\nRisk Level: ${result.portfolio_risk}\\nHigh Impact Events: ${result.high_impact_count}\\nAnalyzed Stocks: ${result.analyzed_stocks}`);
            
            // Refresh dashboard
            refreshDashboard();
        }

        // Refresh dashboard
        function refreshDashboard() {
            loadPortfolioSummary();
            loadInsights();
        }

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            refreshDashboard();
        });
    </script>
</body>
</html>
"""

# API Routes
@app.route('/')
def dashboard():
    """Serve the dashboard HTML"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/app', methods=['POST'])
def api_handler():
    """Handle API requests"""
    try:
        data = request.get_json() or {}
        action = data.get('action', 'status')
        
        if action == 'analyze_ticker':
            ticker = data.get('ticker', 'AAPL')
            return jsonify(fetch_stock_data(ticker))
        
        elif action == 'portfolio_analysis':
            return jsonify(analyze_portfolio())
        
        elif action == 'insights':
            # Return recent insights from memory
            recent_insights = INSIGHTS_STORAGE[-10:] if INSIGHTS_STORAGE else []
            return jsonify({
                "insights": recent_insights,
                "total_count": len(INSIGHTS_STORAGE)
            })
        
        elif action == 'send_test_email':
            subject = data.get('subject', 'Test Email')
            message = data.get('message', 'Test message from Multi-Agent Portfolio Analysis')
            return jsonify(send_email(subject, message))
        
        else:
            return jsonify({"error": "Invalid action"})
            
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/app', methods=['GET'])
def status():
    """Return system status"""
    return jsonify({
        "status": "Multi-Agent Portfolio Analysis System",
        "version": "2.0.0",
        "framework": "Flask (Vercel Compatible)",
        "portfolio": PORTFOLIO,
        "insights_count": len(INSIGHTS_STORAGE),
        "endpoints": [
            "GET / - Dashboard",
            "POST /api/app - API endpoints",
            "GET /api/app - System status"
        ]
    })

# Vercel handler
def handler(request):
    """Vercel entry point"""
    return app.test_client().open(
        request.path,
        method=request.method,
        headers=request.headers,
        data=request.get_data()
    )

# For local development
if __name__ == '__main__':
    app.run(debug=True) 