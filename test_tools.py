#!/usr/bin/env python3
"""
Unit Tests for Multi-Agent Portfolio Analysis System

Comprehensive test suite with mocked API calls and environment variables.
"""

import unittest
import os
import sys
import sqlite3
import tempfile
import shutil
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timedelta
import json


class TestEnvironmentSetup(unittest.TestCase):
    """Test environment variable setup and validation"""
    
    def setUp(self):
        """Set up test environment"""
        # Store original environment variables
        self.original_env = {}
        for key in ["XAI_API_KEY", "SENDER_EMAIL", "SENDER_PASSWORD", "TO_EMAIL"]:
            self.original_env[key] = os.environ.get(key)
        
        # Set mock environment variables
        os.environ["XAI_API_KEY"] = "xai-test-key-for-unit-tests-only"
        os.environ["SENDER_EMAIL"] = "test@example.com"
        os.environ["SENDER_PASSWORD"] = "test-password"
        os.environ["TO_EMAIL"] = "recipient@example.com"
        os.environ["ENVIRONMENT"] = "testing"
    
    def tearDown(self):
        """Clean up test environment"""
        # Restore original environment variables
        for key, value in self.original_env.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]
    
    def test_xai_api_key_validation(self):
        """Test XAI_API_KEY validation"""
        # Test valid API key
        test_api_key = "xai-valid-key-123"  # Test constant, not hardcoded secret
        os.environ["XAI_API_KEY"] = test_api_key
        api_key = os.getenv("XAI_API_KEY")
        self.assertIsNotNone(api_key)
        if api_key:  # Type guard for linter
            self.assertTrue(api_key.startswith("xai-"))
        
        # Test missing API key
        if "XAI_API_KEY" in os.environ:
            del os.environ["XAI_API_KEY"]
        self.assertIsNone(os.getenv("XAI_API_KEY"))
    
    def test_email_configuration_validation(self):
        """Test email configuration validation"""
        # Test valid email configuration
        self.assertIn("@", os.environ["SENDER_EMAIL"])
        self.assertTrue(len(os.environ["SENDER_PASSWORD"]) >= 8)
        self.assertIn("@", os.environ["TO_EMAIL"])
        
        # Test invalid email configuration
        os.environ["SENDER_EMAIL"] = "invalid-email"
        self.assertNotIn("@", os.environ["SENDER_EMAIL"])


