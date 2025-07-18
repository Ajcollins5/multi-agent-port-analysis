#!/usr/bin/env python3
"""
Unit tests for individual agents

⚠️  DEPRECATED: These tests need to be rewritten for the new Supabase agents  
The legacy agent imports have been migrated to Supabase-based architecture.
Many tests in this file will fail until updated to use:
- SupabaseRiskAgent instead of risk_agent
- BaseAgent with news analysis instead of news_agent
- BaseAgent with event detection instead of event_sentinel
"""

import unittest
import asyncio
import os
import sys
import json
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timedelta

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# DEPRECATED: Legacy agent imports have been migrated to Supabase
# These tests need to be updated to use the new Supabase agents
# from api.agents.risk_agent import fetch_stock_data, determine_impact_level, analyze_portfolio_risk, send_email
# from api.agents.news_agent import analyze_news_sentiment, get_market_news_impact, estimate_news_impact
# from api.agents.event_sentinel import detect_portfolio_events, generate_event_summary, detect_correlations
from api.agents.knowledge_curator import curate_knowledge_quality, identify_knowledge_gaps, refine_insight
from api.supervisor import SupervisorAgent

class TestRiskAgent(unittest.TestCase):
    """Test cases for RiskAgent functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_ticker = "AAPL"
        self.test_portfolio = ["AAPL", "GOOGL", "MSFT"]
        
    @patch('api.agents.risk_agent.yf')
    @patch('api.agents.risk_agent.INSIGHTS_STORAGE', [])
    def test_fetch_stock_data_success(self, mock_yf):
        """Test successful stock data fetching"""
        # Mock yfinance data
        mock_data = Mock()
        mock_data.empty = False
        mock_data.__getitem__ = Mock(side_effect=lambda x: {
            'Close': Mock(pct_change=Mock(return_value=Mock(std=Mock(return_value=0.03))),
                         iloc=[-1, -2]),
            'Volume': Mock(iloc=[-1], empty=False)
        }[x])
        mock_data['Close'].iloc = [100.0, 98.0]  # Mock prices
        mock_data['Volume'].iloc = [1000000]  # Mock volume
        
        mock_yf.download.return_value = mock_data
        
        result = fetch_stock_data(self.test_ticker)
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertEqual(result['ticker'], self.test_ticker)
        self.assertIn('current_price', result)
        self.assertIn('volatility', result)
        self.assertIn('impact_level', result)
        self.assertIn('high_impact', result)
        self.assertIn('timestamp', result)
        
    @patch('api.agents.risk_agent.yf')
    def test_fetch_stock_data_no_data(self, mock_yf):
        """Test handling of no data scenario"""
        mock_data = Mock()
        mock_data.empty = True
        mock_yf.download.return_value = mock_data
        
        result = fetch_stock_data(self.test_ticker)
        
        self.assertIn('error', result)
        self.assertIn('No data found', result['error'])
        
    @patch('api.agents.risk_agent.yf')
    def test_fetch_stock_data_exception(self, mock_yf):
        """Test exception handling"""
        mock_yf.download.side_effect = Exception("API Error")
        
        result = fetch_stock_data(self.test_ticker)
        
        self.assertIn('error', result)
        self.assertIn('API Error', result['error'])
        
    @patch('api.agents.risk_agent.yf')
    def test_determine_impact_level_high(self, mock_yf):
        """Test high impact level determination"""
        mock_data = Mock()
        mock_data.empty = False
        mock_data.__getitem__ = Mock(side_effect=lambda x: {
            'Close': Mock(pct_change=Mock(return_value=Mock(std=Mock(return_value=0.06))))
        }[x])
        
        mock_yf.download.return_value = mock_data
        
        result = determine_impact_level(self.test_ticker)
        
        self.assertEqual(result['impact_level'], 'HIGH')
        self.assertEqual(result['risk_score'], 5)
        
    @patch('api.agents.risk_agent.yf')
    def test_determine_impact_level_medium(self, mock_yf):
        """Test medium impact level determination"""
        mock_data = Mock()
        mock_data.empty = False
        mock_data.__getitem__ = Mock(side_effect=lambda x: {
            'Close': Mock(pct_change=Mock(return_value=Mock(std=Mock(return_value=0.03))))
        }[x])
        
        mock_yf.download.return_value = mock_data
        
        result = determine_impact_level(self.test_ticker)
        
        self.assertEqual(result['impact_level'], 'MEDIUM')
        self.assertEqual(result['risk_score'], 3)
        
    @patch('api.agents.risk_agent.yf')
    def test_determine_impact_level_low(self, mock_yf):
        """Test low impact level determination"""
        mock_data = Mock()
        mock_data.empty = False
        mock_data.__getitem__ = Mock(side_effect=lambda x: {
            'Close': Mock(pct_change=Mock(return_value=Mock(std=Mock(return_value=0.01))))
        }[x])
        
        mock_yf.download.return_value = mock_data
        
        result = determine_impact_level(self.test_ticker)
        
        self.assertEqual(result['impact_level'], 'LOW')
        self.assertEqual(result['risk_score'], 1)
        
    @patch('api.agents.risk_agent.fetch_stock_data')
    def test_analyze_portfolio_risk(self, mock_fetch):
        """Test portfolio risk analysis"""
        # Mock successful stock data
        mock_fetch.return_value = {
            'ticker': 'AAPL',
            'volatility': 0.03,
            'high_impact': False,
            'current_price': 150.0
        }
        
        result = analyze_portfolio_risk(self.test_portfolio)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['portfolio_size'], 3)
        self.assertIn('portfolio_risk', result)
        self.assertIn('results', result)
        self.assertIn('agent', result)
        self.assertEqual(result['agent'], 'RiskAgent')
        
    @patch('api.agents.risk_agent.smtplib.SMTP')
    @patch.dict(os.environ, {
        'SENDER_EMAIL': 'test@example.com',
        'SENDER_PASSWORD': 'password',
        'TO_EMAIL': 'recipient@example.com',
        'SMTP_SERVER': 'smtp.gmail.com',
        'SMTP_PORT': '587'
    })
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending"""
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        result = send_email("Test Subject", "Test Body")
        
        self.assertTrue(result['success'])
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()
        
    @patch('api.agents.risk_agent.smtplib.SMTP')
    @patch.dict(os.environ, {
        'SENDER_EMAIL': 'test@example.com',
        'SENDER_PASSWORD': 'password',
        'TO_EMAIL': 'recipient@example.com'
    })
    def test_send_email_failure(self, mock_smtp):
        """Test email sending failure"""
        mock_smtp.side_effect = Exception("SMTP Error")
        
        result = send_email("Test Subject", "Test Body")
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)


