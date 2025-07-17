#!/usr/bin/env python3

"""
Integration Tests for Multi-Agent Portfolio Analysis System
Tests end-to-end workflows, data flow, and agent coordination
"""

import unittest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import asyncio
import time
import warnings
warnings.filterwarnings("ignore")

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all components
from api.agents.risk_agent import fetch_stock_data, analyze_portfolio_risk
from api.agents.news_agent import analyze_news_sentiment, get_market_news_impact
from api.agents.event_sentinel import detect_portfolio_events, generate_event_summary
from api.agents.knowledge_curator import curate_knowledge_quality, identify_knowledge_gaps
from api.supervisor import SupervisorAgent
from api.database.storage_manager import DatabaseManager
from api.notifications.email_handler import send_email, send_bulk_notifications
from api.scheduler.cron_handler import CronManager

class TestMultiAgentWorkflow(unittest.TestCase):
    """Integration tests for multi-agent workflows"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_portfolio = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
        self.supervisor = SupervisorAgent()
        self.db_manager = DatabaseManager()
        
    @patch('api.agents.risk_agent.yf')
    @patch('api.agents.news_agent.yf')
    @patch('api.agents.event_sentinel.yf')
    @patch('api.agents.knowledge_curator.INSIGHTS_STORAGE', [])
    @patch('api.agents.event_sentinel.EVENTS_STORAGE', [])
    def test_complete_portfolio_analysis_workflow(self, mock_yf_event, mock_yf_news, mock_yf_risk):
        """Test complete portfolio analysis workflow from start to finish"""
        # Mock market data for all agents
        mock_data = self._create_mock_market_data()
        mock_yf_risk.download.return_value = mock_data
        mock_yf_news.download.return_value = mock_data
        mock_yf_event.download.return_value = mock_data
        
        # Mock stock info
        mock_ticker = Mock()
        mock_ticker.info = {
            'longName': 'Apple Inc.',
            'currentPrice': 150.0,
            'marketCap': 2500000000000
        }
        mock_yf_news.Ticker.return_value = mock_ticker
        
        # Step 1: Risk Analysis
        risk_results = analyze_portfolio_risk(self.test_portfolio)
        
        # Verify risk analysis
        self.assertIsInstance(risk_results, dict)
        self.assertEqual(risk_results['agent'], 'RiskAgent')
        self.assertEqual(risk_results['portfolio_size'], len(self.test_portfolio))
        self.assertIn('portfolio_risk', risk_results)
        self.assertIn('results', risk_results)
        
        # Step 2: News Sentiment Analysis
        news_results = get_market_news_impact(self.test_portfolio)
        
        # Verify news analysis
        self.assertIsInstance(news_results, dict)
        self.assertEqual(news_results['agent'], 'NewsAgent')
        self.assertIn('overall_sentiment', news_results)
        self.assertIn('sentiment_breakdown', news_results)
        
        # Step 3: Event Detection
        event_results = detect_portfolio_events(self.test_portfolio)
        
        # Verify event detection
        self.assertIsInstance(event_results, dict)
        self.assertEqual(event_results['agent'], 'EventSentinel')
        self.assertIn('portfolio_risk', event_results)
        self.assertIn('events', event_results)
        
        # Step 4: Knowledge Curation
        knowledge_results = curate_knowledge_quality()
        
        # Verify knowledge curation
        self.assertIsInstance(knowledge_results, dict)
        self.assertEqual(knowledge_results['agent'], 'KnowledgeCurator')
        self.assertIn('quality_score', knowledge_results)
        
        # Step 5: Verify data consistency across agents
        self._verify_data_consistency(risk_results, news_results, event_results, knowledge_results)
        
    def test_data_flow_between_agents(self):
        """Test data flow and information sharing between agents"""
        # Test that insights from one agent are accessible to others
        with patch('api.agents.risk_agent.INSIGHTS_STORAGE') as mock_storage:
            # Create mock insights
            mock_insights = [
                {
                    'ticker': 'AAPL',
                    'insight': 'High volatility detected',
                    'agent': 'RiskAgent',
                    'timestamp': datetime.now().isoformat()
                }
            ]
            mock_storage.__iter__ = Mock(return_value=iter(mock_insights))
            mock_storage.__len__ = Mock(return_value=len(mock_insights))
            mock_storage.append = Mock()
            
            # Test knowledge curator can access risk insights
            knowledge_results = curate_knowledge_quality()
            
            # Verify knowledge curator processed risk insights
            self.assertIsInstance(knowledge_results, dict)
            self.assertIn('total_insights', knowledge_results)
            
    @patch('api.database.storage_manager.sqlite3')
    def test_database_integration_workflow(self, mock_sqlite):
        """Test database integration across all agents"""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_sqlite.connect.return_value = mock_conn
        
        # Test database operations
        db_manager = DatabaseManager()
        
        # Store insights from different agents
        test_insights = [
            {'ticker': 'AAPL', 'insight': 'Risk analysis complete', 'agent': 'RiskAgent'},
            {'ticker': 'GOOGL', 'insight': 'News sentiment positive', 'agent': 'NewsAgent'},
            {'ticker': 'MSFT', 'insight': 'Event detected', 'agent': 'EventSentinel'}
        ]
        
        for insight in test_insights:
            result = db_manager.store_insight(insight['ticker'], insight['insight'], insight['agent'])
            self.assertTrue(result['success'])
            
        # Test insight retrieval
        mock_cursor.fetchall.return_value = [
            ('AAPL', 'Risk analysis complete', datetime.now().isoformat(), 'RiskAgent'),
            ('GOOGL', 'News sentiment positive', datetime.now().isoformat(), 'NewsAgent')
        ]
        
        insights = db_manager.get_insights()
        self.assertTrue(insights['success'])
        self.assertEqual(len(insights['insights']), 2)
        
    @patch('api.notifications.email_handler.smtplib.SMTP')
    @patch.dict(os.environ, {
        'SENDER_EMAIL': 'test@example.com',
        'SENDER_PASSWORD': 'password',
        'TO_EMAIL': 'recipient@example.com'
    })
    def test_notification_workflow_integration(self, mock_smtp):
        """Test notification workflow integration with agents"""
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        # Test high-impact event notification workflow
        high_impact_events = [
            {
                'ticker': 'AAPL',
                'event_type': 'HIGH_VOLATILITY',
                'message': 'AAPL volatility exceeds 5%',
                'timestamp': datetime.now().isoformat()
            },
            {
                'ticker': 'GOOGL',
                'event_type': 'VOLUME_SPIKE',
                'message': 'GOOGL volume spike detected',
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        # Test bulk notification
        result = send_bulk_notifications(
            subject="Portfolio Alert: High Impact Events",
            events=high_impact_events,
            recipient_emails=['test@example.com']
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['emails_sent'], 1)
        
    def test_error_propagation_across_agents(self):
        """Test how errors propagate across the multi-agent system"""
        # Test what happens when one agent fails
        with patch('api.agents.risk_agent.yf') as mock_yf:
            mock_yf.download.side_effect = Exception("Market data unavailable")
            
            # Risk agent should handle the error gracefully
            result = analyze_portfolio_risk(self.test_portfolio)
            
            # Verify error handling
            self.assertIsInstance(result, dict)
            self.assertIn('error', result)
            
            # Other agents should continue working
            with patch('api.agents.news_agent.yf') as mock_news_yf:
                mock_news_yf.download.return_value = self._create_mock_market_data()
                mock_ticker = Mock()
                mock_ticker.info = {'longName': 'Apple Inc.', 'currentPrice': 150.0}
                mock_news_yf.Ticker.return_value = mock_ticker
                
                news_result = get_market_news_impact(self.test_portfolio)
                self.assertIsInstance(news_result, dict)
                self.assertEqual(news_result['agent'], 'NewsAgent')
                
    def test_supervisor_orchestration(self):
        """Test supervisor agent orchestration of all agents"""
        supervisor = SupervisorAgent()
        
        # Test comprehensive analysis orchestration
        with patch('api.supervisor.requests.post') as mock_post:
            # Mock successful agent responses
            mock_responses = [
                Mock(status_code=200, json=Mock(return_value={
                    'success': True, 
                    'data': {'volatility': 0.03, 'portfolio_risk': 'MEDIUM'}
                })),
                Mock(status_code=200, json=Mock(return_value={
                    'success': True, 
                    'data': {'sentiment': 'POSITIVE', 'overall_sentiment': 'POSITIVE'}
                })),
                Mock(status_code=200, json=Mock(return_value={
                    'success': True, 
                    'data': {'events': [], 'portfolio_risk': 'LOW'}
                })),
                Mock(status_code=200, json=Mock(return_value={
                    'success': True, 
                    'data': {'quality_score': 85, 'gaps': []}
                }))
            ]
            mock_post.side_effect = mock_responses
            
            result = supervisor.orchestrate_analysis("AAPL", "comprehensive")
            
            # Verify orchestration
            self.assertIsInstance(result, dict)
            self.assertEqual(result['ticker'], 'AAPL')
            self.assertIn('agent_results', result)
            self.assertIn('synthesis', result)
            
    def test_concurrent_agent_execution(self):
        """Test concurrent execution of multiple agents"""
        # Test that multiple agents can run simultaneously without conflicts
        with patch('api.agents.risk_agent.yf') as mock_yf_risk, \
             patch('api.agents.news_agent.yf') as mock_yf_news, \
             patch('api.agents.event_sentinel.yf') as mock_yf_event:
            
            mock_data = self._create_mock_market_data()
            mock_yf_risk.download.return_value = mock_data
            mock_yf_news.download.return_value = mock_data
            mock_yf_event.download.return_value = mock_data
            
            # Mock stock info for news agent
            mock_ticker = Mock()
            mock_ticker.info = {'longName': 'Apple Inc.', 'currentPrice': 150.0}
            mock_yf_news.Ticker.return_value = mock_ticker
            
            # Simulate concurrent execution
            import threading
            import queue
            
            results_queue = queue.Queue()
            
            def run_risk_analysis():
                result = analyze_portfolio_risk(["AAPL"])
                results_queue.put(('risk', result))
                
            def run_news_analysis():
                result = get_market_news_impact(["AAPL"])
                results_queue.put(('news', result))
                
            def run_event_detection():
                result = detect_portfolio_events(["AAPL"])
                results_queue.put(('events', result))
            
            # Start concurrent threads
            threads = [
                threading.Thread(target=run_risk_analysis),
                threading.Thread(target=run_news_analysis),
                threading.Thread(target=run_event_detection)
            ]
            
            for thread in threads:
                thread.start()
                
            for thread in threads:
                thread.join()
            
            # Collect results
            results = {}
            while not results_queue.empty():
                agent_type, result = results_queue.get()
                results[agent_type] = result
            
            # Verify all agents completed successfully
            self.assertEqual(len(results), 3)
            self.assertIn('risk', results)
            self.assertIn('news', results)
            self.assertIn('events', results)
            
    def test_real_time_updates_workflow(self):
        """Test real-time updates workflow"""
        # Test that changes in one agent trigger updates in others
        with patch('api.agents.event_sentinel.EVENTS_STORAGE') as mock_events:
            # Simulate new event
            new_event = {
                'type': 'HIGH_VOLATILITY',
                'ticker': 'AAPL',
                'message': 'High volatility detected',
                'timestamp': datetime.now().isoformat()
            }
            
            mock_events.append(new_event)
            mock_events.__len__ = Mock(return_value=1)
            mock_events.__iter__ = Mock(return_value=iter([new_event]))
            
            # Test event summary generation
            summary = generate_event_summary(1)
            
            # Verify event was processed
            self.assertIsInstance(summary, dict)
            self.assertEqual(summary['total_events'], 1)
            self.assertIn('agent', summary)
            
    def _create_mock_market_data(self):
        """Create mock market data for testing"""
        mock_data = Mock()
        mock_data.empty = False
        mock_data.__getitem__ = Mock(side_effect=lambda x: {
            'Close': Mock(
                pct_change=Mock(return_value=Mock(std=Mock(return_value=0.03))),
                iloc=[150.0, 148.0]
            ),
            'Volume': Mock(
                mean=Mock(return_value=1000000),
                iloc=[1200000],
                empty=False
            )
        }[x])
        return mock_data
        
    def _verify_data_consistency(self, risk_results, news_results, event_results, knowledge_results):
        """Verify data consistency across agent results"""
        # Check that all agents processed the same portfolio
        self.assertEqual(risk_results['portfolio_size'], len(self.test_portfolio))
        self.assertEqual(news_results['analyzed_tickers'], len(self.test_portfolio))
        
        # Check timestamp consistency (should be within reasonable time window)
        timestamps = [
            datetime.fromisoformat(risk_results['timestamp']),
            datetime.fromisoformat(news_results['timestamp']),
            datetime.fromisoformat(event_results['timestamp']),
            datetime.fromisoformat(knowledge_results['timestamp'])
        ]
        
        time_window = timedelta(minutes=5)
        for i in range(len(timestamps) - 1):
            self.assertLess(
                abs(timestamps[i] - timestamps[i + 1]),
                time_window,
                "Agent timestamps should be within 5 minutes of each other"
            )


class TestDatabaseIntegration(unittest.TestCase):
    """Integration tests for database operations"""
    
    def setUp(self):
        """Set up database test environment"""
        self.db_manager = DatabaseManager()
        
    @patch('api.database.storage_manager.sqlite3')
    def test_end_to_end_database_workflow(self, mock_sqlite):
        """Test complete database workflow from storage to retrieval"""
        # Mock database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_sqlite.connect.return_value = mock_conn
        
        # Test complete workflow
        test_data = {
            'ticker': 'AAPL',
            'insight': 'Comprehensive analysis shows positive outlook',
            'agent': 'RiskAgent',
            'metadata': {'volatility': 0.03, 'risk_score': 3}
        }
        
        # Store data
        store_result = self.db_manager.store_insight(
            test_data['ticker'],
            test_data['insight'],
            test_data['agent'],
            test_data['metadata']
        )
        
        self.assertTrue(store_result['success'])
        
        # Retrieve data
        mock_cursor.fetchall.return_value = [
            (test_data['ticker'], test_data['insight'], datetime.now().isoformat(), test_data['agent'])
        ]
        
        get_result = self.db_manager.get_insights(ticker=test_data['ticker'])
        
        self.assertTrue(get_result['success'])
        self.assertEqual(len(get_result['insights']), 1)
        self.assertEqual(get_result['insights'][0]['ticker'], test_data['ticker'])
        
    @patch('api.database.storage_manager.sqlite3')
    def test_database_transaction_handling(self, mock_sqlite):
        """Test database transaction handling and rollback"""
        # Mock database connection with transaction support
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_sqlite.connect.return_value = mock_conn
        
        # Test transaction rollback on error
        mock_cursor.execute.side_effect = Exception("Database error")
        
        result = self.db_manager.store_insight('AAPL', 'Test insight', 'TestAgent')
        
        # Verify rollback was called
        mock_conn.rollback.assert_called_once()
        self.assertFalse(result['success'])
        self.assertIn('error', result)


class TestNotificationIntegration(unittest.TestCase):
    """Integration tests for notification system"""
    
    @patch('api.notifications.email_handler.smtplib.SMTP')
    @patch.dict(os.environ, {
        'SENDER_EMAIL': 'test@example.com',
        'SENDER_PASSWORD': 'password',
        'TO_EMAIL': 'recipient@example.com'
    })
    def test_notification_system_integration(self, mock_smtp):
        """Test integration of notification system with agents"""
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        # Test notification triggered by high-impact event
        event_data = {
            'ticker': 'AAPL',
            'volatility': 0.08,
            'impact_level': 'HIGH',
            'message': 'Critical volatility threshold exceeded'
        }
        
        # Send notification
        result = send_email(
            subject=f"🚨 CRITICAL ALERT: {event_data['ticker']}",
            body=f"High impact event detected:\n{event_data['message']}\nVolatility: {event_data['volatility']:.2%}"
        )
        
        self.assertTrue(result['success'])
        mock_server.sendmail.assert_called_once()


class TestSchedulerIntegration(unittest.TestCase):
    """Integration tests for scheduler system"""
    
    def setUp(self):
        """Set up scheduler test environment"""
        self.cron_manager = CronManager()
        
    @patch('api.scheduler.cron_handler.time.sleep')
    @patch('api.scheduler.cron_handler.requests.post')
    def test_automated_analysis_scheduling(self, mock_post, mock_sleep):
        """Test automated analysis scheduling workflow"""
        # Mock successful agent responses
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value={'success': True, 'data': {'analysis': 'complete'}})
        )
        
        # Configure scheduler
        schedule_config = {
            'enabled': True,
            'interval': 60,  # 1 minute for testing
            'portfolio': ['AAPL', 'GOOGL'],
            'agents': ['risk', 'news', 'events']
        }
        
        result = self.cron_manager.schedule_analysis(schedule_config)
        
        self.assertTrue(result['success'])
        self.assertIn('job_id', result)


if __name__ == '__main__':
    # Run integration tests
    unittest.main(verbosity=2, buffer=True) 