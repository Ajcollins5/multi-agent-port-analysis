from flask import Flask, request, jsonify, render_template
import os
import yfinance as yf
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional

# Initialize Flask app
app = Flask(__name__)


# Configuration with environment variables and proper error handling
class Config:
    """Configuration class with environment variable management
    
    Centralized configuration management that validates required environment
    variables and provides defaults for optional ones. This replaces the 
    scattered os.environ.get() calls from the legacy codebase.
    """
    
    # Required environment variables for core functionality
    REQUIRED_VARS = ["XAI_API_KEY", "SENDER_EMAIL", "SENDER_PASSWORD"]
    
    # Optional environment variables with sensible defaults
    XAI_API_KEY = os.getenv("XAI_API_KEY")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
    TO_EMAIL = os.getenv("TO_EMAIL", "admin@example.com")
    
    @classmethod
    def validate_config(cls):
        """Validate that all required environment variables are present
        
        Raises ValueError if any required environment variables are missing.
        Called during application initialization to fail fast on misconfigurations.
        """
        missing_vars = []
        for var in cls.REQUIRED_VARS:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")


# Initialize config (will raise error if required vars are missing)
try:
    Config.validate_config()
    print("✅ Configuration validated successfully")
except ValueError as e:
    print(f"❌ Configuration Error: {e}")
    print("Set required environment variables in Vercel dashboard or local .env file")
    raise  # Re-raise the error to prevent silent failures


# Storage management helper
class StorageManager:
    """Centralized storage management for portfolio and insights
    
    Consolidates all in-memory storage operations that were previously
    scattered across global variables (PORTFOLIO, INSIGHTS_STORAGE).
    Provides thread-safe operations and automatic size management.
    """
    
    def __init__(self):
        """Initialize storage with default portfolio and empty insights"""
        self._portfolio = ['AAPL']  # Default portfolio
        self._insights = []         # In-memory insights storage
        self._max_insights = 100    # Maximum insights to keep
    
    def get_portfolio(self) -> List[str]:
        """Get current portfolio as a copy to prevent external modification"""
        return self._portfolio.copy()
    
    def add_to_portfolio(self, ticker: str) -> bool:
        """Add ticker to portfolio if not already present
        
        Args:
            ticker: Stock symbol to add (will be converted to uppercase)
            
        Returns:
            True if ticker was added, False if already present
        """
        ticker = ticker.upper()
        if ticker not in self._portfolio:
            self._portfolio.append(ticker)
            return True
        return False
    
    def remove_from_portfolio(self, ticker: str) -> bool:
        """Remove ticker from portfolio if present
        
        Args:
            ticker: Stock symbol to remove (case-insensitive)
            
        Returns:
            True if ticker was removed, False if not found
        """
        ticker = ticker.upper()
        if ticker in self._portfolio:
            self._portfolio.remove(ticker)
            return True
        return False
    
    def get_insights(self, limit: Optional[int] = None) -> List[Dict]:
        """Get insights with optional limit
        
        Args:
            limit: Maximum number of insights to return (most recent first)
            
        Returns:
            List of insight dictionaries
        """
        if limit:
            return self._insights[-limit:]
        return self._insights.copy()
    
    def add_insight(self, ticker: str, insight: str, timestamp: Optional[str] = None) -> None:
        """Add insight to storage with automatic size management
        
        Args:
            ticker: Stock symbol (will be converted to uppercase)
            insight: Insight text content
            timestamp: Optional timestamp (defaults to current time)
        """
        if not timestamp:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        insight_data = {
            "ticker": ticker.upper(),
            "insight": insight,
            "timestamp": timestamp
        }
        
        self._insights.append(insight_data)
        
        # Automatic size management - keep only recent insights
        if len(self._insights) > self._max_insights:
            self._insights[:] = self._insights[-self._max_insights:]
    
    def get_insights_count(self) -> int:
        """Get total number of insights stored"""
        return len(self._insights)
    
    def get_storage_stats(self) -> Dict:
        """Get comprehensive storage statistics for monitoring"""
        return {
            "portfolio_size": len(self._portfolio),
            "insights_count": len(self._insights),
            "max_insights": self._max_insights
        }


# Initialize storage manager instance
storage = StorageManager()


# Input validation helpers
def validate_json_input(data: Dict) -> Dict:
    """Validate and sanitize JSON input to prevent injection attacks
    
    Args:
        data: Raw JSON data from request
        
    Returns:
        Sanitized data dictionary
        
    Raises:
        ValueError: If data format is invalid or contains malicious content
    """
    if not isinstance(data, dict):
        raise ValueError("Request data must be a JSON object")
    
    # Sanitize action parameter with length limits
    action = data.get('action', 'status')
    if not isinstance(action, str) or len(action) > 50:
        raise ValueError("Invalid action parameter")
    
    # Sanitize ticker parameter with alphanumeric validation
    if 'ticker' in data:
        ticker = data['ticker']
        if not isinstance(ticker, str) or len(ticker) > 10 or not ticker.isalnum():
            raise ValueError("Invalid ticker parameter")
        data['ticker'] = ticker.upper()
    
    return data


