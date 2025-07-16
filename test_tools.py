#!/usr/bin/env python3
"""
Comprehensive test suite for Multi-Agent Portfolio Analysis System tools
Tests all agent tools including fetch_stock_data, EventSentinel, and KnowledgeCurator tools
"""

import unittest
import sqlite3
import pandas as pd
import yfinance as yf
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from datetime import datetime, timedelta

# Add the main module to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import functions from main.py
from main import (
    fetch_stock_data,
    determine_impact_level,
    store_insight,
    query_past_insights,
    update_agent_system_messages,
    refine_insight,
    query_knowledge_evolution,
    detect_portfolio_events,
    generate_event_summary,
    curate_knowledge_quality,
    identify_knowledge_gaps,
    send_email,
    PORTFOLIO,
    cursor,
    conn
)

class TestStockDataTools(unittest.TestCase):
    """Test suite for stock data related tools"""
    
    def setUp(self):
        """Set up test environment"""
        # Create test database
        self.test_conn = sqlite3.connect(':memory:')
        self.test_cursor = self.test_conn.cursor()
        self.test_cursor.execute('''
            CREATE TABLE insights (
                ticker TEXT, 
                insight TEXT, 
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.test_conn.commit()
    
    def tearDown(self):
        """Clean up test environment"""
        self.test_conn.close()
    
    @patch('main.yf.download')
    def test_fetch_stock_data_high_volatility(self, mock_download):
        """Test fetch_stock_data with high volatility scenario"""
        # Mock high volatility data
        mock_data = pd.DataFrame({
            'Close': [100, 105, 95, 110, 90]  # High volatility scenario
        })
        mock_download.return_value = mock_data
        
        with patch('main.send_email') as mock_email:
            result = fetch_stock_data("TSLA")
            
            # Verify high volatility detection
            self.assertIn("TSLA", result)
            self.assertIn("Volatility", result)
            
            # Verify email was sent for high impact event
            mock_email.assert_called_once()
            
            # Check email content
            call_args = mock_email.call_args
            self.assertIn("HIGH IMPACT EVENT", call_args[0][0])  # subject
            self.assertIn("TSLA", call_args[0][1])  # body
    
    @patch('main.yf.download')
    def test_fetch_stock_data_low_volatility(self, mock_download):
        """Test fetch_stock_data with low volatility scenario"""
        # Mock low volatility data
        mock_data = pd.DataFrame({
            'Close': [100, 101, 100.5, 101.5, 100.8]  # Low volatility
        })
        mock_download.return_value = mock_data
        
        with patch('main.send_email') as mock_email:
            result = fetch_stock_data("AAPL")
            
            # Verify low volatility result
            self.assertIn("AAPL", result)
            self.assertIn("Volatility", result)
            
            # Verify no email was sent (low volatility)
            mock_email.assert_not_called()
    
    @patch('main.yf.download')
    def test_determine_impact_level_scenarios(self, mock_download):
        """Test determine_impact_level with different volatility scenarios"""
        # Test high impact
        mock_data = pd.DataFrame({
            'Close': [100, 107, 95, 110, 88]  # High volatility
        })
        mock_download.return_value = mock_data
        
        result = determine_impact_level("TSLA")
        self.assertIn("high", result)
        self.assertIn("TSLA", result)
        
        # Test medium impact
        mock_data = pd.DataFrame({
            'Close': [100, 103, 98, 104, 97]  # Medium volatility
        })
        mock_download.return_value = mock_data
        
        result = determine_impact_level("AAPL")
        self.assertIn("medium", result)
        
        # Test low impact
        mock_data = pd.DataFrame({
            'Close': [100, 100.5, 99.8, 100.2, 100.1]  # Low volatility
        })
        mock_download.return_value = mock_data
        
        result = determine_impact_level("MSFT")
        self.assertIn("low", result)
    
    @patch('main.yf.download')
    def test_fetch_stock_data_error_handling(self, mock_download):
        """Test error handling in fetch_stock_data"""
        # Mock download failure
        mock_download.side_effect = Exception("Network error")
        
        with self.assertRaises(Exception):
            fetch_stock_data("INVALID")

class TestInsightTools(unittest.TestCase):
    """Test suite for insight management tools"""
    
    def setUp(self):
        """Set up test database"""
        self.test_conn = sqlite3.connect(':memory:')
        self.test_cursor = self.test_conn.cursor()
        self.test_cursor.execute('''
            CREATE TABLE insights (
                ticker TEXT, 
                insight TEXT, 
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.test_conn.commit()
    
    def tearDown(self):
        """Clean up test environment"""
        self.test_conn.close()
    
    @patch('main.cursor')
    @patch('main.conn')
    def test_store_insight(self, mock_conn, mock_cursor):
        """Test store_insight functionality"""
        result = store_insight("AAPL", "Test insight about AAPL")
        
        # Verify database interaction
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        
        # Check return value
        self.assertEqual(result, "Insight stored.")
    
    @patch('main.cursor')
    def test_query_past_insights(self, mock_cursor):
        """Test query_past_insights functionality"""
        # Mock database results
        mock_cursor.fetchall.return_value = [
            ("Test insight 1", "2024-01-01 10:00:00"),
            ("Test insight 2", "2024-01-01 11:00:00")
        ]
        
        result = query_past_insights("AAPL", limit=2)
        
        # Verify query was executed
        mock_cursor.execute.assert_called_once()
        
        # Check result format
        self.assertIn("Test insight 1", result)
        self.assertIn("2024-01-01 10:00:00", result)
        self.assertIn("|", result)  # Separator
    
    @patch('main.cursor')
    def test_query_past_insights_empty(self, mock_cursor):
        """Test query_past_insights with no results"""
        mock_cursor.fetchall.return_value = []
        
        result = query_past_insights("NONEXISTENT")
        
        self.assertEqual(result, "No previous insights found.")
    
    @patch('main.cursor')
    @patch('main.conn')
    def test_refine_insight(self, mock_conn, mock_cursor):
        """Test refine_insight functionality"""
        # Mock past insights
        mock_cursor.fetchall.return_value = [
            ("Past insight 1", "2024-01-01 10:00:00"),
            ("Past insight 2", "2024-01-01 11:00:00")
        ]
        
        result = refine_insight("AAPL", "New insight about AAPL")
        
        # Verify database operations
        self.assertEqual(mock_cursor.execute.call_count, 2)  # Query + Insert
        mock_conn.commit.assert_called_once()
        
        # Check return value
        self.assertIn("AAPL", result)
        self.assertIn("Knowledge evolution applied", result)

class TestEventSentinelTools(unittest.TestCase):
    """Test suite for EventSentinel tools"""
    
    @patch('main.yf.download')
    @patch('main.PORTFOLIO', ['AAPL', 'TSLA', 'MSFT'])
    def test_detect_portfolio_events_high_risk(self, mock_download):
        """Test detect_portfolio_events with high risk scenario"""
        # Mock high volatility for multiple stocks
        def mock_download_side_effect(ticker, **kwargs):
            if ticker == "AAPL":
                return pd.DataFrame({'Close': [100, 107, 95, 110, 88]})  # High volatility
            elif ticker == "TSLA":
                return pd.DataFrame({'Close': [200, 215, 190, 220, 185]})  # High volatility
            else:
                return pd.DataFrame({'Close': [150, 152, 149, 151, 150]})  # Low volatility
        
        mock_download.side_effect = mock_download_side_effect
        
        result = detect_portfolio_events()
        
        # Verify high risk detection
        self.assertIn("HIGH", result)
        self.assertIn("AAPL", result)
        self.assertIn("TSLA", result)
        self.assertIn("HIGH VOLATILITY", result)
    
    @patch('main.yf.download')
    @patch('main.PORTFOLIO', ['AAPL', 'MSFT'])
    def test_detect_portfolio_events_low_risk(self, mock_download):
        """Test detect_portfolio_events with low risk scenario"""
        # Mock low volatility for all stocks
        mock_data = pd.DataFrame({
            'Close': [100, 100.5, 99.8, 100.2, 100.1]  # Low volatility
        })
        mock_download.return_value = mock_data
        
        result = detect_portfolio_events()
        
        # Verify low risk detection
        self.assertIn("LOW", result)
        self.assertIn("0/2", result)  # No high volatility stocks
    
    @patch('main.cursor')
    def test_generate_event_summary_with_data(self, mock_cursor):
        """Test generate_event_summary with recent insights"""
        # Mock recent insights
        mock_cursor.fetchall.return_value = [
            ("AAPL", "Test insight 1", "2024-01-01 10:00:00"),
            ("TSLA", "REFINED: Test insight 2", "2024-01-01 11:00:00"),
            ("AAPL", "Test insight 3", "2024-01-01 12:00:00")
        ]
        
        result = generate_event_summary()
        
        # Verify summary content
        self.assertIn("EVENT ANALYSIS SUMMARY", result)
        self.assertIn("3 insights", result)
        self.assertIn("AAPL, TSLA", result)
        self.assertIn("KNOWLEDGE EVOLUTION", result)
        self.assertIn("1/3 refined", result)
    
    @patch('main.cursor')
    def test_generate_event_summary_empty(self, mock_cursor):
        """Test generate_event_summary with no recent data"""
        mock_cursor.fetchall.return_value = []
        
        result = generate_event_summary()
        
        # Verify empty summary
        self.assertIn("No recent activity", result)
        self.assertIn("EVENT ANALYSIS SUMMARY", result)

class TestKnowledgeCuratorTools(unittest.TestCase):
    """Test suite for KnowledgeCurator tools"""
    
    @patch('main.cursor')
    def test_curate_knowledge_quality_with_data(self, mock_cursor):
        """Test curate_knowledge_quality with insights"""
        # Mock insights data
        mock_cursor.fetchall.return_value = [
            ("AAPL", "Test insight 1", "2024-01-01 10:00:00"),
            ("AAPL", "REFINED: Test insight 2", "2024-01-01 11:00:00"),
            ("TSLA", "Test insight 3", "2024-01-01 12:00:00"),
            ("TSLA", "REFINED: Test insight 4", "2024-01-01 13:00:00")
        ]
        
        result = curate_knowledge_quality()
        
        # Verify quality assessment
        self.assertIn("KNOWLEDGE QUALITY ASSESSMENT", result)
        self.assertIn("Total Insights: 4", result)
        self.assertIn("Refined Insights: 2", result)
        self.assertIn("50.0%", result)
        self.assertIn("Coverage: 2 tickers", result)
    
    @patch('main.cursor')
    def test_curate_knowledge_quality_empty(self, mock_cursor):
        """Test curate_knowledge_quality with no insights"""
        mock_cursor.fetchall.return_value = []
        
        result = curate_knowledge_quality()
        
        self.assertEqual(result, "No insights available for curation.")
    
    @patch('main.cursor')
    @patch('main.PORTFOLIO', ['AAPL', 'TSLA'])
    def test_identify_knowledge_gaps(self, mock_cursor):
        """Test identify_knowledge_gaps functionality"""
        # Mock database responses for different queries
        def mock_execute_side_effect(query, params=None):
            if "COUNT(*)" in query and "REFINED" not in query:
                if params and params[0] == "AAPL":
                    return [(10,)]  # AAPL has 10 insights
                elif params and params[0] == "TSLA":
                    return [(3,)]   # TSLA has 3 insights
            elif "REFINED" in query:
                return [(2,)]  # Mock refined count
            elif "DATE(timestamp)" in query:
                return [
                    ("2024-01-01", 5),
                    ("2024-01-02", 3),
                    ("2024-01-03", 2)
                ]
        
        mock_cursor.fetchone.side_effect = mock_execute_side_effect
        mock_cursor.fetchall.return_value = [
            ("2024-01-01", 5),
            ("2024-01-02", 3),
            ("2024-01-03", 2)
        ]
        
        result = identify_knowledge_gaps()
        
        # Verify gap analysis
        self.assertIn("KNOWLEDGE GAP ANALYSIS", result)
        self.assertIn("AAPL", result)
        self.assertIn("TSLA", result)
        self.assertIn("RECENT ACTIVITY", result)
        self.assertIn("RECOMMENDATIONS", result)

class TestEmailNotifications(unittest.TestCase):
    """Test suite for email notification functionality"""
    
    @patch('main.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending"""
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        result = send_email("Test Subject", "Test Body", "test@example.com")
        
        # Verify SMTP interaction
        mock_smtp.assert_called_once()
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()
        
        # Check return value
        self.assertTrue(result)
    
    @patch('main.smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp):
        """Test email sending failure"""
        mock_smtp.side_effect = Exception("SMTP Error")
        
        result = send_email("Test Subject", "Test Body", "test@example.com")
        
        # Check return value for failure
        self.assertFalse(result)

class TestKnowledgeEvolution(unittest.TestCase):
    """Test suite for knowledge evolution functionality"""
    
    @patch('main.cursor')
    def test_query_knowledge_evolution_sufficient_data(self, mock_cursor):
        """Test query_knowledge_evolution with sufficient data"""
        # Mock insights data
        mock_cursor.fetchall.return_value = [
            ("Test insight 1", "2024-01-01 10:00:00"),
            ("REFINED: Test insight 2", "2024-01-01 11:00:00"),
            ("Test insight 3", "2024-01-01 12:00:00")
        ]
        
        result = query_knowledge_evolution("AAPL")
        
        # Verify evolution analysis
        self.assertIn("Knowledge evolution for AAPL", result)
        self.assertIn("3 insights", result)
        self.assertIn("Refined insights: 1/3", result)
    
    @patch('main.cursor')
    def test_query_knowledge_evolution_insufficient_data(self, mock_cursor):
        """Test query_knowledge_evolution with insufficient data"""
        mock_cursor.fetchall.return_value = [
            ("Test insight 1", "2024-01-01 10:00:00")
        ]
        
        result = query_knowledge_evolution("AAPL")
        
        # Verify insufficient data message
        self.assertIn("Insufficient data", result)
        self.assertIn("Only 1 insights", result)

class TestIntegration(unittest.TestCase):
    """Integration tests for tool interactions"""
    
    @patch('main.yf.download')
    @patch('main.cursor')
    @patch('main.conn')
    def test_end_to_end_analysis_flow(self, mock_conn, mock_cursor, mock_download):
        """Test complete analysis flow from data fetch to insight storage"""
        # Mock stock data with high volatility
        mock_data = pd.DataFrame({
            'Close': [100, 107, 95, 110, 88]  # High volatility
        })
        mock_download.return_value = mock_data
        
        # Mock past insights for knowledge evolution
        mock_cursor.fetchall.return_value = [
            ("Past insight 1", "2024-01-01 10:00:00"),
            ("Past insight 2", "2024-01-01 11:00:00")
        ]
        
        with patch('main.send_email') as mock_email:
            # Test the flow
            fetch_result = fetch_stock_data("AAPL")
            impact_result = determine_impact_level("AAPL")
            
            # Verify high impact detection
            self.assertIn("AAPL", fetch_result)
            self.assertIn("high", impact_result)
            
            # Verify email notification
            mock_email.assert_called()
            
            # Test knowledge evolution
            past_insights = query_past_insights("AAPL")
            self.assertIn("Past insight", past_insights)

if __name__ == '__main__':
    # Configure test runner
    unittest.main(verbosity=2, buffer=True) 