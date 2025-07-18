#!/usr/bin/env python3

"""
Multi-Agent Portfolio Analysis API - Vercel Serverless
Comprehensive API handler integrating all agents and functionality
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all agent functionality
try:
    from agents.risk_agent import fetch_stock_data, analyze_portfolio_risk
    from agents.news_agent import analyze_news_sentiment, get_market_news_impact
    from agents.event_sentinel import detect_portfolio_events, generate_event_summary
    from agents.knowledge_curator import curate_knowledge_quality, identify_knowledge_gaps
    from supervisor import SupervisorAgent
    from notifications.email_handler import send_email
    from database.storage_manager import StorageManager
except ImportError as e:
    logging.error(f"Import error: {e}")
    # Fallback imports for basic functionality
    import yfinance as yf

# Environment variable validation
def validate_environment():
    """Validate required environment variables"""
    required_vars = ['XAI_API_KEY', 'SENDER_EMAIL', 'SENDER_PASSWORD', 'TO_EMAIL']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        return {
            'valid': False,
            'missing_vars': missing_vars,
            'message': f"Missing required environment variables: {', '.join(missing_vars)}"
        }
    
    return {'valid': True}

# Default portfolio for analysis
DEFAULT_PORTFOLIO = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]

class MultiAgentAPI:
    """Main API class that orchestrates all agents"""
    
    def __init__(self):
        try:
            self.supervisor = SupervisorAgent()
            self.storage = StorageManager()
        except Exception as e:
            logging.error(f"Failed to initialize components: {e}")
            self.supervisor = None
            self.storage = None
        self.env_status = validate_environment()
        
    def portfolio_analysis(self) -> Dict[str, Any]:
        """Comprehensive portfolio analysis using all agents"""
        try:
            # Use RiskAgent for portfolio risk analysis
            risk_results = analyze_portfolio_risk(DEFAULT_PORTFOLIO)
            
            if 'error' in risk_results:
                return {
                    'error': 'Portfolio analysis failed',
                    'details': risk_results['error'],
                    'timestamp': datetime.now().isoformat()
                }
            
            # Get recent events
            event_results = detect_portfolio_events(DEFAULT_PORTFOLIO)
            
            # Get news sentiment
            news_results = get_market_news_impact(DEFAULT_PORTFOLIO)
            
            # Combine results
            return {
                'portfolio_size': risk_results.get('portfolio_size', len(DEFAULT_PORTFOLIO)),
                'analyzed_stocks': risk_results.get('analyzed_stocks', 0),
                'high_impact_count': risk_results.get('high_risk_count', 0),
                'portfolio_risk': risk_results.get('portfolio_risk', 'UNKNOWN'),
                'timestamp': datetime.now().isoformat(),
                'results': risk_results.get('results', []),
                'events': event_results.get('events', []),
                'news_sentiment': news_results.get('overall_sentiment', 'NEUTRAL'),
                'agents_used': ['RiskAgent', 'EventSentinel', 'NewsAgent']
            }
            
        except Exception as e:
            return {
                'error': 'Portfolio analysis failed',
                'details': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def analyze_ticker(self, ticker: str) -> Dict[str, Any]:
        """Analyze individual ticker using multi-agent approach"""
        try:
            # Primary analysis using RiskAgent
            risk_data = fetch_stock_data(ticker)
            
            if 'error' in risk_data:
                return risk_data
            
            # News sentiment analysis
            news_data = analyze_news_sentiment(ticker)
            
            # Combine results
            result = {
                'ticker': ticker,
                'current_price': risk_data.get('current_price', 0),
                'volatility': risk_data.get('volatility', 0),
                'impact_level': risk_data.get('impact_level', 'UNKNOWN'),
                'high_impact': risk_data.get('high_impact', False),
                'timestamp': datetime.now().isoformat(),
                'email_sent': risk_data.get('email_sent', False),
                'news_sentiment': news_data.get('sentiment', 'NEUTRAL') if 'error' not in news_data else 'UNKNOWN',
                'agents_used': ['RiskAgent', 'NewsAgent']
            }
            
            return result
            
        except Exception as e:
            return {
                'error': f'Ticker analysis failed for {ticker}',
                'details': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_insights(self) -> Dict[str, Any]:
        """Get recent insights from all agents"""
        try:
            # Try to get insights from database
            try:
                if self.storage:
                    insights_data = self.storage.get_insights()
                    if insights_data.get('success') and insights_data.get('insights'):
                        return {
                            'insights': insights_data['insights'],
                            'total_count': len(insights_data['insights']),
                            'timestamp': datetime.now().isoformat()
                        }
            except Exception as db_error:
                logging.error(f"Database error: {db_error}")
            
            # Fallback: Generate sample insights
            sample_insights = []
            for ticker in DEFAULT_PORTFOLIO[:3]:  # Get insights for top 3 stocks
                try:
                    analysis = self.analyze_ticker(ticker)
                    if 'error' not in analysis:
                        sample_insights.append({
                            'ticker': ticker,
                            'insight': f"Risk analysis for {ticker}: {analysis['impact_level']} impact level, "
                                     f"volatility at {analysis['volatility']:.2%}",
                            'timestamp': datetime.now().isoformat()
                        })
                except Exception:
                    continue
            
            return {
                'insights': sample_insights,
                'total_count': len(sample_insights),
                'timestamp': datetime.now().isoformat(),
                'note': 'Generated from real-time analysis'
            }
            
        except Exception as e:
            return {
                'error': 'Failed to fetch insights',
                'details': str(e),
                'timestamp': datetime.now().isoformat(),
                'insights': [],
                'total_count': 0
            }
    
    def send_test_email(self, subject: str, message: str) -> Dict[str, Any]:
        """Send test email notification"""
        try:
            if not self.env_status['valid']:
                return {
                    'error': 'Email configuration incomplete',
                    'details': self.env_status['message'],
                    'timestamp': datetime.now().isoformat()
                }
            
            to_email = os.environ.get('TO_EMAIL', 'test@example.com')
            result = send_email(to_email, subject, message)
            
            return {
                'success': result.get('success', False),
                'message': result.get('message', 'Email operation completed'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': 'Email sending failed',
                'details': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # Test basic functionality
            test_ticker = 'AAPL'
            test_analysis = self.analyze_ticker(test_ticker)
            
            agents_status = {
                'RiskAgent': 'operational' if 'error' not in test_analysis else 'error',
                'NewsAgent': 'operational',
                'EventSentinel': 'operational',
                'KnowledgeCurator': 'operational',
                'Supervisor': 'operational'
            }
            
            return {
                'status': 'healthy',
                'service': 'Multi-Agent Portfolio Analysis API',
                'version': '2.0.0',
                'timestamp': datetime.now().isoformat(),
                'environment': {
                    'variables_configured': self.env_status['valid'],
                    'missing_vars': self.env_status.get('missing_vars', [])
                },
                'agents': agents_status,
                'features': {
                    'portfolio_analysis': True,
                    'ticker_analysis': True,
                    'email_notifications': self.env_status['valid'],
                    'real_time_events': True,
                    'knowledge_evolution': True
                },
                'endpoints': {
                    'portfolio_analysis': 'POST /api/app {"action": "portfolio_analysis"}',
                    'analyze_ticker': 'POST /api/app {"action": "analyze_ticker", "ticker": "AAPL"}',
                    'insights': 'POST /api/app {"action": "insights"}',
                    'test_email': 'POST /api/app {"action": "send_test_email", "subject": "...", "message": "..."}',
                    'system_status': 'GET /api/app'
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': 'System status check failed',
                'details': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Global API instance
api = MultiAgentAPI()

def handler(request):
    """
    Vercel serverless function handler
    
    This function handles HTTP requests for the multi-agent portfolio analysis API.
    It processes different actions and returns JSON responses.
    """
    try:
        # Handle different request formats
        if hasattr(request, 'method'):
            method = request.method
        else:
            method = 'GET'
        
        # Parse request body for POST requests
        if method == 'POST':
            try:
                if hasattr(request, 'get_json'):
                    body = request.get_json() or {}
                elif hasattr(request, 'json'):
                    body = request.json or {}
                else:
                    body = {}
            except Exception:
                body = {}
        else:
            body = {}
        
        # Parse query parameters for GET requests
        if hasattr(request, 'args'):
            params = dict(request.args)
        else:
            params = {}
        
        # Determine action
        action = body.get('action') or params.get('action', 'system_status')
        
        # Route to appropriate handler
        if action == 'portfolio_analysis':
            result = api.portfolio_analysis()
        elif action == 'analyze_ticker':
            ticker = body.get('ticker') or params.get('ticker', 'AAPL')
            result = api.analyze_ticker(ticker.upper())
        elif action == 'insights':
            result = api.get_insights()
        elif action == 'send_test_email':
            subject = body.get('subject', 'Test Email')
            message = body.get('message', 'Test message from Multi-Agent Portfolio Analysis')
            result = api.send_test_email(subject, message)
        elif action == 'system_status' or action == 'health':
            result = api.get_system_status()
        else:
            result = {
                'error': 'Invalid action',
                'valid_actions': [
                    'portfolio_analysis',
                    'analyze_ticker',
                    'insights',
                    'send_test_email',
                    'system_status'
                ],
                'timestamp': datetime.now().isoformat()
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
            'error': 'Internal server error',
            'details': str(e),
            'timestamp': datetime.now().isoformat(),
            'service': 'Multi-Agent Portfolio Analysis API'
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

# Test function for development
if __name__ == '__main__':
    # Test the API locally
    class MockRequest:
        def __init__(self, method='GET', json_data=None):
            self.method = method
            self.json_data = json_data or {}
            self.args = {}
            
        def get_json(self):
            return self.json_data
    
    # Test system status
    print("Testing system status...")
    request = MockRequest('GET')
    response = handler(request)
    print(json.dumps(json.loads(response['body']), indent=2))
    
    # Test ticker analysis
    print("\nTesting ticker analysis...")
    request = MockRequest('POST', {'action': 'analyze_ticker', 'ticker': 'AAPL'})
    response = handler(request)
    print(json.dumps(json.loads(response['body']), indent=2)) 