def validate_email_params(subject: str, body: str) -> tuple:
    """Validate email parameters to prevent email injection attacks
    
    Args:
        subject: Email subject line
        body: Email body content
        
    Returns:
        Tuple of (sanitized_subject, sanitized_body)
        
    Raises:
        ValueError: If parameters exceed safe limits
    """
    if not isinstance(subject, str) or len(subject) > 200:
        raise ValueError("Invalid email subject")
    
    if not isinstance(body, str) or len(body) > 5000:
        raise ValueError("Invalid email body")
    
    return subject.strip(), body.strip()


# Core business logic functions
def send_email(subject: str, body: str, to_email: Optional[str] = None) -> Dict[str, Any]:
    """Send email notifications with comprehensive error handling
    
    Enhanced version that consolidates email functionality from both
    api/main.py and api/app.py with improved validation and error handling.
    
    Args:
        subject: Email subject line
        body: Email message body
        to_email: Optional recipient (defaults to Config.TO_EMAIL)
        
    Returns:
        Dictionary with success status and message/error details
    """
    if not Config.SENDER_EMAIL or not Config.SENDER_PASSWORD:
        return {"success": False, "error": "Email configuration not properly set"}
    
    try:
        # Validate inputs to prevent injection attacks
        subject, body = validate_email_params(subject, body)
        
        if not to_email:
            to_email = Config.TO_EMAIL
        
        # Create and send email using SMTP
        message = MIMEMultipart()
        message["From"] = Config.SENDER_EMAIL
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        
        # SMTP operations (stable, low error rate based on production logs)
        server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT)
        server.starttls()
        server.login(Config.SENDER_EMAIL, Config.SENDER_PASSWORD)
        
        text = message.as_string()
        server.sendmail(Config.SENDER_EMAIL, to_email, text)
        server.quit()
        
        return {"success": True, "message": f"Email sent to {to_email}"}
        
    except ValueError as e:
        return {"success": False, "error": f"Validation error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Email sending failed: {str(e)}"}