class TestNewsAgent(unittest.TestCase):
    """Test cases for NewsAgent functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_ticker = "AAPL"
        self.test_tickers = ["AAPL", "GOOGL", "MSFT"]
        
    @patch('api.agents.news_agent.yf')
    @patch('api.agents.news_agent.INSIGHTS_STORAGE', [])
    def test_analyze_news_sentiment_positive(self, mock_yf):
        """Test positive news sentiment analysis"""
        # Mock stock info
        mock_ticker = Mock()
        mock_ticker.info = {
            'longName': 'Apple Inc.',
            'currentPrice': 150.0,
            'marketCap': 2500000000000
        }
        mock_yf.Ticker.return_value = mock_ticker
        
        # Mock price data showing positive movement
        mock_data = Mock()
        mock_data.empty = False
        mock_data.__getitem__ = Mock(side_effect=lambda x: {
            'Close': Mock(iloc=[145.0, 150.0])  # Price increase
        }[x])
        mock_yf.download.return_value = mock_data
        
        result = analyze_news_sentiment(self.test_ticker)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['ticker'], self.test_ticker)
        self.assertEqual(result['sentiment'], 'POSITIVE')
        self.assertIn('impact_level', result)
        self.assertIn('confidence', result)
        
    @patch('api.agents.news_agent.yf')
    def test_analyze_news_sentiment_negative(self, mock_yf):
        """Test negative news sentiment analysis"""
        mock_ticker = Mock()
        mock_ticker.info = {
            'longName': 'Apple Inc.',
            'currentPrice': 140.0,
            'marketCap': 2300000000000
        }
        mock_yf.Ticker.return_value = mock_ticker
        
        # Mock price data showing negative movement
        mock_data = Mock()
        mock_data.empty = False
        mock_data.__getitem__ = Mock(side_effect=lambda x: {
            'Close': Mock(iloc=[150.0, 140.0])  # Price decrease
        }[x])
        mock_yf.download.return_value = mock_data
        
        result = analyze_news_sentiment(self.test_ticker)
        
        self.assertEqual(result['sentiment'], 'NEGATIVE')
        
    @patch('api.agents.news_agent.analyze_news_sentiment')
    def test_get_market_news_impact(self, mock_analyze):
        """Test market news impact analysis"""
        # Mock different sentiment results
        mock_analyze.side_effect = [
            {'sentiment': 'POSITIVE', 'impact_level': 'HIGH'},
            {'sentiment': 'NEGATIVE', 'impact_level': 'MEDIUM'},
            {'sentiment': 'NEUTRAL', 'impact_level': 'LOW'}
        ]
        
        result = get_market_news_impact(self.test_tickers)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['analyzed_tickers'], 3)
        self.assertIn('overall_sentiment', result)
        self.assertIn('sentiment_breakdown', result)
        self.assertIn('agent', result)
        
    @patch('api.agents.news_agent.yf')
    def test_estimate_news_impact(self, mock_yf):
        """Test news impact estimation"""
        mock_ticker = Mock()
        mock_ticker.info = {'longName': 'Apple Inc.'}
        mock_yf.Ticker.return_value = mock_ticker
        
        # Mock data with high volatility and volume spike
        mock_data = Mock()
        mock_data.empty = False
        mock_data.__getitem__ = Mock(side_effect=lambda x: {
            'Close': Mock(pct_change=Mock(return_value=Mock(std=Mock(return_value=0.06)))),
            'Volume': Mock(mean=Mock(return_value=1000000), iloc=[2000000])
        }[x])
        mock_yf.download.return_value = mock_data
        
        result = estimate_news_impact(self.test_ticker)
        
        self.assertEqual(result['impact_estimate'], 'HIGH')
        self.assertGreater(result['confidence'], 0.8)


class TestEventSentinel(unittest.TestCase):
    """Test cases for EventSentinel functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_portfolio = ["AAPL", "GOOGL", "MSFT"]
        
    @patch('api.agents.event_sentinel.yf')
    @patch('api.agents.event_sentinel.EVENTS_STORAGE', [])
    def test_detect_portfolio_events_high_volatility(self, mock_yf):
        """Test detection of high volatility events"""
        # Mock high volatility data
        mock_data = Mock()
        mock_data.empty = False
        mock_data.__getitem__ = Mock(side_effect=lambda x: {
            'Close': Mock(pct_change=Mock(return_value=Mock(std=Mock(return_value=0.06))),
                         iloc=[150.0]),
            'Volume': Mock(mean=Mock(return_value=1000000), iloc=[1500000])
        }[x])
        mock_yf.download.return_value = mock_data
        
        result = detect_portfolio_events(self.test_portfolio)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['portfolio_risk'], 'HIGH')
        self.assertGreater(result['high_volatility_count'], 0)
        self.assertIn('events', result)
        self.assertIn('agent', result)
        
    @patch('api.agents.event_sentinel.EVENTS_STORAGE')
    def test_generate_event_summary(self, mock_storage):
        """Test event summary generation"""
        # Mock event data
        mock_events = [
            {
                'type': 'HIGH_VOLATILITY',
                'ticker': 'AAPL',
                'timestamp': datetime.now().isoformat()
            },
            {
                'type': 'VOLUME_SPIKE',
                'ticker': 'GOOGL',
                'timestamp': datetime.now().isoformat()
            }
        ]
        mock_storage.__iter__ = Mock(return_value=iter(mock_events))
        mock_storage.__len__ = Mock(return_value=len(mock_events))
        
        result = generate_event_summary(24)
        
        self.assertIsInstance(result, dict)
        self.assertIn('total_events', result)
        self.assertIn('event_types', result)
        self.assertIn('agent', result)
        
    @patch('api.agents.event_sentinel.yf')
    def test_detect_correlations(self, mock_yf):
        """Test correlation detection"""
        # Mock correlation data
        mock_data = Mock()
        mock_data.empty = False
        mock_data.__getitem__ = Mock(side_effect=lambda x: {
            'Close': Mock(pct_change=Mock(return_value=Mock(
                dropna=Mock(return_value=Mock(
                    align=Mock(return_value=(Mock(corr=Mock(return_value=0.85)), Mock())),
                    __len__=Mock(return_value=30)
                ))
            )))
        }[x])
        mock_yf.download.return_value = mock_data
        
        result = detect_correlations(self.test_portfolio)
        
        self.assertIsInstance(result, dict)
        self.assertIn('correlation_pairs', result)
        self.assertIn('agent', result)