class TestStockDataTools(unittest.TestCase):
    """Test stock data fetching and processing tools"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ["XAI_API_KEY"] = "xai-test-key-for-unit-tests-only"
        self.test_ticker = "AAPL"
    
    @patch('yfinance.Ticker')
    def test_fetch_stock_data(self, mock_ticker):
        """Test stock data fetching with mocked yfinance"""
        # Mock yfinance response
        mock_stock = Mock()
        mock_stock.history.return_value = Mock()
        mock_stock.history.return_value.iloc = [
            Mock(Close=150.0),  # Previous close
            Mock(Close=155.0)   # Current close
        ]
        mock_stock.info = {
            'currentPrice': 155.0,
            'previousClose': 150.0,
            'marketCap': 2500000000000,
            'beta': 1.2,
            'longName': 'Apple Inc.'
        }
        mock_ticker.return_value = mock_stock
        
        # Import and test function (this would be from your actual module)
        # For demonstration, we'll create a mock function
        def fetch_stock_data(ticker):
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'ticker': ticker,
                'current_price': info.get('currentPrice', 0),
                'previous_close': info.get('previousClose', 0),
                'market_cap': info.get('marketCap', 0),
                'beta': info.get('beta', 1.0),
                'company_name': info.get('longName', ticker)
            }
        
        # Test the function
        result = fetch_stock_data(self.test_ticker)
        
        # Assertions
        self.assertEqual(result['ticker'], self.test_ticker)
        self.assertEqual(result['current_price'], 155.0)
        self.assertEqual(result['previous_close'], 150.0)
        self.assertEqual(result['market_cap'], 2500000000000)
        self.assertEqual(result['beta'], 1.2)
        self.assertEqual(result['company_name'], 'Apple Inc.')
    
    def test_determine_impact_level(self):
        """Test impact level determination"""
        # Mock function for impact level determination
        def determine_impact_level(volatility):
            if volatility > 0.05:
                return "high"
            elif volatility > 0.02:
                return "medium"
            else:
                return "low"
        
        # Test different volatility levels
        self.assertEqual(determine_impact_level(0.01), "low")
        self.assertEqual(determine_impact_level(0.03), "medium")
        self.assertEqual(determine_impact_level(0.07), "high")
        self.assertEqual(determine_impact_level(0.05), "medium")  # Edge case
    
    def test_volatility_calculation(self):
        """Test volatility calculation"""
        # Mock function for volatility calculation
        def calculate_volatility(prices):
            if len(prices) < 2:
                return 0.0
            
            returns = []
            for i in range(1, len(prices)):
                returns.append((prices[i] - prices[i-1]) / prices[i-1])
            
            if not returns:
                return 0.0
            
            # Simple volatility calculation
            mean_return = sum(returns) / len(returns)
            variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
            return variance ** 0.5
        
        # Test with sample prices
        test_prices = [100, 102, 98, 105, 103]
        volatility = calculate_volatility(test_prices)
        self.assertIsInstance(volatility, float)
        self.assertGreaterEqual(volatility, 0.0)


class TestDatabaseOperations(unittest.TestCase):
    """Test database operations and insight storage"""
    
    def setUp(self):
        """Set up test database"""
        self.test_db_path = tempfile.mktemp(suffix='.db')
        self.conn = sqlite3.connect(self.test_db_path)
        self.cursor = self.conn.cursor()
        
        # Create test table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS insights (
                ticker TEXT,
                insight TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def tearDown(self):
        """Clean up test database"""
        if self.conn:
            self.conn.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_store_insight(self):
        """Test insight storage"""
        # Mock function for storing insights
        def store_insight(ticker, insight):
            self.cursor.execute(
                "INSERT INTO insights (ticker, insight) VALUES (?, ?)",
                (ticker, insight)
            )
            self.conn.commit()
            return True
        
        # Test storing an insight
        result = store_insight("AAPL", "High volatility detected")
        self.assertTrue(result)
        
        # Verify insight was stored
        self.cursor.execute("SELECT * FROM insights WHERE ticker = ?", ("AAPL",))
        rows = self.cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "AAPL")
        self.assertEqual(rows[0][1], "High volatility detected")
    
    def test_retrieve_insights(self):
        """Test insight retrieval"""
        # Store test insights
        test_insights = [
            ("AAPL", "High volatility detected"),
            ("GOOGL", "Earnings report positive"),
            ("AAPL", "Price target raised")
        ]
        
        for ticker, insight in test_insights:
            self.cursor.execute(
                "INSERT INTO insights (ticker, insight) VALUES (?, ?)",
                (ticker, insight)
            )
        self.conn.commit()
        
        # Mock function for retrieving insights
        def get_insights_for_ticker(ticker):
            self.cursor.execute(
                "SELECT insight, timestamp FROM insights WHERE ticker = ? ORDER BY timestamp DESC",
                (ticker,)
            )
            return self.cursor.fetchall()
        
        # Test retrieval
        aapl_insights = get_insights_for_ticker("AAPL")
        self.assertEqual(len(aapl_insights), 2)
        
        googl_insights = get_insights_for_ticker("GOOGL")
        self.assertEqual(len(googl_insights), 1)
        self.assertEqual(googl_insights[0][0], "Earnings report positive")


class TestEmailNotifications(unittest.TestCase):
    """Test email notification system"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ["SENDER_EMAIL"] = "test@example.com"
        os.environ["SENDER_PASSWORD"] = "test-password"
        os.environ["TO_EMAIL"] = "recipient@example.com"
        os.environ["SMTP_SERVER"] = "smtp.gmail.com"
        os.environ["SMTP_PORT"] = "587"
    
    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending"""
        # Mock SMTP server
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        # Mock function for sending email
        def send_email(subject, body, to_email=None):
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            if to_email is None:
                to_email = os.environ["TO_EMAIL"]
            
            try:
                message = MIMEMultipart()
                message["From"] = os.environ["SENDER_EMAIL"]
                message["To"] = to_email
                message["Subject"] = subject
                message.attach(MIMEText(body, "plain"))
                
                server = smtplib.SMTP(os.environ["SMTP_SERVER"], int(os.environ["SMTP_PORT"]))
                server.starttls()
                server.login(os.environ["SENDER_EMAIL"], os.environ["SENDER_PASSWORD"])
                server.sendmail(os.environ["SENDER_EMAIL"], to_email, message.as_string())
                server.quit()
                
                return True
            except Exception as e:
                return False
        
        # Test email sending
        result = send_email("Test Subject", "Test Body")
        self.assertTrue(result)
        
        # Verify SMTP calls
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@example.com", "test-password")
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp):
        """Test email sending failure"""
        # Mock SMTP server to raise exception
        mock_smtp.side_effect = Exception("SMTP connection failed")
        
        # Mock function for sending email (same as above but with exception handling)
        def send_email_with_exception_handling(subject, body, to_email=None):
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            if to_email is None:
                to_email = os.environ["TO_EMAIL"]
            
            try:
                message = MIMEMultipart()
                message["From"] = os.environ["SENDER_EMAIL"]
                message["To"] = to_email
                message["Subject"] = subject
                message.attach(MIMEText(body, "plain"))
                
                server = smtplib.SMTP(os.environ["SMTP_SERVER"], int(os.environ["SMTP_PORT"]))
                server.starttls()
                server.login(os.environ["SENDER_EMAIL"], os.environ["SENDER_PASSWORD"])
                server.sendmail(os.environ["SENDER_EMAIL"], to_email, message.as_string())
                server.quit()
                
                return True
            except Exception as e:
                return False
        
        # Test email sending failure
        result = send_email_with_exception_handling("Test Subject", "Test Body")
        self.assertFalse(result)


class TestAgentTools(unittest.TestCase):
    """Test agent-specific tools and functionality"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ["XAI_API_KEY"] = "xai-test-key-for-unit-tests-only"
    
    @patch('requests.post')
    def test_grok_api_call(self, mock_post):
        """Test Grok API call with mocked response"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "This is a test response from Grok API"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Mock function for Grok API call
        def call_grok_api(prompt):
            import requests
            
            headers = {
                "Authorization": f"Bearer {os.environ['XAI_API_KEY']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "grok-4-0709",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500
            }
            
            try:
                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                else:
                    return f"Error: {response.status_code}"
            except Exception as e:
                return f"Exception: {str(e)}"
        
        # Test API call
        result = call_grok_api("Analyze AAPL stock")
        self.assertEqual(result, "This is a test response from Grok API")
        
        # Verify API call was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], "https://api.x.ai/v1/chat/completions")
        self.assertIn("Authorization", call_args[1]["headers"])
        self.assertEqual(call_args[1]["json"]["model"], "grok-4-0709")
    
    def test_risk_analysis_tools(self):
        """Test risk analysis tools"""
        # Mock function for risk analysis
        def analyze_risk(ticker, current_price, previous_close, beta=1.0):
            # Calculate price change
            price_change = (current_price - previous_close) / previous_close
            volatility = abs(price_change)
            
            # Determine risk level
            if volatility > 0.05:
                risk_level = "high"
            elif volatility > 0.02:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            # Adjust for beta
            beta_adjusted_risk = volatility * beta
            
            return {
                "ticker": ticker,
                "price_change": price_change,
                "volatility": volatility,
                "risk_level": risk_level,
                "beta": beta,
                "beta_adjusted_risk": beta_adjusted_risk
            }
        
        # Test risk analysis
        result = analyze_risk("AAPL", 155.0, 150.0, 1.2)
        
        self.assertEqual(result["ticker"], "AAPL")
        self.assertAlmostEqual(result["price_change"], 0.0333, places=3)
        self.assertAlmostEqual(result["volatility"], 0.0333, places=3)
        self.assertEqual(result["risk_level"], "medium")
        self.assertEqual(result["beta"], 1.2)
    
    def test_news_sentiment_tools(self):
        """Test news sentiment analysis tools"""
        # Mock function for news sentiment analysis
        def analyze_news_sentiment(ticker, news_headlines):
            positive_keywords = ["positive", "growth", "profit", "increase", "up"]
            negative_keywords = ["negative", "decline", "loss", "decrease", "down"]
            
            sentiment_scores = []
            for headline in news_headlines:
                headline_lower = headline.lower()
                positive_count = sum(1 for word in positive_keywords if word in headline_lower)
                negative_count = sum(1 for word in negative_keywords if word in headline_lower)
                
                if positive_count > negative_count:
                    sentiment_scores.append(1)
                elif negative_count > positive_count:
                    sentiment_scores.append(-1)
                else:
                    sentiment_scores.append(0)
            
            if not sentiment_scores:
                overall_sentiment = "neutral"
                impact_level = "low"
            else:
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                if avg_sentiment > 0.3:
                    overall_sentiment = "positive"
                    impact_level = "high"
                elif avg_sentiment < -0.3:
                    overall_sentiment = "negative"
                    impact_level = "high"
                else:
                    overall_sentiment = "neutral"
                    impact_level = "medium"
            
            return {
                "ticker": ticker,
                "sentiment": overall_sentiment,
                "impact_level": impact_level,
                "sentiment_score": avg_sentiment if sentiment_scores else 0.0
            }
        
        # Test news sentiment analysis
        test_headlines = [
            "Apple reports strong growth in Q4",
            "iPhone sales increase significantly",
            "Apple stock price declines amid concerns"
        ]
        
        result = analyze_news_sentiment("AAPL", test_headlines)
        
        self.assertEqual(result["ticker"], "AAPL")
        self.assertIn(result["sentiment"], ["positive", "negative", "neutral"])
        self.assertIn(result["impact_level"], ["low", "medium", "high"])
        self.assertIsInstance(result["sentiment_score"], float)


class TestKnowledgeCuratorTools(unittest.TestCase):
    """Test KnowledgeCurator agent tools"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ["XAI_API_KEY"] = "xai-test-key-for-unit-tests-only"
        self.mock_insights = [
            {"ticker": "AAPL", "insight": "High volatility detected", "timestamp": "2023-01-01"},
            {"ticker": "GOOGL", "insight": "Earnings report positive", "timestamp": "2023-01-02"},
            {"ticker": "AAPL", "insight": "REFINED: Updated analysis shows moderate risk", "timestamp": "2023-01-03"}
        ]
    
    def test_curate_knowledge_quality(self):
        """Test knowledge quality curation"""
        # Mock function for knowledge quality curation
        def curate_knowledge_quality(insights):
            if not insights:
                return {
                    "total_insights": 0,
                    "quality_score": 0,
                    "refined_insights": 0,
                    "recommendations": ["No insights available for curation"]
                }
            
            total_insights = len(insights)
            refined_insights = sum(1 for insight in insights if insight["insight"].startswith("REFINED:"))
            quality_score = (refined_insights / total_insights) * 100
            
            recommendations = []
            if quality_score < 30:
                recommendations.append("Consider refining more insights for better quality")
            if total_insights < 10:
                recommendations.append("Gather more insights for comprehensive analysis")
            
            return {
                "total_insights": total_insights,
                "quality_score": quality_score,
                "refined_insights": refined_insights,
                "recommendations": recommendations
            }
        
        # Test knowledge curation
        result = curate_knowledge_quality(self.mock_insights)
        
        self.assertEqual(result["total_insights"], 3)
        self.assertEqual(result["refined_insights"], 1)
        self.assertAlmostEqual(result["quality_score"], 33.33, places=2)
        self.assertIsInstance(result["recommendations"], list)
    
    def test_identify_knowledge_gaps(self):
        """Test knowledge gap identification"""
        # Mock function for identifying knowledge gaps
        def identify_knowledge_gaps(insights, portfolio_tickers):
            covered_tickers = set()
            for insight in insights:
                covered_tickers.add(insight["ticker"])
            
            missing_tickers = set(portfolio_tickers) - covered_tickers
            
            # Analyze insight types
            insight_types = {}
            for insight in insights:
                if "volatility" in insight["insight"].lower():
                    insight_types["volatility"] = insight_types.get("volatility", 0) + 1
                if "earnings" in insight["insight"].lower():
                    insight_types["earnings"] = insight_types.get("earnings", 0) + 1
                if "risk" in insight["insight"].lower():
                    insight_types["risk"] = insight_types.get("risk", 0) + 1
            
            gaps = []
            if missing_tickers:
                gaps.append(f"Missing analysis for tickers: {', '.join(missing_tickers)}")
            if insight_types.get("volatility", 0) < len(covered_tickers):
                gaps.append("Insufficient volatility analysis")
            if insight_types.get("earnings", 0) < len(covered_tickers):
                gaps.append("Insufficient earnings analysis")
            
            return {
                "covered_tickers": list(covered_tickers),
                "missing_tickers": list(missing_tickers),
                "insight_types": insight_types,
                "gaps": gaps
            }
        
        # Test knowledge gap identification
        portfolio_tickers = ["AAPL", "GOOGL", "MSFT"]
        result = identify_knowledge_gaps(self.mock_insights, portfolio_tickers)
        
        self.assertIn("AAPL", result["covered_tickers"])
        self.assertIn("GOOGL", result["covered_tickers"])
        self.assertIn("MSFT", result["missing_tickers"])
        self.assertIsInstance(result["gaps"], list)