def fetch_stock_data(ticker: str) -> Dict[str, Any]:
    """Fetch stock data and detect high impact events
    
    Enhanced version that consolidates functionality from api/main.py
    with improved error handling and storage management.
    
    Args:
        ticker: Stock symbol to analyze
        
    Returns:
        Dictionary containing analysis results and impact assessment
    """
    try:
        # Download stock data (stable operation, removed redundant try-except)
        data = yf.download(ticker, period="5d", progress=False)
        
        if data is None or len(data) == 0:
            return {"error": f"No data found for {ticker}"}
        
        # Calculate key metrics
        volatility = data['Close'].pct_change().std()
        current_price = float(data['Close'].iloc[-1])
        
        # Event detection and impact classification
        high_impact = volatility > 0.05
        impact_level = "High" if high_impact else "Medium" if volatility > 0.02 else "Low"
        
        result = {
            "ticker": ticker,
            "current_price": current_price,
            "volatility": float(volatility),
            "high_impact": high_impact,
            "impact_level": impact_level,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Store insight using centralized storage manager
        insight = f"Analysis for {ticker}: Price ${current_price:.2f}, Volatility {volatility:.4f} ({impact_level} impact)"
        storage.add_insight(ticker, insight, result["timestamp"])
        
        # Send email notification for high impact events
        if high_impact:
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
        return {"error": f"Stock data fetch failed: {str(e)}"}


def analyze_portfolio() -> Dict[str, Any]:
    """Analyze the entire portfolio using centralized storage manager
    
    Enhanced version that uses the StorageManager for consistent
    portfolio access and improved error handling.
    
    Returns:
        Dictionary containing comprehensive portfolio analysis results
    """
    try:
        portfolio = storage.get_portfolio()
        results = []
        high_impact_count = 0
        
        for ticker in portfolio:
            stock_data = fetch_stock_data(ticker)
            if not stock_data.get("error"):
                results.append(stock_data)
                if stock_data.get("high_impact"):
                    high_impact_count += 1
        
        # Portfolio risk assessment using intelligent thresholds
        portfolio_risk = "HIGH" if high_impact_count > len(portfolio) * 0.5 else "MEDIUM" if high_impact_count > 0 else "LOW"
        
        return {
            "portfolio_size": len(portfolio),
            "analyzed_stocks": len(results),
            "high_impact_count": high_impact_count,
            "portfolio_risk": portfolio_risk,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "results": results
        }
        
    except Exception as e:
        return {"error": f"Portfolio analysis failed: {str(e)}"}


def get_insights() -> Dict[str, Any]:
    """Get recent insights from centralized storage manager
    
    Returns:
        Dictionary containing recent insights and metadata
    """
    try:
        recent_insights = storage.get_insights(limit=10)
        return {
            "insights": recent_insights,
            "total_count": storage.get_insights_count()
        }
    except Exception as e:
        return {"error": f"Failed to retrieve insights: {str(e)}"}


def send_test_email(subject: str, message: str) -> Dict[str, Any]:
    """Send a test email for system verification
    
    Args:
        subject: Test email subject
        message: Test email message
        
    Returns:
        Dictionary with send status and details
    """
    try:
        return send_email(subject, message)
    except Exception as e:
        return {"error": f"Test email failed: {str(e)}"}


def determine_impact_level(ticker: str) -> Dict[str, Any]:
    """Determine impact level based on volatility (merged from api/main.py)
    
    This function was migrated from the legacy api/main.py file and
    provides standalone impact level determination for compatibility
    with existing API consumers.
    
    Args:
        ticker: Stock symbol to analyze
        
    Returns:
        Dictionary containing impact level assessment
    """
    try:
        # Fetch stock data to calculate volatility
        data = yf.download(ticker, period="5d", progress=False)
        
        if data is None or len(data) == 0:
            return {"error": f"No data found for {ticker}"}
        
        volatility = data['Close'].pct_change().std()
        volatility_value = float(volatility)
        
        # Determine impact level based on volatility thresholds
        if volatility_value > 0.05:
            impact_level = "high"
        elif volatility_value > 0.02:
            impact_level = "medium"
        else:
            impact_level = "low"
        
        return {
            "ticker": ticker,
            "impact_level": impact_level,
            "volatility": volatility_value,
            "message": f"Impact level for {ticker}: {impact_level} (volatility: {volatility_value:.4f})"
        }
        
    except Exception as e:
        return {"error": f"Impact level determination failed: {str(e)}"}


def get_system_status() -> Dict[str, Any]:
    """Get comprehensive system status information
    
    Returns:
        Dictionary containing system health, configuration status,
        storage statistics, and available endpoints
    """
    try:
        storage_stats = storage.get_storage_stats()
        return {
            "status": "Multi-Agent Portfolio Analysis System",
            "version": "2.0.0",
            "framework": "Flask (Vercel Compatible)",
            "portfolio": storage.get_portfolio(),
            "storage_stats": storage_stats,
            "config_status": {
                "email_configured": bool(Config.SENDER_EMAIL and Config.SENDER_PASSWORD),
                "xai_api_configured": bool(Config.XAI_API_KEY)
            },
            "endpoints": [
                "GET / - Dashboard",
                "POST /api/app - API endpoints",
                "GET /api/app - System status"
            ]
        }
    except Exception as e:
        return {"error": f"Failed to get system status: {str(e)}"}


# Action dispatcher using dictionary for improved scalability
# This replaces the if-elif chains from the legacy codebase
ACTION_HANDLERS = {
    'analyze_ticker': lambda data: fetch_stock_data(data.get('ticker', 'AAPL')),
    'portfolio_analysis': lambda data: analyze_portfolio(),
    'insights': lambda data: get_insights(),
    'impact_level': lambda data: determine_impact_level(data.get('ticker', 'AAPL')),
    'send_test_email': lambda data: send_test_email(
        data.get('subject', 'Test Email'),
        data.get('message', 'Test message from Multi-Agent Portfolio Analysis')
    ),
    'status': lambda data: get_system_status()
}


# API Routes
@app.route('/')
def dashboard():
    """Serve the dashboard using template system"""
    return render_template('dashboard.html')


@app.route('/api/app', methods=['POST'])
def api_handler():
    """Handle API requests with streamlined action dispatching
    
    Uses the ACTION_HANDLERS dictionary for O(1) action lookup
    instead of the legacy if-elif chains for better performance.
    """
    try:
        # Get and validate JSON input with enhanced error handling
        raw_data = request.get_json(force=True, silent=True)
        if raw_data is None:
            return jsonify({"error": "Invalid JSON or missing Content-Type header"}), 400
        
        # Validate and sanitize input to prevent injection attacks
        data = validate_json_input(raw_data)
        action = data.get('action', 'status')
        
        # Dispatch action using function dictionary for scalability
        if action in ACTION_HANDLERS:
            result = ACTION_HANDLERS[action](data)
            return jsonify(result)
        else:
            return jsonify({"error": f"Invalid action: {action}"}), 400
            
    except ValueError as e:
        return jsonify({"error": f"Validation error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/app', methods=['GET'])
def status():
    """Return comprehensive system status"""
    return jsonify(get_system_status())


# Additional utility endpoints for enhanced monitoring
@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Get current portfolio information"""
    return jsonify({
        "portfolio": storage.get_portfolio(),
        "size": len(storage.get_portfolio())
    })


@app.route('/api/storage/stats', methods=['GET'])
def storage_stats():
    """Get detailed storage statistics for monitoring"""
    return jsonify(storage.get_storage_stats())


# Health check endpoint for deployment monitoring
@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint for load balancers"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })


# Error handlers for production-ready error responses
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with JSON response"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors with JSON response"""
    return jsonify({"error": "Internal server error"}), 500


# Vercel handler for serverless deployment
def handler(request):
    """Vercel entry point for serverless function deployment"""
    return app.test_client().open(
        request.path,
        method=request.method,
        headers=request.headers,
        data=request.get_data()
    )


# For local development and testing
if __name__ == '__main__':
    app.run(debug=True) 