class TestKnowledgeCurator(unittest.TestCase):
    """Test cases for KnowledgeCurator functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_ticker = "AAPL"
        
    @patch('api.agents.knowledge_curator.INSIGHTS_STORAGE')
    def test_curate_knowledge_quality_with_data(self, mock_storage):
        """Test knowledge quality curation with data"""
        # Mock insight data
        mock_insights = [
            {
                'ticker': 'AAPL',
                'insight': 'REFINED: Market analysis shows strong performance',
                'agent': 'RiskAgent',
                'timestamp': datetime.now().isoformat()
            },
            {
                'ticker': 'GOOGL',
                'insight': 'Initial analysis of market trends',
                'agent': 'NewsAgent',
                'timestamp': datetime.now().isoformat()
            }
        ]
        mock_storage.__iter__ = Mock(return_value=iter(mock_insights))
        mock_storage.__len__ = Mock(return_value=len(mock_insights))
        
        result = curate_knowledge_quality()
        
        self.assertIsInstance(result, dict)
        self.assertIn('quality_score', result)
        self.assertIn('total_insights', result)
        self.assertIn('recommendations', result)
        self.assertIn('agent', result)
        
    @patch('api.agents.knowledge_curator.INSIGHTS_STORAGE', [])
    def test_curate_knowledge_quality_no_data(self, mock_storage):
        """Test knowledge quality curation with no data"""
        result = curate_knowledge_quality()
        
        self.assertEqual(result['total_insights'], 0)
        self.assertEqual(result['quality_score'], 0)
        
    @patch('api.agents.knowledge_curator.INSIGHTS_STORAGE')
    def test_identify_knowledge_gaps(self, mock_storage):
        """Test knowledge gap identification"""
        # Mock limited insight data
        mock_insights = [
            {
                'ticker': 'AAPL',
                'insight': 'Basic analysis',
                'agent': 'RiskAgent',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat()
            }
        ]
        mock_storage.__iter__ = Mock(return_value=iter(mock_insights))
        mock_storage.__len__ = Mock(return_value=len(mock_insights))
        
        result = identify_knowledge_gaps(24)
        
        self.assertIsInstance(result, dict)
        self.assertIn('gaps', result)
        self.assertIn('recommendations', result)
        self.assertIn('agent', result)
        
    @patch('api.agents.knowledge_curator.INSIGHTS_STORAGE', [])
    def test_refine_insight(self, mock_storage):
        """Test insight refinement"""
        original_insight = "Basic market analysis"
        additional_context = "Enhanced with volatility data"
        
        result = refine_insight(self.test_ticker, original_insight, additional_context)
        
        self.assertIsInstance(result, dict)
        self.assertIn('refined_insight', result)
        self.assertIn('REFINED:', result['refined_insight'])
        self.assertIn('agent', result)


class TestSupervisor(unittest.TestCase):
    """Test cases for Supervisor functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.supervisor = SupervisorAgent()
        self.test_ticker = "AAPL"
        
    @patch('api.supervisor.requests.post')
    def test_orchestrate_analysis_comprehensive(self, mock_post):
        """Test comprehensive analysis orchestration"""
        # Mock successful agent responses
        mock_responses = [
            Mock(status_code=200, json=Mock(return_value={'success': True, 'data': {'volatility': 0.03}})),
            Mock(status_code=200, json=Mock(return_value={'success': True, 'data': {'sentiment': 'POSITIVE'}})),
            Mock(status_code=200, json=Mock(return_value={'success': True, 'data': {'events': []}})),
            Mock(status_code=200, json=Mock(return_value={'success': True, 'data': {'quality_score': 85}}))
        ]
        mock_post.side_effect = mock_responses
        
        result = self.supervisor.orchestrate_analysis(self.test_ticker)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['ticker'], self.test_ticker)
        self.assertIn('agent_results', result)
        self.assertIn('synthesis', result)
        
    @patch('api.supervisor.requests.post')
    def test_orchestrate_analysis_with_errors(self, mock_post):
        """Test analysis orchestration with agent errors"""
        # Mock failed agent response
        mock_post.side_effect = Exception("Network error")
        
        result = self.supervisor.orchestrate_analysis(self.test_ticker)
        
        self.assertIsInstance(result, dict)
        self.assertIn('errors', result)
        self.assertGreater(len(result['errors']), 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for multi-agent workflows"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.test_portfolio = ["AAPL", "GOOGL", "MSFT"]
        self.supervisor = SupervisorAgent()
        
    @patch('api.agents.risk_agent.yf')
    @patch('api.agents.news_agent.yf')
    @patch('api.agents.event_sentinel.yf')
    def test_full_portfolio_analysis_workflow(self, mock_yf_event, mock_yf_news, mock_yf_risk):
        """Test complete portfolio analysis workflow"""
        # Mock data for all agents
        mock_data = Mock()
        mock_data.empty = False
        mock_data.__getitem__ = Mock(side_effect=lambda x: {
            'Close': Mock(pct_change=Mock(return_value=Mock(std=Mock(return_value=0.03))),
                         iloc=[150.0, 148.0]),
            'Volume': Mock(mean=Mock(return_value=1000000), iloc=[1200000], empty=False)
        }[x])
        
        mock_yf_risk.download.return_value = mock_data
        mock_yf_news.download.return_value = mock_data
        mock_yf_event.download.return_value = mock_data
        
        # Mock ticker info
        mock_ticker = Mock()
        mock_ticker.info = {'longName': 'Apple Inc.', 'currentPrice': 150.0}
        mock_yf_news.Ticker.return_value = mock_ticker
        
        # Test risk analysis
        risk_result = analyze_portfolio_risk(self.test_portfolio)
        self.assertIsInstance(risk_result, dict)
        self.assertEqual(risk_result['agent'], 'RiskAgent')
        
        # Test news analysis
        news_result = get_market_news_impact(self.test_portfolio)
        self.assertIsInstance(news_result, dict)
        self.assertEqual(news_result['agent'], 'NewsAgent')
        
        # Test event detection
        event_result = detect_portfolio_events(self.test_portfolio)
        self.assertIsInstance(event_result, dict)
        self.assertEqual(event_result['agent'], 'EventSentinel')


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def test_missing_environment_variables(self):
        """Test handling of missing environment variables"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                # This should raise an error about missing XAI_API_KEY
                from api.agents.risk_agent import XAI_API_KEY
                
    def test_invalid_ticker_format(self):
        """Test handling of invalid ticker formats"""
        invalid_tickers = ["", "INVALID_TICKER_TOO_LONG", "123", "!@#"]
        
        for ticker in invalid_tickers:
            with patch('api.agents.risk_agent.yf') as mock_yf:
                mock_yf.download.side_effect = Exception("Invalid ticker")
                
                result = fetch_stock_data(ticker)
                self.assertIn('error', result)
                
    def test_network_timeout_handling(self):
        """Test handling of network timeouts"""
        with patch('api.agents.risk_agent.yf') as mock_yf:
            mock_yf.download.side_effect = Exception("Timeout")
            
            result = fetch_stock_data("AAPL")
            self.assertIn('error', result)
            self.assertIn('Timeout', result['error'])
            
    def test_rate_limit_handling(self):
        """Test handling of API rate limits"""
        with patch('api.agents.risk_agent.yf') as mock_yf:
            mock_yf.download.side_effect = Exception("Rate limit exceeded")
            
            result = fetch_stock_data("AAPL")
            self.assertIn('error', result)
            self.assertIn('Rate limit', result['error'])


if __name__ == '__main__':
    # Configure test runner
    unittest.main(verbosity=2, buffer=True) 