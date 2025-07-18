import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..database.supabase_manager import supabase_manager

class BaseAgent:
    """
    Base class for all agents with Supabase integration
    
    This class provides a unified interface for all agents to interact with the database,
    handling common operations like storing insights, events, and retrieving data.
    """
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.storage = supabase_manager
        
        # Validate storage manager
        if not self.storage:
            logging.error(f"Supabase manager not initialized for {agent_name}")
            raise ValueError(f"Database connection not available for {agent_name}")
    
    async def store_insight(self, ticker: str, insight: str, 
                          metadata: Optional[Dict[str, Any]] = None,
                          volatility: Optional[float] = None,
                          impact_level: Optional[str] = None,
                          confidence: Optional[float] = None) -> Dict[str, Any]:
        """
        Store insight in Supabase with real-time updates
        
        Args:
            ticker: Stock ticker symbol
            insight: The insight text
            metadata: Additional metadata as JSON
            volatility: Stock volatility (0-1)
            impact_level: Impact level (LOW, MEDIUM, HIGH)
            confidence: Confidence score (0-1)
            
        Returns:
            Dict with success status and insight_id
        """
        try:
            result = await self.storage.store_insight(
                ticker=ticker,
                insight=insight,
                agent=self.agent_name,
                metadata=metadata,
                volatility=volatility,
                impact_level=impact_level,
                confidence=confidence
            )
            
            if result["success"]:
                logging.info(f"{self.agent_name} stored insight for {ticker}: {insight[:50]}...")
            else:
                logging.error(f"{self.agent_name} failed to store insight: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logging.error(f"{self.agent_name} error storing insight: {e}")
            return {"success": False, "error": str(e)}
    
    async def store_event(self, event_type: str, ticker: str, message: str,
                        severity: str = "INFO",
                        metadata: Optional[Dict[str, Any]] = None,
                        volatility: Optional[float] = None,
                        volume_spike: Optional[float] = None,
                        portfolio_risk: Optional[str] = None) -> Dict[str, Any]:
        """
        Store event in Supabase with real-time broadcasting
        
        Args:
            event_type: Type of event
            ticker: Stock ticker symbol
            message: Event message
            severity: Event severity (INFO, LOW, MEDIUM, HIGH, CRITICAL)
            metadata: Additional metadata as JSON
            volatility: Stock volatility
            volume_spike: Volume spike ratio
            portfolio_risk: Portfolio risk level
            
        Returns:
            Dict with success status and event_id
        """
        try:
            result = await self.storage.store_event(
                event_type=event_type,
                ticker=ticker,
                message=message,
                severity=severity,
                metadata=metadata,
                volatility=volatility,
                volume_spike=volume_spike,
                portfolio_risk=portfolio_risk
            )
            
            if result["success"]:
                logging.info(f"{self.agent_name} stored {severity} event for {ticker}: {message[:50]}...")
            else:
                logging.error(f"{self.agent_name} failed to store event: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logging.error(f"{self.agent_name} error storing event: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_insights(self, ticker: Optional[str] = None, limit: int = 10,
                         impact_level: Optional[str] = None,
                         time_window_hours: Optional[int] = None) -> Dict[str, Any]:
        """
        Get insights with filtering
        
        Args:
            ticker: Filter by ticker symbol
            limit: Maximum number of insights to return
            impact_level: Filter by impact level
            time_window_hours: Filter by time window in hours
            
        Returns:
            Dict with insights list and metadata
        """
        try:
            result = await self.storage.get_insights(
                ticker=ticker,
                limit=limit,
                agent=self.agent_name,
                impact_level=impact_level,
                time_window_hours=time_window_hours
            )
            
            if result["success"]:
                logging.info(f"{self.agent_name} retrieved {len(result['insights'])} insights")
            else:
                logging.error(f"{self.agent_name} failed to get insights: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logging.error(f"{self.agent_name} error getting insights: {e}")
            return {"success": False, "error": str(e), "insights": []}
    
    async def get_events(self, ticker: Optional[str] = None, 
                       event_type: Optional[str] = None,
                       severity: Optional[str] = None,
                       time_window_hours: int = 24,
                       limit: int = 50) -> Dict[str, Any]:
        """
        Get events with filtering
        
        Args:
            ticker: Filter by ticker symbol
            event_type: Filter by event type
            severity: Filter by severity level
            time_window_hours: Filter by time window in hours
            limit: Maximum number of events to return
            
        Returns:
            Dict with events list and metadata
        """
        try:
            result = await self.storage.get_events(
                ticker=ticker,
                event_type=event_type,
                severity=severity,
                time_window_hours=time_window_hours,
                limit=limit
            )
            
            if result["success"]:
                logging.info(f"{self.agent_name} retrieved {len(result['events'])} events")
            else:
                logging.error(f"{self.agent_name} failed to get events: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logging.error(f"{self.agent_name} error getting events: {e}")
            return {"success": False, "error": str(e), "events": []}
    
    async def store_knowledge_evolution(self, ticker: str, evolution_type: str,
                                      previous_insight: str, refined_insight: str,
                                      improvement_score: float,
                                      context: Optional[str] = None,
                                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Store knowledge evolution tracking
        
        Args:
            ticker: Stock ticker symbol
            evolution_type: Type of evolution
            previous_insight: Previous insight text
            refined_insight: Refined insight text
            improvement_score: Improvement score (0-1)
            context: Additional context
            metadata: Additional metadata
            
        Returns:
            Dict with success status and evolution_id
        """
        try:
            result = await self.storage.store_knowledge_evolution(
                ticker=ticker,
                evolution_type=evolution_type,
                previous_insight=previous_insight,
                refined_insight=refined_insight,
                improvement_score=improvement_score,
                agent=self.agent_name,
                context=context,
                metadata=metadata
            )
            
            if result["success"]:
                logging.info(f"{self.agent_name} stored knowledge evolution for {ticker}")
            else:
                logging.error(f"{self.agent_name} failed to store knowledge evolution: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logging.error(f"{self.agent_name} error storing knowledge evolution: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_knowledge_evolution(self, ticker: Optional[str] = None,
                                   evolution_type: Optional[str] = None,
                                   limit: int = 20) -> Dict[str, Any]:
        """
        Get knowledge evolution with trend analysis
        
        Args:
            ticker: Filter by ticker symbol
            evolution_type: Filter by evolution type
            limit: Maximum number of evolutions to return
            
        Returns:
            Dict with evolutions list and trend analysis
        """
        try:
            result = await self.storage.get_knowledge_evolution(
                ticker=ticker,
                evolution_type=evolution_type,
                agent=self.agent_name,
                limit=limit
            )
            
            if result["success"]:
                logging.info(f"{self.agent_name} retrieved {len(result['evolutions'])} knowledge evolutions")
            else:
                logging.error(f"{self.agent_name} failed to get knowledge evolution: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logging.error(f"{self.agent_name} error getting knowledge evolution: {e}")
            return {"success": False, "error": str(e), "evolutions": []}
    
    async def store_system_metric(self, metric_type: str, metric_value: float,
                                additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Store system performance metrics
        
        Args:
            metric_type: Type of metric
            metric_value: Metric value
            additional_data: Additional data as JSON
            
        Returns:
            Dict with success status and metric_id
        """
        try:
            # Add agent context to additional data
            if additional_data is None:
                additional_data = {}
            additional_data["agent"] = self.agent_name
            
            result = await self.storage.store_system_metric(
                metric_type=metric_type,
                metric_value=metric_value,
                additional_data=additional_data
            )
            
            if result["success"]:
                logging.info(f"{self.agent_name} stored system metric: {metric_type} = {metric_value}")
            else:
                logging.error(f"{self.agent_name} failed to store system metric: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logging.error(f"{self.agent_name} error storing system metric: {e}")
            return {"success": False, "error": str(e)}
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get agent information
        
        Returns:
            Dict with agent information
        """
        return {
            "agent_name": self.agent_name,
            "storage_available": self.storage is not None,
            "timestamp": datetime.now().isoformat()
        }
    
    async def run_async_task(self, task_func, *args, **kwargs):
        """
        Helper method to run async tasks with error handling
        
        Args:
            task_func: Async function to run
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function or error dict
        """
        try:
            return await task_func(*args, **kwargs)
        except Exception as e:
            logging.error(f"{self.agent_name} async task error: {e}")
            return {"success": False, "error": str(e)}
    
    def run_sync_task(self, async_func, *args, **kwargs):
        """
        Helper method to run async functions from sync context
        
        Args:
            async_func: Async function to run
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function or error dict
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, create a task
                return asyncio.create_task(async_func(*args, **kwargs))
            else:
                # If not in async context, run with asyncio.run
                return asyncio.run(async_func(*args, **kwargs))
        except Exception as e:
            logging.error(f"{self.agent_name} sync task error: {e}")
            return {"success": False, "error": str(e)}


class AsyncAgentMixin:
    """
    Mixin class for agents that need async functionality
    
    This mixin provides utilities for running async operations in sync contexts
    and handling async/await patterns consistently.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._async_context = None
    
    async def initialize_async(self):
        """Initialize async resources"""
        if hasattr(self.storage, '_get_pool'):
            await self.storage._get_pool()
    
    async def cleanup_async(self):
        """Cleanup async resources"""
        if hasattr(self.storage, 'close'):
            await self.storage.close()
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize_async()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup_async()


# Example usage and testing
async def test_base_agent():
    """Test the base agent functionality"""
    try:
        agent = BaseAgent("TestAgent")
        
        # Test storing insight
        insight_result = await agent.store_insight(
            ticker="AAPL",
            insight="Test insight from base agent",
            volatility=0.02,
            impact_level="MEDIUM",
            confidence=0.85
        )
        
        print(f"Insight stored: {insight_result}")
        
        # Test storing event
        event_result = await agent.store_event(
            event_type="TEST_EVENT",
            ticker="AAPL",
            message="Test event from base agent",
            severity="INFO"
        )
        
        print(f"Event stored: {event_result}")
        
        # Test getting insights
        insights = await agent.get_insights(ticker="AAPL", limit=5)
        print(f"Retrieved insights: {len(insights.get('insights', []))}")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_base_agent()) 