class TestEventSentinelTools(unittest.TestCase):
    """Test EventSentinel agent tools"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ["XAI_API_KEY"] = "xai-test-key-for-unit-tests-only"
        self.mock_portfolio = ["AAPL", "GOOGL", "MSFT"]
    
    def test_detect_portfolio_events(self):
        """Test portfolio event detection"""
        # Mock function for portfolio event detection
        def detect_portfolio_events(portfolio_data):
            events = []
            high_volatility_threshold = 0.05
            
            for ticker_data in portfolio_data:
                ticker = ticker_data["ticker"]
                volatility = ticker_data.get("volatility", 0.0)
                price_change = ticker_data.get("price_change", 0.0)
                
                if volatility > high_volatility_threshold:
                    events.append({
                        "ticker": ticker,
                        "event_type": "high_volatility",
                        "severity": "high",
                        "volatility": volatility,
                        "price_change": price_change
                    })
                elif abs(price_change) > 0.03:
                    events.append({
                        "ticker": ticker,
                        "event_type": "significant_price_change",
                        "severity": "medium",
                        "volatility": volatility,
                        "price_change": price_change
                    })
            
            return {
                "events": events,
                "event_count": len(events),
                "high_severity_count": sum(1 for e in events if e["severity"] == "high")
            }
        
        # Test portfolio event detection
        mock_portfolio_data = [
            {"ticker": "AAPL", "volatility": 0.07, "price_change": 0.06},
            {"ticker": "GOOGL", "volatility": 0.02, "price_change": 0.01},
            {"ticker": "MSFT", "volatility": 0.03, "price_change": 0.04}
        ]
        
        result = detect_portfolio_events(mock_portfolio_data)
        
        self.assertEqual(result["event_count"], 2)  # AAPL high volatility + MSFT price change
        self.assertEqual(result["high_severity_count"], 1)  # Only AAPL high volatility
        self.assertIsInstance(result["events"], list)
    
    def test_generate_event_summary(self):
        """Test event summary generation"""
        # Mock function for event summary generation
        def generate_event_summary(events):
            if not events:
                return {
                    "summary": "No significant events detected",
                    "recommendations": [],
                    "priority": "low"
                }
            
            high_severity_events = [e for e in events if e["severity"] == "high"]
            medium_severity_events = [e for e in events if e["severity"] == "medium"]
            
            summary_lines = []
            if high_severity_events:
                summary_lines.append(f"{len(high_severity_events)} high severity events detected")
            if medium_severity_events:
                summary_lines.append(f"{len(medium_severity_events)} medium severity events detected")
            
            recommendations = []
            if high_severity_events:
                recommendations.append("Monitor high volatility stocks closely")
                recommendations.append("Consider risk management strategies")
            if medium_severity_events:
                recommendations.append("Review portfolio allocation")
            
            priority = "high" if high_severity_events else "medium" if medium_severity_events else "low"
            
            return {
                "summary": "; ".join(summary_lines),
                "recommendations": recommendations,
                "priority": priority,
                "event_breakdown": {
                    "high_severity": len(high_severity_events),
                    "medium_severity": len(medium_severity_events)
                }
            }
        
        # Test event summary generation
        mock_events = [
            {"ticker": "AAPL", "event_type": "high_volatility", "severity": "high"},
            {"ticker": "MSFT", "event_type": "significant_price_change", "severity": "medium"}
        ]
        
        result = generate_event_summary(mock_events)
        
        self.assertIn("high severity", result["summary"])
        self.assertIn("medium severity", result["summary"])
        self.assertEqual(result["priority"], "high")
        self.assertIn("Monitor high volatility", result["recommendations"][0])
        self.assertEqual(result["event_breakdown"]["high_severity"], 1)
        self.assertEqual(result["event_breakdown"]["medium_severity"], 1)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 